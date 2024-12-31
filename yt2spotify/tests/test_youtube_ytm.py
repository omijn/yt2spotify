import os

import pytest

from yt2spotify.models import SearchParams
from yt2spotify.services.factory import MusicServiceFactory
from yt2spotify.services.service_names import ServiceNameEnum


@pytest.mark.parametrize("test_url,expected_search_hint",
    [
        ("https://www.youtube.com/@coldplay", "artist"),    # artist with custom handle
        ("https://www.youtube.com/channel/UCaziuyHLR37c2jBkHrYSQMA", "artist"),   # artist with channel id
        ("https://www.youtube.com/watch?v=dQw4w9WgXcQ", "song"),    # video title contains (Official Music Video)
        ("https://www.youtube.com/watch?v=ffxKSjUwKdU", "song"),    # video title contains (Official Video), channel name has Vevo
        ("https://www.youtube.com/watch?v=hT_nvWreIhg", "song"),    # normal video title but channel name has VEVO
        ("https://www.youtube.com/playlist?list=OLAK5uy_mbiRc-WQKXNRCfAeZBsoA-hILP3Oeu2WU", "album"),    # Coldplay - Everyday Life album (official), but channel name according to API is YouTube instead of Coldplay
        ("https://www.youtube.com/playlist?list=PLFAcddgaFN8zqIJrTakvM9qWnR7iIrXnj", "album"),   # Michael Jackson - Thriller album by MusicVevo channel
        ("https://youtu.be/5waF8YR3GmQ", "song"),    # short link
        ("https://m.youtube.com/watch?v=dQw4w9WgXcQ", "song"),    # Basic mobile video
        ("https://m.youtube.com/@coldplay", "artist"),            # Mobile artist page
        ("https://m.youtube.com/playlist?list=PLFAcddgaFN8zqIJrTakvM9qWnR7iIrXnj", "album")  # Mobile playlist
    ]
)
def test_url_parsing(test_url, expected_search_hint):
    assert os.getenv("YOUTUBE_API_KEY") is not None
    yt = MusicServiceFactory.create(ServiceNameEnum.YOUTUBE_YTM)
    search_params = yt.url_to_search_params(test_url)
    assert search_params.search_type_hint == expected_search_hint

@pytest.mark.parametrize("search_params",
    [
        SearchParams(artist="Coldplay", search_type_hint="artist"),
        SearchParams(name="Postcards from far away", artist="Coldplay", search_type_hint="artist"),
        SearchParams(album="Mylo Xyloto", artist="Coldplay", search_type_hint="album")
    ]
)
def test_search_with_params(search_params):
    assert os.getenv("YOUTUBE_API_KEY") is not None
    yt = MusicServiceFactory.create(ServiceNameEnum.YOUTUBE_YTM)
    results = yt.search_with_params(search_params)
    assert len(results.results) > 0

@pytest.mark.parametrize("mobile_url,regular_url", [
    ("https://m.youtube.com/watch?v=dQw4w9WgXcQ", "https://www.youtube.com/watch?v=dQw4w9WgXcQ"),
    ("https://m.youtube.com/@coldplay", "https://www.youtube.com/@coldplay"),
    ("https://m.youtube.com/playlist?list=PLFAcddgaFN8zqIJrTakvM9qWnR7iIrXnj", "https://www.youtube.com/playlist?list=PLFAcddgaFN8zqIJrTakvM9qWnR7iIrXnj")
])
def test_mobile_url_equivalence(mobile_url, regular_url):
    yt = MusicServiceFactory.create(ServiceNameEnum.YOUTUBE_YTM)
    mobile_params = yt.url_to_search_params(mobile_url)
    regular_params = yt.url_to_search_params(regular_url)
    assert mobile_params == regular_params