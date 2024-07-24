import os
import sqlite3
import configparser
import numpy as np

# Load configuration
config = configparser.ConfigParser()
config.read('config.cfg')

# Database paths
db_playlist = config['db']['playlists_db']
db_songs = config['db']['songs_db']
output_path = config['output']['hfcbfcf_output']

# Connect to the playlists and songs databases
conn_playlist = sqlite3.connect(db_playlist)
cur_playlist = conn_playlist.cursor()
conn_songs = sqlite3.connect(db_songs)
cur_songs = conn_songs.cursor()


def get_track_details(track_id):
    """Fetch track details and associated artists."""
    query = "SELECT track_name, artist_ids FROM tracks WHERE track_id = ?"
    cur_songs.execute(query, (track_id,))
    result = cur_songs.fetchone()

    if not result:
        return {'artist_name': 'Artist Not In Database', 'track_name': 'Track Not In Database'}

    track_name, artist_ids = result
    track_name = track_name if track_name else "Unknown Track"
    artist_ids = artist_ids if artist_ids else ""

    artist_names = []
    genres = set()
    for artist_id in artist_ids.split(','):
        artist_query = "SELECT artist_name, artist_genres FROM artists WHERE artist_id = ?"
        cur_songs.execute(artist_query, (artist_id.strip(),))
        artist_result = cur_songs.fetchone()
        if artist_result:
            artist_name, artist_genres = artist_result
            artist_names.append(artist_name)
            genres.update(artist_genres.split(','))
        else:
            artist_names.append('Unknown Artist')

    artist_name = ", ".join(artist_names)
    return {'artist_name': artist_name, 'track_name': track_name, 'genres': genres}


def get_audio_features(track_id):
    """Fetch audio features for a given track."""
    query = """
        SELECT duration_ms, popularity, acousticness, danceability, energy,
               instrumentalness, key, liveness, loudness, mode,
               speechiness, tempo, time_signature, valence
        FROM tracks WHERE track_id = ?
    """
    cur_songs.execute(query, (track_id,))
    return cur_songs.fetchone()


def calculate_distance(features1, features2):
    """Calculate Euclidean distance between two sets of features."""
    return np.linalg.norm(np.array(features1) - np.array(features2))


def calculate_genre_similarity(input_genres, playlist_genres):
    """Calculate similarity between input genres and playlist genres."""
    input_genres_set = set(input_genres)
    playlist_genres_set = set(playlist_genres.split(','))
    intersection = input_genres_set & playlist_genres_set
    union = input_genres_set | playlist_genres_set
    return len(intersection) / len(union) if union else 0


def fetch_all_playlists():
    """Fetch all playlists from the database."""
    cur_playlist.execute("""
        SELECT playlist_id, creator_id, min_duration_ms, max_duration_ms, min_popularity, max_popularity,
            min_acousticness, max_acousticness, min_danceability, max_danceability, min_energy, max_energy,
            min_instrumentalness, max_instrumentalness, min_key, max_key, min_liveness, max_liveness,
            min_loudness, max_loudness, min_mode, max_mode, min_speechiness, max_speechiness, min_tempo, max_tempo,
            min_time_signature, max_time_signature, min_valence, max_valence, most_genres
        FROM playlists
    """)
    return cur_playlist.fetchall()


def get_playlist_tracks(playlist_id):
    """Fetch tracks in a playlist."""
    cur_playlist.execute(
        "SELECT playlist_items FROM items WHERE playlist_id = ?", (playlist_id,))
    result = cur_playlist.fetchone()
    return result[0].split(',') if result else []


def get_track_weight(track_id):
    """Fetch the weight of a track."""
    cur_playlist.execute(
        "SELECT weight FROM weights WHERE track_id = ?", (track_id,))
    result = cur_playlist.fetchone()
    return result[0] if result else 1


