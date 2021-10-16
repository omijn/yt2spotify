import configparser
import os
import re
from typing import Optional, Tuple

from spotipy import Spotify

from yt2spotify.models import SearchParams, SearchResult, AlbumDetails, SearchResultItem
from yt2spotify.services.abstract_service import MusicService


def read_spotify_config(config_path: str) -> Tuple[str, str]:
    config = configparser.ConfigParser()
    config.read(config_path)
    client_id = config['spotify']['client_id']
    client_secret = config['spotify']['client_secret']

    return client_id, client_secret


client_id, client_secret = read_spotify_config('config.ini')
os.environ['SPOTIPY_CLIENT_ID'] = client_id
os.environ['SPOTIPY_CLIENT_SECRET'] = client_secret


class SpotifyService(MusicService):
    spotifypattern = re.compile(r'(?:https://)?open\.spotify\.com/track/.*')

    def __init__(self, sp_client: Optional[Spotify] = None):
        self.sp_client = sp_client if sp_client is not None else Spotify()

    def url_to_search_params(self, url: str) -> SearchParams:
        if not self.spotifypattern.match(url):
            raise ValueError("Invalid Spotify URL")

        track_info = self.sp_client.track(url)
        track_name = track_info['name']
        track_album = track_info['album']['name']
        track_artist = track_info['artists'][0]['name']

        return SearchParams(name=track_name, album=track_album, artist=track_artist)

    def search_with_params(self, params: SearchParams) -> SearchResult:
        spotify_search_query = f"{params.name} {params.artist}"
        results = self.sp_client.search(spotify_search_query, limit=10, type="track")

        response = []
        for item in results['tracks']['items']:
            resp_item = SearchResultItem(
                url=item['external_urls']['spotify'],
                uri=item['uri'],
                name=item['name'],
                artists=[artist['name'] for artist in item['artists']],
                album=AlbumDetails(
                    art_url=item['album']['images'][0]['url'],
                    name=item['album']['name'],
                    release_year=item['album']['release_date'][:4]
                )
            )

            response.append(resp_item)

        manual_search_link = f"https://open.spotify.com/search/{spotify_search_query}"
        return SearchResult.parse_obj({'results': response, 'manual_search_link': manual_search_link})
