import re
import csv
import spotipy
import configparser
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.exceptions import SpotifyException

# Load configuration
config = configparser.ConfigParser()
config.read('config.cfg')

SPOTIPY_CLIENT_ID = config['spotify']['client_id']
SPOTIPY_CLIENT_SECRET = config['spotify']['client_secret']

user_ids = ['31wu7p6cb6llyephgywn7yyhk7hq']

client_credentials_manager = SpotifyClientCredentials(
    client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

# Function to save playlist tracks to CSV


def save_playlist_to_csv(user_id, playlist_id, fetched_artists):
    path = config['dir']['raw']
    filename = f"{path}/{user_id}_{playlist_id}.csv"

    results = sp.playlist_tracks(playlist_id)
    tracks = results['items']

    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['spotify_id', 'artists_id'])

        for item in tracks:
            track = item['track']
            track_id = track['id']
            artist_ids = [artist['id'] for artist in track['artists']]

            # Add artist IDs to fetched_artists set
            for artist_id in artist_ids:
                fetched_artists.add(artist_id)

            writer.writerow([track_id, ','.join(artist_ids)])

    print(f"Saved {filename}")


# Load fetched user IDs from file
fetched_users_file = config['file']['fetched_users']
try:
    with open(fetched_users_file, 'r') as f:
        fetched_users = set(f.read().splitlines())
except FileNotFoundError:
    fetched_users = set()

# Load fetched artist IDs from file
fetched_artists_file = config['file']['fetched_artists']
try:
    with open(fetched_artists_file, 'r') as f:
        fetched_artists = set(f.read().splitlines())
except FileNotFoundError:
    fetched_artists = set()

# Process each user
for user_id in user_ids:
    if user_id in fetched_users:
        print(f"Skipping {user_id}, already fetched.")
        continue

    try:
        playlists = sp.user_playlists(user_id)

        for playlist in playlists['items']:
            playlist_id = playlist['id']
            save_playlist_to_csv(user_id, playlist_id, fetched_artists)

        fetched_users.add(user_id)

    except SpotifyException as e:
        if e.http_status == 429:
            print(f"Rate limit exceeded. Last processed playlist: {
                  playlist_id}")
            break  # Stop further processing
        else:
            print(f"Spotify error: {e}")
            break  # Stop further processing
    except Exception as e:
        print(f"An error occurred: {e}")
        break  # Stop further processing

# Save updated fetched user IDs to file
with open(fetched_users_file, 'w') as f:
    for user_id in fetched_users:
        f.write(user_id + '\n')

# Save updated fetched artist IDs to file
with open(fetched_artists_file, 'w') as f:
    for artist_id in fetched_artists:
        f.write(artist_id + '\n')
