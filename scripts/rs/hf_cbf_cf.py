import sqlite3
import configparser
import numpy as np
from scipy.spatial.distance import euclidean

# Read configuration
config = configparser.ConfigParser()
config.read('config.cfg')

db_playlist = config['db']['playlists_db']
db_songs = config['db']['songs_db']
output_path = config['output']['hfcbfcf_output']
n_recommend = int(config['rs']['n_recommend'])
# Penalty weight for repeated artists
artist_penalty = float(config['rs'].get('artist_penalty', 5.0))
# Weight for distance in the final score
distance_weight = float(config['rs'].get('distance_weight', 0.55))
# Weight for interaction in the final score
interaction_weight = float(config['rs'].get('interaction_weight', 0.45))

# Connect to the databases
conn_playlist = sqlite3.connect(db_playlist)
cur_playlist = conn_playlist.cursor()
conn_songs = sqlite3.connect(db_songs)
cur_songs = conn_songs.cursor()


def fetch_all_tracks_features():
    query = """
    SELECT
        t.track_id,
        t.track_name,
        t.artist_ids,
        a.artist_genres,
        t.duration_ms,
        t.popularity,
        t.acousticness,
        t.danceability,
        t.energy,
        t.instrumentalness,
        t.key,
        t.liveness,
        t.loudness,
        t.mode,
        t.speechiness,
        t.tempo,
        t.time_signature,
        t.valence
    FROM tracks t
    JOIN artists a ON t.artist_ids LIKE '%' || a.artist_id || '%'
    """
    cur_songs.execute(query)
    tracks = cur_songs.fetchall()
    return tracks


def fetch_artist_name_and_genres(artist_ids):
    if not artist_ids:
        return "Unknown Artist", "Unknown Genres"
    artist_ids = artist_ids.split(',')
    query = "SELECT artist_name, artist_genres FROM artists WHERE artist_id=?"
    artist_names = []
    artist_genres = []
    for artist_id in artist_ids:
        cur_songs.execute(query, (artist_id,))
        artist_info = cur_songs.fetchone()
        if artist_info:
            artist_names.append(artist_info[0])
            artist_genres.extend(artist_info[1].split(','))
    return ", ".join(artist_names), ", ".join(set(artist_genres))


def fetch_user_interaction_weights():
    query = "SELECT track_id, weight FROM weights"
    cur_playlist.execute(query)
    weights = cur_playlist.fetchall()
    weight_dict = {track_id: weight for track_id, weight in weights}
    return weight_dict


def normalize_features(features):
    """Normalize features to have zero mean and unit variance."""
    return (features - np.mean(features)) / np.std(features)


def one_hot_encode_genres(genres, all_genres):
    encoding = np.zeros(len(all_genres))
    for genre in genres.split(','):
        if genre in all_genres:
            encoding[all_genres.index(genre)] = 1
    return encoding


