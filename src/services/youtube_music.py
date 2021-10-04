from typing import List, Optional
import re
from src.services.abstract_service import MusicService
from src.models import SearchParams, SearchResult
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

    def search_with_params(self, params: SearchParams) -> List[SearchResult]:
        pass
