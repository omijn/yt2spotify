import argparse
import re
import sys
import configparser
from ytmusicapi import YTMusic
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

def get_spotify_client(client_id, client_secret):
    return spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=client_id, client_secret=client_secret))

def get_yt_client():
    return YTMusic()

def read_spotify_config(config_path):
    config = configparser.ConfigParser()
    config.read(config_path)
    client_id = config['spotify']['client_id']
    client_secret = config['spotify']['client_secret']

    return client_id, client_secret

def yt2spotify(yt, sp, url):
    ytvideopattern = r'(?<=v=)[-\w]+'   # TODO: change this to re.compile in webservice version
    videos = re.findall(ytvideopattern, url)
    if len(videos) == 0:
        raise ValueError("no YouTube video ID found in URL. Are you sure you're using the right URL?")

    video_id = videos[0]
    song = yt.get_song(videoId=video_id)
    
    spotify_search_query = f"{song['title']} {song['artists'][0]}"
    results = sp.search(spotify_search_query, limit=5, type="track")

    res_urls = []
    for item in results['tracks']['items']:
        res_urls.append(item['external_urls']['spotify'])

    return res_urls

def spotify2yt(sp, yt, url):
    raise NotImplementedError

def main():
    parser = argparse.ArgumentParser(description="Convert between YouTube Music and Spotify links", allow_abbrev=True)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-y", "--youtube", help="YouTube Music link (enclose link in double or single quotes)")
    group.add_argument("-s", "--spotify", help="Spotify link (enclose link in double or single quotes)")
    parser.add_argument("--config", default="config.ini", help="Path to config file")
    args = parser.parse_args()


    client_id, client_secret = read_spotify_config(args.config)
    sp = get_spotify_client(client_id, client_secret)
    yt = get_yt_client()

    if args.youtube:
        try:
            spotify_urls = yt2spotify(yt, sp, args.youtube)
        except ValueError as e:
            print(e)
            sys.exit(1)

        [print(u) for u in spotify_urls]

    elif args.spotify:    
        spotify2yt(sp, yt, args.spotify)

if __name__ == "__main__":
    main()