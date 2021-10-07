import spotipy
from spotipy import SpotifyClientCredentials

from yt2spotify.converter import Converter
from yt2spotify.services.spotify import SpotifyService, read_spotify_config
from yt2spotify.services.youtube_music import YoutubeMusicService


def test_convert_yt_to_spotify():
    yt = YoutubeMusicService()
    client_id, client_secret = read_spotify_config('../../config.ini')
    sp_client = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=client_id, client_secret=client_secret))
    sp = SpotifyService(sp_client)

    converter = Converter(yt, sp)

    results = converter.convert("https://music.youtube.com/watch?v=dGeEuyG_DIc&feature=share")
    assert len(results.results) > 0


def test_convert_spotify_to_y2():
    yt = YoutubeMusicService()
    client_id, client_secret = read_spotify_config('../../config.ini')
    sp_client = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=client_id, client_secret=client_secret))
    sp = SpotifyService(sp_client)

    converter = Converter(sp, yt)

    results = converter.convert("https://open.spotify.com/track/4cOdK2wGLETKBW3PvgPWqT")
    assert len(results.results) > 0

