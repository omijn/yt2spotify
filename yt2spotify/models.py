from pydantic import BaseModel, Field, validator
from typing import List
from yt2spotify.services.service_names import ServiceNameEnum


class ConvertRequest(BaseModel):
    url: str = Field(..., description="URL to convert")
    from_service: ServiceNameEnum = Field(..., description="service to convert from")
    to_service: ServiceNameEnum = Field(..., description="service to convert to")

    @validator('to_service')
    def services_are_different(cls, v, values):
        if 'from_service' in values and v == values['from_service']:
            raise ValueError('from_service and to_service must be different')
        return v


class SearchParams(BaseModel):
    name: str = Field(...)
    album: str = Field(default=None)
    artist: str = Field(...)


class AlbumDetails(BaseModel):
    art_url: str = Field(default=None)
    name: str = Field(...)
    release_year: str = Field(default=None)


class SearchResultItem(BaseModel):
    url: str = Field(...)
    uri: str = Field(...)
    album: AlbumDetails = Field(...)
    name: str = Field(...)
    artists: List[str] = Field(...)


class SearchResult(BaseModel):
    results: List[SearchResultItem] = Field(default=[])
    manual_search_link: str = Field(...)
