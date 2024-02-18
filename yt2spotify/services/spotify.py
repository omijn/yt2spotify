import configparser
import re
from typing import Optional, Tuple
from urllib.parse import urljoin, urlparse

from spotipy import Spotify

from yt2spotify.models import SearchParams, SearchResult, SearchResultItem
from yt2spotify.services.abstract_service import MusicService
from yt2spotify.services.service_names import ServiceNameEnum


def read_spotify_config(config_path: str) -> Tuple[str, str]:
    config = configparser.ConfigParser()
    config.read(config_path)
    client_id = config['spotify']['client_id']
    client_secret = config['spotify']['client_secret']

    return client_id, client_secret


class SpotifyService(MusicService):
    spotifypattern = re.compile(r'(?:https://)?open\.spotify\.com/(track|artist|album)/.+')
    name = ServiceNameEnum.SPOTIFY

    def __init__(self, sp_client: Optional[Spotify] = None):
        self.sp_client = sp_client if sp_client is not None else Spotify()

    @classmethod
    def detect(cls, url: str) -> bool:
        if not cls.spotifypattern.match(url):
            return False
        return True

    def url_to_search_params(self, url: str) -> SearchParams:
        url = urljoin(url, urlparse(url).path)

        url_type = self.spotifypattern.findall(url)[0]
        if url_type == "track":
            track_info = self.sp_client.track(url)
            track_name = track_info['name']
            track_album = track_info['album']['name']
            track_artist = track_info['artists'][0]['name']
            return SearchParams(name=track_name, album=track_album, artist=track_artist, search_type_hint="song")
        elif url_type == "artist":
            artist_info = self.sp_client.artist(url)
            artist_name = artist_info['name']
            return SearchParams(artist=artist_name, search_type_hint="artist")
        else:
            album_info = self.sp_client.album(url)
            album_name = album_info['name']
            album_artist = album_info['artists'][0]['name']
            return SearchParams(album=album_name, artist=album_artist, search_type_hint="album")

    def search_with_params(self, params: SearchParams) -> SearchResult:
        if params.search_type_hint == "album":
            search_query = f"{params.album} {params.artist}"
            results = self.sp_client.search(search_query, limit=10, type="album")
            response = []
            for item in results['albums']['items']:
                resp_item = SearchResultItem(
                    url=item['external_urls']['spotify'] if 'external_urls' in item else "",
                    uri=item['uri'],
                    description1=item['name'],
                    description2=item['release_date'][:4],
                    description3=", ".join([artist['name'] for artist in item['artists']]),
                    description4="Album",
                    art_url=item['images'][0]['url'],
                )

                response.append(resp_item)

        elif params.search_type_hint == "artist":
            search_query = f"{params.artist}"
            results = self.sp_client.search(search_query, limit=10, type="artist")
            response = []
            for item in results['artists']['items']:
                resp_item = SearchResultItem(
                    url=item['external_urls']['spotify'],
                    uri=item['uri'],
                    description1=item['name'],
                    description4="Artist",
                    art_url=item['images'][0]['url'] if len(item['images']) > 0 else ""
                )

                response.append(resp_item)

        else:
            search_query = f"{params.name} {params.artist}"
            results = self.sp_client.search(search_query, limit=10, type="track")
            response = []
            for item in results['tracks']['items']:
                resp_item = SearchResultItem(
                    url=item['external_urls']['spotify'],
                    uri=item['uri'],
                    description1=item['name'],
                    description2=f"{item['album']['name']} ({item['album']['release_date'][:4]})",
                    description3=", ".join([artist['name'] for artist in item['artists']]),
                    description4="Track",
                    art_url=item['album']['images'][0]['url'],
                )

                response.append(resp_item)

        manual_search_link = f"https://open.spotify.com/search/{search_query}"
        return SearchResult.parse_obj({'results': response, 'manual_search_link': manual_search_link})
