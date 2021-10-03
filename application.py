import argparse
import re
import sys
import configparser
from ytmusicapi import YTMusic
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from flask import Flask, request, jsonify, Response, render_template
from urllib.parse import unquote


def read_spotify_config(config_path):
    config = configparser.ConfigParser()
    config.read(config_path)
    client_id = config['spotify']['client_id']
    client_secret = config['spotify']['client_secret']

    return client_id, client_secret


application = Flask(__name__)
ytvideopattern = re.compile(r'(?<=v=)[-\w]+')
yt = YTMusic()
client_id, client_secret = read_spotify_config('config.ini')
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=client_id, client_secret=client_secret))


def get_spotify_client(client_id, client_secret):
    pass


def get_yt_client():
    pass


@application.route('/')
def index():
    return application.send_static_file('index.html')


@application.route('/y2s')
def yt2spotify():
    url = request.args.get('url')
    if url == "" or url is None:
        return Response("no URL parameter in request", status=400)  # TODO: look into custom exception handlers

    url = unquote(url)

    videos = ytvideopattern.findall(url)
    if len(videos) == 0:
        return Response("Invalid YouTube Music URL", status=400)  # TODO: mimetype=application/json?

    video_id = videos[0]
    song = yt.get_song(videoId=video_id)

    song_title = song['videoDetails']['title']
    song_artist = song['videoDetails']['author'].removesuffix(" - Topic")
    spotify_search_query = f"{song_title} {song_artist}"
    results = sp.search(spotify_search_query, limit=5, type="track")

    response = {'results': []}
    for item in results['tracks']['items']:
        resp_item = {
            'url': item['external_urls']['spotify'],
            'album': {
                'art': item['album']['images'][0]['url'],
                'name': item['album']['name'],
                'release_date': item['album']['release_date'][:4]
            },
            'name': item['name'],
            'artists': [artist['name'] for artist in item['artists']]
        }
        response['results'].append(resp_item)

    return jsonify(response)


def spotify2yt(sp, yt, url):
    raise NotImplementedError


if __name__ == "__main__":
    application.run(host='0.0.0.0', port=5000)
