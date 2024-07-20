import sqlite3
import time
import configparser
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.exceptions import SpotifyException
from collections import Counter

config = configparser.ConfigParser()
config.read('config.cfg')

songs_db_path = config['db']['songs_db']
playlists_db_path = config['db']['playlists_db']

SPOTIPY_CLIENT_ID = config['spotify']['client_id']
SPOTIPY_CLIENT_SECRET = config['spotify']['client_secret']

client_credentials_manager = SpotifyClientCredentials(
    client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)


def fill_artists_table():
    conn = sqlite3.connect(songs_db_path)
    cursor = conn.cursor()

    # Updating artists
    while True:
        cursor.execute(
            "SELECT * FROM artists WHERE artist_name IS NULL LIMIT 5")
        artists = cursor.fetchall()
        if not artists:
            break

        for artist in artists:
            artist_id = artist[0]
            try:
                artist_info = sp.artist(artist_id)
                artist_name = artist_info['name']
                artist_genres = ",".join(artist_info['genres'])
                cursor.execute("UPDATE artists SET artist_name = ?, artist_genres = ? WHERE artist_id = ?",
                               (artist_name, artist_genres, artist_id))
                print(f'Updated artist name, genres for {
                      artist_id}: {artist_name}, {artist_genres}')
            except SpotifyException as e:
                print(f"Error fetching artist {artist_id}: {e}")
        conn.commit()
        time.sleep(float(config['api']['delay_time']))

    conn.close()
    print("Finished updating artists with Spotify data.")


def fill_tracks_table():
    conn = sqlite3.connect(songs_db_path)
    cursor = conn.cursor()

    # Updating tracks
    while True:
        cursor.execute("SELECT * FROM tracks WHERE track_name IS NULL LIMIT 5")
        tracks = cursor.fetchall()
        if not tracks:
            break

        for track in tracks:
            track_id = track[0]
            try:
                track_info = sp.track(track_id)
                audio_features_list = sp.audio_features(track_id)

                # Check if audio_features_list is not empty and contains valid data
                if audio_features_list and audio_features_list[0]:
                    audio_features = audio_features_list[0]
                else:
                    raise SpotifyException(
                        f"No audio features available for track {track_id}")

                track_name = track_info['name']
                artist_ids = ",".join([artist['id']
                                      for artist in track_info['artists']])
                duration_ms = track_info['duration_ms']
                popularity = track_info['popularity']
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

                cursor.execute("""
                    UPDATE tracks SET
                        track_name = ?, artist_ids = ?, duration_ms = ?, popularity = ?, 
                        acousticness = ?, danceability = ?, energy = ?,
                        instrumentalness = ?, key = ?, liveness = ?, loudness = ?, mode = ?,
                        speechiness = ?, tempo = ?, time_signature = ?, valence = ?
                    WHERE track_id = ?
                """, (
                    track_name, artist_ids, duration_ms, popularity,
                    acousticness, danceability, energy,
                    instrumentalness, key, liveness, loudness, mode,
                    speechiness, tempo, time_signature, valence, track_id
                ))

                print(f'Updated track info for {track_id}: {track_name}')
            except SpotifyException as e:
                print(f"Error fetching track {track_id}: {e}")
            except Exception as e:
                print(f"Unexpected error for track {track_id}: {e}")
        conn.commit()
        time.sleep(float(config['api']['delay_time']))

    conn.close()
    print("Finished updating tracks with Spotify data.")


