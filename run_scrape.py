import time
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
DELAY_TIME = float(config['api']['delay_time'])

user_ids = [
    "derickjoshua", "31s3jiykttdjbkazhzrxit65b6fu", "31kuqmrp4y4qlc6unmahnfbmnyty",
    "31ey7pwluroi2jtsqicezjeh2m34", "pn2vesv93a5q269r34lccpkez",
    "31ytcsf3t7nlspzu4ti2pmdbtq4i", "31ylxjygzhuin4zf2ptxugttz4ay",
    "31tx2wbxwjo7e73exgl2q5as4xha", "31vfqi547vy26k7g6pahinzseude"
]

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


def fetch_and_store_playlist_data(user_id, conn_playlists, conn_songs):
    try:
        offset = 0
        limit = 50
        fetched_playlist_ids = set()

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

                    # Store playlist details
                    cursor = conn_playlists.cursor()
                    cursor.execute('''
                        INSERT OR IGNORE INTO playlists (playlist_id, creator_id, original_track_count)
                        VALUES (?, ?, ?)
                    ''', (playlist_id, user_id, playlist_details['tracks']['total']))
                    conn_playlists.commit()

                    # Store playlist items
                    track_ids = [track['track']['id']
                                 for track in playlist_details['tracks']['items'][:7]]
                    playlist_items = ','.join(track_ids)
                    cursor.execute('''
                        INSERT OR REPLACE INTO items (playlist_id, playlist_items)
                        VALUES (?, ?)
                    ''', (playlist_id, playlist_items))
                    conn_playlists.commit()

                    # Fetch and store track and artist details
                    track_data = sp.tracks(track_ids)
                    audio_features_list = sp.audio_features(track_ids)

                    for track, audio_features in zip(track_data['tracks'], audio_features_list):
                        track_id = track['id']
                        track_name = track['name']
                        artist_ids = ",".join([artist['id']
                                              for artist in track['artists']])
                        duration_ms = track['duration_ms']
                        popularity = track['popularity']
                        acousticness = audio_features['acousticness']
                        danceability = audio_features['danceability']
                        energy = audio_features['energy']
                        instrumentalness = audio_features['instrumentalness']
                        key = audio_features['key']
                        liveness = audio_features['liveness']
                        loudness = audio_features['loudness']
                        mode = audio_features['mode']
                        speechiness = audio_features['speechiness']
                        tempo = audio_features['tempo']
                        time_signature = audio_features['time_signature']
                        valence = audio_features['valence']

                        # Store track details
                        cursor = conn_songs.cursor()
                        cursor.execute('''
                            INSERT OR IGNORE INTO tracks (track_id, track_name, artist_ids, duration_ms, popularity, 
                            acousticness, danceability, energy, instrumentalness, key, liveness, loudness, mode, 
                            speechiness, tempo, time_signature, valence) 
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (
                            track_id, track_name, artist_ids, duration_ms, popularity,
                            acousticness, danceability, energy, instrumentalness, key, liveness, loudness, mode,
                            speechiness, tempo, time_signature, valence
                        ))

                        # Store artist details
                        for artist in track['artists']:
                            artist_id = artist['id']
                            artist_info = sp.artist(artist_id)
                            artist_name = artist_info['name']
                            artist_genres = ",".join(artist_info['genres'])

                            cursor.execute('''
                                INSERT OR IGNORE INTO artists (artist_id, artist_name, artist_genres) 
                                VALUES (?, ?, ?)
                            ''', (artist_id, artist_name, artist_genres))
                            print(f'Updated artist name, genres for {
                                  artist_id}: {artist_name}, {artist_genres}')

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
    try:
        with open(fetched_users_file, 'r') as f:
            fetched_users = set(f.read().splitlines())
    except FileNotFoundError:
        fetched_users = set()

    conn_playlists = create_connection(playlists_db_path)
    conn_songs = create_connection(songs_db_path)

    if conn_playlists is None or conn_songs is None:
        print("Error! Cannot create the database connections.")
        return

    for user_id in user_ids:
        if user_id in fetched_users:
            print(f"Skipping {user_id}, already fetched.")
            continue

        fetch_and_store_playlist_data(user_id, conn_playlists, conn_songs)
        fetched_users.add(user_id)

    with open(fetched_users_file, 'w') as f:
        for user_id in fetched_users:
            f.write(user_id + '\n')

    conn_playlists.close()
    conn_songs.close()

    print("Playlist scraping completed.")


if __name__ == "__main__":
    main()
