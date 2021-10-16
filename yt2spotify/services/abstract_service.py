from abc import ABC, abstractmethod

from yt2spotify.models import SearchParams, SearchResult


class MusicService(ABC):
    @abstractmethod
    def url_to_search_params(self, url: str) -> SearchParams:
        pass

    @abstractmethod
    def search_with_params(self, params: SearchParams) -> SearchResult:
        pass
