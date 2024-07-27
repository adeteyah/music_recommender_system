import sqlite3
import configparser
import math
import numpy as np

config = configparser.ConfigParser()
config.read('config.cfg')

db_playlist = config['db']['playlists_db']
db_songs = config['db']['songs_db']
output_path = config['output']['o_hfcfcbf_output']
n_recommend = int(config['rs']['n_recommend'])

# Connect to the databases
conn_playlist = sqlite3.connect(db_playlist)
cur_playlist = conn_playlist.cursor()
conn_songs = sqlite3.connect(db_songs)
cur_songs = conn_songs.cursor()


def fetch_inputted_ids_details(ids):
    details = []
    query = """
    SELECT t.track_id, t.track_name, a.artist_name, a.artist_genres, t.acousticness, t.danceability, t.energy,
           t.instrumentalness, t.key, t.liveness, t.loudness, t.mode, t.speechiness, t.tempo, t.time_signature,
           t.valence
    FROM tracks t
    JOIN artists a ON t.artist_ids LIKE '%' || a.artist_id || '%'
    WHERE t.track_id = ?
    """
    for track_id in ids:
        cur_songs.execute(query, (track_id,))
        track = cur_songs.fetchone()
        if track:
            details.append(track)
    return details


def fetch_playlists_with_tracks(ids):
    playlists = {}
    query = """
    SELECT i.playlist_id, i.playlist_items
    FROM items i
    WHERE i.playlist_items LIKE ? OR i.playlist_items LIKE ? OR i.playlist_items LIKE ?
    """
    like_patterns = [f"%{track_id}%" for track_id in ids]

    for pattern in like_patterns:
        cur_playlist.execute(query, (pattern, pattern, pattern))
        rows = cur_playlist.fetchall()
        for row in rows:
            playlist_id, items = row
            track_ids = set(item.strip() for item in items.split(','))
            matched_ids = track_ids.intersection(ids)
            if len(matched_ids) >= 2:
                if playlist_id not in playlists:
                    playlists[playlist_id] = set()
                playlists[playlist_id].update(matched_ids)

    return playlists


def fetch_all_tracks_in_playlists(playlists):
    all_tracks = set()
    for playlist_id in playlists.keys():
        cur_playlist.execute(
            "SELECT playlist_items FROM items WHERE playlist_id = ?", (playlist_id,))
        items = cur_playlist.fetchone()[0]
        track_ids = set(item.strip() for item in items.split(','))
        all_tracks.update(track_ids)
    return all_tracks


def fetch_track_details(track_ids):
    details = {}
    query = """
    SELECT t.track_id, t.track_name, a.artist_name, a.artist_genres
    FROM tracks t
    JOIN artists a ON t.artist_ids LIKE '%' || a.artist_id || '%'
    WHERE t.track_id = ?
    """
    for track_id in track_ids:
        cur_songs.execute(query, (track_id,))
        track = cur_songs.fetchone()
        if track:
            details[track_id] = track
    return details


def fetch_track_features(track_ids):
    features = {}
    query = """
    SELECT t.track_id, t.acousticness, t.danceability, t.energy, t.instrumentalness, t.key, t.liveness,
           t.loudness, t.mode, t.speechiness, t.tempo, t.time_signature, t.valence
    FROM tracks t
    WHERE t.track_id = ?
    """
    for track_id in track_ids:
        cur_songs.execute(query, (track_id,))
        feature = cur_songs.fetchone()
        if feature:
            features[track_id] = feature[1:]
    return features


def euclidean_distance(vec1, vec2):
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(vec1, vec2)))


def calculate_dynamic_weights(input_features, track_features):
    input_features_matrix = np.array(list(input_features.values()))
    track_features_matrix = np.array(list(track_features.values()))

    input_mean = np.mean(input_features_matrix, axis=0)
    track_mean = np.mean(track_features_matrix, axis=0)

    distance_norm_factor = np.linalg.norm(input_mean - track_mean)

    # Adjust this if needed based on input characteristics
    interaction_norm_factor = len(input_features)

    return distance_norm_factor, interaction_norm_factor


def normalize_features(features, norm_factor):
    if norm_factor == 0:
        # Return zeros if no variation in the features
        return np.zeros(features.shape)
    return (features - np.min(features)) / norm_factor


def o_hfcbfcf_result(ids):
    input_details = fetch_inputted_ids_details(ids)
    input_features = {detail[0]: np.array(
        detail[4:], dtype=float) for detail in input_details}

    playlists = fetch_playlists_with_tracks(ids)
    all_tracks = fetch_all_tracks_in_playlists(playlists)
    all_tracks.discard(None)  # Remove None values if any

    track_details = fetch_track_details(all_tracks)
    track_features = fetch_track_features(all_tracks)

    distance_norm_factor, interaction_norm_factor = calculate_dynamic_weights(
        input_features, track_features)

    recommendations = []

    for track_id, features in track_features.items():
        if track_id in input_features:
            continue

        min_distance = float('inf')
        for input_track_id, input_features_values in input_features.items():
            distance = euclidean_distance(features, input_features_values)
            if distance < min_distance:
                min_distance = distance

        normalized_distance = normalize_features(
            np.array([min_distance]), distance_norm_factor)[0]

        # Calculate user interaction weight
        count = sum(track_id in playlist for playlist in playlists.values())
        normalized_interaction = normalize_features(
            np.array([count]), interaction_norm_factor)[0]

        combined_score = normalized_distance + normalized_interaction

        recommendations.append(
            (track_id, track_details[track_id][1], track_details[track_id][2], count, min_distance, combined_score))

    # Sort recommendations based on the combined score
    recommendations.sort(key=lambda x: x[5], reverse=True)

    with open(output_path, 'w', encoding='utf-8') as file:
        file.write("Inputted IDs:\n")
        for idx, (track_id, track_name, artist_name, artist_genres, *_) in enumerate(input_details, 1):
            file.write(f"{idx}. {artist_name} - {track_name} [https://open.spotify.com/track/{
                       track_id}] - Genres: {artist_genres}\n")

        file.write("\nSongs Recommendation:\n")
        for idx, (track_id, track_name, artist_name, count, distance, combined_score) in enumerate(recommendations[:n_recommend], 1):
            file.write(f"{idx}. {artist_name} - {track_name} [https://open.spotify.com/track/{track_id}] | Count: {
                       count} | Distance: {distance:.2f} | Combined Score: {combined_score:.2f}\n")

    print(f'Recommendations written to: {output_path}')


if __name__ == "__main__":
    ids = [
        '6uunyBNvRyzQl5imkPYdEb',
        '5MAK1nd8R6PWnle1Q1WJvh',
        '1ZyQGXH9dZ4AecevHhKUxi',
        '2xXNLutYAOELYVObYb1C1S',
        '5eAKNw3ftVX16LYECfmEsw',
    ]
    o_hfcbfcf_result(ids)
