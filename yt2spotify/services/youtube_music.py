from typing import List, Optional
import re
from urllib.parse import quote_plus

from yt2spotify.services.abstract_service import MusicService
from yt2spotify.models import SearchParams, SearchResult, SearchResultItem, AlbumDetails
from ytmusicapi import YTMusic


class YoutubeMusicService(MusicService):
    ytpattern = re.compile(r'(?:https://)?music\.youtube\.com/watch\?.*(?<=v=)([-\w]+).*')

    def __init__(self, yt_client: Optional[YTMusic] = None):
        self.yt_client = yt_client if yt_client is not None else YTMusic()

    def url_to_search_params(self, url: str) -> SearchParams:
        videos = self.ytpattern.findall(url)
        if len(videos) == 0:
            raise ValueError("Invalid YouTube Music URL")

        video_id = videos[0]
        song = self.yt_client.get_song(videoId=video_id)

        song_title = song['videoDetails']['title']
        song_artist = song['videoDetails']['author'].removesuffix(" - Topic")

        return SearchParams(name=song_title, artist=song_artist)

    def search_with_params(self, params: SearchParams) -> SearchResult:
        limit = 10
        search_query = f"{params.name} {params.artist}"
        results = self.yt_client.search(search_query, filter='songs', limit=limit)

        response = []
        for i, item in enumerate(results):
            resp_item = SearchResultItem(
                url=f"https://music.youtube.com/watch?v={item['videoId']}",
                uri=f"https://music.youtube.com/watch?v={item['videoId']}",
                name=item['title'],
                artists=[artist['name'] for artist in item['artists']],
                album=AlbumDetails(
                    art_url=item['thumbnails'][-1]['url'],
                    name=item['album']['name'],
                    release_year=item['year'] or ''
                )
            )

            response.append(resp_item)
            if i == (limit - 1):
                break

        manual_search_link = f"https://music.youtube.com/search?q={quote_plus(search_query)}"
        return SearchResult.parse_obj({'results': response, 'manual_search_link': manual_search_link})

