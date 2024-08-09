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

DB = config['rs']['db_path']
CLIENT_ID = config['api']['client_id']
CLIENT_SECRET = config['api']['client_secret']
DELAY_TIME = float(config['api']['delay_time'])
N_MINIMUM = int(config['rs']['n_minimum_playlist_songs'])
N_SCRAPE = int(config['rs']['n_scrape'])

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


def fetch_playlist_tracks(playlist_id):
    logger.info(f'Fetching tracks from playlist {
                playlist_id} with a limit of {N_SCRAPE} items')
    track_ids = []
    limit = N_SCRAPE

    try:
        results = sp.playlist_tracks(playlist_id)
        while results and len(track_ids) < limit:
            for item in results['items']:
                track = item.get('track')
                if track:
                    track_id = track.get('id')
                    if track_id:
                        track_ids.append(track_id)
                else:
                    logger.warning(f'Unexpected track item structure: {item}')
            if len(track_ids) >= limit or not results['next']:
                break
            results = sp.next(results)
            time.sleep(DELAY_TIME)
    except SpotifyException as e:
        logger.error(f"Error fetching playlist tracks: {e}")

    return track_ids[:limit]


def fetch_track_details_and_audio_features(track_ids):
    logger.info(f'Fetching track details and audio features for {
                len(track_ids)} tracks')
    try:
        tracks = sp.tracks(track_ids)
        audio_features = sp.audio_features(track_ids)

        track_data = []
        for track, features in zip(tracks['tracks'], audio_features):
            if not track or not features:
                if not track:
                    logger.warning(f"No track found for given ID.")
                if not features:
                    logger.warning(f"No audio features found for track ID.")
                continue

            feature_values = [features[key] for key in [
                'acousticness', 'danceability', 'energy', 'instrumentalness',
                'key', 'liveness', 'loudness', 'mode', 'speechiness',
                'tempo', 'time_signature', 'valence']]

            track_data.append((
                track['id'], track['name'],
                [artist['id'] for artist in track['artists']],
                *feature_values
            ))

        return track_data
    except SpotifyException as e:
        logger.error(f"Error fetching track details and audio features: {e}")
        return None


def fetch_artist_details(artist_id):
    logger.info(f'Fetching artist details for {artist_id}')
    try:
        artist = sp.artist(artist_id)
        return (artist_id, artist['name'], ','.join(artist['genres']))
    except SpotifyException as e:
        logger.error(f"Error fetching artist details for {artist_id}: {e}")
        return None


def record_exists(table_name, record_id):
    cursor.execute(f'SELECT 1 FROM {table_name} WHERE {
                   table_name[:-1]}_id = ?', (record_id,))
    return cursor.fetchone() is not None


def update_playlist_metrics(playlist_id, track_ids):
    logger.info(f'Updating metrics for playlist {playlist_id}')
    if not track_ids:
        return

    track_details = []
    for track_id in track_ids:
        cursor.execute('SELECT * FROM songs WHERE song_id = ?', (track_id,))
        track_details.append(cursor.fetchone())

    artist_counts = Counter()
    genre_counts = Counter()
    audio_features = {feature: [] for feature in [
        'acousticness', 'danceability', 'energy', 'instrumentalness',
        'key', 'liveness', 'loudness', 'mode', 'speechiness',
        'tempo', 'time_signature', 'valence']}

    track_genres = []

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
                    track_genres.extend(genres)
                    genre_counts.update(genres)
                artist_counts[artist_id] += 1
            for feature, value in zip(audio_features.keys(), features):
                audio_features[feature].append(value)

    most_common_genres = set(genre for genre, _ in genre_counts.most_common(1))

    minority_track_ids = set()
    for details in track_details:
        if details:
            _, _, artist_ids, *features = details
            artist_ids = artist_ids.split(',')
            for artist_id in artist_ids:
                cursor.execute(
                    'SELECT artist_genres FROM artists WHERE artist_id = ?', (artist_id,))
                artist_genres = cursor.fetchone()
                if artist_genres:
                    genres = set(artist_genres[0].split(','))
                    if not genres & most_common_genres:
                        minority_track_ids.add(details[0])

    filtered_track_ids = [
        track_id for track_id in track_ids if track_id not in minority_track_ids]

    top_artists = [artist_id for artist_id, _ in artist_counts.most_common(20)]
    top_genres = [genre for genre, _ in genre_counts.most_common(20)]

    top_artists += [None] * (20 - len(top_artists))
    top_genres += [None] * (20 - len(top_genres))

    min_max_features = {feature: (min(values), max(values)) if values else (None, None)
                        for feature, values in audio_features.items()}

    cursor.execute('''
        UPDATE playlists SET 
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
            min_valence = ?, max_valence = ?,
            playlist_items_fetched = ?,
            playlist_items = ?
        WHERE playlist_id = ?
    ''', (
        ','.join(filter(None, top_artists)), ','.join(
            filter(None, top_genres)),
        *[min_max_features[feature][i] for feature in [
            'acousticness', 'danceability', 'energy', 'instrumentalness',
            'key', 'liveness', 'loudness', 'mode', 'speechiness',
            'tempo', 'time_signature', 'valence'] for i in range(2)],
        len(filtered_track_ids),
        ','.join(filtered_track_ids),
        playlist_id
    ))
    conn.commit()


