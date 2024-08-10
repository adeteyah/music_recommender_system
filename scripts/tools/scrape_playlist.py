import sqlite3
import configparser
import spotipy
import time
import collections
from spotipy.oauth2 import SpotifyClientCredentials

# Load configuration
config = configparser.ConfigParser()
config.read('config.cfg')

DB = config['rs']['db_path']
CLIENT_ID = config['api']['client_id']
CLIENT_SECRET = config['api']['client_secret']
DELAY_TIME = float(config['scrape']['delay_time'])

# Spotify API credentials
client_credentials_manager = SpotifyClientCredentials(
    client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

# Connect to SQLite database
conn = sqlite3.connect(DB)
cursor = conn.cursor()


def load_existing_ids():
    existing_songs = {row[0]
                      for row in cursor.execute('SELECT song_id FROM songs')}
    existing_artists = {row[0] for row in cursor.execute(
        'SELECT artist_id FROM artists')}
    existing_playlists = {row[0] for row in cursor.execute(
        'SELECT playlist_id FROM playlists')}
    return existing_songs, existing_artists, existing_playlists


existing_songs, existing_artists, existing_playlists = load_existing_ids()


def insert_song(song_data):
    song_id = song_data['song_id']

    # Check if the song already exists
    cursor.execute("SELECT 1 FROM songs WHERE song_id = ?", (song_id,))
    if cursor.fetchone():
        print(f"Song {song_id} already exists, skipping insertion.")
        return  # Skip insertion if the song already exists

    cursor.execute('''
        INSERT INTO songs (song_id, song_name, artist_ids, acousticness, danceability, energy,
                           instrumentalness, key, liveness, loudness, mode, speechiness, tempo,
                           time_signature, valence)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                   (song_data['song_id'], song_data['song_name'], song_data['artist_ids'],
                    song_data['acousticness'], song_data['danceability'], song_data['energy'],
                    song_data['instrumentalness'], song_data['key'], song_data['liveness'],
                    song_data['loudness'], song_data['mode'], song_data['speechiness'],
                    song_data['tempo'], song_data['time_signature'], song_data['valence']))

    existing_songs.add(song_id)  # Add to existing_songs set


def insert_artist(artist):
    cursor.execute('''
        INSERT INTO artists (artist_id, artist_name, artist_genres)
        VALUES (?, ?, ?)
    ''', artist)
    conn.commit()


def insert_playlist(playlist):
    cursor.execute('''
        INSERT INTO playlists (playlist_id, playlist_creator_id, playlist_original_items, playlist_items)
        VALUES (?, ?, ?, ?)
    ''', playlist)
    conn.commit()


def update_playlist_metadata(playlist_id, metadata):
    cursor.execute('''
        UPDATE playlists 
        SET playlist_items_fetched = ?, 
            playlist_top_artist_ids = ?, 
            playlist_top_genres = ?, 
            min_acousticness = ?, 
            max_acousticness = ?, 
            min_danceability = ?, 
            max_danceability = ?, 
            min_energy = ?, 
            max_energy = ?, 
            min_instrumentalness = ?, 
            max_instrumentalness = ?, 
            min_key = ?, 
            max_key = ?, 
            min_liveness = ?, 
            max_liveness = ?, 
            min_loudness = ?, 
            max_loudness = ?, 
            min_mode = ?, 
            max_mode = ?, 
            min_speechiness = ?, 
            max_speechiness = ?, 
            min_tempo = ?, 
            max_tempo = ?, 
            min_time_signature = ?, 
            max_time_signature = ?, 
            min_valence = ?, 
            max_valence = ? 
        WHERE playlist_id = ?
    ''', (*metadata, playlist_id))
    conn.commit()


def scrape(ids):
    for playlist_id in ids:
        try:
            playlist = sp.playlist(playlist_id)
            playlist_creator_id = playlist['owner']['id']
            playlist_items = playlist['tracks']['items']

            # Check if the playlist has at least 2 songs
            if len(playlist_items) < 2:
                print(f"Skipping playlist {
                      playlist_id} because it has fewer than 2 songs.")
                continue  # Skip this playlist

            track_ids = []
            for item in playlist_items:
                try:
                    track = item['track']
                    song_id = track['id']
                    if not song_id:
                        continue  # Skip if song_id is None or invalid

                    if song_id not in existing_songs:
                        # Prepare song data as a dictionary
                        song_data = {
                            'song_id': song_id,
                            'song_name': track['name'],
                            'artist_ids': ','.join([artist['id'] for artist in track['artists']]),
                        }

                        # Fetch audio features
                        features = sp.audio_features([song_id])[0]
                        if features is None:
                            continue  # Skip if audio features are not available

                        song_data.update({
                            'acousticness': features.get('acousticness', 0.0),
                            'danceability': features.get('danceability', 0.0),
                            'energy': features.get('energy', 0.0),
                            'instrumentalness': features.get('instrumentalness', 0.0),
                            'key': features.get('key', 0),
                            'liveness': features.get('liveness', 0.0),
                            'loudness': features.get('loudness', 0.0),
                            'mode': features.get('mode', 0),
                            'speechiness': features.get('speechiness', 0.0),
                            'tempo': features.get('tempo', 0.0),
                            'time_signature': features.get('time_signature', 4),
                            'valence': features.get('valence', 0.0)
                        })

                        # Insert song data into the songs table
                        insert_song(song_data)

                    track_ids.append(song_id)

                except Exception as e:
                    print(f"Error processing song {song_id}: {e}")
                    continue  # Skip to the next song if there's an error

            # Insert the playlist data
            if playlist_id not in existing_playlists:
                cursor.execute('''
                    INSERT INTO playlists (playlist_id, playlist_creator_id, playlist_original_items, playlist_items)
                    VALUES (?, ?, ?, ?)''',
                               (playlist_id, playlist_creator_id, len(track_ids), ','.join(track_ids)))
                existing_playlists.add(playlist_id)

        except Exception as e:
            print(f"Error processing playlist {playlist_id}: {e}")
            continue  # Skip to the next playlist if there's an error

    conn.commit()


def calculate_playlist_metadata(playlist_id):
    # Fetch the playlist items
    cursor.execute(
        'SELECT playlist_items FROM playlists WHERE playlist_id = ?', (playlist_id,))
    result = cursor.fetchone()
    if not result:
        print(f"Playlist {playlist_id} not found in database.")
        return
    song_ids = result[0].split(',')

    # Fetch audio features for all songs in the playlist
    cursor.execute(f'''
        SELECT acousticness, danceability, energy, instrumentalness, key, liveness, loudness, mode, speechiness, tempo,
               time_signature, valence, artist_ids
        FROM songs WHERE song_id IN ({','.join(['?'] * len(song_ids))})
    ''', song_ids)
    rows = cursor.fetchall()

    if not rows:
        print(f"No songs found for playlist {playlist_id}.")
        return

    # Initialize min/max variables
    min_acousticness, max_acousticness = float('inf'), float('-inf')
    min_danceability, max_danceability = float('inf'), float('-inf')
    min_energy, max_energy = float('inf'), float('-inf')
    min_instrumentalness, max_instrumentalness = float('inf'), float('-inf')
    min_key, max_key = float('inf'), float('-inf')
    min_liveness, max_liveness = float('inf'), float('-inf')
    min_loudness, max_loudness = float('inf'), float('-inf')
    min_mode, max_mode = float('inf'), float('-inf')
    min_speechiness, max_speechiness = float('inf'), float('-inf')
    min_tempo, max_tempo = float('inf'), float('-inf')
    min_time_signature, max_time_signature = float('inf'), float('-inf')
    min_valence, max_valence = float('inf'), float('-inf')

    # Collect artist and genre information
    artist_counts = {}
    genre_counts = {}

    for row in rows:
        acousticness, danceability, energy, instrumentalness, key, liveness, loudness, mode, speechiness, tempo, time_signature, valence, artist_ids = row

        # Update min/max values
        min_acousticness = min(min_acousticness, acousticness)
        max_acousticness = max(max_acousticness, acousticness)
        min_danceability = min(min_danceability, danceability)
        max_danceability = max(max_danceability, danceability)
        min_energy = min(min_energy, energy)
        max_energy = max(max_energy, energy)
        min_instrumentalness = min(min_instrumentalness, instrumentalness)
        max_instrumentalness = max(max_instrumentalness, instrumentalness)
        min_key = min(min_key, key)
        max_key = max(max_key, key)
        min_liveness = min(min_liveness, liveness)
        max_liveness = max(max_liveness, liveness)
        min_loudness = min(min_loudness, loudness)
        max_loudness = max(max_loudness, loudness)
        min_mode = min(min_mode, mode)
        max_mode = max(max_mode, mode)
        min_speechiness = min(min_speechiness, speechiness)
        max_speechiness = max(max_speechiness, speechiness)
        min_tempo = min(min_tempo, tempo)
        max_tempo = max(max_tempo, tempo)
        min_time_signature = min(min_time_signature, time_signature)
        max_time_signature = max(max_time_signature, time_signature)
        min_valence = min(min_valence, valence)
        max_valence = max(max_valence, valence)

        # Update artist and genre counts
        artist_ids_list = artist_ids.split(',')
        for artist_id in artist_ids_list:
            cursor.execute(
                'SELECT artist_genres FROM artists WHERE artist_id = ?', (artist_id,))
            result = cursor.fetchone()
            if result:
                genres = result[0].split(',')
                for genre in genres:
                    genre_counts[genre] = genre_counts.get(genre, 0) + 1

            artist_counts[artist_id] = artist_counts.get(artist_id, 0) + 1

    # Find top 20 artists and genres
    top_artists = sorted(artist_counts.items(),
                         key=lambda x: x[1], reverse=True)[:20]
    top_genres = sorted(genre_counts.items(),
                        key=lambda x: x[1], reverse=True)[:20]

    top_artist_ids = ','.join([artist[0] for artist in top_artists])
    top_genres_list = ','.join([genre[0] for genre in top_genres])

    # Update the playlist record with calculated values
    cursor.execute('''
        UPDATE playlists
        SET playlist_top_artist_ids = ?, playlist_top_genres = ?, playlist_items_fetched = ?,
            min_acousticness = ?, max_acousticness = ?,
            min_danceability = ?, max_danceability = ?,
            min_energy = ?, max_energy = ?,
            min_instrumentalness = ?, max_instrumentalness = ?,
            min_key = ?, max_key = ?,
            min_liveness = ?, max_liveness = ?,
            min_loudness = ?, max_loudness = ?,
            min_mode = ?, max_mode = ?,
            min_speechiness = ?, max_speechiness = ?,
            min_tempo = ?, max_tempo = ?,
            min_time_signature = ?, max_time_signature = ?,
            min_valence = ?, max_valence = ?
        WHERE playlist_id = ?
    ''', (
        top_artist_ids, top_genres_list, len(song_ids),
        min_acousticness, max_acousticness,
        min_danceability, max_danceability,
        min_energy, max_energy,
        min_instrumentalness, max_instrumentalness,
        min_key, max_key,
        min_liveness, max_liveness,
        min_loudness, max_loudness,
        min_mode, max_mode,
        min_speechiness, max_speechiness,
        min_tempo, max_tempo,
        min_time_signature, max_time_signature,
        min_valence, max_valence,
        playlist_id
    ))

    conn.commit()
    print(f"Metadata for playlist {playlist_id} updated successfully.")


if __name__ == "__main__":
    ids = ['6YYoJll65jHxCYVPdkd5CD', '2p0DCsarph7j5s1KAxrHPf',
           '0mh7pPwHuGaDtlyURlhDzE', '3peBvggvKVhBf6LOqOFYTW']
    scrape(ids)
    for playlist_id in ids:
        calculate_playlist_metadata(playlist_id)
        print(f"Updated metadata for playlist {playlist_id}")
