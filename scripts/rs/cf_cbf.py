import sqlite3
import configparser
from collections import defaultdict
from scipy.spatial import distance
import numpy as np

config = configparser.ConfigParser()
config.read('config.cfg')

DB = config['rs']['db_path']
OUTPUT_PATH = config['rs']['cf_cbf_output']


def get_song_details(cursor, track_id):
    cursor.execute(
        'SELECT song_name, artist_ids FROM songs WHERE song_id = ?', (track_id,))
    song = cursor.fetchone()
    if song:
        song_name, artist_ids = song
        artist_ids_list = artist_ids.split(',')

        # Fetch artist names
        artist_names = []
        for artist_id in artist_ids_list:
            cursor.execute(
                'SELECT artist_name FROM artists WHERE artist_id = ?', (artist_id,))
            artist = cursor.fetchone()
            if artist:
                artist_names.append(artist[0])
        return song_name, artist_names
    return None, None


def fetch_audio_features(cursor, track_id):
    cursor.execute(
        f'SELECT {config["rs"]["selected_features"]} FROM songs WHERE song_id = ?', (track_id,))
    return cursor.fetchone()


def fetch_genres(cursor, track_id):
    cursor.execute(
        'SELECT artist_ids FROM songs WHERE song_id = ?', (track_id,))
    artist_ids = cursor.fetchone()[0].split(',')
    genres = set()
    for artist_id in artist_ids:
        cursor.execute(
            'SELECT artist_genres FROM artists WHERE artist_id = ?', (artist_id,))
        artist_genres = cursor.fetchone()[0]
        genres.update(artist_genres.split(','))
    return genres


def calculate_similarity(features1, features2):
    if features1 and features2:
        return 1 - distance.euclidean(features1, features2)
    return 0


def calculate_genre_similarity(genres1, genres2):
    if genres1 and genres2:
        intersection = len(genres1.intersection(genres2))
        union = len(genres1.union(genres2))
        return intersection / union if union != 0 else 0
    return 0


def cf(cursor, ids):
    matched_playlists = []

    # Find playlists that contain the specified track IDs
    for playlist_id, creator_id, track_ids in cursor.execute('SELECT playlist_id, playlist_creator_id, playlist_items FROM playlists'):
        track_ids_list = track_ids.split(',')
        if any(track_id in track_ids_list for track_id in ids):
            matched_playlists.append((playlist_id, creator_id))

    return matched_playlists


def cbf(cursor, ids):
    input_features = []
    input_genres = set()

    # Fetch audio features and genres for input IDs
    for track_id in ids:
        features = fetch_audio_features(cursor, track_id)
        genres = fetch_genres(cursor, track_id)
        if features:
            input_features.append(features)
        if genres:
            input_genres.update(genres)

    input_features_array = np.array(input_features)

    # Calculate min and max audio features for input IDs
    min_max_features = {}
    feature_names = config['rs']['selected_features'].split(', ')
    for j, feature in enumerate(feature_names, 1):
        min_value = np.min(input_features_array[:, j-1])
        max_value = np.max(input_features_array[:, j-1])
        min_max_features[feature] = {'min': min_value, 'max': max_value}

    return input_features, input_genres, min_max_features


