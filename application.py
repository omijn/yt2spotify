from urllib.parse import unquote

import spotipy
from flask import Flask, request, Response
from spotipy.oauth2 import SpotifyClientCredentials

from yt2spotify import models
from yt2spotify.converter import Converter
from yt2spotify.services.service_names import ServiceNameEnum
from yt2spotify.services.spotify import SpotifyService, read_spotify_config
from yt2spotify.services.youtube_music import YoutubeMusicService

application = Flask(__name__)

client_id, client_secret = read_spotify_config('config.ini')
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=client_id, client_secret=client_secret))

ytmusic_service = YoutubeMusicService()
spotify_service = SpotifyService(sp)


def create_converter_name(from_service: ServiceNameEnum, to_service: ServiceNameEnum):
    return f"{from_service}-to-{to_service}"


converters = {
    create_converter_name(ServiceNameEnum.YOUTUBE_MUSIC, ServiceNameEnum.SPOTIFY):
        Converter(
            from_service=ytmusic_service,
            to_service=spotify_service
        ),
    create_converter_name(ServiceNameEnum.SPOTIFY, ServiceNameEnum.YOUTUBE_MUSIC):
        Converter(
            from_service=spotify_service,
            to_service=ytmusic_service
        )
}


@application.route('/')
def index():
    return application.send_static_file('index.html')


@application.route('/convert', methods=['GET'])
def convert():
    url = request.args.get('url')
    from_service = request.args.get('from_service')
    to_service = request.args.get('to_service')
    try:
        req = models.ConvertRequest(url=url, from_service=from_service, to_service=to_service)
    except Exception as e:
        return Response(response="You need to provide a link to convert and select a service to convert from and to",
                        status=400)

    url = unquote(req.url)
    converter_name = create_converter_name(req.from_service, req.to_service)
    converter = converters[converter_name]

    try:
        result = converter.convert(url)
        return Response(response=result.json(), status=200, mimetype='application/json')
    except ValueError as e:
        return Response(response=str(e), status=400)
    except Exception as e:
        return Response(response="That didn't work.", status=500)


if __name__ == "__main__":
    application.run(host='0.0.0.0', port=5000)
