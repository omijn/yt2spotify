import os
import json
import spotipy
from spotipy import SpotifyClientCredentials
from ytmusicapi import YTMusic, OAuthCredentials
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
            ytm_client_id = os.environ.get("YOUTUBE_MUSIC_CLIENT_ID")
            ytm_client_secret = os.environ.get("YOUTUBE_MUSIC_CLIENT_SECRET")
            ytm_oauth_json = os.environ.get("YOUTUBE_MUSIC_OAUTH_JSON")
            ytm_oauth = json.loads(ytm_oauth_json)
            ytm_client = YTMusic(ytm_oauth, oauth_credentials=OAuthCredentials(client_id=ytm_client_id, client_secret=ytm_client_secret))
            return YoutubeMusicService(ytm_client)
        elif name == ServiceNameEnum.YOUTUBE_STANDARD:
            api_key = os.environ.get("YOUTUBE_API_KEY")
            yt_client = googleapiclient.discovery.build("youtube", "v3", developerKey=api_key, cache_discovery=False)
            return YoutubeService(yt_client)
        elif name == ServiceNameEnum.YOUTUBE_YTM:
            ytm_service = YoutubeMusicService()
            api_key = os.environ.get("YOUTUBE_API_KEY")
            yt_client = googleapiclient.discovery.build("youtube", "v3", developerKey=api_key, cache_discovery=False)
            yt_service = YoutubeService(yt_client)
            return YoutubeYTMService(ytm_service, yt_service)