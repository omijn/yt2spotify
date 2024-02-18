import re
from typing import Optional
from urllib.parse import quote_plus

from ytmusicapi import YTMusic

from yt2spotify.errors import NotFoundError
from yt2spotify.models import SearchParams, SearchResult, SearchResultItem
from yt2spotify.services.abstract_service import MusicService
from yt2spotify.services.service_names import ServiceNameEnum, FormattedServiceNameEnum


class YoutubeMusicService(MusicService):
    ytmpattern = re.compile(r'(?:https://)?music\.youtube\.com/watch\?.*(?<=v=)([-\w]+).*')
    ytmchannel_pattern = re.compile(r'(?:https://)?music\.youtube\.com/channel/([-\w]+).*')
    ytmplaylist_pattern = re.compile(r'(?:https://)?music\.youtube\.com/playlist\?.*(?<=list=)([-\w]+).*')
    name = ServiceNameEnum.YOUTUBE_MUSIC

    def __init__(self, ytm_client: Optional[YTMusic] = None):
        self.ytm_client = ytm_client if ytm_client is not None else YTMusic()

    @classmethod
    def detect(cls, url: str) -> bool:
        if not cls.ytmpattern.match(url) and not cls.ytmchannel_pattern.match(url) and not cls.ytmplaylist_pattern.match(
                url):
            return False
        return True

    def url_to_search_params(self, url: str) -> SearchParams:
        video = self.ytmpattern.findall(url)
        if len(video) > 0:
            video_id = video[0]
            try:
                song = self.ytm_client.get_song(videoId=video_id)
            except Exception as e:
                if "not found" in str(e).lower() or "404" in str(e):
                    raise NotFoundError("song", FormattedServiceNameEnum.YOUTUBE_MUSIC)
                raise e
            song_title = song['videoDetails']['title']
            song_artist = song['videoDetails']['author'].removesuffix(" - Topic")
            return SearchParams(name=song_title, artist=song_artist, search_type_hint="song")

        channel = self.ytmchannel_pattern.findall(url)
        if len(channel) > 0:
            channel_id = channel[0]
            try:
                artist = self.ytm_client.get_artist(channelId=channel_id)
            except Exception as e:
                if "not found" in str(e).lower() or "404" in str(e):
                    raise NotFoundError("artist", FormattedServiceNameEnum.YOUTUBE_MUSIC)
                raise e
            artist_name = artist['name']
            return SearchParams(artist=artist_name, search_type_hint="artist")

        playlist = self.ytmplaylist_pattern.findall(url)
        if len(playlist) > 0:
            playlist_id = playlist[0]
            album_browse_id = self.ytm_client.get_album_browse_id(audioPlaylistId=playlist_id)
            try:
                album = self.ytm_client.get_album(browseId=album_browse_id)
            except Exception as e:
                if "not found" in str(e).lower() or "404" in str(e):
                    raise NotFoundError("album", FormattedServiceNameEnum.YOUTUBE_MUSIC)
                raise e
            album_name = album['title']
            album_artist = album['artists'][0]['name']
            return SearchParams(artist=album_artist, album=album_name, search_type_hint="album")

    def search_with_params(self, params: SearchParams) -> SearchResult:
        limit = 10
        if params.search_type_hint == "album":
            search_query = f"{params.album} {params.artist}"
            results = self.ytm_client.search(search_query, filter="albums", limit=limit)
            response = []
            for i, item in enumerate(results[:limit]):
                resp_item = SearchResultItem(
                    url=f"https://music.youtube.com/browse/{item['browseId']}",
                    uri=f"https://music.youtube.com/browse/{item['browseId']}",
                    description1=item['title'],
                    description2=item['year'] or '',
                    description3=", ".join([artist['name'] for artist in item['artists']]),
                    description4="Album",
                    art_url=item['thumbnails'][-1]['url'],
                )

                response.append(resp_item)

        elif params.search_type_hint == "artist":
            search_query = f"{params.artist}"
            results = self.ytm_client.search(search_query, filter="artists", limit=limit)

            response = []
            for i, item in enumerate(results[:limit]):
                resp_item = SearchResultItem(
                    url=f"https://music.youtube.com/channel/{item['browseId']}",
                    uri=f"https://music.youtube.com/channel/{item['browseId']}",
                    description1=item['artist'],
                    description4="Artist",
                    art_url=item['thumbnails'][-1]['url'],
                )

                response.append(resp_item)
        else:
            search_query = f"{params.name} {params.artist}"
            results = self.ytm_client.search(search_query, filter="songs", limit=limit)
            response = []
            for i, item in enumerate(results[:limit]):
                resp_item = SearchResultItem(
                    url=f"https://music.youtube.com/watch?v={item['videoId']}",
                    uri=f"https://music.youtube.com/watch?v={item['videoId']}",
                    description1=item['title'],
                    description2=f"{item['album']['name'] if item['album'] else 'Unknown album'} {'(' + item['year'] + ')' if item['year'] else ''}",
                    description3=", ".join([artist['name'] for artist in item['artists']]),
                    description4="Track",
                    art_url=item['thumbnails'][-1]['url'],
                )

                response.append(resp_item)

        manual_search_link = f"https://music.youtube.com/search?q={quote_plus(search_query)}"
        return SearchResult.parse_obj({'results': response, 'manual_search_link': manual_search_link})
