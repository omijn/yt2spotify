import os

import pytest

from yt2spotify.converter import Converter
from yt2spotify.services.factory import MusicServiceFactory
from yt2spotify.services.service_names import ServiceNameEnum


@pytest.mark.parametrize("test_url",
    [
        "https://music.youtube.com/watch?v=dGeEuyG_DIc&feature=share", # song
        "https://music.youtube.com/playlist?list=OLAK5uy_nbZjqOa38wTK9K4tvhOgPfyKdRnXnYT_4&si=ovpniEj_3ETQJTD6", # album
        "https://music.youtube.com/channel/UC2XdaAVUannpujzv32jcouQ", # artist
    ])
def test_convert_ytm_to_spotify(test_url):
    assert os.getenv("SPOTIPY_CLIENT_ID") is not None
    assert os.getenv("SPOTIPY_CLIENT_SECRET") is not None
    ytm = MusicServiceFactory.create(ServiceNameEnum.YOUTUBE_MUSIC)
    sp = MusicServiceFactory.create(ServiceNameEnum.SPOTIFY)

    converter = Converter(ytm, sp)

    results = converter.convert(test_url)
    assert len(results.results) > 0

@pytest.mark.parametrize("test_url",
    [
        "https://open.spotify.com/track/4cOdK2wGLETKBW3PvgPWqT", # song
        "https://open.spotify.com/album/2FeyIYDDAQqcOJKOKhvHdr", # album
        "https://open.spotify.com/artist/66CXWjxzNUsdJxJ2JdwvnR", # artist
    ])
def test_convert_spotify_to_ytm(test_url):
    assert os.getenv("SPOTIPY_CLIENT_ID") is not None
    assert os.getenv("SPOTIPY_CLIENT_SECRET") is not None
    ytm = MusicServiceFactory.create(ServiceNameEnum.YOUTUBE_MUSIC)
    sp = MusicServiceFactory.create(ServiceNameEnum.SPOTIFY)

    converter = Converter(sp, ytm)

    results = converter.convert(test_url)
    assert len(results.results) > 0


@pytest.mark.parametrize("test_url",
    [
        "https://open.spotify.com/track/4cOdK2wGLETKBW3PvgPWqT", # song
        "https://open.spotify.com/album/2FeyIYDDAQqcOJKOKhvHdr", # album
        "https://open.spotify.com/artist/66CXWjxzNUsdJxJ2JdwvnR", # artist
    ])
def test_convert_spotify_to_yt(test_url):
    assert os.getenv("SPOTIPY_CLIENT_ID") is not None
    assert os.getenv("SPOTIPY_CLIENT_SECRET") is not None
    assert os.getenv("YOUTUBE_API_KEY") is not None
    yt = MusicServiceFactory.create(ServiceNameEnum.YOUTUBE_YTM)
    sp = MusicServiceFactory.create(ServiceNameEnum.SPOTIFY)

    converter = Converter(sp, yt)

    results = converter.convert(test_url)
    assert len(results.results) > 0

