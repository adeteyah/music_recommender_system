from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from collections import defaultdict
import sqlite3
import configparser
import re

# Read configuration file
config = configparser.ConfigParser()
config.read('config.cfg')

MODEL = 'Content-based Filtering + Collaborative Filtering'
DB = config['rs']['db_path']
OUTPUT_PATH = config['rs']['cbf_cf_output']
CBF_FEATURES = config['hp']['cbf_cf_features'].split(', ')
REAL_BOUND_VAL = float(config['hp']['cbf_cf_real_bound'])
MODE_BOUND_VAL = int(config['hp']['cbf_cf_mode_bound'])
TIME_SIGNATURE_BOUND_VAL = int(config['hp']['cbf_cf_time_signature_bound'])
TEMPO_BOUND_VAL = float(config['hp']['cbf_cf_tempo_bound'])
SONGS_PER_ARTIST = int(config['hp']['songs_per_artist'])
ALL_GENRES = ["pop", "rock", "hip hop", "jazz", "classical",
              "electronic", "country", "blues", "reggae", "soul"]

# Define specific bound values for features
SEPARATE_BOUNDS = {
    'mode': MODE_BOUND_VAL,
    'time_signature': TIME_SIGNATURE_BOUND_VAL,
    'tempo': TEMPO_BOUND_VAL
}


def get_song_vector(song_info, all_genres):
    # Assuming the first 3 fields are song_id, song_name, artist_ids
    audio_features = np.array(song_info[3:])
    # Assuming single artist per song for simplicity
    artist_id = song_info[2].split(',')[0]
    genres = get_artist_info(conn, artist_id)[1].split(',')
    genre_vector = generate_genre_vector(genres, all_genres)
    return np.concatenate([audio_features, genre_vector])


def generate_genre_vector(genres, all_genres):
    genre_vector = np.zeros(len(all_genres))
    for genre in genres:
        if genre in all_genres:
            genre_vector[all_genres.index(genre)] = 1
    return genre_vector


def get_all_genres(conn):
    query = "SELECT DISTINCT artist_genres FROM artists"
    cursor = conn.cursor()
    cursor.execute(query)
    all_genres_set = set()
    for row in cursor.fetchall():
        genres = row[0].split(',')
        all_genres_set.update([genre.strip()
                              for genre in genres if genre.strip()])
    return sorted(all_genres_set)


def get_song_info(conn, song_id, features):
    features_sql = ', '.join(features)
    query = f"""
        SELECT s.song_id, s.song_name, s.artist_ids, {features_sql}
        FROM songs s
        WHERE s.song_id = ?
    """
    cursor = conn.cursor()
    cursor.execute(query, (song_id,))
    return cursor.fetchone()


def get_artist_info(conn, artist_id):
    query = f"""
        SELECT artist_name, artist_genres
        FROM artists
        WHERE artist_id = ?
    """
    cursor = conn.cursor()
    cursor.execute(query, (artist_id,))
    return cursor.fetchone()


def calculate_similarity(song_vector, input_vector):
    song_vector = song_vector.reshape(1, -1)
    input_vector = input_vector.reshape(1, -1)
    similarity = cosine_similarity(song_vector, input_vector)[0][0]
    return similarity


def normalize_song_name(song_name):
    return re.sub(r'\(.*?\)', '', song_name).strip().lower()


def count_song_in_playlists(conn, song_id):
    query = f"""
        SELECT COUNT(*)
        FROM playlists
        WHERE playlist_items LIKE ?
    """
    cursor = conn.cursor()
    cursor.execute(query, (f'%{song_id}%',))
    return cursor.fetchone()[0]


def get_similar_audio_features(conn, features, input_audio_features, inputted_ids, inputted_songs, mandatory_genres, all_genres):
    feature_conditions = []
    for i, feature in enumerate(features):
        feature_name = feature.split('.')[-1]
        bound_val = SEPARATE_BOUNDS.get(feature_name, REAL_BOUND_VAL)
        lower_bound = input_audio_features[i] - bound_val
        upper_bound = input_audio_features[i] + bound_val
        feature_conditions.append(f"{feature_name} BETWEEN {
                                  lower_bound} AND {upper_bound}")

    conditions_sql = ' AND '.join(feature_conditions)
    genre_conditions = ' OR '.join(
        [f"a.artist_genres LIKE '%{genre}%'" for genre in mandatory_genres])
    combined_conditions_sql = f"{conditions_sql} AND ({genre_conditions})"
    features_sql = ', '.join(features)

    query = f"""
        SELECT s.song_id, s.song_name, s.artist_ids, {features_sql}
        FROM songs s
        JOIN artists a ON s.artist_ids = a.artist_id
        WHERE {combined_conditions_sql}
    """
    cursor = conn.cursor()
    cursor.execute(query)
    songs = cursor.fetchall()

    input_vector = get_song_vector(
        (None, None, None, *input_audio_features), all_genres)
    filtered_songs = []

    for song in songs:
        song_id, song_name, artist_ids = song[:3]
        song_vector = get_song_vector(song, all_genres)
        similarity = calculate_similarity(song_vector, input_vector)
        filtered_songs.append((similarity, song))

    # Sort songs by similarity (highest first, i.e., closer to 1)
    filtered_songs.sort(key=lambda x: -x[0])
    return filtered_songs