def process_playlist(playlist_id):
    logger.info(f'Processing playlist {playlist_id}')
    try:
        if playlist_id in existing_playlists:
            logger.info(f"Playlist with ID: {playlist_id} already exists.")
            return

        playlist_details = sp.playlist(playlist_id)
        total_tracks = playlist_details['tracks']['total']
        creator_id = playlist_details['owner']['id']

        if total_tracks >= N_MINIMUM:
            track_ids = fetch_playlist_tracks(playlist_id)
            new_song_ids = set()
            valid_track_ids = []

            unique_artist_ids = set()
            tracks_to_fetch = []
            for track_id in track_ids:
                if track_id not in existing_songs:
                    tracks_to_fetch.append(track_id)
                valid_track_ids.append(track_id)

            track_data = fetch_track_details_and_audio_features(
                tracks_to_fetch)

            if track_data:
                for track_details in track_data:
                    song_id, song_name, artist_ids, *track_features = track_details
                    cursor.execute('''
                        INSERT OR REPLACE INTO songs (
                            song_id, song_name, artist_ids, acousticness, 
                            danceability, energy, instrumentalness, 
                            key, liveness, loudness, mode, 
                            speechiness, tempo, time_signature, valence
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (song_id, song_name, ','.join(artist_ids), *track_features))

                    new_song_ids.add(song_id)
                    valid_track_ids.append(song_id)

                    unique_artist_ids.update(artist_ids)

                    for artist_id in artist_ids:
                        if artist_id not in existing_artists:
                            artist_details = fetch_artist_details(artist_id)
                            if artist_details:
                                cursor.execute('''
                                    INSERT OR REPLACE INTO artists (
                                        artist_id, artist_name, artist_genres
                                    ) VALUES (?, ?, ?)
                                ''', artist_details)
                                existing_artists.add(artist_id)

                    existing_songs.add(track_id)

                time.sleep(DELAY_TIME)

            cursor.execute('''
                INSERT OR REPLACE INTO playlists (
                    playlist_id, playlist_creator_id, playlist_original_items
                ) VALUES (?, ?, ?)
            ''', (playlist_id, creator_id, total_tracks))
            conn.commit()

            existing_playlists.add(playlist_id)
            update_playlist_metrics(playlist_id, valid_track_ids)
        else:
            logger.info(f"Playlist {playlist_id} has less than {
                        N_MINIMUM} tracks and will be skipped.")
    except SpotifyException as e:
        logger.error(f"Error processing playlist {playlist_id}: {e}")


if __name__ == '__main__':
    playlist_ids = ['4ShulrGSaVc6ZvbLzuegYK', '4HR8Y0emDAiE1wM3XILoZP', '5KgQT9YWz3EqhIN4Jh69IU', '4wkCgQR6AQ3F1yKfXsVfo6', '6bd0a0UHF8wGthySFrxRFg', '73n5eYkmp0xA46hPXg4AJ5', '49i2nsUghVlzKOnNJtzhkJ',
                    '08VwBRNVGPcF0vT5uKAHtT', '3l5y0IdNtMYFf4YEqQjWj2', '0PtjYd3OYwJ6CvzdLJVoP9', '6h8B6q9PumfbQFf6gJ2zqI', '7k30DQOSdd8qIQbhsxzsxV', '4qiS6MsylP3SQhfAre2O9g', '0RxrVAVY0Bz067UajBMYPS']

    for playlist_id in playlist_ids:
        process_playlist(playlist_id)

    logger.info("Processing completed.")
