import os
import sqlite3
import configparser

config = configparser.ConfigParser()
config.read('config.cfg')

db_playlist = config['db']['playlists_db']
db_songs = config['db']['songs_db']
output_path = config['output']['cf_output']

# Connect to the playlists database
conn_playlist = sqlite3.connect(db_playlist)
cur_playlist = conn_playlist.cursor()

# Connect to the songs database
conn_songs = sqlite3.connect(db_songs)
cur_songs = conn_songs.cursor()


def get_track_details(track_id):
    # Query the tracks database to get the track name and artist IDs
    query = "SELECT track_name, artist_ids FROM tracks WHERE track_id = ?"
    cur_songs.execute(query, (track_id,))
    result = cur_songs.fetchone()

    if not result:
        return {'artist_name': 'Artist Not In Database', 'track_name': 'Track Not In Database'}

    track_name, artist_ids = result

    # Handle the case where artist_ids might be None
    if track_name is None:
        track_name = "Unknown Track"

    if artist_ids is None:
        artist_ids = ""

    # Query the artists database to get the artist names
    artist_names = []
    for artist_id in artist_ids.split(','):
        artist_query = "SELECT artist_name FROM artists WHERE artist_id = ?"
        cur_songs.execute(artist_query, (artist_id.strip(),))
        artist_result = cur_songs.fetchone()
        if artist_result:
            artist_names.append(artist_result[0])
        else:
            artist_names.append('Unknown Artist')

    artist_name = ", ".join(artist_names)

    return {'artist_name': artist_name, 'track_name': track_name}


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


def cf_result(ids):
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

    # Write the results to a file
    with open(output_path, 'w', encoding='utf-8') as file:
        # Write the inputted IDs list
        file.write("Inputted IDs:\n")
        for idx, track_id in enumerate(ids, start=1):
            details = get_track_details(track_id)
            file.write(f"{idx}. {details['artist_name']} - {
                       details['track_name']} [https://open.spotify.com/track/{track_id}]\n")

        # Write the recommendation list
        file.write("\nRecommendation Result:\n")
        for row in rows_playlist:
            # Split playlist_items by comma
            playlist_items = row[-1].split(',')
            playlist_tracks.append(set(item.strip()
                                   for item in playlist_items))
            for item in playlist_items:
                item = item.strip()
                if item not in track_ids:  # Check if item is not in track_ids
                    if item not in track_details:
                        track_details[item] = get_track_details(item)
                    if item not in track_count:
                        track_count[item] = 0
                    track_count[item] += 1

        # Sort the tracks by count in descending order
        sorted_tracks = sorted(track_count.items(),
                               key=lambda x: x[1], reverse=True)

        # Limit the recommendations to 100
        limited_tracks = sorted_tracks[:int(config['rs']['n_recommend'])]

        for idx, (item, count) in enumerate(limited_tracks, start=1):
            details = track_details[item]
            file.write(f"{idx}. {details['artist_name']} - {details['track_name']
                                                            } [https://open.spotify.com/track/{item}] | Count: {count}\n")

        # Update contributed playlists based on the limited recommendations
        limited_track_ids = {item for item, count in limited_tracks}

        file.write("\nContributed Playlists:\n")
        playlist_contributions = {}
        for row in rows_playlist:
            playlist_id = row[0]
            creator_id = row[1]
            # Split playlist_items by comma
            playlist_items = row[-1].split(',')

            # Count the number of contributed tracks that are in the limited recommendations
            contribution_count = sum(
                1 for item in playlist_items if item.strip() in limited_track_ids)

            if contribution_count > 0:
                playlist_key = (playlist_id, creator_id)
                if playlist_key not in playlist_contributions:
                    playlist_contributions[playlist_key] = contribution_count
                else:
                    playlist_contributions[playlist_key] += contribution_count

        # Sort the playlist contributions by count in descending order
        sorted_contributions = sorted(
            playlist_contributions.items(), key=lambda x: x[1], reverse=True)

        for idx, ((playlist_id, creator_id), count) in enumerate(sorted_contributions, start=1):
            file.write(f"{idx}. {count} Tracks from [https://open.spotify.com/playlist/{
                       playlist_id}] by [https://open.spotify.com/user/{creator_id}]\n")

        # Calculate relationships between inputted IDs
        relationships = calculate_relationship(ids, playlist_tracks)
        file.write("\nTrack Relationships:\n")
        for idx, ((id1, id2), relationship) in enumerate(relationships.items(), start=1):
            details1 = get_track_details(id1)
            details2 = get_track_details(id2)
            file.write(f"{idx}. {details1['track_name']} [https://open.spotify.com/track/{id1}] & {
                       details2['track_name']} [https://open.spotify.com/track/{id2}] have a {relationship} relationship\n")

    print(f'CF Result written to: {output_path}')


if __name__ == "__main__":
    ids = ['01beCqR9wsVnwzkAJZyTqq', '5XeFesFbtLpXzIVDNQP22n', '0yc6Gst2xkRu0eMLeRMGCX', '0Eqg0CQ7bK3RQIMPw1A7pl',
           '4SqWKzw0CbA05TGszDgMlc', '5drW6PGRxkE6MxttzVLNk5', '6ilc4vQcwMPlvAHFfsTGng', '1SKPmfSYaPsETbRHaiA18G']
    cf_result(ids)
