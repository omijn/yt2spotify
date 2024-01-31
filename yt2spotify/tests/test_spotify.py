import os

import pytest

from yt2spotify.services.factory import MusicServiceFactory
from yt2spotify.services.service_names import ServiceNameEnum


@pytest.mark.parametrize("test_url,expected_search_hint",
    [
        ("https://open.spotify.com/track/6jBCehpNMkwFVF3dz4nLIW?si=y1dqtIB0SumdJGBqKSASQg&context=spotify%3Asearch%3Aits%2Btricky", "song"),
        ("https://open.spotify.com/track/4uJSCrI7r0usNJ3aaHAuC6?si=e4509e1f214946fb", "song"),
        ("https://open.spotify.com/album/7kjLKy9JLbwM9F7eDQEnd2", "album"),
        ("https://open.spotify.com/artist/66CXWjxzNUsdJxJ2JdwvnR", "artist")
    ]
)
def test_url_parsing(test_url, expected_search_hint):
    assert os.getenv("SPOTIPY_CLIENT_ID") is not None
    assert os.getenv("SPOTIPY_CLIENT_SECRET") is not None
    sp = MusicServiceFactory.create(ServiceNameEnum.SPOTIFY)
    search_params = sp.url_to_search_params(test_url)
    assert search_params.search_type_hint == expected_search_hint