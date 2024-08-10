import sqlite3
import configparser
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.exceptions import SpotifyException
import time
from collections import Counter
import logging

# Setup logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load configuration
config = configparser.ConfigParser()
config.read('config.cfg')

# Constants
DB_PATH = config['rs']['db_path']
CLIENT_ID = config['api']['client_id']
CLIENT_SECRET = config['api']['client_secret']
DELAY_TIME = float(config['scrape']['delay_time'])
N_MINIMUM_PLAYLIST_SONGS = int(config['scrape']['n_minimum_playlist_songs'])
N_SCRAPE = int(config['scrape']['n_scrape'])

# Spotify API credentials
sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(
    client_id=CLIENT_ID, client_secret=CLIENT_SECRET))

# Connect to SQLite database
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Helper Functions


def load_existing_ids():
    """Load existing IDs from the database."""
    return {
        'songs': {row[0] for row in cursor.execute('SELECT song_id FROM songs')},
        'artists': {row[0] for row in cursor.execute('SELECT artist_id FROM artists')},
        'playlists': {row[0] for row in cursor.execute('SELECT playlist_id FROM playlists')}
    }


def fetch_data_from_spotify(api_call, error_msg, **kwargs):
    """Generic function to fetch data from Spotify API and handle errors."""
    try:
        return api_call(**kwargs)
    except SpotifyException as e:
        logger.error(f"{error_msg}: {e}")
    return None


def insert_or_replace(table_name, columns, values):
    """Insert or replace a record in a table."""
    placeholders = ','.join('?' for _ in values)
    cursor.execute(f'INSERT OR REPLACE INTO {table_name} ({
                   columns}) VALUES ({placeholders})', values)

# Data Processing Functions


def fetch_playlist_tracks(playlist_id):
    """Fetch tracks from a playlist."""
    logger.info(f'Fetching tracks from playlist {
                playlist_id} (limit: {N_SCRAPE})')
    track_ids = []

    results = fetch_data_from_spotify(sp.playlist_tracks, f"API Error: Couldn't fetch tracks from playlist {
                                      playlist_id}", playlist_id=playlist_id)

    while results and len(track_ids) < N_SCRAPE:
        track_ids.extend(
            track['id'] for item in results['items'] if (track := item.get('track')) and track.get('id')
        )
        if len(track_ids) >= N_SCRAPE or not results['next']:
            break
        results = sp.next(results)
        time.sleep(DELAY_TIME)

    return track_ids[:N_SCRAPE]


def fetch_track_and_features(track_ids):
    """Fetch track details and audio features."""
    logger.info(
        f'Fetching track details and audio features (count: {len(track_ids)})')
    track_data = []

    for track_id in track_ids:
        track = fetch_data_from_spotify(sp.track, f"API Error: Skipping track {
                                        track_id} due to fetch error", track_id=track_id)
        features = fetch_data_from_spotify(sp.audio_features, f"API Error: Skipping features for track {
                                           track_id}", tracks=[track_id])[0]

        if track and features:
            track_data.append((
                track['id'], track['name'],
                ','.join(artist['id'] for artist in track['artists']),
                *[features[key] for key in [
                    'acousticness', 'danceability', 'energy', 'instrumentalness',
                    'key', 'liveness', 'loudness', 'mode', 'speechiness',
                    'tempo', 'time_signature', 'valence'
                ]]
            ))

    return track_data


def fetch_artist_details(artist_id):
    """Fetch artist details."""
    artist = fetch_data_from_spotify(sp.artist, f"API Error: Couldn't fetch details for artist {
                                     artist_id}", artist_id=artist_id)
    if artist:
        return (artist_id, artist['name'], ','.join(artist['genres']))
    return None


