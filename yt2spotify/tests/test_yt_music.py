import pytest

from yt2spotify.services.factory import MusicServiceFactory
from yt2spotify.services.service_names import ServiceNameEnum


@pytest.mark.parametrize("test_url,expected_search_hint",
    [
        ("https://music.youtube.com/watch?v=agPV1ZvtLHI&si=klsijOktQeoa4avd", "song"),
        ("https://music.youtube.com/playlist?list=OLAK5uy_l1U925dsiDi2DqlG-KCbODG6BaibpxbQE&si=4BaMhBCiremnvdil", "album"),
        ("https://music.youtube.com/channel/UCoIOOL7QKuBhQHVKL8y7BEQ?si=osCb8S8l7ZmRUPlU", "artist")
    ]
)
def test_url_parsing(test_url, expected_search_hint):
    yt = MusicServiceFactory.create(ServiceNameEnum.YOUTUBE_MUSIC)
    search_params = yt.url_to_search_params(test_url)
    assert search_params.search_type_hint == expected_search_hint