def write_results_to_file(output_path, input_ids, invalid_tracks, top_playlists, track_counts, track_details, weights, track_sources):
    """Write the results to the output file."""
    with open(output_path, 'w', encoding='utf-8') as file:
        file.write("Inputted IDs:\n")
        for idx, track_id in enumerate(input_ids, start=1):
            details = get_track_details(track_id)
            if track_id in invalid_tracks:
                file.write(f"{idx}. {details['artist_name']} - {details['track_name']
                                                                } [https://open.spotify.com/track/{track_id}] (Unfetched Audio Features)\n")
            else:
                file.write(f"{idx}. {details['artist_name']} - {
                           details['track_name']} [https://open.spotify.com/track/{track_id}]\n")

        file.write("\nRecommendation Result:\n")
        for idx, (playlist_id, creator_id, score) in enumerate(top_playlists, start=1):
            file.write(f"{idx}. [https://open.spotify.com/user/{
                       creator_id}] - [https://open.spotify.com/playlist/{playlist_id}] | Combined Score: {score:.2f}\n")

        file.write("\nSongs Recommendations:\n")
        sorted_tracks = sorted(track_counts.items(
        ), key=lambda x: weights.get(x[0], 1), reverse=True)
        for idx, (track_id, count) in enumerate(sorted_tracks, start=1):
            # Ensure inputted track IDs are not shown in recommendations and limit to 24 items
            if track_id not in input_ids and idx <= int(config['rs']['n_recommend']):
                details = track_details.get(
                    track_id, {'artist_name': 'Unknown Artist', 'track_name': 'Unknown Track'})
                from_info = ", ".join(
                    f"From: {playlist_id}" for playlist_id in track_sources.get(track_id, []))
                file.write(f"{idx}. {details['artist_name']} - {details['track_name']} [https://open.spotify.com/track/{
                           track_id}] | Count: {count}, Weight: {weights.get(track_id, 1)} | {from_info}\n")


def hfcbfcf_result(ids):
    try:
        input_features = {}
        input_genres = set()
        invalid_tracks = []

        for track_id in ids:
            details = get_track_details(track_id)
            audio_features = get_audio_features(track_id)

            if details['track_name'] == 'Track Not In Database' or not audio_features or any(f is None for f in audio_features):
                invalid_tracks.append(track_id)
            else:
                input_features[track_id] = audio_features
                input_genres.update(details['genres'])

        all_playlists = fetch_all_playlists()

        playlist_distances = []
        for playlist in all_playlists:
            playlist_id, creator_id = playlist[0], playlist[1]
            min_features = playlist[2:16]
            max_features = playlist[16:30]
            playlist_genres = playlist[30]

            if input_features:
                min_distance = np.mean([calculate_distance(
                    input_features[id], min_features) for id in ids if id in input_features])
                max_distance = np.mean([calculate_distance(
                    input_features[id], max_features) for id in ids if id in input_features])
                avg_distance = (min_distance + max_distance) / 2
                genre_similarity = calculate_genre_similarity(
                    input_genres, playlist_genres)
                combined_score = avg_distance * (1 - genre_similarity)
                playlist_distances.append(
                    (playlist_id, creator_id, combined_score))

        sorted_playlists = sorted(playlist_distances, key=lambda x: x[2])
        top_playlists = sorted_playlists[:5]

        # Gather tracks from the top playlists
        track_counts = {}
        track_sources = {}
        for playlist_id in [p[0] for p in top_playlists]:
            track_ids = get_playlist_tracks(playlist_id)
            for track_id in track_ids:
                track_id = track_id.strip()
                if track_id not in track_sources:
                    track_sources[track_id] = []
                track_sources[track_id].append(playlist_id)
                track_counts[track_id] = track_counts.get(track_id, 0) + 1

        # Fetch details for these tracks and their weights
        track_details = {}
        weights = {}
        for track_id in track_counts.keys():
            details = get_track_details(track_id)
            track_details[track_id] = {
                'artist_name': details['artist_name'], 'track_name': details['track_name']}
            weights[track_id] = get_track_weight(track_id)

        write_results_to_file(output_path, ids, invalid_tracks, top_playlists,
                              track_counts, track_details, weights, track_sources)
        print(f'Result written to: {output_path}')
    except Exception as e:
        print(f"Error details: {e}")


if __name__ == "__main__":
    ids = ['5E30LdtzQTGqRvNd7l6kG5']  # Example input with track_ids
    hfcbfcf_result(ids)
