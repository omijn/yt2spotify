import spotipy
from spotipy import SpotifyClientCredentials

from yt2spotify.services.abstract_service import MusicService
from yt2spotify.services.service_names import ServiceNameEnum
from yt2spotify.services.spotify import SpotifyService
from yt2spotify.services.youtube_music import YoutubeMusicService


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