def cbf_cf(ids):
    conn = sqlite3.connect(DB)
    features = ['s.' + feature for feature in CBF_FEATURES]
    songs_info = [get_song_info(conn, song_id, features) for song_id in ids]
    all_genres = get_all_genres(conn)

    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        f.write('INPUTTED IDS\n')
        input_audio_features_list = []
        inputted_ids_set = set(ids)

        for idx, song_info in enumerate(songs_info, start=1):
            if not song_info:
                continue

            song_id, song_name, artist_ids, *audio_features = song_info
            input_audio_features_list.append(audio_features)
            song_url = f"https://open.spotify.com/track/{song_id}"
            features_str = ', '.join(
                [f"{CBF_FEATURES[i]}: {audio_features[i]}" for i in range(len(audio_features))])

            artist_info = get_artist_info(conn, artist_ids.split(
                ',')[0]) if artist_ids else ('N/A', 'N/A')
            artist_name = artist_info[0] if artist_info[0] else 'N/A'
            genres = artist_info[1] if artist_info[1] else 'N/A'

            line = (f"{idx}. {song_url} {artist_name} - {song_name if song_name else 'N/A'} | "
                    f"Genres: {genres} | {features_str}\n")
            f.write(line)

        for input_audio_features, song_info in zip(input_audio_features_list, songs_info):
            artist_info = get_artist_info(conn, song_info[2].split(
                ',')[0]) if song_info[2] else ('N/A', 'N/A')
            artist_name = artist_info[0] if artist_info[0] else 'N/A'
            genres = artist_info[1] if artist_info[1] else 'N/A'

            header = f"https://open.spotify.com/track/{song_info[0]} {
                artist_name} - {song_info[1]} | Genres: {genres}"
            f.write(f"\nSONGS RECOMMENDATION: {header}\n")

            mandatory_genres = [genre.strip() for genre in genres.split(
                ',') if genre.strip() != 'N/A']
            if mandatory_genres:
                similar_songs_info = get_similar_audio_features(
                    conn, features, input_audio_features, inputted_ids_set, songs_info, mandatory_genres, all_genres)

                # Store songs with their count, similarity score, and audio features in a list
                songs_with_count_and_similarity = []
                for similarity, song in similar_songs_info:
                    song_id, song_name, artist_ids, *audio_features = song
                    song_url = f"https://open.spotify.com/track/{song_id}"
                    features_str = ', '.join(
                        [f"{CBF_FEATURES[i]}: {audio_features[i]}" for i in range(len(audio_features))])

                    artist_info = get_artist_info(conn, artist_ids.split(
                        ',')[0]) if artist_ids else ('N/A', 'N/A')
                    artist_name = artist_info[0] if artist_info[0] else 'N/A'
                    genres = artist_info[1] if artist_info[1] else 'N/A'

                    # Count the number of playlists containing the song
                    playlist_count = count_song_in_playlists(conn, song_id)

                    # Append the song info along with the similarity score, count, and audio features to the list
                    songs_with_count_and_similarity.append(
                        (song_url, artist_name, song_name, genres, features_str, playlist_count, similarity, audio_features))

                # Sort the songs by similarity score (closest first) and then by playlist count
                songs_with_count_and_similarity.sort(
                    key=lambda x: (x[6], -x[5]))

                # Write the sorted songs with similarity scores to the file
                for idx, (song_url, artist_name, song_name, genres, features_str, playlist_count, similarity, _) in enumerate(songs_with_count_and_similarity, start=1):
                    line = (f"{idx}. {song_url} {artist_name} - {song_name if song_name else 'N/A'} | "
                            f"Genres: {genres} | {features_str} | Count: {playlist_count} | Similarity: {similarity:.4f}\n")
                    f.write(line)

    conn.close()
    print('Result for', MODEL, 'stored at', OUTPUT_PATH)


if __name__ == "__main__":
    ids = ['2kJwzbxV2ppxnQoYw4GLBZ',
           '3Sbova9DAY3pc9GTAACT4b', '5O2P9iiztwhomNh8xkR9lJ']
    cbf_cf(ids)
