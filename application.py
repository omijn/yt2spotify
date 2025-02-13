import logging
import os
from urllib.parse import unquote

from flask import Flask, request, Response
from pydantic import ValidationError

from yt2spotify import models
from yt2spotify.converter import Converter
from yt2spotify.errors import NotFoundError
from yt2spotify.services.spotify import SpotifyService
from yt2spotify.services.youtube_music import YoutubeMusicService
from yt2spotify.services.youtube_ytm import YoutubeYTMService

application = Flask(__name__)

required_vars = ['SPOTIPY_CLIENT_ID', 'SPOTIPY_CLIENT_SECRET', 'YOUTUBE_API_KEY']
for var in required_vars:
    if var not in os.environ:
        raise Exception(f"'{var}' env var is required")


@application.route('/convert', methods=['GET'])
def convert():
    url = request.args.get('url')

    from_service = None
    for cls in [YoutubeMusicService, SpotifyService, YoutubeYTMService]:
        if cls.detect(url):
            from_service = cls.name
            break

    if from_service is None:
        return Response(response="URL is incomplete or doesn't match any known streaming services", status=400)

    to_service = request.args.get('to_service')
    allowed_to_services = [YoutubeMusicService, SpotifyService, YoutubeYTMService]
    if to_service not in [cls.name for cls in allowed_to_services]:
        return Response(response=f"Invalid target service.", status=400)

    try:
        # TODO: return nicer error if to_service is None
        req = models.ConvertRequest(url=url, from_service=from_service, to_service=to_service)
    except ValidationError as e:
        # TODO: be more specific about error
        msg = str(e.errors()[0]['ctx']['error'])
        return Response(response=msg, status=400)

    url = unquote(req.url)
    converter = Converter.by_names(from_service_name=req.from_service, to_service_name=req.to_service)

    try:
        result = converter.convert(url)
        return Response(response=result.json(), status=200, mimetype='application/json')
    except NotFoundError as e:
        logging.exception(f"'not found' error for URL '{url}'")
        return Response(response=str(e), status=404)
    except ValueError as e:
        logging.exception(f"conversion error for URL '{url}'")
        return Response(response=str(e), status=400)
    except Exception as e:
        logging.exception(f"conversion error for URL '{url}'")
        return Response(response="Something went wrong.", status=500)


if __name__ == "__main__":
    application.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
