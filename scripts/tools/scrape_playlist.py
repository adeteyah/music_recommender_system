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
DB = config['rs']['db_path']
CLIENT_ID = config['api']['client_id']
CLIENT_SECRET = config['api']['client_secret']
DELAY_TIME = float(config['scrape']['delay_time'])
N_MINIMUM = int(config['scrape']['n_minimum_playlist_songs'])
N_SCRAPE = int(config['scrape']['n_scrape'])

# Spotify API credentials
sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(
    client_id=CLIENT_ID, client_secret=CLIENT_SECRET))

# Connect to SQLite database
conn = sqlite3.connect(DB)
cursor = conn.cursor()

IDS = []


def load_existing_ids():
    """Load existing IDs from the database."""
    existing_songs = {row[0]
                      for row in cursor.execute('SELECT song_id FROM songs')}
    existing_artists = {row[0] for row in cursor.execute(
        'SELECT artist_id FROM artists')}
    existing_playlists = {row[0] for row in cursor.execute(
        'SELECT playlist_id FROM playlists')}
    return existing_songs, existing_artists, existing_playlists


existing_songs, existing_artists, existing_playlists = load_existing_ids()


def fetch_playlist_tracks(playlist_id):
    """Fetch tracks from a playlist."""
    logger.info(f'Fetching tracks from playlist {
                playlist_id} with a limit of {N_SCRAPE} items')
    track_ids = []
    try:
        results = sp.playlist_tracks(playlist_id)
        while results and len(track_ids) < N_SCRAPE:
            track_ids.extend(track['id'] for item in results['items'] if (
                track := item.get('track')) and track.get('id'))
            if len(track_ids) >= N_SCRAPE or not results['next']:
                break
            results = sp.next(results)
            time.sleep(DELAY_TIME)
    except SpotifyException as e:
        logger.error(f"Error fetching playlist tracks: {e}")
    return track_ids[:N_SCRAPE]


def fetch_track_details_and_audio_features(track_ids):
    logger.info(f'Fetching track details and audio features for {
                len(track_ids)} tracks')
    valid_track_data = []

    for track_id in track_ids:
        try:
            # Fetch track details and audio features for each individual track ID
            track = sp.track(track_id)
            features = sp.audio_features([track_id])[0]

            if track and features:
                track_data = (
                    track['id'], track['name'],
                    ','.join(artist['id'] for artist in track['artists']),
                    *[features[key] for key in [
                        'acousticness', 'danceability', 'energy', 'instrumentalness',
                        'key', 'liveness', 'loudness', 'mode', 'speechiness',
                        'tempo', 'time_signature', 'valence']]
                )
                valid_track_data.append(track_data)

        except SpotifyException as e:
            # Log the error and skip this track
            logger.error(f"Can't fetch track. Skipping track {track_id}: {e}")
        except Exception as e:
            # Catch any other potential errors and skip the track
            logger.error(f"Unexpected error occurred while fetching track {
                         track_id}. Skipping track: {e}")

    return valid_track_data


def fetch_artist_details(artist_id):
    """Fetch artist details."""
    logger.info(f'Fetching artist details for {artist_id}')
    try:
        artist = sp.artist(artist_id)
        return (artist_id, artist['name'], ','.join(artist['genres']))
    except SpotifyException as e:
        logger.error(f"Error fetching artist details for {artist_id}: {e}")
        return None


def insert_or_replace(table_name, columns, values):
    """Insert or replace a record in a table."""
    cursor.execute(f'INSERT OR REPLACE INTO {table_name} ({columns}) VALUES ({
                   ",".join("?" for _ in values)})', values)


