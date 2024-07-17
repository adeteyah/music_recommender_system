import configparser
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

config = configparser.ConfigParser()
config.read('config.cfg')

SPOTIPY_CLIENT_ID = config['spotify']['client_id']
SPOTIPY_CLIENT_SECRET = config['spotify']['client_secret']

client_credentials_manager = SpotifyClientCredentials(
    client_id=SPOTIPY_CLIENT_ID,
    client_secret=SPOTIPY_CLIENT_SECRET
)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)


def get_track_title(track_id):
    track_info = sp.track(track_id)
    track_title = track_info['name']
    return track_title


if __name__ == "__main__":
    track_id = '6rqhFgbbKwnb9MLmUQDhG6'
    track_title = get_track_title(track_id)
    print(f"Track Title: {track_title}")
