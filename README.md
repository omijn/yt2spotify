## yt2spotify

Convert between YouTube music and Spotify links. Right now, this is just a CLI tool written in Python and only works in the direction of YouTube Music -> Spotify but not the other way around. Support for the reverse direction as well as a public web API/web app/Android app are being planned. 

### Setup
1. Create a virtual environment and install dependencies

```
python3 -m venv env
. env/bin/activate
pip install -r requirements.txt
```

2. Create a Spotify app

Follow the instructions in the Spotify developer guide to create an app and get the OAuth2.0 client ID and client secret for it (you won't have to do this once I get around to figuring out desktop/web distribution of this application).

3. Create a config file

Create a `config.ini` file in the root of the repository with the following contents:

```
[spotify]
client_id=YOUR CLIENT ID HERE
client_secret=YOUR CLIENT SECRET HERE
```

### Usage
You can now find a song to convert and run the converter! You can either grab the YouTube music URL from the search bar in the browser window or click on 'Share' in the song options.

Make sure to enclose your YouTube music URL in double or single quotes:

    python yt2spotify.py -y "https://music.youtube.com/watch?v=dGeEuyG_DIc&feature=share"

A list of Spotify URLs will be returned. Usually the first one is the one you need. 