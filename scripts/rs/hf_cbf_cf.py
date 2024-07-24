import sqlite3
import configparser
import numpy as np
from scipy.spatial.distance import euclidean

config = configparser.ConfigParser()
config.read('config.cfg')

db_playlist = config['db']['playlists_db']
db_songs = config['db']['songs_db']
output_path = config['output']['cbf_output']

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
        t.valence,
        IFNULL(w.weight, 0) as weight
    FROM tracks t
    JOIN artists a ON t.artist_ids LIKE '%' || a.artist_id || '%'
    LEFT JOIN weights w ON t.track_id = w.track_id
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


def one_hot_encode_genres(genres, all_genres):
    encoding = np.zeros(len(all_genres))
    for genre in genres.split(','):
        if genre in all_genres:
            encoding[all_genres.index(genre)] = 1
    return encoding


def normalize_features(features):
    """Normalize features to have zero mean and unit variance."""
    return (features - np.mean(features)) / np.std(features)


def calculate_distances(input_tracks, all_tracks, all_genres):
    distances = []
    for all_track in all_tracks:
        all_track_id = all_track[0]
        if any(all_track_id == input_track[0] for input_track in input_tracks):
            continue

        # Normalize audio features
        all_features = normalize_features(
            np.array(all_track[4:19], dtype=float))
        all_genres_encoding = one_hot_encode_genres(all_track[3], all_genres)
        all_features = np.concatenate([all_features, all_genres_encoding])

        weight = all_track[-1]  # Fetch the weight
        for input_track in input_tracks:
            input_features = normalize_features(
                np.array(input_track[4:19], dtype=float))
            input_genres_encoding = one_hot_encode_genres(
                input_track[3], all_genres)
            input_features = np.concatenate(
                [input_features, input_genres_encoding])
            distance = euclidean(input_features, all_features)
            # Adjust distance by weight, higher weight reduces distance
            distance /= (weight + 1)
            artist_name, _ = fetch_artist_name_and_genres(all_track[2])
            distances.append(
                (all_track_id, all_track[1], artist_name, distance))
    distances.sort(key=lambda x: x[3])
    return distances


def cbf_result(ids):
    input_tracks = []
    for track_id in ids:
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
            t.valence,
            IFNULL(w.weight, 0) as weight
        FROM tracks t
        JOIN artists a ON t.artist_ids LIKE '%' || a.artist_id || '%'
        LEFT JOIN weights w ON t.track_id = w.track_id
        WHERE t.track_id=?
        """, (track_id,))
        track = cur_songs.fetchone()
        if track:
            input_tracks.append(track)

    if not input_tracks:
        print("No input tracks found in the database.")
        return

    all_tracks = fetch_all_tracks_features()
    # Extract all unique genres
    all_genres = set()
    for track in all_tracks:
        all_genres.update(track[3].split(','))

    all_genres = list(all_genres)
    distances = calculate_distances(input_tracks, all_tracks, all_genres)

    with open(output_path, 'w') as file:
        file.write("Inputted IDs:\n")
        for idx, input_track in enumerate(input_tracks, 1):
            artist_name, artist_genres = fetch_artist_name_and_genres(
                input_track[2])
            file.write(f"{idx}. {artist_name} - {input_track[1]} [https://open.spotify.com/track/{
                       input_track[0]}] - Genres: {artist_genres}\n")

        file.write("\nSongs Recommendation:\n")
        recommended_artists = set()
        for idx, (track_id, track_name, artist_name, distance) in enumerate(distances[:int(config['rs']['n_recommend'])], 1):
            if artist_name in recommended_artists:
                continue
            recommended_artists.add(artist_name)
            file.write(f"{idx}. {artist_name} - {track_name} [https://open.spotify.com/track/{
                       track_id}] - Distance: {distance:.2f}\n")

    print(f'CBF Result written to: {output_path}')


if __name__ == "__main__":
    # Example input with track_ids
    ids = [
        '2tznHmp70DxMyr2XhWLOW0',
        '2Z5wXgysowvzl0nKGNGU0t',
    ]
    cbf_result(ids)
