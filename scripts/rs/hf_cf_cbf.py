import os
import sqlite3
import configparser
from math import sqrt

config = configparser.ConfigParser()
config.read('config.cfg')

db_playlist = config['db']['playlists_db']
db_songs = config['db']['songs_db']
output_path = config['output']['hfcfcbf_output']

# Connect to the playlists database
conn_playlist = sqlite3.connect(db_playlist)
cur_playlist = conn_playlist.cursor()

# Connect to the songs database
conn_songs = sqlite3.connect(db_songs)
cur_songs = conn_songs.cursor()


def get_track_details(track_id):
    query = """
    SELECT track_name, artist_ids, acousticness, danceability, energy, instrumentalness, liveness, loudness, speechiness, tempo, valence
    FROM tracks WHERE track_id = ?
    """
    cur_songs.execute(query, (track_id,))
    result = cur_songs.fetchone()

    if not result:
        return {
            'artist_name': 'Artist Not In Database',
            'track_name': 'Track Not In Database',
            'acousticness': 0.0, 'danceability': 0.0, 'energy': 0.0,
            'instrumentalness': 0.0, 'liveness': 0.0, 'loudness': 0.0,
            'speechiness': 0.0, 'tempo': 0.0, 'valence': 0.0
        }

    (track_name, artist_ids, acousticness, danceability, energy,
     instrumentalness, liveness, loudness, speechiness, tempo, valence) = result

    track_name = track_name if track_name is not None else "Unknown Track"
    artist_ids = artist_ids if artist_ids is not None else ""

    # Query the artists database to get the artist names and genres
    artist_names = []
    artist_genres = set()
    for artist_id in artist_ids.split(','):
        artist_query = "SELECT artist_name, artist_genres FROM artists WHERE artist_id = ?"
        cur_songs.execute(artist_query, (artist_id.strip(),))
        artist_result = cur_songs.fetchone()
        if artist_result:
            artist_name, genres = artist_result
            artist_names.append(artist_name)
            if genres:
                artist_genres.update(genres.split(','))
        else:
            artist_names.append('Unknown Artist')

    artist_name = ", ".join(artist_names)
    genres = ", ".join(artist_genres)

    track_details = {
        'artist_name': artist_name,
        'track_name': track_name,
        'acousticness': acousticness if acousticness is not None else 0.0,
        'danceability': danceability if danceability is not None else 0.0,
        'energy': energy if energy is not None else 0.0,
        'instrumentalness': instrumentalness if instrumentalness is not None else 0.0,
        'liveness': liveness if liveness is not None else 0.0,
        'loudness': loudness if loudness is not None else 0.0,
        'speechiness': speechiness if speechiness is not None else 0.0,
        'tempo': tempo if tempo is not None else 0.0,
        'valence': valence if valence is not None else 0.0,
        'genres': genres
    }

    return track_details


def calculate_audio_similarity(track1, track2):
    features1 = [track1.get('acousticness', 0.0), track1.get('danceability', 0.0), track1.get('energy', 0.0), track1.get('instrumentalness', 0.0),
                 track1.get('liveness', 0.0), track1.get('loudness', 0.0), track1.get('speechiness', 0.0), track1.get('tempo', 0.0), track1.get('valence', 0.0)]
    features2 = [track2.get('acousticness', 0.0), track2.get('danceability', 0.0), track2.get('energy', 0.0), track2.get('instrumentalness', 0.0),
                 track2.get('liveness', 0.0), track2.get('loudness', 0.0), track2.get('speechiness', 0.0), track2.get('tempo', 0.0), track2.get('valence', 0.0)]

    distance = sqrt(sum((f1 - f2) ** 2 for f1,
                    f2 in zip(features1, features2)))

    return distance


def calculate_relationship(ids, playlist_tracks):
    relationships = {}
    for i in range(len(ids)):
        for j in range(i + 1, len(ids)):
            id1, id2 = ids[i], ids[j]
            common_playlists = 0
            for tracks in playlist_tracks:
                if id1 in tracks and id2 in tracks:
                    common_playlists += 1
            if common_playlists >= 2:
                relationship = 'High'
            elif common_playlists == 1:
                relationship = 'Medium'
            else:
                relationship = 'Low'
            relationships[(id1, id2)] = relationship
    return relationships


