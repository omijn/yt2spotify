from yt2spotify.services.abstract_service import MusicService
from yt2spotify.services.factory import MusicServiceFactory
from yt2spotify.services.service_names import ServiceNameEnum


class Converter:
    def __init__(self, from_service: MusicService, to_service: MusicService):
        self.from_service = from_service
        self.to_service = to_service

    @classmethod
    def by_names(cls, from_service_name: ServiceNameEnum, to_service_name: ServiceNameEnum):
        from_service = MusicServiceFactory.create(from_service_name)
        to_service = MusicServiceFactory.create(to_service_name)
        return cls(from_service, to_service)

    def convert(self, url):
        search_params = self.from_service.url_to_search_params(url)
        search_results = self.to_service.search_with_params(search_params)
        return search_results
