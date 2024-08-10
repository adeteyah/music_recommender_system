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
        if playlist_id in existing_playlists:
            print(f"Playlist {playlist_id} already exists. Skipping...")
            continue

        playlist = sp.playlist(playlist_id)
        playlist_creator_id = playlist['owner']['id']
        playlist_original_items = len(playlist['tracks']['items'])
        track_ids = []
        artist_ids_set = set()

        for item in playlist['tracks']['items']:
            track = item['track']
            if not track:
                continue

            song_id = track['id']
            if song_id in existing_songs:
                track_ids.append(song_id)
                continue

            song_name = track['name']
            artist_ids = ','.join([artist['id']
                                  for artist in track['artists']])
            artist_ids_set.update(artist['id'] for artist in track['artists'])

            # Fetch audio features
            audio_features = sp.audio_features([song_id])[0]
            if audio_features is None:
                print(f"Audio features not found for song: {song_id}")
                continue

            # Extract audio features
            acousticness = audio_features.get('acousticness', None)
            danceability = audio_features.get('danceability', None)
            energy = audio_features.get('energy', None)
            instrumentalness = audio_features.get('instrumentalness', None)
            key = audio_features.get('key', None)
            liveness = audio_features.get('liveness', None)
            loudness = audio_features.get('loudness', None)
            mode = audio_features.get('mode', None)
            speechiness = audio_features.get('speechiness', None)
            tempo = audio_features.get('tempo', None)
            time_signature = audio_features.get('time_signature', None)
            valence = audio_features.get('valence', None)

            song_data = (song_id, song_name, artist_ids, acousticness, danceability, energy,
                         instrumentalness, key, liveness, loudness, mode, speechiness, tempo,
                         time_signature, valence)
            insert_song(song_data)
            track_ids.append(song_id)

        for artist_id in artist_ids_set:
            if artist_id in existing_artists:
                continue

            artist = sp.artist(artist_id)
            artist_name = artist['name']
            artist_genres = ','.join(artist['genres'])

            artist_data = (artist_id, artist_name, artist_genres)
            insert_artist(artist_data)

        playlist_data = (playlist_id, playlist_creator_id,
                         playlist_original_items, ','.join(track_ids))
        insert_playlist(playlist_data)

        print(f"Finished scraping playlist {playlist_id}")
        time.sleep(DELAY_TIME)


def calculate_playlist_metadata(playlist_id):
    # Fetch playlist items
    cursor.execute(
        "SELECT playlist_items FROM playlists WHERE playlist_id = ?", (playlist_id,))
    result = cursor.fetchone()
    if not result:
        print(f"No playlist items found for playlist {playlist_id}.")
        return

    playlist_items = result[0].split(',')

    if len(playlist_items) < 2:
        print(f"Skipping metadata calculation for playlist {
              playlist_id} as it has fewer than 2 songs.")
        return

    # Initialize min/max values
    min_acousticness = min_danceability = min_energy = min_instrumentalness = float(
        'inf')
    max_acousticness = max_danceability = max_energy = max_instrumentalness = float(
        '-inf')
    min_key = min_liveness = min_loudness = min_mode = min_speechiness = min_tempo = min_time_signature = min_valence = float(
        'inf')
    max_key = max_liveness = max_loudness = max_mode = max_speechiness = max_tempo = max_time_signature = max_valence = float(
        '-inf')

    artist_genres = {}
    artist_counts = {}

    # Process each song in the playlist
    for song_id in playlist_items:
        cursor.execute("SELECT * FROM songs WHERE song_id = ?", (song_id,))
        song_data = cursor.fetchone()
        if not song_data:
            print(f"Song {song_id} not found in the songs table.")
            continue

        _, _, artist_ids, acousticness, danceability, energy, instrumentalness, key, liveness, loudness, mode, speechiness, tempo, time_signature, valence = song_data

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

        # Count artist appearances and genres
        for artist_id in artist_ids.split(','):
            cursor.execute(
                "SELECT artist_name, artist_genres FROM artists WHERE artist_id = ?", (artist_id,))
            artist_info = cursor.fetchone()
            if artist_info:
                artist_name, genres = artist_info
                artist_counts[artist_name] = artist_counts.get(
                    artist_name, 0) + 1

                if genres:
                    for genre in genres.split(','):
                        artist_genres[genre] = artist_genres.get(genre, 0) + 1

    # Sort and select top 20 artists and genres
    top_artists = sorted(
        artist_counts, key=artist_counts.get, reverse=True)[:20]
    top_genres = sorted(
        artist_genres, key=artist_genres.get, reverse=True)[:20]

    # Update playlist metadata
    cursor.execute('''
        UPDATE playlists
        SET playlist_items_fetched = ?, playlist_top_artist_ids = ?, playlist_top_genres = ?,
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
        WHERE playlist_id = ?''',
                   (len(playlist_items), ','.join(top_artists), ','.join(top_genres),
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
                    playlist_id))
    conn.commit()


if __name__ == "__main__":
    ids = ['5reCpCSw8NgB5QjGILvrhX', '1Uon4YjxrFKECs3cxuq0s7', '3DtdtaTZfZPNEqttZ2vVG0', '70mJkUkq5bIP6w6BI25cov', '6mqJU05sWmXTuY1iO1RXmK', '7vq57TiBTpm5IMfiWs5PBh', '7E8T698a0KyfUuXyE5Wrve', '6vBkuOkhUAu77sBYdMAVDJ', '1YXxGeLWtd8qeHJTc6zW6u',
           '5xl6pngUNTpJkMEcgq70an', '15NJtngbNqxyN47NV7ssXJ', '29xqS54FRT6qeWDXnYLwOE', '4BFbPoGAwZsEJJKW7c0IUF', '4yNUxofGRcnw7UknxONOYC', '3iuP5ovrQcGkfRtLk11zau', '2S9qc8q5xU9M9HtLWKHFRJ', '64L6MntymuqQRuif9nVM6c', '2JsYYV1eTQsHjznasUIaru', '4x9Id1MUfg681SR5tR40vV']
    scrape(ids)
    for playlist_id in ids:
        calculate_playlist_metadata(playlist_id)
        print(f"Updated metadata for playlist {playlist_id}")
