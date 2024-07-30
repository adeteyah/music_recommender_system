import sqlite3
import configparser
import random

# Load the configuration
config = configparser.ConfigParser()
config.read('config.cfg')

# Database paths
db_playlist_path = config['db']['playlists_db']
db_songs_path = config['db']['songs_db']

# Output path for recommendations
output_path = config['output']['cf_output']

# Number of recommendations to limit
n_recommend = int(config['rs']['n_recommend'])


def get_playlist_ids_for_tracks(track_ids):
    playlist_ids = set()
    with sqlite3.connect(db_playlist_path) as conn:
        cursor = conn.cursor()
        query = "SELECT playlist_id FROM items WHERE playlist_items LIKE ?"
        for track_id in track_ids:
            cursor.execute(query, ('%' + track_id + '%',))
            rows = cursor.fetchall()
            for row in rows:
                playlist_ids.add(row[0])
    return playlist_ids


def get_tracks_from_playlists(playlist_ids, input_track_ids):
    tracks = set()
    with sqlite3.connect(db_playlist_path) as conn:
        cursor = conn.cursor()
        query = "SELECT playlist_items FROM items WHERE playlist_id = ?"
        for playlist_id in playlist_ids:
            cursor.execute(query, (playlist_id,))
            rows = cursor.fetchall()
            for row in rows:
                playlist_items = row[0].split(',')
                for track_id in playlist_items:
                    if track_id not in input_track_ids:
                        tracks.add(track_id)
    return tracks


def get_track_details(track_ids):
    track_details = {}
    with sqlite3.connect(db_songs_path) as conn:
        cursor = conn.cursor()
        query = """
            SELECT tracks.track_id, tracks.track_name, artists.artist_name
            FROM tracks
            JOIN artists ON tracks.artist_ids LIKE '%' || artists.artist_id || '%'
            WHERE tracks.track_id = ?
        """
        for track_id in track_ids:
            cursor.execute(query, (track_id,))
            row = cursor.fetchone()
            if row:
                track_details[track_id] = f"{row[2]} - {row[1]} [{row[0]}]"
    return track_details


def recommend_tracks(input_track_ids):
    playlist_ids = get_playlist_ids_for_tracks(input_track_ids)
    recommended_track_ids = get_tracks_from_playlists(
        playlist_ids, input_track_ids)

    # Give penalty to artists to prevent them from showing up again
    artist_penalty = {}
    with sqlite3.connect(db_songs_path) as conn:
        cursor = conn.cursor()
        query = "SELECT artist_ids FROM tracks WHERE track_id = ?"
        for track_id in input_track_ids:
            cursor.execute(query, (track_id,))
            row = cursor.fetchone()
            if row:
                artist_ids = row[0].split(',')
                for artist_id in artist_ids:
                    artist_penalty[artist_id] = 0.5

    # Filter tracks based on artist penalty
    final_recommended_tracks = set()
    for track_id in recommended_track_ids:
        cursor.execute(query, (track_id,))
        row = cursor.fetchone()
        if row:
            artist_ids = row[0].split(',')
            if not any(artist_id in artist_penalty for artist_id in artist_ids):
                final_recommended_tracks.add(track_id)

    # Randomly sort the tracks
    final_recommended_tracks = list(final_recommended_tracks)
    random.shuffle(final_recommended_tracks)

    # Limit the number of recommendations
    final_recommended_tracks = final_recommended_tracks[:n_recommend]

    return get_track_details(final_recommended_tracks)


def cf_result(input_track_ids):
    # Fetch input track details
    input_tracks = get_track_details(input_track_ids)

    # Categorize by matched playlist
    playlist_ids = get_playlist_ids_for_tracks(input_track_ids)
    categorized_tracks = {}
    for playlist_id in playlist_ids:
        playlist_tracks = get_tracks_from_playlists(
            [playlist_id], input_track_ids)
        categorized_tracks[playlist_id] = playlist_tracks

    # Generate recommendations
    recommendations = recommend_tracks(input_track_ids)

    # Write to the output file
    with open(output_path, 'w') as f:
        f.write("# Inputted IDs\n")
        for track_id in input_track_ids:
            f.write(f"{input_tracks[track_id]}\n")

        f.write("\n# Categorizing IDs (Categorize by MATCHED PLAYLIST)\n")
        for playlist_id, tracks in categorized_tracks.items():
            f.write(f"Group #{playlist_id}\n")
            for track_id in tracks:
                f.write(f"a. {track_id}\n")

        f.write("\n# Recommendations\n")
        for track_id, track_detail in recommendations.items():
            f.write(f"{track_detail}\n")

    print('Result: ', output_path)


if __name__ == "__main__":
    ids = [
        '6uunyBNvRyzQl5imkPYdEb',
        '5MAK1nd8R6PWnle1Q1WJvh',
        '1ZyQGXH9dZ4AecevHhKUxi',
        '2xXNLutYAOELYVObYb1C1S',
        '5eAKNw3ftVX16LYECfmEsw',
    ]
    cf_result(ids)
