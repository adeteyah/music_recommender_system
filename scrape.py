import time
import sqlite3
import configparser
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.exceptions import SpotifyException
from scripts.seed import fill
from scripts.seed import verify

# Load configuration
config = configparser.ConfigParser()
config.read('config.cfg')

SPOTIPY_CLIENT_ID = config['spotify']['client_id']
SPOTIPY_CLIENT_SECRET = config['spotify']['client_secret']
DELAY_TIME = float(config['api']['delay_time'])

user_ids = ['']

client_credentials_manager = SpotifyClientCredentials(
    client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

# SQLite database file paths
playlists_db_path = config['db']['playlists_db']
songs_db_path = config['db']['songs_db']


def create_connection(db_file):
    try:
        return sqlite3.connect(db_file)
    except sqlite3.Error as e:
        print(f"Error connecting to database: {e}")
        return None


def insert_track_id_into_lyrics(cursor, track_id):
    cursor.execute(
        "INSERT OR IGNORE INTO lyrics (track_id) VALUES (?)", (track_id,))


def store_playlist_details(cursor, playlist_id, user_id, track_count):
    cursor.execute('''
        INSERT OR IGNORE INTO playlists (playlist_id, creator_id, original_track_count)
        VALUES (?, ?, ?)
    ''', (playlist_id, user_id, track_count))


def store_playlist_items(cursor, playlist_id, track_ids):
    playlist_items = ','.join(track_ids)
    cursor.execute('''
        INSERT OR REPLACE INTO items (playlist_id, playlist_items)
        VALUES (?, ?)
    ''', (playlist_id, playlist_items))


def store_track_details(cursor, track, audio_features):
    cursor.execute('''
        INSERT OR IGNORE INTO tracks (track_id, track_name, artist_ids, duration_ms, popularity, 
        acousticness, danceability, energy, instrumentalness, key, liveness, loudness, mode, 
        speechiness, tempo, time_signature, valence) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        track['id'], track['name'], ",".join(
            [artist['id'] for artist in track['artists']]),
        track['duration_ms'], track['popularity'], audio_features['acousticness'],
        audio_features['danceability'], audio_features['energy'],
        audio_features['instrumentalness'], audio_features['key'],
        audio_features['liveness'], audio_features['loudness'], audio_features['mode'],
        audio_features['speechiness'], audio_features['tempo'],
        audio_features['time_signature'], audio_features['valence']
    ))
    insert_track_id_into_lyrics(cursor, track['id'])


def store_artist_details(cursor, artist, fetched_artist_ids):
    cursor.execute('SELECT 1 FROM artists WHERE artist_id = ?',
                   (artist['id'],))
    if cursor.fetchone():
        fetched_artist_ids.add(artist['id'])
        return

    artist_info = sp.artist(artist['id'])
    cursor.execute('''
        INSERT OR IGNORE INTO artists (artist_id, artist_name, artist_genres) 
        VALUES (?, ?, ?)
    ''', (artist['id'], artist_info['name'], ",".join(artist_info['genres'])))
    fetched_artist_ids.add(artist['id'])


def fetch_and_store_playlist_data(user_id, conn_playlists, conn_songs):
    try:
        offset = 0
        limit = 1
        fetched_playlist_ids = set()
        fetched_artist_ids = set()

        while True:
            playlists = sp.user_playlists(user_id, offset=offset, limit=limit)
            if not playlists['items']:
                break

            for playlist in playlists['items']:
                if playlist['public']:
                    playlist_id = playlist['id']
                    if playlist_id in fetched_playlist_ids:
                        continue

                    fetched_playlist_ids.add(playlist_id)

                    playlist_details = sp.playlist(playlist_id)
                    if playlist_details['tracks']['total'] <= 5:
                        print(f"Skipping playlist {
                              playlist_id}, not enough tracks.")
                        continue

                    cursor = conn_playlists.cursor()
                    store_playlist_details(
                        cursor, playlist_id, user_id, playlist_details['tracks']['total'])

                    track_ids = [track['track']['id'] for track in playlist_details['tracks']
                                 ['items'][:24] if track['track']['id'] is not None]
                    if not track_ids:
                        continue

                    store_playlist_items(cursor, playlist_id, track_ids)
                    conn_playlists.commit()

                    track_data = sp.tracks(track_ids)
                    audio_features_list = sp.audio_features(track_ids)

                    for track, audio_features in zip(track_data['tracks'], audio_features_list):
                        if track is None or audio_features is None:
                            continue

                        if None in [track['id'], track['name'], track['duration_ms'], track['popularity'],
                                    audio_features['acousticness'], audio_features['danceability'],
                                    audio_features['energy'], audio_features['instrumentalness'],
                                    audio_features['key'], audio_features['liveness'],
                                    audio_features['loudness'], audio_features['mode'],
                                    audio_features['speechiness'], audio_features['tempo'],
                                    audio_features['time_signature'], audio_features['valence']]:
                            print(f"Skipping track {
                                  track['id']} due to missing data.")
                            continue

                        cursor = conn_songs.cursor()
                        store_track_details(cursor, track, audio_features)

                        for artist in track['artists']:
                            if artist['id'] not in fetched_artist_ids:
                                store_artist_details(
                                    cursor, artist, fetched_artist_ids)

                        conn_songs.commit()

                    print(f"Saved playlist details for {playlist_id}")
                    time.sleep(DELAY_TIME)

            offset += limit

    except SpotifyException as e:
        if e.http_status == 429:
            print(f"Rate limit exceeded for user: {user_id}")
        else:
            print(f"Spotify error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")


def main():
    fetched_users_file = config['file']['fetched_users']
    fetched_users = set()

    try:
        with open(fetched_users_file, 'r') as f:
            fetched_users.update(f.read().splitlines())
    except FileNotFoundError:
        pass

    conn_playlists = create_connection(playlists_db_path)
    conn_songs = create_connection(songs_db_path)

    if conn_playlists is None or conn_songs is None:
        print("Error! Cannot create the database connections.")
        return

    try:
        for user_id in user_ids:
            if user_id in fetched_users:
                print(f"Skipping {user_id}, already fetched.")
                continue

            fetch_and_store_playlist_data(user_id, conn_playlists, conn_songs)
            fetched_users.add(user_id)

            with open(fetched_users_file, 'a') as f:
                f.write(user_id + '\n')
    except KeyboardInterrupt:
        print("Interrupted with Keyboard")
    finally:
        if conn_playlists:
            conn_playlists.close()
        if conn_songs:
            conn_songs.close()

    print("Playlist scraping completed.")


if __name__ == "__main__":
    main()
