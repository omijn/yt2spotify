import os

import spotipy
from spotipy import SpotifyClientCredentials

from yt2spotify.services.abstract_service import MusicService
from yt2spotify.services.service_names import ServiceNameEnum
from yt2spotify.services.spotify import SpotifyService
from yt2spotify.services.youtube_standard import YoutubeService
from yt2spotify.services.youtube_music import YoutubeMusicService

import googleapiclient.discovery

from yt2spotify.services.youtube_ytm import YoutubeYTMService


class MusicServiceFactory:
    @classmethod
    def create(cls, name: ServiceNameEnum) -> MusicService:
        if name == ServiceNameEnum.SPOTIFY:
            # auth manager gets creds from environment variables
            auth_manager = SpotifyClientCredentials()
            spotify_client = spotipy.Spotify(auth_manager=auth_manager)
            return SpotifyService(spotify_client)
        elif name == ServiceNameEnum.YOUTUBE_MUSIC:
            return YoutubeMusicService()
        elif name == ServiceNameEnum.YOUTUBE_STANDARD:
            api_key = os.environ.get("YOUTUBE_API_KEY")
            yt_client = googleapiclient.discovery.build("youtube", "v3", developerKey=api_key)
            return YoutubeService(yt_client)
        elif name == ServiceNameEnum.YOUTUBE_YTM:
            ytm_service = YoutubeMusicService()
            api_key = os.environ.get("YOUTUBE_API_KEY")
            yt_client = googleapiclient.discovery.build("youtube", "v3", developerKey=api_key)
            yt_service = YoutubeService(yt_client)
            return YoutubeYTMService(ytm_service, yt_service)