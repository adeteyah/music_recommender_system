import os
import sqlite3
import configparser

config = configparser.ConfigParser()
config.read('config.cfg')

db_playlist = config['db']['playlists_db']
db_songs = config['db']['songs_db']

output_path = config['output']['cf_output']


def cf_result(ids):
    # Connect to the playlists database
    conn_playlist = sqlite3.connect(db_playlist)
    cursor_playlist = conn_playlist.cursor()

    # Connect to the songs database
    conn_songs = sqlite3.connect(db_songs)
    cursor_songs = conn_songs.cursor()

    # Retrieve track and artist information for inputted IDs
    input_ids_info = []
    for track_id in ids:
        cursor_songs.execute(
            "SELECT track_name, artist_ids FROM tracks WHERE track_id=?", (track_id,))
        track_row = cursor_songs.fetchone()
        if track_row:
            track_name, artist_ids = track_row
            if not track_name:
                track_name = "(Unknown)"
            artist_names = []
            for artist_id in artist_ids.split(', '):
                cursor_songs.execute(
                    "SELECT artist_name FROM artists WHERE artist_id=?", (artist_id,))
                artist_row = cursor_songs.fetchone()
                if artist_row:
                    artist_name = artist_row[0]
                    if not artist_name:
                        artist_name = "(Unknown)"
                    artist_names.append(artist_name)
            if not artist_names:
                artist_names.append("(Unknown)")
            input_ids_info.append({
                'track_id': track_id,
                'track_name': track_name,
                'artists': ', '.join(artist_names)
            })

    # Find all playlists that contain the given track IDs
    query = "SELECT playlist_id, playlist_items FROM items"
    cursor_playlist.execute(query)
    playlists = cursor_playlist.fetchall()

    track_counts = {}
    playlist_contributions = {}
    for playlist_id, playlist_items in playlists:
        items = playlist_items.split(', ')
        match_count = sum(1 for track_id in items if track_id in ids)
        if match_count > 0:
            playlist_contributions[playlist_id] = match_count
            for item in items:
                if item not in track_counts:
                    track_counts[item] = 0
                track_counts[item] += 1

    # Retrieve track and artist information for all tracks
    track_info = {}
    for track_id in track_counts.keys():
        cursor_songs.execute(
            "SELECT track_name, artist_ids FROM tracks WHERE track_id=?", (track_id,))
        track_row = cursor_songs.fetchone()
        if track_row:
            track_name, artist_ids = track_row
            if not track_name:
                track_name = "(Unknown)"
            artist_names = []
            for artist_id in artist_ids.split(', '):
                cursor_songs.execute(
                    "SELECT artist_name FROM artists WHERE artist_id=?", (artist_id,))
                artist_row = cursor_songs.fetchone()
                if artist_row:
                    artist_name = artist_row[0]
                    if not artist_name:
                        artist_name = "(Unknown)"
                    artist_names.append(artist_name)
            if not artist_names:
                artist_names.append("(Unknown)")
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

    # Sort playlists by contribution
    sorted_playlists = sorted(
        playlist_contributions.items(), key=lambda item: item[1], reverse=True)

    # Format the results
    results = "Inputted IDS\n"
    for idx, track in enumerate(input_ids_info, 1):
        track_url = f"https://open.spotify.com/track/{track['track_id']}"
        results += f"{idx}. {track['artists']
                             } - {track['track_name']} [{track_url}]\n"

    results += "\nPlaylist Contributed\n"
    rank = 1
    for playlist_id, count in sorted_playlists:
        playlist_url = f"https://open.spotify.com/playlist/{playlist_id}"
        results += f"{rank}. {count} Tracks | Playlist ID: {playlist_url}\n"
        rank += 1

    results += "\nSongs Recommendation\n"
    rank = 1
    for track_id, info in sorted_tracks:
        track_url = f"https://open.spotify.com/track/{track_id}"
        results += f"{rank}. {info['artists']} - {info['track_name']
                                                  } [{track_url}] | Rank: {info['count']}\n"
        rank += 1

    # Write the results to a text file
    with open(output_path, 'w') as f:
        f.write(results)

    return results


if __name__ == "__main__":
    ids = ['5xNUR50KxswPRAvx7S163g', '66y7x28jXOPrcmu3D5Zjh6',
           '05BNReYSRjMs0gL2Nq9DX6', '05eqt8RvGphc7EpuAR0e20']
    result = cf_result(ids)
    print(f'CF Recommendation is stored in {output_path}')
