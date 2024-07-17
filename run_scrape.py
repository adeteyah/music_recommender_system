import sqlite3
import configparser
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.exceptions import SpotifyException

# Load configuration
config = configparser.ConfigParser()
config.read('config.cfg')

SPOTIPY_CLIENT_ID = config['spotify']['client_id']
SPOTIPY_CLIENT_SECRET = config['spotify']['client_secret']

user_ids = ['hyxtvqg8fbh2fa6k2rgugfun2']

client_credentials_manager = SpotifyClientCredentials(
    client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

# SQLite database file path
db_file = config['db']['playlists_db']

# Function to connect to SQLite database


def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except sqlite3.Error as e:
        print(e)
    return conn

# Function to save playlist details to SQLite database


def save_playlist_to_database(user_id, playlist_id, conn):
    try:
        # Fetch playlist details
        playlist = sp.playlist(playlist_id)

        # Only process playlists with more than 15 tracks
        if playlist['tracks']['total'] <= 15:
            print(f"Skipping playlist {playlist_id}, not enough tracks.")
            return

        # Insert or update playlists table
        cursor = conn.cursor()
        cursor.execute('''INSERT OR IGNORE INTO playlists (playlist_id, creator_id, playlist_track_count)
                          VALUES (?, ?, ?)''',
                       (playlist_id, user_id, playlist['tracks']['total']))
        conn.commit()

        # Insert items into items table
        tracks = playlist['tracks']['items'][:50]  # Fetch only 50 tracks
        playlist_items = ','.join([track['track']['id'] for track in tracks])

        cursor.execute('''INSERT OR REPLACE INTO items (playlist_id, playlist_items)
                          VALUES (?, ?)''',
                       (playlist_id, playlist_items))
        conn.commit()

        print(f"Saved playlist details for {playlist_id}")

    except SpotifyException as e:
        if e.http_status == 429:
            print(f"Rate limit exceeded. Last processed playlist: {
                  playlist_id}")
        else:
            print(f"Spotify error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")


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

    conn = create_connection(db_file)
    if conn is not None:
        try:
            playlists = sp.user_playlists(user_id)

            for playlist in playlists['items']:
                playlist_id = playlist['id']
                save_playlist_to_database(user_id, playlist_id, conn)

            fetched_users.add(user_id)

        except SpotifyException as e:
            if e.http_status == 429:
                print(f"Rate limit exceeded. Last processed user: {user_id}")
            else:
                print(f"Spotify error: {e}")
        except Exception as e:
            print(f"An error occurred: {e}")

        conn.close()
    else:
        print("Error! Cannot create the database connection.")

# Save updated fetched user IDs to file
with open(fetched_users_file, 'w') as f:
    for user_id in fetched_users:
        f.write(user_id + '\n')

# Save updated fetched artist IDs to file
with open(fetched_artists_file, 'w') as f:
    for artist_id in fetched_artists:
        f.write(artist_id + '\n')

print("Data import completed.")
