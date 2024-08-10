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
N_MINIMUM = int(config['scrape']['n_minimum_playlist_songs'])
N_SCRAPE = int(config['scrape']['n_scrape'])

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


def insert_song(song):
    cursor.execute('''
        INSERT INTO songs (song_id, song_name, artist_ids, acousticness, danceability, energy, 
                           instrumentalness, key, liveness, loudness, mode, speechiness, tempo, 
                           time_signature, valence)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', song)
    conn.commit()


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
    cursor.execute(
        'SELECT playlist_items FROM playlists WHERE playlist_id = ?', (playlist_id,))
    playlist_items = cursor.fetchone()[0]

    if not playlist_items:
        return

    track_ids = playlist_items.split(',')

    if not track_ids:
        return

    # Initialize min/max with extreme values
    min_max_values = {
        'acousticness': [float('inf'), float('-inf')],
        'danceability': [float('inf'), float('-inf')],
        'energy': [float('inf'), float('-inf')],
        'instrumentalness': [float('inf'), float('-inf')],
        'key': [float('inf'), float('-inf')],
        'liveness': [float('inf'), float('-inf')],
        'loudness': [float('inf'), float('-inf')],
        'mode': [float('inf'), float('-inf')],
        'speechiness': [float('inf'), float('-inf')],
        'tempo': [float('inf'), float('-inf')],
        'time_signature': [float('inf'), float('-inf')],
        'valence': [float('inf'), float('-inf')]
    }

    artist_counter = collections.Counter()
    genre_counter = collections.Counter()

    for track_id in track_ids:
        cursor.execute('SELECT * FROM songs WHERE song_id = ?', (track_id,))
        song = cursor.fetchone()
        if not song:
            continue

        (song_id, song_name, artist_ids, acousticness, danceability, energy, instrumentalness,
         key, liveness, loudness, mode, speechiness, tempo, time_signature, valence) = song

        # Update min/max values
        min_max_values['acousticness'][0] = min(
            min_max_values['acousticness'][0], acousticness)
        min_max_values['acousticness'][1] = max(
            min_max_values['acousticness'][1], acousticness)
        min_max_values['danceability'][0] = min(
            min_max_values['danceability'][0], danceability)
        min_max_values['danceability'][1] = max(
            min_max_values['danceability'][1], danceability)
        min_max_values['energy'][0] = min(min_max_values['energy'][0], energy)
        min_max_values['energy'][1] = max(min_max_values['energy'][1], energy)
        min_max_values['instrumentalness'][0] = min(
            min_max_values['instrumentalness'][0], instrumentalness)
        min_max_values['instrumentalness'][1] = max(
            min_max_values['instrumentalness'][1], instrumentalness)
        min_max_values['key'][0] = min(min_max_values['key'][0], key)
        min_max_values['key'][1] = max(min_max_values['key'][1], key)
        min_max_values['liveness'][0] = min(
            min_max_values['liveness'][0], liveness)
        min_max_values['liveness'][1] = max(
            min_max_values['liveness'][1], liveness)
        min_max_values['loudness'][0] = min(
            min_max_values['loudness'][0], loudness)
        min_max_values['loudness'][1] = max(
            min_max_values['loudness'][1], loudness)
        min_max_values['mode'][0] = min(min_max_values['mode'][0], mode)
        min_max_values['mode'][1] = max(min_max_values['mode'][1], mode)
        min_max_values['speechiness'][0] = min(
            min_max_values['speechiness'][0], speechiness)
        min_max_values['speechiness'][1] = max(
            min_max_values['speechiness'][1], speechiness)
        min_max_values['tempo'][0] = min(min_max_values['tempo'][0], tempo)
        min_max_values['tempo'][1] = max(min_max_values['tempo'][1], tempo)
        min_max_values['time_signature'][0] = min(
            min_max_values['time_signature'][0], time_signature)
        min_max_values['time_signature'][1] = max(
            min_max_values['time_signature'][1], time_signature)
        min_max_values['valence'][0] = min(
            min_max_values['valence'][0], valence)
        min_max_values['valence'][1] = max(
            min_max_values['valence'][1], valence)

        # Update artist and genre counters
        artist_ids_list = artist_ids.split(',')
        for artist_id in artist_ids_list:
            cursor.execute(
                'SELECT artist_genres FROM artists WHERE artist_id = ?', (artist_id,))
            genres = cursor.fetchone()[0]
            genre_list = genres.split(',')
            genre_counter.update(genre_list)
            artist_counter.update([artist_id])

    # Get top 20 artists and genres
    top_artists = [artist for artist, _ in artist_counter.most_common(20)]
    top_genres = [genre for genre, _ in genre_counter.most_common(20)]

    metadata = (
        len(track_ids),
        ','.join(top_artists),
        ','.join(top_genres),
        min_max_values['acousticness'][0], min_max_values['acousticness'][1],
        min_max_values['danceability'][0], min_max_values['danceability'][1],
        min_max_values['energy'][0], min_max_values['energy'][1],
        min_max_values['instrumentalness'][0], min_max_values['instrumentalness'][1],
        min_max_values['key'][0], min_max_values['key'][1],
        min_max_values['liveness'][0], min_max_values['liveness'][1],
        min_max_values['loudness'][0], min_max_values['loudness'][1],
        min_max_values['mode'][0], min_max_values['mode'][1],
        min_max_values['speechiness'][0], min_max_values['speechiness'][1],
        min_max_values['tempo'][0], min_max_values['tempo'][1],
        min_max_values['time_signature'][0], min_max_values['time_signature'][1],
        min_max_values['valence'][0], min_max_values['valence'][1]
    )
    update_playlist_metadata(playlist_id, metadata)


if __name__ == "__main__":
    ids = ['2pX1fAX4EkSb14SPHAZndB', '0yEJHHdRIIWceGp0Rt1JT1']
    scrape(ids)
    for playlist_id in ids:
        calculate_playlist_metadata(playlist_id)
        print(f"Updated metadata for playlist {playlist_id}")
