import re
from typing import Optional
from urllib.parse import quote_plus

from ytmusicapi import YTMusic

from yt2spotify.models import SearchParams, SearchResult, SearchResultItem
from yt2spotify.services.abstract_service import MusicService
from yt2spotify.services.service_names import ServiceNameEnum


class YoutubeMusicService(MusicService):
    ytpattern = re.compile(r'(?:https://)?music\.youtube\.com/watch\?.*(?<=v=)([-\w]+).*')
    ytchannel_pattern = re.compile(r'(?:https://)?music\.youtube\.com/channel/([-\w]+).*')
    ytplaylist_pattern = re.compile(r'(?:https://)?music\.youtube\.com/playlist\?.*(?<=list=)([-\w]+).*')
    name = ServiceNameEnum.YOUTUBE_MUSIC

    def __init__(self, yt_client: Optional[YTMusic] = None):
        self.yt_client = yt_client if yt_client is not None else YTMusic()

    @classmethod
    def detect(cls, url: str) -> bool:
        if not cls.ytpattern.match(url) and not cls.ytchannel_pattern.match(url) and not cls.ytplaylist_pattern.match(
                url):
            return False
        return True

    def url_to_search_params(self, url: str) -> SearchParams:
        if not self.detect(url):
            raise ValueError("Invalid YouTube Music URL")

        video = self.ytpattern.findall(url)
        if len(video) > 0:
            video_id = video[0]
            song = self.yt_client.get_song(videoId=video_id)
            song_title = song['videoDetails']['title']
            song_artist = song['videoDetails']['author'].removesuffix(" - Topic")
            return SearchParams(name=song_title, artist=song_artist, search_type_hint="song")

        channel = self.ytchannel_pattern.findall(url)
        if len(channel) > 0:
            channel_id = channel[0]
            artist = self.yt_client.get_artist(channelId=channel_id)
            artist_name = artist['name']
            return SearchParams(artist=artist_name, search_type_hint="artist")

        playlist = self.ytplaylist_pattern.findall(url)
        if len(playlist) > 0:
            playlist_id = playlist[0]
            album_browse_id = self.yt_client.get_album_browse_id(audioPlaylistId=playlist_id)
            album = self.yt_client.get_album(browseId=album_browse_id)
            album_name = album['title']
            album_artist = album['artists'][0]['name']
            return SearchParams(artist=album_artist, album=album_name, search_type_hint="album")

    def search_with_params(self, params: SearchParams) -> SearchResult:
        limit = 10
        if params.search_type_hint == "album":
            search_query = f"{params.album} {params.artist}"
            results = self.yt_client.search(search_query, filter="albums", limit=limit)
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
            results = self.yt_client.search(search_query, filter="artists", limit=limit)

            response = []
            for i, item in enumerate(results[:limit]):
                resp_item = SearchResultItem(
                    url=f"https://music.youtube.com/browse/{item['browseId']}",
                    uri=f"https://music.youtube.com/browse/{item['browseId']}",
                    description1=item['artist'],
                    description4="Artist",
                    art_url=item['thumbnails'][-1]['url'],
                )

                response.append(resp_item)
        else:
            search_query = f"{params.name} {params.artist}"
            results = self.yt_client.search(search_query, filter="songs", limit=limit)
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
