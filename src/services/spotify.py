from typing import Optional

from spotipy import Spotify

from src.models import SearchParams, SearchResult, AlbumDetails, SearchResultItem
from src.services.abstract_service import MusicService


class SpotifyService(MusicService):
    def __init__(self, sp_client: Optional[Spotify] = None):
        self.sp_client = sp_client if sp_client is not None else Spotify()

    def url_to_search_params(self, url: str) -> SearchParams:
        pass

    def search_with_params(self, params: SearchParams) -> SearchResult:
        spotify_search_query = f"{params.name} {params.artist}"
        results = self.sp_client.search(spotify_search_query, limit=10, type="track")

        response = []
        for item in results['tracks']['items']:
            resp_item = SearchResultItem(
                url=item['external_urls']['spotify'],
                uri=item['uri'],
                name=item['name'],
                artists=[artist['name'] for artist in item['artists']],
                album=AlbumDetails(
                    art_url=item['album']['images'][0]['url'],
                    name=item['album']['name'],
                    release_year=item['album']['release_date'][:4]
                )
            )

            response.append(resp_item)

        manual_search_link = f"https://open.spotify.com/search/{spotify_search_query}"
        return SearchResult.parse_obj({'results': response, 'manual_search_link': manual_search_link})
