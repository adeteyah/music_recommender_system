import sqlite3
import configparser
import random
import math

config = configparser.ConfigParser()
config.read('config.cfg')

db_playlist = config['db']['playlists_db']
db_songs = config['db']['songs_db']
output_path = config['output']['hfcfcbf_output']

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


def hfcfcbf_result(ids):
    # Get details for inputted IDs
    input_details = fetch_inputted_ids_details(ids)
    input_features = {detail[0]: detail[4:] for detail in input_details}

    # Get matched playlists
    playlists = fetch_playlists_with_tracks(ids)

    # Collect all tracks from matched playlists, excluding inputted IDs
    all_tracks = fetch_all_tracks_in_playlists(playlists)
    all_tracks.discard(None)  # Remove None values if any

    # Fetch details for all tracks
    track_details = fetch_track_details(all_tracks)
    track_features = fetch_track_features(all_tracks)

    # Calculate distances and prepare recommendations
    track_counts = {}
    track_playlists = {}
    track_distances = {}

    for track_id, features in track_features.items():
        if track_id in input_features:
            continue

        min_distance = float('inf')
        for input_track_id, input_features_values in input_features.items():
            distance = euclidean_distance(features, input_features_values)
            if distance < min_distance:
                min_distance = distance

        track_distances[track_id] = min_distance

    for playlist_id, matched_ids in playlists.items():
        cur_playlist.execute(
            "SELECT playlist_items FROM items WHERE playlist_id = ?", (playlist_id,))
        items = cur_playlist.fetchone()[0]
        track_ids = set(item.strip() for item in items.split(','))

        for track_id in track_ids - set(ids):
            if track_id in track_counts:
                track_counts[track_id] += 1
            else:
                track_counts[track_id] = 1

            if track_id in track_playlists:
                track_playlists[track_id].add(playlist_id)
            else:
                track_playlists[track_id] = {playlist_id}

    # Fetch details for recommended tracks
    track_details = fetch_track_details(track_counts.keys())

    # Identify eliminated and used inputted IDs
    matched_track_ids = set(
        track_id for playlist_tracks in playlists.values() for track_id in playlist_tracks)
    eliminated_input_ids = [
        track_id for track_id in ids if track_id not in matched_track_ids]
    used_input_ids = [
        track_id for track_id in ids if track_id in matched_track_ids]
    eliminated_input_details = fetch_inputted_ids_details(eliminated_input_ids)
    used_input_details = fetch_inputted_ids_details(used_input_ids)

    # Prepare the recommendations for sorting
    recommendations = []
    for track_id, count in track_counts.items():
        distance = track_distances.get(track_id, float('inf'))
        playlists_str = ', '.join(
            f"https://open.spotify.com/playlist/{playlist_id}" for playlist_id in track_playlists[track_id])
        track_name, artist_name, artist_genres = track_details[track_id][1:4]
        recommendations.append(
            (track_id, track_name, artist_name, count, distance, playlists_str))

    # Define the sorting key function
    def sort_key(rec):
        track_id, track_name, artist_name, count, distance, playlists_str = rec
        # Smallest distance is the primary sorting criterion
        primary = distance
        # Count is the secondary sorting criterion
        secondary = -count
        # Playlist count as tertiary sorting criterion if count > 1
        tertiary = -len(track_playlists[track_id]) if count > 1 else 0
        return primary, secondary, tertiary, random.random()

    # Sort recommendations with the defined sorting key
    recommendations.sort(key=sort_key)

    with open(output_path, 'w', encoding='utf-8') as file:  # Specify UTF-8 encoding
        file.write("Inputted IDs:\n")
        for idx, (track_id, track_name, artist_name, artist_genres, *_) in enumerate(input_details, 1):
            file.write(f"{idx}. {artist_name} - {track_name} [https://open.spotify.com/track/{
                       track_id}] - Genres: {artist_genres}\n")

        file.write("\nEliminated Inputs:\n")
        for idx, (track_id, track_name, artist_name, artist_genres, *_) in enumerate(eliminated_input_details, 1):
            file.write(f"{idx}. {artist_name} - {track_name} [https://open.spotify.com/track/{
                       track_id}] - Genres: {artist_genres}\n")

        file.write("\nUsed Inputs:\n")
        for idx, (track_id, track_name, artist_name, artist_genres, *_) in enumerate(used_input_details, 1):
            file.write(f"{idx}. {artist_name} - {track_name} [https://open.spotify.com/track/{
                       track_id}] - Genres: {artist_genres}\n")

        file.write("\nMatched Playlists:\n")
        for idx, (playlist_id, matched_ids) in enumerate(playlists.items(), 1):
            creator_id = cur_playlist.execute(
                "SELECT creator_id FROM playlists WHERE playlist_id = ?", (playlist_id,)).fetchone()[0]
            matched_ids_str = ", ".join(matched_ids)
            file.write(f"{idx}. https://open.spotify.com/user/{creator_id} - https://open.spotify.com/playlist/{
                       playlist_id} [Inputted IDs: {matched_ids_str}]\n")

        file.write("\nSongs Recommendation:\n")
        for idx, (track_id, track_name, artist_name, count, distance, playlists_str) in enumerate(recommendations, 1):
            file.write(f"{idx}. {artist_name} - {track_name} [https://open.spotify.com/track/{
                       track_id}] | Count: {count} | Distance: {distance:.2f} - {playlists_str}\n")

    print(f'CF Result written to: {output_path}')


if __name__ == "__main__":
    ids = [
        '3vkCueOmm7xQDoJ17W1Pm3',
        '5vPO5ouEv8iedKWxzmSv7b',
        '3qhlB30KknSejmIvZZLjOD',
    ]
    hfcfcbf_result(ids)