def fetch_playlist_items():
    conn = sqlite3.connect(playlists_db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT playlist_items FROM items")
    playlist_items = cursor.fetchone()

    conn.close()

    if playlist_items:
        # Splitting comma-separated track_ids
        track_ids = playlist_items[0].split(',')
        return track_ids
    else:
        return []


def fetch_track_info(track_id):
    conn = sqlite3.connect(songs_db_path)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT track_name, duration_ms, popularity, acousticness, danceability,
        energy, instrumentalness, key, liveness, loudness, mode,
        speechiness, tempo, time_signature, valence
        FROM tracks
        WHERE track_id = ?
    """, (track_id,))
    track_info = cursor.fetchone()

    conn.close()
    return track_info


def fill_playlists_table():
    conn_playlists = sqlite3.connect(playlists_db_path)
    cursor_playlists = conn_playlists.cursor()

    cursor_playlists.execute("SELECT playlist_id, playlist_items FROM items")
    playlists = cursor_playlists.fetchall()

    conn_songs = sqlite3.connect(songs_db_path)
    cursor_songs = conn_songs.cursor()

    for playlist_id, playlist_items in playlists:
        track_ids = playlist_items.split(',')

        min_max_values = {
            'duration_ms': [],
            'popularity': [],
            'acousticness': [],
            'danceability': [],
            'energy': [],
            'instrumentalness': [],
            'key': [],
            'liveness': [],
            'loudness': [],
            'mode': [],
            'speechiness': [],
            'tempo': [],
            'time_signature': [],
            'valence': [],
            'artist_ids': [],
            'genres': []
        }

        for track_id in track_ids:
            cursor_songs.execute("""
                SELECT duration_ms, popularity, acousticness, danceability, energy,
                instrumentalness, key, liveness, loudness, mode,
                speechiness, tempo, time_signature, valence, artist_ids
                FROM tracks
                WHERE track_id = ?
            """, (track_id,))
            track_info = cursor_songs.fetchone()

            if track_info:
                min_max_values['duration_ms'].append(track_info[0])
                min_max_values['popularity'].append(track_info[1])
                min_max_values['acousticness'].append(track_info[2])
                min_max_values['danceability'].append(track_info[3])
                min_max_values['energy'].append(track_info[4])
                min_max_values['instrumentalness'].append(track_info[5])
                min_max_values['key'].append(track_info[6])
                min_max_values['liveness'].append(track_info[7])
                min_max_values['loudness'].append(track_info[8])
                min_max_values['mode'].append(track_info[9])
                min_max_values['speechiness'].append(track_info[10])
                min_max_values['tempo'].append(track_info[11])
                min_max_values['time_signature'].append(track_info[12])
                min_max_values['valence'].append(track_info[13])
                min_max_values['artist_ids'].extend(track_info[14].split(','))

                # Fetch genres for each artist in the track
                for artist_id in track_info[14].split(','):
                    cursor_songs.execute(
                        "SELECT artist_genres FROM artists WHERE artist_id = ?", (artist_id,))
                    artist_genres = cursor_songs.fetchone()
                    if artist_genres:
                        min_max_values['genres'].extend(
                            artist_genres[0].split(','))

        if min_max_values['duration_ms']:
            # Get the most common artist ID
            most_artist_id = max(
                set(min_max_values['artist_ids']), key=min_max_values['artist_ids'].count)

            # Get the top 5 most common genres
            genre_counts = Counter(min_max_values['genres'])
            most_genres = ",".join(
                [genre for genre, count in genre_counts.most_common(5)])

            cursor_playlists.execute("""
                UPDATE playlists SET
                    min_duration_ms = ?, max_duration_ms = ?, min_popularity = ?, max_popularity = ?, 
                    min_acousticness = ?, max_acousticness = ?, min_danceability = ?, max_danceability = ?, 
                    min_energy = ?, max_energy = ?, min_instrumentalness = ?, max_instrumentalness = ?, 
                    min_key = ?, max_key = ?, min_liveness = ?, max_liveness = ?, 
                    min_loudness = ?, max_loudness = ?, min_mode = ?, max_mode = ?, 
                    min_speechiness = ?, max_speechiness = ?, min_tempo = ?, max_tempo = ?, 
                    min_time_signature = ?, max_time_signature = ?, min_valence = ?, max_valence = ?, 
                    most_artist_id = ?, most_genres = ?
                WHERE playlist_id = ?
            """, (
                min(min_max_values['duration_ms']), max(
                    min_max_values['duration_ms']),
                min(min_max_values['popularity']), max(
                    min_max_values['popularity']),
                min(min_max_values['acousticness']), max(
                    min_max_values['acousticness']),
                min(min_max_values['danceability']), max(
                    min_max_values['danceability']),
                min(min_max_values['energy']), max(min_max_values['energy']),
                min(min_max_values['instrumentalness']), max(
                    min_max_values['instrumentalness']),
                min(min_max_values['key']), max(min_max_values['key']),
                min(min_max_values['liveness']), max(
                    min_max_values['liveness']),
                min(min_max_values['loudness']), max(
                    min_max_values['loudness']),
                min(min_max_values['mode']), max(min_max_values['mode']),
                min(min_max_values['speechiness']), max(
                    min_max_values['speechiness']),
                min(min_max_values['tempo']), max(min_max_values['tempo']),
                min(min_max_values['time_signature']), max(
                    min_max_values['time_signature']),
                min(min_max_values['valence']), max(min_max_values['valence']),
                most_artist_id, most_genres, playlist_id
            ))
        else:
            print(f"No track information found for playlist {playlist_id}")

    conn_playlists.commit()
    conn_playlists.close()
    conn_songs.close()

    print("Finished updating playlists with audio feature data.")


def choose_process():
    while True:
        print("\nChoose a process to run:")
        print("1. Fill tracks information table")
        print("2. Fill artists information table")
        print("3. Process playlist items")
        print("4. Exit")
        choice = input("Enter your choice (1, 2, 3, or 4): ")

        if choice == '1':
            fill_tracks_table()
        elif choice == '2':
            fill_artists_table()
        elif choice == '3':
            fill_playlists_table()
        elif choice == '4':
            print("Exiting the program.")
            break
        else:
            print("Invalid choice. Please enter '1', '2', '3', or '4'.")

        return_to_menu = input("Return to menu (Y/N)? ").strip().lower()
        if return_to_menu != 'y':
            print("Exiting the program.")
            break


if __name__ == "__main__":
    choose_process()

print("Scrape completed.")