def update_playlist_metrics(playlist_id, track_ids):
    """Update playlist metrics in the database."""
    logger.info(f'Updating metrics for playlist {playlist_id}')
    if not track_ids:
        return

    track_details = [cursor.execute(
        'SELECT * FROM songs WHERE song_id = ?', (track_id,)).fetchone() for track_id in track_ids]
    artist_counts, genre_counts = Counter(), Counter()
    audio_features = {feature: [] for feature in [
        'acousticness', 'danceability', 'energy', 'instrumentalness', 'key', 'liveness',
        'loudness', 'mode', 'speechiness', 'tempo', 'time_signature', 'valence']}

    for details in track_details:
        if details:
            _, _, artist_ids, *features = details
            artist_ids = artist_ids.split(',')
            for artist_id in artist_ids:
                cursor.execute(
                    'SELECT artist_genres FROM artists WHERE artist_id = ?', (artist_id,))
                artist_genres = cursor.fetchone()
                if artist_genres:
                    genres = artist_genres[0].split(',')
                    genre_counts.update(genres)
                artist_counts[artist_id] += 1
            for feature, value in zip(audio_features.keys(), features):
                audio_features[feature].append(value)

    most_common_genres = set(genre for genre, _ in genre_counts.most_common(1))
    minority_track_ids = {
        details[0] for details in track_details if details and not set(details[2].split(',')).intersection(most_common_genres)
    }
    filtered_track_ids = [
        track_id for track_id in track_ids if track_id not in minority_track_ids]

    top_artists = [artist_id for artist_id, _ in artist_counts.most_common(20)]
    top_genres = [genre for genre, _ in genre_counts.most_common(20)]

    min_max_features = {feature: (min(values), max(values)) if values else (
        None, None) for feature, values in audio_features.items()}

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
        ','.join(top_artists), ','.join(top_genres),
        *[min_max_features[feature][i] for feature in audio_features.keys()
          for i in range(2)],
        len(filtered_track_ids), ','.join(filtered_track_ids), playlist_id
    ))
    conn.commit()

    cursor.execute(
        'DELETE FROM playlists WHERE playlist_items IS NULL OR playlist_items = ""')
    conn.commit()


def process_playlist(playlist_id):
    """Process a single playlist."""
    logger.info(f'Processing playlist {playlist_id}')
    if playlist_id in existing_playlists:
        logger.info(f"Playlist with ID: {playlist_id} already exists.")
        return

    try:
        playlist_details = sp.playlist(playlist_id)
        total_tracks = playlist_details['tracks']['total']
        creator_id = playlist_details['owner']['id']

        if total_tracks >= N_MINIMUM:
            track_ids = fetch_playlist_tracks(playlist_id)
            tracks_to_fetch = [
                track_id for track_id in track_ids if track_id not in existing_songs]

            track_data = fetch_track_details_and_audio_features(
                tracks_to_fetch)
            if track_data:
                for track_details in track_data:
                    song_id, song_name, artist_ids_str, *track_features = track_details
                    insert_or_replace('songs', '''
                        song_id, song_name, artist_ids, acousticness, danceability, energy,
                        instrumentalness, key, liveness, loudness, mode, speechiness, tempo,
                        time_signature, valence
                    ''', (song_id, song_name, artist_ids_str, *track_features))
                    new_artist_ids = artist_ids_str.split(',')
                    for artist_id in new_artist_ids:
                        if artist_id not in existing_artists:
                            artist_details = fetch_artist_details(artist_id)
                            if artist_details:
                                insert_or_replace(
                                    'artists', 'artist_id, artist_name, artist_genres', artist_details)
                                existing_artists.add(artist_id)
                    existing_songs.add(song_id)
                time.sleep(DELAY_TIME)

            insert_or_replace('playlists', 'playlist_id, playlist_creator_id, playlist_original_items',
                              (playlist_id, creator_id, total_tracks))
            conn.commit()

            existing_playlists.add(playlist_id)
            update_playlist_metrics(playlist_id, track_ids)
        else:
            logger.info(f"Playlist {playlist_id} has less than {
                        N_MINIMUM} tracks and will be skipped.")
    except SpotifyException as e:
        logger.error(f"Error processing playlist {playlist_id}: {e}")


if __name__ == '__main__':
    for playlist_id in IDS:
        process_playlist(playlist_id)
    logger.info("Processing completed.")
