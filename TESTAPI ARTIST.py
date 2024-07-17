import configparser
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# Load configuration
config = configparser.ConfigParser()
config.read('config.cfg')

# Extract credentials
SPOTIPY_CLIENT_ID = config['spotify']['client_id']
SPOTIPY_CLIENT_SECRET = config['spotify']['client_secret']

# Authenticate with Spotify API
client_credentials_manager = SpotifyClientCredentials(
    client_id=SPOTIPY_CLIENT_ID,
    client_secret=SPOTIPY_CLIENT_SECRET
)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

# Function to get artist's name and genre by artist ID


def get_artist_info(artist_id):
    try:
        artist = sp.artist(artist_id)
        artist_name = artist['name']
        artist_genres = artist['genres']
        return artist_name, artist_genres
    except Exception as e:
        print(f"An error occurred: {e}")
        return None, None


# Example usage with an artist ID
artist_id = '1Xyo4u8uXC1ZmMpatF05PJ'  # Example: The Weeknd's artist ID
artist_name, artist_genres = get_artist_info(artist_id)

if artist_name and artist_genres:
    print(f"Artist Name: {artist_name}")
    print(f"Artist Genres: {', '.join(artist_genres)}")
else:
    print("Failed to retrieve artist information.")
