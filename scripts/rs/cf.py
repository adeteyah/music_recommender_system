import os
import sqlite3
import configparser

config = configparser.ConfigParser()
config.read('config.cfg')

db_playlist = config['db']['playlists_db']
db_songs = config['db']['songs_db']


def cf_result(ids):
    # Connect to the playlists database
    conn_playlist = sqlite3.connect(db_playlist)
    cursor_playlist = conn_playlist.cursor()

    # Connect to the songs database
    conn_songs = sqlite3.connect(db_songs)
    cursor_songs = conn_songs.cursor()

    # Find all playlists that contain the given track IDs
    query = "SELECT playlist_id, playlist_items FROM items"
    cursor_playlist.execute(query)
    playlists = cursor_playlist.fetchall()

    track_counts = {}
    for playlist_id, playlist_items in playlists:
        items = playlist_items.split(', ')
        for track_id in items:
            if track_id in ids:
                for item in items:
                    if item not in track_counts:
                        track_counts[item] = 0
                    track_counts[item] += 1

    # Retrieve track and artist information from the songs database
    track_info = {}
    for track_id in track_counts.keys():
        cursor_songs.execute(
            "SELECT track_name, artist_ids FROM tracks WHERE track_id=?", (track_id,))
        track_row = cursor_songs.fetchone()
        if track_row:
            track_name, artist_ids = track_row
            artist_names = []
            for artist_id in artist_ids.split(', '):
                cursor_songs.execute(
                    "SELECT artist_name FROM artists WHERE artist_id=?", (artist_id,))
                artist_row = cursor_songs.fetchone()
                if artist_row:
                    artist_names.append(artist_row[0])
            track_info[track_id] = {
                'track_name': track_name,
                'artists': ', '.join(artist_names),
                'count': track_counts[track_id]
            }

    conn_playlist.close()
    conn_songs.close()

    # Sort the tracks by count
    sorted_tracks = sorted(
        track_info.items(), key=lambda item: item[1]['count'], reverse=True)

    # Format the results
    results = "Contribution Rank:\n"
    rank = 1
    for track_id, info in sorted_tracks:
        results += f"{rank}. {info['artists']
                              } - {info['track_name']} | Rank: {info['count']}\n"
        rank += 1

    # Write the results to a text file
    with open('recommendations.txt', 'w') as f:
        f.write(results)

    return results


if __name__ == "__main__":
    ids = ['5xNUR50KxswPRAvx7S163g', '66y7x28jXOPrcmu3D5Zjh6']
    result = cf_result(ids)
    print(result)
