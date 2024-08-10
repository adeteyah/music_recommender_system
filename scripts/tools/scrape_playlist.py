import sqlite3
import configparser
import spotipy
import time
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


if __name__ == "__main__":
    ids = ['2pX1fAX4EkSb14SPHAZndB', '0yEJHHdRIIWceGp0Rt1JT1']
    scrape(ids)
