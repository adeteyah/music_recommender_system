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


def load_existing_ids(cursor):
    existing_songs = {row[0]
                      for row in cursor.execute('SELECT song_id FROM songs')}
    existing_artists = {row[0] for row in cursor.execute(
        'SELECT artist_id FROM artists')}
    existing_playlists = {row[0] for row in cursor.execute(
        'SELECT playlist_id FROM playlists')}
    return existing_songs, existing_artists, existing_playlists


def fetch_playlist_tracks(playlist_id, limit):
    logger.info(f'Fetching tracks from playlist {
                playlist_id} with a limit of {limit} items')
    track_ids = []

    try:
        results = sp.playlist_tracks(playlist_id, limit=limit)
        track_ids = [item['track']['id'] for item in results['items']
                     if item.get('track') and item['track'].get('id')]

        while len(track_ids) < limit and results.get('next'):
            results = sp.next(results)
            track_ids.extend([item['track']['id'] for item in results['items'] if item.get(
                'track') and item['track'].get('id')])
            time.sleep(DELAY_TIME)
    except SpotifyException as e:
        logger.error(f"Error fetching playlist tracks: {e}")

    return track_ids[:limit]


def fetch_track_details_and_audio_features(track_ids):
    logger.info(f'Fetching track details and audio features for {
                len(track_ids)} tracks')

    try:
        tracks = sp.tracks(track_ids)['tracks']
        audio_features = sp.audio_features(track_ids)

        track_data = []
        for track, features in zip(tracks, audio_features):
            if not track or not features:
                logger.warning(f"Missing track or audio features for track ID: {
                               track.get('id', 'Unknown')}")
                continue

            feature_values = [features[key] for key in [
                'acousticness', 'danceability', 'energy', 'instrumentalness',
                'key', 'liveness', 'loudness', 'mode', 'speechiness',
                'tempo', 'time_signature', 'valence']]

            track_data.append((
                track['id'], track['name'],
                # Convert list to a comma-separated string
                ','.join([artist['id'] for artist in track['artists']]),
                *feature_values
            ))

        return track_data
    except SpotifyException as e:
        logger.error(f"Error fetching track details and audio features: {e}")
        return []


def fetch_artist_details(artist_id):
    logger.info(f'Fetching artist details for {artist_id}')
    try:
        artist = sp.artist(artist_id)
        return (artist_id, artist['name'], ','.join(artist['genres']))
    except SpotifyException as e:
        logger.error(f"Error fetching artist details for {artist_id}: {e}")
        return None


def update_playlist_metrics(cursor, playlist_id, track_ids):
    logger.info(f'Updating metrics for playlist {playlist_id}')
    if not track_ids:
        return

    cursor.execute('SELECT * FROM songs WHERE song_id IN ({})'.format(
        ','.join(['?']*len(track_ids))), track_ids)
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

    minority_track_ids = {details[0] for details in track_details if details and not set(cursor.execute(
        'SELECT artist_genres FROM artists WHERE artist_id = ?', (details[2].split(',')[0],)).fetchone()[0].split(',')).intersection(most_common_genres)}

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


def process_playlist(cursor, playlist_id, existing_songs, existing_artists, existing_playlists):
    logger.info(f'Processing playlist {playlist_id}')
    try:
        if playlist_id in existing_playlists:
            logger.info(f"Playlist with ID: {playlist_id} already exists.")
            return

        playlist_details = sp.playlist(playlist_id)
        total_tracks = playlist_details['tracks']['total']
        creator_id = playlist_details['owner']['id']

        if total_tracks >= N_MINIMUM:
            track_ids = fetch_playlist_tracks(playlist_id, N_SCRAPE)
            new_song_ids = set()

            tracks_to_fetch = [
                track_id for track_id in track_ids if track_id not in existing_songs]

            track_data = fetch_track_details_and_audio_features(
                tracks_to_fetch)

            if track_data:
                cursor.executemany('''
                    INSERT OR REPLACE INTO songs (
                        song_id, song_name, artist_ids, acousticness,
                        danceability, energy, instrumentalness,
                        key, liveness, loudness, mode,
                        speechiness, tempo, time_signature, valence
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', track_data)
                new_song_ids.update([track[0] for track in track_data])

            new_artist_ids = set()

            for track in track_data:
                artist_ids = track[2].split(',')
                new_artist_ids.update(artist_ids)

            artists_to_fetch = [
                artist_id for artist_id in new_artist_ids if artist_id not in existing_artists]

            for artist_id in artists_to_fetch:
                artist_details = fetch_artist_details(artist_id)
                if artist_details:
                    cursor.execute('''
                        INSERT OR REPLACE INTO artists (artist_id, artist_name, artist_genres)
                        VALUES (?, ?, ?)
                    ''', artist_details)

            update_playlist_metrics(cursor, playlist_id, track_ids)

            cursor.execute('''
                INSERT OR REPLACE INTO playlists (
                    playlist_id, playlist_name, playlist_description,
                    creator_id, playlist_num_tracks, playlist_num_followers,
                    playlist_top_artist_ids, playlist_top_genres,
                    min_acousticness, max_acousticness, min_danceability, max_danceability,
                    min_energy, max_energy, min_instrumentalness, max_instrumentalness,
                    min_key, max_key, min_liveness, max_liveness,
                    min_loudness, max_loudness, min_mode, max_mode,
                    min_speechiness, max_speechiness, min_tempo, max_tempo,
                    min_time_signature, max_time_signature, min_valence, max_valence,
                    playlist_items_fetched, playlist_items
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                playlist_id, playlist_details['name'], playlist_details['description'],
                creator_id, total_tracks, playlist_details['followers']['total'],
                None, None, None, None, None, None, None, None, None, None, None, None,
                None, None, None, None, None, None, None, None, None, None,
                len(track_ids), ','.join(track_ids)
            ))
        else:
            logger.info(f"Playlist with ID: {
                        playlist_id} has less than the minimum required tracks.")

    except SpotifyException as e:
        logger.error(f"Error processing playlist {playlist_id}: {e}")


def main():
    with sqlite3.connect(DB) as conn:
        cursor = conn.cursor()
        existing_songs, existing_artists, existing_playlists = load_existing_ids(
            cursor)

        playlist_ids = ['2pX1fAX4EkSb14SPHAZndB', '0yEJHHdRIIWceGp0Rt1JT1', '6cB00x9bpjzbIWua0Nt58l', '1EXiX8R5G6H2XHDy37Ufdj', '64FkxTLLTbbPG3B0AAsErs', '5plMEplzpwP6iUJjYOsVqv',
                        '5vSGXhW33I9KFtKTslVdzg', '4nnhWjcavAqdFGHkRrxPuX', '3NraeakOx8Ms5x3LDekFFk', '6jeJcuvFUVEo3JXYA49gms', '6QtUzZuHzFPxUcIo1U8lSh', '2yIJO3lKN5h3lbayRXXm38', '4aIG2sbsxzAoKRCLrKx6x4']
        for playlist_id in playlist_ids:
            process_playlist(cursor, playlist_id, existing_songs,
                             existing_artists, existing_playlists)

        conn.commit()


if __name__ == "__main__":
    main()