def update_playlist_metrics(playlist_id, track_ids):
    """Update playlist metrics in the database."""
    logger.info(f'Updating metrics for playlist {playlist_id}')
    if not track_ids:
        return

    artist_counts, genre_counts = Counter(), Counter()
    audio_features = {feature: [] for feature in [
        'acousticness', 'danceability', 'energy', 'instrumentalness',
        'key', 'liveness', 'loudness', 'mode', 'speechiness',
        'tempo', 'time_signature', 'valence']}

    track_details = [cursor.execute(
        'SELECT * FROM songs WHERE song_id = ?', (track_id,)).fetchone() for track_id in track_ids]

    for details in track_details:
        if details:
            artist_ids, *features = details[2:4], details[4:]
            artist_ids = artist_ids[0].split(',')

            for artist_id in artist_ids:
                artist_genres = cursor.execute(
                    'SELECT artist_genres FROM artists WHERE artist_id = ?', (artist_id,)).fetchone()
                if artist_genres:
                    genre_counts.update(artist_genres[0].split(','))
                artist_counts[artist_id] += 1

            for feature, value in zip(audio_features.keys(), features):
                audio_features[feature].append(value)

    min_max_features = {feature: (min(values), max(values)) if values else (
        None, None) for feature, values in audio_features.items()}
    top_artists = ','.join(
        [artist_id for artist_id, _ in artist_counts.most_common(20)])
    top_genres = ','.join([genre for genre, _ in genre_counts.most_common(20)])
    filtered_track_ids = [track_id for track_id in track_ids if set(cursor.execute(
        'SELECT artist_genres FROM artists WHERE artist_id = ?', (track_id.split(',')[0],)).fetchone()[0].split(',')).intersection(genre_counts)]

    insert_or_replace('playlists', '''
        playlist_top_artist_ids, playlist_top_genres, 
        min_acousticness, max_acousticness, min_danceability, max_danceability, 
        min_energy, max_energy, min_instrumentalness, max_instrumentalness, 
        min_key, max_key, min_liveness, max_liveness, 
        min_loudness, max_loudness, min_mode, max_mode, 
        min_speechiness, max_speechiness, min_tempo, max_tempo, 
        min_time_signature, max_time_signature, min_valence, max_valence, 
        playlist_items_fetched, playlist_items, playlist_id
    ''', (
        top_artists, top_genres,
        *[min_max_features[feature][i] for feature in audio_features.keys()
          for i in range(2)],
        len(filtered_track_ids), ','.join(filtered_track_ids), playlist_id
    ))
    conn.commit()

# Main Process


def process_playlist(playlist_id, existing_ids):
    """Process a single playlist."""
    logger.info(f'Processing playlist {playlist_id}')

    if playlist_id in existing_ids['playlists']:
        logger.info(f"Already fetched playlist: {playlist_id}")
        return

    playlist = fetch_data_from_spotify(sp.playlist, f"API Error: Couldn't process playlist {
                                       playlist_id}", playlist_id=playlist_id)
    if not playlist or playlist['tracks']['total'] < N_MINIMUM_PLAYLIST_SONGS:
        logger.info(f"Skipping playlist {playlist_id} (less than {
                    N_MINIMUM_PLAYLIST_SONGS} tracks).")
        return

    track_ids = fetch_playlist_tracks(playlist_id)
    tracks_to_fetch = [
        track_id for track_id in track_ids if track_id not in existing_ids['songs']]

    track_data = fetch_track_and_features(tracks_to_fetch)
    for track in track_data:
        song_id, song_name, artist_ids_str, *track_features = track
        insert_or_replace('songs', 'song_id, song_name, artist_ids, acousticness, danceability, energy, instrumentalness, key, liveness, loudness, mode, speechiness, tempo, time_signature, valence',
                          (song_id, song_name, artist_ids_str, *track_features))

        for artist_id in artist_ids_str.split(','):
            if artist_id not in existing_ids['artists']:
                artist_details = fetch_artist_details(artist_id)
                if artist_details:
                    insert_or_replace(
                        'artists', 'artist_id, artist_name, artist_genres', artist_details)
                    existing_ids['artists'].add(artist_id)

        existing_ids['songs'].add(song_id)
        time.sleep(DELAY_TIME)

    insert_or_replace('playlists', 'playlist_id, playlist_creator_id, playlist_original_items',
                      (playlist_id, playlist['owner']['id'], playlist['tracks']['total']))
    conn.commit()

    existing_ids['playlists'].add(playlist_id)
    update_playlist_metrics(playlist_id, track_ids)


# Entry Point
if __name__ == '__main__':
    existing_ids = load_existing_ids()
    IDS = []  # Add playlist IDs to process
    for playlist_id in IDS:
        process_playlist(playlist_id, existing_ids)
    logger.info("Processing complete.")
