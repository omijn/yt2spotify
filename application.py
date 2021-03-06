import os
from urllib.parse import unquote

from flask import Flask, request, Response

from yt2spotify import models
from yt2spotify.converter import Converter
from yt2spotify.services.spotify import SpotifyService
from yt2spotify.services.youtube_music import YoutubeMusicService

application = Flask(__name__)

required_vars = ['SPOTIPY_CLIENT_ID', 'SPOTIPY_CLIENT_SECRET']
for var in required_vars:
    if var not in os.environ:
        raise Exception(f"'{var}' env var is required")


@application.route('/')
def index():
    return application.send_static_file('index.html')


@application.route('/convert', methods=['GET'])
def convert():
    url = request.args.get('url')

    from_service = None
    for cls in [YoutubeMusicService, SpotifyService]:
        if cls.detect(url):
            from_service = cls.name
            break

    if from_service is None:
        return Response(response="URL doesn't match any known streaming services", status=400)

    to_service = request.args.get('to_service')
    try:
        req = models.ConvertRequest(url=url, from_service=from_service, to_service=to_service)
    except Exception as e:
        # TODO: be more specific about error
        return Response(response="You need to provide a link to convert and select a service to convert from and to",
                        status=400)

    url = unquote(req.url)
    converter = Converter.by_names(from_service_name=req.from_service, to_service_name=req.to_service)

    try:
        result = converter.convert(url)
        return Response(response=result.json(), status=200, mimetype='application/json')
    except ValueError as e:
        return Response(response=str(e), status=400)
    except Exception as e:
        return Response(response="That didn't work.", status=500)


if __name__ == "__main__":
    application.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
