import sqlite3
import configparser
import random

# Load the configuration
config = configparser.ConfigParser()
config.read('config.cfg')

db_playlist_path = config['db']['playlists_db']
db_songs_path = config['db']['songs_db']
output_path = config['output']['cf_output']
n_recommend = int(config['rs']['n_recommend'])

# Connect to the databases
conn_playlist = sqlite3.connect(db_playlist_path)
conn_songs = sqlite3.connect(db_songs_path)


def cf_result(ids):
    matched_playlists = find_playlists_containing_ids(ids)
    categorized_ids = categorize_ids_by_playlist(matched_playlists, ids)
    results = recommend_songs(categorized_ids)
    write_results_to_file(results, ids)


def find_playlists_containing_ids(ids):
    matched_playlists = {}
    with conn_playlist:
        cursor = conn_playlist.cursor()
        for track_id in ids:
            cursor.execute(
                "SELECT playlist_id FROM items WHERE playlist_items LIKE ?", (f"%{track_id}%",))
            playlists = cursor.fetchall()
            for playlist in playlists:
                playlist_id = playlist[0]
                if playlist_id not in matched_playlists:
                    matched_playlists[playlist_id] = []
                matched_playlists[playlist_id].append(track_id)
    return matched_playlists


def categorize_ids_by_playlist(matched_playlists, ids):
    categorized_ids = {}
    for playlist_id, track_ids in matched_playlists.items():
        group_key = tuple(track_ids)
        if group_key not in categorized_ids:
            categorized_ids[group_key] = []
        categorized_ids[group_key].append(playlist_id)
    return categorized_ids


def recommend_songs(categorized_ids):
    results = []
    for group_key, playlist_ids in categorized_ids.items():
        group_tracks = []
        with conn_playlist:
            cursor = conn_playlist.cursor()
            for playlist_id in playlist_ids:
                cursor.execute(
                    "SELECT playlist_items FROM items WHERE playlist_id = ?", (playlist_id,))
                playlist_items = cursor.fetchone()[0].split(',')
                group_tracks.extend(playlist_items)

        # Filter out input tracks and penalize repeated artists
        group_tracks = set(group_tracks) - set(group_key)
        track_scores = get_track_scores(group_tracks)
        sorted_tracks = sorted(track_scores.items(),
                               key=lambda x: x[1], reverse=True)
        shuffled_tracks = sorted_tracks[:n_recommend]
        random.shuffle(shuffled_tracks)

        results.append((group_key, shuffled_tracks))
    return results


def get_track_scores(tracks):
    track_scores = {}
    artist_penalties = {}
    with conn_songs:
        cursor = conn_songs.cursor()
        for track_id in tracks:
            cursor.execute(
                "SELECT artist_ids FROM tracks WHERE track_id = ?", (track_id,))
            artist_ids = cursor.fetchone()[0].split(',')
            penalty = sum(artist_penalties.get(artist_id, 0)
                          for artist_id in artist_ids)
            track_scores[track_id] = 1 / (1 + penalty)
            for artist_id in artist_ids:
                artist_penalties[artist_id] = artist_penalties.get(
                    artist_id, 0) + 0.5
    return track_scores


def write_results_to_file(results, input_ids):
    with open(output_path, 'w') as f:
        f.write("# Inputted IDs\n")
        for track_id in input_ids:
            track_info = get_track_info(track_id)
            f.write(f"{track_info}\n")

        f.write("\n# Categorizing IDs (Categorize by MATCHED PLAYLIST)\n")
        for group_key, playlist_ids in results:
            group_tracks_info = [get_track_info(
                track_id) for track_id in group_key]
            f.write(f"1. Group: {', '.join(group_tracks_info)}\n")
            for playlist_id in playlist_ids:
                playlist_info = get_playlist_info(playlist_id)
                f.write(f"a. {playlist_info}\n")

        for group_key, recommended_tracks in results:
            f.write(f"\n# Group (Input: {', '.join(group_key)})\n")
            for track_id, _ in recommended_tracks:
                track_info = get_track_info(track_id)
                f.write(f"{track_info}\n")


def get_track_info(track_id):
    with conn_songs:
        cursor = conn_songs.cursor()
        cursor.execute(
            "SELECT track_name, artist_ids FROM tracks WHERE track_id = ?", (track_id,))
        track_name, artist_ids = cursor.fetchone()
        artist_names = []
        for artist_id in artist_ids.split(','):
            cursor.execute(
                "SELECT artist_name FROM artists WHERE artist_id = ?", (artist_id,))
            artist_name = cursor.fetchone()[0]
            artist_names.append(artist_name)
        return f"{', '.join(artist_names)} - {track_name} [{track_id}]"


def get_playlist_info(playlist_id):
    with conn_playlist:
        cursor = conn_playlist.cursor()
        cursor.execute(
            "SELECT creator_id FROM playlists WHERE playlist_id = ?", (playlist_id,))
        creator_id = cursor.fetchone()[0]
        return f"[{playlist_id}] by {creator_id}"


if __name__ == "__main__":
    ids = [
        '6uunyBNvRyzQl5imkPYdEb',
        '5MAK1nd8R6PWnle1Q1WJvh',
        '1ZyQGXH9dZ4AecevHhKUxi',
        '2xXNLutYAOELYVObYb1C1S',
        '5eAKNw3ftVX16LYECfmEsw',
    ]
    cf_result(ids)
