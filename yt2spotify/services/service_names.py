from enum import Enum


class ServiceNameEnum(str, Enum):
    YOUTUBE_MUSIC = 'youtube_music'
    SPOTIFY = 'spotify'

class FormattedServiceNameEnum(str, Enum):
    YOUTUBE_MUSIC = 'YouTube Music'
    SPOTIFY = 'Spotify'