def hfcfcbf_result(ids):
    join_playlist_query = """
        SELECT p.playlist_id, p.creator_id, p.original_track_count,
            i.playlist_items
        FROM playlists p
        JOIN items i ON p.playlist_id = i.playlist_id
        WHERE """

    join_playlist_query += " OR ".join(["i.playlist_items LIKE ?"] * len(ids))
    cur_playlist.execute(join_playlist_query, ['%' + id + '%' for id in ids])

    rows_playlist = cur_playlist.fetchall()

    # Extract track_ids from ids list for comparison
    track_ids = set(ids)

    # Store track details in a dictionary for easy access
    track_details = {}
    track_count = {}
    playlist_tracks = []

    input_track_details = [get_track_details(track_id) for track_id in ids]

    with open(output_path, 'w', encoding='utf-8') as file:
        file.write("Inputted IDs:\n")
        for idx, track_id in enumerate(ids, start=1):
            details = get_track_details(track_id)
            file.write(f"{idx}. {details['artist_name']} - {
                       details['track_name']} [https://open.spotify.com/track/{track_id}]\n")

        file.write("\nRecommendation Result:\n")
        for row in rows_playlist:
            playlist_items = row[-1].split(',')
            playlist_tracks.append(set(item.strip()
                                   for item in playlist_items))
            for item in playlist_items:
                item = item.strip()
                if item not in track_ids:
                    if item not in track_details:
                        track_details[item] = get_track_details(item)
                    if item not in track_count:
                        track_count[item] = 0
                    track_count[item] += 1

        # Calculate similarity and store it with count
        track_similarity = {}
        for item, count in track_count.items():
            details = track_details[item]
            similarities = [
                calculate_audio_similarity(details, input_detail)
                for input_detail in input_track_details
            ]
            average_similarity = sum(similarities) / len(similarities)
            track_similarity[item] = (count, average_similarity)

        # Sort tracks by similarity and count
        sorted_tracks = sorted(track_similarity.items(),
                               key=lambda x: (x[1][1], x[1][0]), reverse=False)

        # Limit the recommendations to 100
        limited_tracks = sorted_tracks[:int(config['rs']['n_recommend'])]

        for idx, (item, (count, similarity)) in enumerate(limited_tracks, start=1):
            details = track_details[item]
            file.write(f"{idx}. {details['artist_name']} - {details['track_name']} [https://open.spotify.com/track/{
                       item}] | Count: {count} | Similarity: {similarity:.2f}\n")

        limited_track_ids = {item for item,
                             (count, similarity) in limited_tracks}

        file.write("\nContributed Playlists:\n")
        playlist_contributions = {}
        for row in rows_playlist:
            playlist_id = row[0]
            creator_id = row[1]
            playlist_items = row[-1].split(',')

            contribution_count = sum(
                1 for item in playlist_items if item.strip() in limited_track_ids)

            if contribution_count > 0:
                playlist_key = (playlist_id, creator_id)
                if playlist_key not in playlist_contributions:
                    playlist_contributions[playlist_key] = contribution_count
                else:
                    playlist_contributions[playlist_key] += contribution_count

        sorted_contributions = sorted(
            playlist_contributions.items(), key=lambda x: x[1], reverse=True)

        for idx, ((playlist_id, creator_id), count) in enumerate(sorted_contributions, start=1):
            file.write(f"{idx}. {count} Tracks from [https://open.spotify.com/playlist/{
                       playlist_id}] by [https://open.spotify.com/user/{creator_id}]\n")

        relationships = calculate_relationship(ids, playlist_tracks)
        file.write("\nTrack Relationships:\n")
        for idx, ((id1, id2), relationship) in enumerate(relationships.items(), start=1):
            details1 = get_track_details(id1)
            details2 = get_track_details(id2)
            file.write(f"{idx}. {details1['track_name']} [https://open.spotify.com/track/{id1}] & {
                       details2['track_name']} [https://open.spotify.com/track/{id2}] have a {relationship} relationship\n")

    print(f'HFCFCBF Result written to: {output_path}')


if __name__ == "__main__":
    ids = [
        '4GfK1qOF3uBWidbPlTCQRL',
        '1gH1h30wkQdd9zhY3j7a8T',
    ]
    hfcfcbf_result(ids)