def cfcbf(ids):
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    matched_playlists = cf(cursor, ids)
    input_features, input_genres, min_max_features = cbf(cursor, ids)

    song_playlists_count = defaultdict(
        lambda: {'count': 0, 'playlists': [], 'features': None, 'genres': set()})

    for playlist_id, _ in matched_playlists:
        cursor.execute(
            'SELECT playlist_items FROM playlists WHERE playlist_id = ?', (playlist_id,))
        track_ids = cursor.fetchone()[0].split(',')

        for track_id in track_ids:
            if track_id not in ids:
                song_playlists_count[track_id]['count'] += 1
                song_playlists_count[track_id]['playlists'].append(playlist_id)
                song_playlists_count[track_id]['features'] = fetch_audio_features(
                    cursor, track_id)
                song_playlists_count[track_id]['genres'] = fetch_genres(
                    cursor, track_id)

    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        # Write inputted IDs with song details
        f.write('Inputted IDs:\n')
        for i, track_id in enumerate(ids, 1):
            song_name, artist_names = get_song_details(cursor, track_id)
            if song_name and artist_names:
                f.write(f'{i}. https://open.spotify.com/track/{track_id} {
                        ", ".join(artist_names)} - {song_name}\n')
            else:
                f.write(f'{i}. https://open.spotify.com/track/{track_id}\n')

        # Write min max audio features of inputted IDs
        f.write('\nInputted IDs Audio Features:\n')
        for j, (feature, values) in enumerate(min_max_features.items(), 1):
            f.write(f'{j}. {feature}: Min={
                    values["min"]}, Max={values["max"]}\n')

        # Write matched playlists
        f.write('\nMatched Playlists:\n')
        for i, (playlist_id, creator_id) in enumerate(matched_playlists, 1):
            f.write(f'{i}. https://open.spotify.com/playlist/{
                    playlist_id} by https://open.spotify.com/user/{creator_id}\n')

            # Fetch min/max audio features from the playlist
            cursor.execute(
                'SELECT min_acousticness, max_acousticness, min_danceability, max_danceability, min_energy, max_energy, min_instrumentalness, max_instrumentalness, min_liveness, max_liveness, min_loudness, max_loudness, min_speechiness, max_speechiness, min_tempo, max_tempo, min_valence, max_valence FROM playlists WHERE playlist_id = ?', (playlist_id,))
            min_max_values = cursor.fetchone()

            if min_max_values:
                feature_names_with_min_max = [
                    ('acousticness', min_max_values[0], min_max_values[1]),
                    ('danceability', min_max_values[2], min_max_values[3]),
                    ('energy', min_max_values[4], min_max_values[5]),
                    ('instrumentalness', min_max_values[6], min_max_values[7]),
                    ('liveness', min_max_values[8], min_max_values[9]),
                    ('loudness', min_max_values[10], min_max_values[11]),
                    ('speechiness', min_max_values[12], min_max_values[13]),
                    ('tempo', min_max_values[14], min_max_values[15]),
                    ('valence', min_max_values[16], min_max_values[17])
                ]

                for j, (feature, min_value, max_value) in enumerate(feature_names_with_min_max, 1):
                    f.write(f'    {j}. {feature.capitalize()}: Min={
                            min_value}, Max={max_value}\n')

        # Calculate similarity scores
        for track_id, data in song_playlists_count.items():
            if data['features']:
                similarities = [calculate_similarity(
                    data['features'], features) for features in input_features]
                data['average_similarity'] = sum(
                    similarities) / len(similarities)
            else:
                data['average_similarity'] = 0

            if data['genres']:
                data['genre_similarity'] = calculate_genre_similarity(
                    data['genres'], input_genres)
            else:
                data['genre_similarity'] = 0

            # Calculate composite score
            data['composite_score'] = (
                data['count'] * float(config['rs']['count_weight']) +
                data['genre_similarity'] * float(config['rs']['genre_weight']) +
                data['average_similarity'] *
                float(config['rs']['audio_weight'])
            )

        # Sort results by composite score
        sorted_songs = sorted(song_playlists_count.items(
        ), key=lambda item: item[1]['composite_score'], reverse=True)

        # Write results
        f.write('\nResult:\n')
        result_index = 1
        for track_id, data in sorted_songs:
            song_name, artist_names = get_song_details(cursor, track_id)
            if song_name and artist_names:
                playlist_ids_str = ', '.join(data['playlists'])
                f.write(f'{result_index}. https://open.spotify.com/track/{track_id} {", ".join(artist_names)} - {song_name} [Count: {
                        data["count"]} | Genre Similarity: {data["genre_similarity"]:.2f} | Audio Similarity: {data["average_similarity"]:.2f}] [{playlist_ids_str}]\n')
                result_index += 1

    conn.close()
    print('CF-CBF: ', OUTPUT_PATH)


if __name__ == "__main__":
    ids = [
        '7j6eSKC2Hv3lcElPyR1bP3',
    ]
    cfcbf(ids)
