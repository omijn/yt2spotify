import re

from yt2spotify.models import SearchParams, SearchResult
from yt2spotify.services.abstract_service import MusicService
from yt2spotify.services.service_names import ServiceNameEnum
from yt2spotify.services.youtube_music import YoutubeMusicService
from yt2spotify.services.youtube_standard import YoutubeService


class YoutubeYTMService(MusicService):
    """
    YouTube Client that uses the YTM client to search for songs, artists, and albums
    to avoid using up the standard client's quota. Uses the YT client to convert the
    url to search params.
    """
    ytpattern = re.compile(r'(?:https://)?(?:www\.)?youtube\.com/watch\?.*(?<=v=)([-\w]+).*')
    ytpattern_short_link = re.compile(r'(?:https://)?youtu\.be/([-_\w]+).*')
    ytchannel_pattern = re.compile(r'(?:https://)?(?:www\.)?youtube\.com/(?:(@[-\w]+)|channel/([-\w]+).*)')
    ytplaylist_pattern = re.compile(r'(?:https://)?(?:www\.)?youtube\.com/playlist\?.*(?<=list=)([-\w]+).*')
    name = ServiceNameEnum.YOUTUBE_YTM

    def __init__(self, ytm_service: YoutubeMusicService, yt_service: YoutubeService):
        self.ytm_service = ytm_service
        self.yt_service = yt_service

    @classmethod
    def detect(cls, url: str) -> bool:
        # convert mobile youtube links to standard Youtube links
        url = url.replace("m.youtube.com", "youtube.com")

        if (
                not cls.ytpattern.match(url)
                and not cls.ytchannel_pattern.match(url)
                and not cls.ytplaylist_pattern.match(url)
                and not cls.ytpattern_short_link.match(url)
        ):
            return False
        return True

    def url_to_search_params(self, url: str) -> SearchParams:
        # url = url.replace("youtube.com", "music.youtube.com").replace("www.", "")
        # return self.ytm_service.url_to_search_params(url)
        
        # convert mobile youtube links to standard Youtube links
        url = url.replace("m.youtube.com", "youtube.com")
        return self.yt_service.url_to_search_params(url)

    def search_with_params(self, params: SearchParams) -> SearchResult:
        search_result = self.ytm_service.search_with_params(params)
        return self._convert_ytm_result_to_youtube_result(search_result)

    def _convert_ytm_result_to_youtube_result(self, ytm_result: SearchResult) -> SearchResult:
        """
        Convert the search result from YTM to YT
        """
        # iterate through results and convert urls/uris to standard YouTube urls by removing the music subdomain
        for result in ytm_result.results:
            result.url = result.url.replace("music.", "")
            result.uri = result.uri.replace("music.", "")

        ytm_result.manual_search_link = ytm_result.manual_search_link.replace("music.", "")
        ytm_result.manual_search_link = ytm_result.manual_search_link.replace("search?q=", "results?search_query=")

        return ytm_result
