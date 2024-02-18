from enum import Enum


class ServiceNameEnum(str, Enum):
    YOUTUBE_MUSIC = 'youtube_music'
    SPOTIFY = 'spotify'
    YOUTUBE_STANDARD = 'youtube'
    YOUTUBE_YTM = 'youtube_ytm'

class FormattedServiceNameEnum(str, Enum):
    YOUTUBE_MUSIC = 'YouTube Music'
    SPOTIFY = 'Spotify'