def calculate_distances(input_tracks, all_tracks, all_genres, weight_dict):
    distances = []
    input_track_ids = {track[0] for track in input_tracks}
    input_genre_set = set()
    for track in input_tracks:
        input_genre_set.update(track[3].split(','))

    all_tracks_dict = {track[0]: track for track in all_tracks}
    artist_track_count = {}

    for all_track_id, all_track in all_tracks_dict.items():
        if all_track_id in input_track_ids:
            continue
        all_features = np.array(all_track[4:], dtype=float)
        all_genres_encoding = one_hot_encode_genres(all_track[3], all_genres)
        all_features = np.concatenate(
            [normalize_features(all_features), all_genres_encoding])

        for input_track in input_tracks:
            input_features = np.array(input_track[4:], dtype=float)
            input_genres_encoding = one_hot_encode_genres(
                input_track[3], all_genres)
            input_features = np.concatenate(
                [normalize_features(input_features), input_genres_encoding])
            distance = euclidean(input_features, all_features)

            # Genre-based filtering
            all_genre_set = set(all_track[3].split(','))
            if not input_genre_set.intersection(all_genre_set):
                continue

            artist_name, _ = fetch_artist_name_and_genres(all_track[2])
            artist_id = all_track[2]
            if artist_id not in artist_track_count:
                artist_track_count[artist_id] = 0
            artist_track_count[artist_id] += 1

            # Apply penalty if the artist is already in the recommendations
            if artist_track_count[artist_id] > 1:
                distance += artist_penalty

            weight = weight_dict.get(all_track_id, 0)
            distances.append(
                (all_track_id, all_track[1], artist_name, distance, weight))

    # Normalize distances and weights
    max_distance = max(distances, key=lambda x: x[3])[3] if distances else 1
    min_distance = min(distances, key=lambda x: x[3])[3] if distances else 0
    max_weight = max(distances, key=lambda x: x[4])[4] if distances else 1
    min_weight = min(distances, key=lambda x: x[4])[4] if distances else 0

    for i, (all_track_id, track_name, artist_name, distance, weight) in enumerate(distances):
        norm_distance = (distance - min_distance) / (max_distance -
                                                     min_distance) if max_distance != min_distance else 0
        norm_weight = (weight - min_weight) / (max_weight -
                                               min_weight) if max_weight != min_weight else 0
        combined_score = (distance_weight * (1 - norm_distance)
                          ) + (interaction_weight * norm_weight)
        distances[i] = (all_track_id, track_name, artist_name,
                        distance, weight, combined_score)

    distances.sort(key=lambda x: -x[5])  # Sort by combined score descending
    return distances


def hfcbfcf_result(ids):
    input_tracks = []
    unique_input_ids = set(ids)

    for track_id in unique_input_ids:
        cur_songs.execute("""
        SELECT
            t.track_id,
            t.track_name,
            t.artist_ids,
            a.artist_genres,
            t.duration_ms,
            t.popularity,
            t.acousticness,
            t.danceability,
            t.energy,
            t.instrumentalness,
            t.key,
            t.liveness,
            t.loudness,
            t.mode,
            t.speechiness,
            t.tempo,
            t.time_signature,
            t.valence
        FROM tracks t
        JOIN artists a ON t.artist_ids LIKE '%' || a.artist_id || '%'
        WHERE t.track_id=?
        """, (track_id,))
        track = cur_songs.fetchone()
        if track:
            input_tracks.append(track)

    if not input_tracks:
        print("No input tracks found in the database.")
        return

    all_tracks = fetch_all_tracks_features()
    all_tracks_dict = {track[0]: track for track in all_tracks}
    all_genres = set()
    for track in all_tracks:
        all_genres.update(track[3].split(','))

    all_genres = list(all_genres)
    weight_dict = fetch_user_interaction_weights()
    distances = calculate_distances(input_tracks, list(
        all_tracks_dict.values()), all_genres, weight_dict)

    recommended_track_ids = set()
    with open(output_path, 'w') as file:
        file.write("Inputted IDs:\n")
        for idx, input_track in enumerate(input_tracks, 1):
            artist_name, artist_genres = fetch_artist_name_and_genres(
                input_track[2])
            file.write(f"{idx}. {artist_name} - {input_track[1]} [https://open.spotify.com/track/{
                       input_track[0]}] - Genres: {artist_genres}\n")

        file.write("\nSongs Recommendation:\n")
        for idx, (track_id, track_name, artist_name, distance, weight, combined_score) in enumerate(distances):
            if track_id in recommended_track_ids:
                continue
            file.write(f"{idx+1}. {artist_name} - {track_name} [https://open.spotify.com/track/{
                       track_id}] - Distance: {distance:.2f} - User Interaction: {weight} - Score: {combined_score:.2f}\n")
            recommended_track_ids.add(track_id)
            if len(recommended_track_ids) >= n_recommend:
                break

    print(f'HFCBFCF Result written to: {output_path}')


if __name__ == "__main__":
    # Example input with track_ids
    ids = [
        '3vkCueOmm7xQDoJ17W1Pm3',
        '5vPO5ouEv8iedKWxzmSv7b',
        '3qhlB30KknSejmIvZZLjOD',
    ]
    hfcbfcf_result(ids)

# Close database connections
conn_playlist.close()
conn_songs.close()
