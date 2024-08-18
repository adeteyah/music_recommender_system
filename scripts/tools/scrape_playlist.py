import sqlite3
import configparser
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# Load configuration


def load_config(config_file='config.cfg'):
    config = configparser.ConfigParser()
    config.read(config_file)
    return config


config = load_config()
DB = config['rs']['db_path']
CLIENT_ID = config['api']['client_id']
CLIENT_SECRET = config['api']['client_secret']
DELAY_TIME = float(config['scrape']['delay_time'])

IDS = ['1WF0oldV2g5EOww54LEsE6', '2wJJQfU6wo0MbvXLRJhdVB',
       '4f2XyEPUu8a8n2xBRMEBwC', '7IwPwJYJYUmEno5LVvmJNm']


def init_spotify(client_id, client_secret):
    credentials_manager = SpotifyClientCredentials(
        client_id=client_id, client_secret=client_secret)
    return spotipy.Spotify(client_credentials_manager=credentials_manager)


sp = init_spotify(CLIENT_ID, CLIENT_SECRET)

# Connect to SQLite database
conn = sqlite3.connect(DB)
cursor = conn.cursor()

# Load existing IDs from the database


def load_existing_ids(cursor):
    existing_songs = {row[0]
                      for row in cursor.execute('SELECT song_id FROM songs')}
    existing_artists = {row[0] for row in cursor.execute(
        'SELECT artist_id FROM artists')}
    existing_playlists = {row[0] for row in cursor.execute(
        'SELECT playlist_id FROM playlists')}
    return existing_songs, existing_artists, existing_playlists


existing_songs, existing_artists, existing_playlists = load_existing_ids(
    cursor)

# Insert song data into the database


def insert_song(cursor, song_data):
    cursor.execute('''
        INSERT OR REPLACE INTO songs (song_id, song_name, artist_ids, acousticness, danceability, energy,
                                      instrumentalness, key, liveness, loudness, mode, speechiness, tempo,
                                      time_signature, valence)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        song_data['song_id'], song_data['song_name'], song_data['artist_ids'],
        song_data['acousticness'], song_data['danceability'], song_data['energy'],
        song_data['instrumentalness'], song_data['key'], song_data['liveness'],
        song_data['loudness'], song_data['mode'], song_data['speechiness'],
        song_data['tempo'], song_data['time_signature'], song_data['valence']
    ))
    existing_songs.add(song_data['song_id'])  # Add to existing_songs set

# Insert artist data into the database


def insert_artist(cursor, artist):
    cursor.execute('''
        INSERT OR REPLACE INTO artists (artist_id, artist_name, artist_genres)
        VALUES (?, ?, ?)
    ''', artist)
    conn.commit()

# Insert playlist data into the database


def insert_playlist(cursor, playlist):
    cursor.execute('''
        INSERT INTO playlists (playlist_id, playlist_creator_id, playlist_original_items, playlist_items)
        VALUES (?, ?, ?, ?)
    ''', playlist)
    conn.commit()

# Update playlist metadata in the database


def update_playlist_metadata(cursor, playlist_id, metadata):
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

# Scrape Spotify playlist data


def scrape_playlists(sp, cursor, ids):
    for playlist_id in ids:
        if playlist_id in existing_playlists:
            print(f"Skipping playlist {playlist_id} as it already exists.")
            continue

        try:
            playlist = sp.playlist(playlist_id)
            playlist_creator_id = playlist['owner']['id']
            playlist_items = playlist['tracks']['items']

            if len(playlist_items) < 2:
                print(f"Skipping playlist {
                      playlist_id} because it has fewer than 2 songs.")
                continue

            track_ids = []
            for item in playlist_items:
                track = item['track']
                song_id = track['id']

                if song_id and song_id not in existing_songs:
                    song_data = extract_song_data(sp, track)
                    if song_data:
                        insert_song(cursor, song_data)

                track_ids.append(song_id)

            # Insert the playlist data
            insert_playlist(cursor, (playlist_id, playlist_creator_id, len(
                track_ids), ','.join(track_ids)))
            existing_playlists.add(playlist_id)

        except Exception as e:
            print(f"Error processing playlist {playlist_id}: {e}")

# Extract song data from Spotify API response


def extract_song_data(sp, track):
    try:
        song_id = track['id']
        song_data = {
            'song_id': song_id,
            'song_name': track['name'],
            'artist_ids': ','.join([artist['id'] for artist in track['artists']]),
        }

        # Fetch audio features
        features = sp.audio_features([song_id])[0]
        if features is None:
            return None

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
        return song_data
    except Exception as e:
        print(f"Error extracting song data: {e}")
        return None

# Calculate and update playlist metadata in the database


def calculate_and_update_playlist_metadata(cursor, playlist_id):
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

    # Corrected order of values in the update statement
    cursor.execute('''
        UPDATE playlists
        SET playlist_items_fetched = ?,
            playlist_top_artist_ids = ?,
            playlist_top_genres = ?,
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
        len(song_ids),
        top_artist_ids,
        top_genres_list,
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


# Main script
if __name__ == "__main__":
    playlist_ids = IDS
    scrape_playlists(sp, cursor, playlist_ids)

    # Assuming you want to calculate metadata for the same playlists after scraping
    for playlist_id in playlist_ids:
        calculate_and_update_playlist_metadata(cursor, playlist_id)

    conn.close()
