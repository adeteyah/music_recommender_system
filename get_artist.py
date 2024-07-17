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


def get_artist_info(artist_id):
    try:
        artist = sp.artist(artist_id)
        artist_name = artist['name']
        artist_genres = artist['genres']
        return artist_name, artist_genres
    except Exception as e:
        print(f"An error occurred: {e}")
        return None, None


if __name__ == "__main__":
    artist_id = '1Xyo4u8uXC1ZmMpatF05PJ'
    artist_name, artist_genres = get_artist_info(artist_id)

    if artist_name and artist_genres:
        print(f"Artist Name: {artist_name}")
        print(f"Artist Genres: {', '.join(artist_genres)}")
    else:
        print("Failed to retrieve artist information.")
