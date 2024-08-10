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


def fetch_playlist_tracks(playlist_id):
    logger.info(f'Fetching tracks from playlist {
                playlist_id} with a limit of {N_SCRAPE} items')
    track_ids = []
    limit = N_SCRAPE

    try:
        results = sp.playlist_tracks(playlist_id)
        while results and len(track_ids) < limit:
            track_ids.extend(
                track['id'] for item in results['items'] if (track := item.get('track')) and track.get('id')
            )
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

        track_data = [
            (
                track['id'],
                track['name'],
                ','.join(artist['id'] for artist in track['artists']),
                features['acousticness'], features['danceability'], features['energy'], features['instrumentalness'],
                features['key'], features['liveness'], features['loudness'], features['mode'],
                features['speechiness'], features['tempo'], features['time_signature'], features['valence']
            )
            for track, features in zip(tracks['tracks'], audio_features) if track and features
        ]

        return track_data
    except SpotifyException as e:
        logger.error(f"Error fetching track details and audio features: {e}")
        return []


def fetch_artist_details(artist_id):
    logger.info(f'Fetching artist details for {artist_id}')
    try:
        artist = sp.artist(artist_id)
        return artist_id, artist['name'], ','.join(artist['genres'])
    except SpotifyException as e:
        logger.error(f"Error fetching artist details for {artist_id}: {e}")
        return None


def update_playlist_metrics(playlist_id, track_ids):
    logger.info(f'Updating metrics for playlist {playlist_id}')
    if not track_ids:
        return

    cursor.execute(
        'SELECT * FROM songs WHERE song_id IN ({})'.format(','.join('?'*len(track_ids))), track_ids)
    track_details = cursor.fetchall()

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

    cursor.execute(
        'DELETE FROM playlists WHERE playlist_items IS NULL')
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
                    ''', (song_id, song_name, artist_ids, *track_features))

                    new_song_ids.add(song_id)
                    valid_track_ids.append(song_id)

                    unique_artist_ids.update(artist_ids.split(','))

            new_artists = []
            for artist_id in unique_artist_ids:
                if artist_id not in existing_artists:
                    artist_details = fetch_artist_details(artist_id)
                    if artist_details:
                        new_artists.append(artist_details)

            cursor.executemany('''
                INSERT OR REPLACE INTO artists (
                    artist_id, artist_name, artist_genres
                ) VALUES (?, ?, ?)
            ''', new_artists)
            conn.commit()

            if new_song_ids:
                existing_songs.update(new_song_ids)
            if unique_artist_ids:
                existing_artists.update(unique_artist_ids)

            cursor.execute('''
                INSERT OR REPLACE INTO playlists (
                    playlist_id, creator_id, total_tracks, playlist_items
                ) VALUES (?, ?, ?, ?)
            ''', (playlist_id, creator_id, total_tracks, ','.join(valid_track_ids)))
            conn.commit()

            update_playlist_metrics(playlist_id, valid_track_ids)
    except SpotifyException as e:
        logger.error(f"Error processing playlist {playlist_id}: {e}")


def main():
    playlist_ids_to_process = ['2pX1fAX4EkSb14SPHAZndB', '0yEJHHdRIIWceGp0Rt1JT1', '6cB00x9bpjzbIWua0Nt58l', '1EXiX8R5G6H2XHDy37Ufdj', '64FkxTLLTbbPG3B0AAsErs', '5plMEplzpwP6iUJjYOsVqv',
                               '5vSGXhW33I9KFtKTslVdzg', '4nnhWjcavAqdFGHkRrxPuX', '3NraeakOx8Ms5x3LDekFFk', '6jeJcuvFUVEo3JXYA49gms', '6QtUzZuHzFPxUcIo1U8lSh', '2yIJO3lKN5h3lbayRXXm38', '4aIG2sbsxzAoKRCLrKx6x4']
    for playlist_id in playlist_ids_to_process:
        process_playlist(playlist_id)


if __name__ == "__main__":
    main()
