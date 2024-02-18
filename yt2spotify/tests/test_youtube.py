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
        ("https://youtu.be/5waF8YR3GmQ", "song")    # short link
    ]
)
def test_url_parsing(test_url, expected_search_hint):
    assert os.getenv("YOUTUBE_API_KEY") is not None
    yt = MusicServiceFactory.create(ServiceNameEnum.YOUTUBE_STANDARD)
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
    yt = MusicServiceFactory.create(ServiceNameEnum.YOUTUBE_STANDARD)
    results = yt.search_with_params(search_params)
    assert len(results.results) > 0