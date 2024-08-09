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
    logger.info(f'Fetching track details and audio features for multiple tracks')
    track_data = []
    try:
        tracks = sp.tracks(track_ids)['tracks']
        audio_features = sp.audio_features(track_ids)

        # Ensure both tracks and features are the same length
        if len(tracks) != len(audio_features):
            logger.warning(
                "Mismatch between number of tracks and audio features")

        for track, features in zip(tracks, audio_features):
            if track and features:
                try:
                    track_data.append((
                        track['id'], track['name'],
                        [artist['id'] for artist in track['artists']],
                        features['acousticness'], features['danceability'],
                        features['energy'], features['instrumentalness'],
                        features['key'], features['liveness'],
                        features['loudness'], features['mode'],
                        features['speechiness'], features['tempo'],
                        features['time_signature'], features['valence']
                    ))
                except KeyError as e:
                    logger.warning(
                        f"Missing expected feature in track or audio features: {e}")
            else:
                if not track:
                    logger.warning(f"Missing track details for some tracks")
                if not features:
                    logger.warning(f"Missing audio features for some tracks")

    except SpotifyException as e:
        logger.error(f"Error fetching track details and audio features: {e}")

    return track_data


def fetch_artist_details(artist_ids):
    logger.info(f'Fetching artist details for multiple artists')
    artist_data = []
    try:
        artists = sp.artists(artist_ids)['artists']
        for artist in artists:
            if artist:
                artist_data.append((
                    artist['id'], artist['name'], ','.join(artist['genres'])
                ))
    except SpotifyException as e:
        logger.error(f"Error fetching artist details: {e}")

    return artist_data


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
            playlist_items = ?
        WHERE playlist_id = ?
    ''', (
        ','.join(filter(None, top_artists)), ','.join(
            filter(None, top_genres)),
        *[min_max_features[feature][i] for feature in [
            'acousticness', 'danceability', 'energy', 'instrumentalness',
            'key', 'liveness', 'loudness', 'mode', 'speechiness',
            'tempo', 'time_signature', 'valence'] for i in range(2)],
        ','.join(filtered_track_ids),
        playlist_id
    ))
    conn.commit()

    cursor.execute(
        'DELETE FROM playlists WHERE playlist_items is NULL OR playlist_items is NULL')
    conn.commit()


def process_playlist(playlist_id):
    logger.info(f'Processing playlist {playlist_id}')
    try:
        if playlist_id in existing_playlists:
            logger.info(f"Playlist with ID: {playlist_id} already exists.")
            return

        playlist_details = sp.playlist(playlist_id)
        total_tracks = playlist_details['tracks']['total']

        if total_tracks >= N_MINIMUM:
            track_ids = fetch_playlist_tracks(playlist_id)
            new_song_ids = set()
            valid_track_ids = []

            track_ids_to_fetch = [
                track_id for track_id in track_ids if track_id not in existing_songs]
            track_details = fetch_track_details_and_audio_features(
                track_ids_to_fetch)

            for track_detail in track_details:
                if track_detail:
                    song_id, song_name, artist_ids, *track_features = track_detail
                    # Convert artist_ids list to a comma-separated string
                    artist_ids_str = ','.join(artist_ids)

                    cursor.execute('''
                        INSERT OR REPLACE INTO songs (
                            song_id, song_name, artist_ids, acousticness, 
                            danceability, energy, instrumentalness, 
                            key, liveness, loudness, mode, 
                            speechiness, tempo, time_signature, valence
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (song_id, song_name, artist_ids_str, *track_features))

                    new_song_ids.add(song_id)
                    valid_track_ids.append(song_id)

                    artist_ids_to_fetch = [
                        artist_id for artist_id in artist_ids if artist_id not in existing_artists]
                    artist_details = fetch_artist_details(artist_ids_to_fetch)

                    for artist_detail in artist_details:
                        if artist_detail:
                            cursor.execute('''
                                INSERT OR REPLACE INTO artists (
                                    artist_id, artist_name, artist_genres
                                ) VALUES (?, ?, ?)
                            ''', artist_detail)
                            existing_artists.add(artist_detail[0])
                else:
                    logger.warning(
                        f"Failed to fetch details for track ID: {track_id}")
            valid_track_ids += [
                track_id for track_id in track_ids if track_id not in new_song_ids]

            track_ids_str = ','.join(valid_track_ids)
            cursor.execute('''
                INSERT OR REPLACE INTO playlists (
                    playlist_id, playlist_creator_id, playlist_original_items, 
                    playlist_items_fetched, playlist_items
                ) VALUES (?, ?, ?, ?, ?)
            ''', (playlist_id, playlist_details['owner']['id'], total_tracks, len(valid_track_ids), track_ids_str))

            conn.commit()

            update_playlist_metrics(playlist_id, valid_track_ids)
        else:
            logger.info(f"Skipping playlist with ID: {
                        playlist_id} because it has fewer than {N_MINIMUM} tracks.")
    except SpotifyException as e:
        logger.error(f"Error processing playlist with ID: {playlist_id}: {e}")


def fetch_user_playlists(username):
    logger.info(f'USER: https://open.spotify.com/user/{username}')
    playlists = []
    try:
        results = sp.user_playlists(username)
        while results:
            playlists.extend(
                item['id'] for item in results['items'] if not item['collaborative'] and item['public']
            )
            if not results['next']:
                break
            results = sp.next(results)
            time.sleep(DELAY_TIME)
    except SpotifyException as e:
        logger.error(f"Error fetching playlists for user {username}: {e}")
    return playlists


usernames = []
try:
    for username in usernames:
        playlist_ids = fetch_user_playlists(username)
        for playlist_id in playlist_ids:
            process_playlist(playlist_id)
finally:
    conn.close()
