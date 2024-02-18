import os
import re
from urllib.parse import quote_plus

import googleapiclient.discovery

from yt2spotify.models import SearchParams, SearchResult, SearchResultItem
from yt2spotify.services.abstract_service import MusicService
from yt2spotify.services.service_names import ServiceNameEnum


class YoutubeService(MusicService):
    ytpattern = re.compile(r'(?:https://)?(?:www\.)?youtube\.com/watch\?.*(?<=v=)([-\w]+).*')
    ytpattern_short_link = re.compile(r'(?:https://)?youtu\.be/([-_\w]+).*')
    ytchannel_pattern = re.compile(r'(?:https://)?(?:www\.)?youtube\.com/(?:(@[-\w]+)|channel/([-\w]+).*)')
    ytplaylist_pattern = re.compile(r'(?:https://)?(?:www\.)?youtube\.com/playlist\?.*(?<=list=)([-\w]+).*')
    name = ServiceNameEnum.YOUTUBE_STANDARD

    def __init__(self, yt_client = None):
        if yt_client is None:
            api_key = os.environ.get("YOUTUBE_API_KEY")
            self.yt_client = googleapiclient.discovery.build("youtube", "v3", developerKey=api_key)
        else:
            self.yt_client = yt_client

    @classmethod
    def detect(cls, url: str) -> bool:
        if (
                not cls.ytpattern.match(url)
                and not cls.ytchannel_pattern.match(url)
                and not cls.ytplaylist_pattern.match(url)
                and not cls.ytpattern_short_link.match(url)
        ):
            return False
        return True

    def url_to_search_params(self, url: str) -> SearchParams:
        if self.ytpattern_short_link.match(url):
            url = url.replace("youtu.be/", "youtube.com/watch?v=")
        video = self.ytpattern.findall(url)
        if len(video) > 0:
            video_id = video[0]
            resp = self.yt_client.videos().list(part="snippet", id=video_id).execute()
            song_title = resp["items"][0]["snippet"]["title"]
            song_artist = resp["items"][0]["snippet"]["channelTitle"]
            return SearchParams(name=song_title, artist=song_artist, search_type_hint="song")

        channel = self.ytchannel_pattern.findall(url)
        if len(channel) > 0:
            channel_id = channel[0][0] if channel[0][0] != "" else channel[0][1]
            if channel_id.startswith("@"):
                resp = self.yt_client.channels().list(part="snippet", forHandle=channel_id).execute()
            else:
                resp = self.yt_client.channels().list(part="snippet", id=channel_id).execute()
            artist_name = resp["items"][0]["snippet"]["title"]
            return SearchParams(artist=artist_name, search_type_hint="artist")

        playlist = self.ytplaylist_pattern.findall(url)
        if len(playlist) > 0:
            playlist_id = playlist[0]
            resp = self.yt_client.playlists().list(part="snippet", id=playlist_id).execute()
            album_name = resp["items"][0]["snippet"]["title"]
            album_artist = resp["items"][0]["snippet"]["channelTitle"]
            if album_artist.lower() == "youtube":
                album_artist = ""
            return SearchParams(artist=album_artist, album=album_name, search_type_hint="album")

    def search_with_params(self, params: SearchParams) -> SearchResult:
        limit = 10
        if params.search_type_hint == "album":
            search_query = f"{params.album} {params.artist}"
            result = self.yt_client.search().list(q=search_query, type="album", part="snippet", maxResults=limit).execute()
            response = []
            for i, item in enumerate(result["items"]):
                if item["id"]["kind"] != "youtube#playlist":
                    continue
                resp_item = SearchResultItem(
                    url=f"https://youtube.com/playlist?list={item['id']['playlistId']}",
                    uri=f"https://youtube.com/playlist?list={item['id']['playlistId']}",
                    description1=item["snippet"]["title"],
                    description2='',
                    description3=item["snippet"]["channelTitle"],
                    description4="Album",
                    art_url=item["snippet"]["thumbnails"]["high"]["url"]
                )

                response.append(resp_item)

        elif params.search_type_hint == "artist":
            search_query = f"{params.artist}"
            results = self.yt_client.search().list(q=search_query, type="channel", part="snippet", maxResults=limit).execute()

            response = []
            for i, item in enumerate(results["items"]):
                resp_item = SearchResultItem(
                    url=f"https://youtube.com/channel/{item['id']['channelId']}",
                    uri=f"https://youtube.com/channel/{item['id']['channelId']}",
                    description1=item["snippet"]["title"],
                    description4="Artist",
                    art_url=item["snippet"]["thumbnails"]["high"]["url"]
                )

                response.append(resp_item)
        else:
            search_query = f"{params.name} {params.artist}"
            results = self.yt_client.search().list(q=search_query, type="video", part="snippet", maxResults=limit).execute()
            response = []
            for i, item in enumerate(results["items"]):
                resp_item = SearchResultItem(
                    url=f"https://youtube.com/watch?v={item['id']['videoId']}",
                    uri=f"https://youtube.com/watch?v={item['id']['videoId']}",
                    description1=item["snippet"]["title"],
                    description2=item["snippet"]["channelTitle"],
                    description3="",
                    description4="Track",
                    art_url=item["snippet"]["thumbnails"]["high"]["url"]
                )

                response.append(resp_item)

        manual_search_link = f"https://www.youtube.com/results?search_query={quote_plus(search_query)}"
        return SearchResult(results=response, manual_search_link=manual_search_link)
