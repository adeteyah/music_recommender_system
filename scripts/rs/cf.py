import sqlite3
import configparser
import random

# Read config file
config = configparser.ConfigParser()
config.read('config.cfg')

db_playlist_path = config['db']['playlists_db']
db_songs_path = config['db']['songs_db']
output_path = config['output']['cf_output']
n_recommend = int(config['rs']['n_recommend'])

# Connect to databases
conn_playlist = sqlite3.connect(db_playlist_path)
conn_songs = sqlite3.connect(db_songs_path)


def get_track_details(track_ids):
    placeholders = ','.join('?' for _ in track_ids)
    query = f'''
    SELECT track_id, track_name, artist_ids FROM tracks
    WHERE track_id IN ({placeholders})
    '''
    cursor = conn_songs.execute(query, track_ids)
    tracks = cursor.fetchall()
    track_details = {}
    for track in tracks:
        track_id, track_name, artist_ids = track
        artist_ids_list = artist_ids.split(',')
        artist_names = get_artist_names(artist_ids_list)
        track_details[track_id] = {
            'track_name': track_name,
            'artist_names': ', '.join(artist_names)
        }
    return track_details


def get_artist_names(artist_ids):
    placeholders = ','.join('?' for _ in artist_ids)
    query = f'''
    SELECT artist_name FROM artists
    WHERE artist_id IN ({placeholders})
    '''
    cursor = conn_songs.execute(query, artist_ids)
    artists = cursor.fetchall()
    return [artist[0] for artist in artists]


def get_playlists_containing_tracks(track_ids):
    placeholders = ','.join('?' for _ in track_ids)
    query = f'''
    SELECT playlist_id FROM items
    WHERE playlist_items LIKE '%' || ? || '%'
    '''
    playlists = set()
    for track_id in track_ids:
        cursor = conn_playlist.execute(query, (track_id,))
        playlists.update([row[0] for row in cursor.fetchall()])
    return list(playlists)


def get_playlist_details(playlist_ids):
    placeholders = ','.join('?' for _ in playlist_ids)
    query = f'''
    SELECT playlist_id, creator_id FROM playlists
    WHERE playlist_id IN ({placeholders})
    '''
    cursor = conn_playlist.execute(query, playlist_ids)
    return cursor.fetchall()


def get_playlist_tracks(playlist_id):
    query = '''
    SELECT playlist_items FROM items
    WHERE playlist_id = ?
    '''
    cursor = conn_playlist.execute(query, (playlist_id,))
    result = cursor.fetchone()
    if result:
        return result[0].split(',')
    return []


def recommend_songs(input_track_ids):
    track_details = get_track_details(input_track_ids)
    playlists = get_playlists_containing_tracks(input_track_ids)
    playlist_details = get_playlist_details(playlists)

    # Categorize input IDs by matched playlists
    categorized_tracks = {}
    for track_id in input_track_ids:
        categorized_tracks[track_id] = []
        for playlist_id in playlists:
            playlist_tracks = get_playlist_tracks(playlist_id)
            if track_id in playlist_tracks:
                categorized_tracks[track_id].append(playlist_id)

    # Prepare recommendation lists
    recommendations = {}
    for group_id, tracks in enumerate(categorized_tracks.items()):
        group_tracks = []
        track_id, playlist_ids = tracks
        for playlist_id in playlist_ids:
            playlist_tracks = get_playlist_tracks(playlist_id)
            for track in playlist_tracks:
                if track not in input_track_ids:
                    group_tracks.append(track)
        random.shuffle(group_tracks)
        recommendations[group_id] = group_tracks[:n_recommend]

    return track_details, categorized_tracks, playlist_details, recommendations


def cf_result(input_track_ids):
    track_details, categorized_tracks, playlist_details, recommendations = recommend_songs(
        input_track_ids)

    with open(output_path, 'w') as f:
        f.write('# Inputted IDs\n')
        for i, track_id in enumerate(input_track_ids, 1):
            track_info = track_details[track_id]
            f.write(f'{i}. {track_info["artist_names"]
                            } - {track_info["track_name"]} [{track_id}]\n')

        f.write('\n# Categorizing IDs\n')
        for group_id, (track_id, playlist_ids) in enumerate(categorized_tracks.items(), 1):
            f.write(f'1. Group #{group_id} : {track_id}\n')
            for playlist_id in playlist_ids:
                playlist_info = next(
                    p for p in playlist_details if p[0] == playlist_id)
                f.write(f'a. [{playlist_id}] by {playlist_info[1]}\n')

        f.write('\n# Songs Recommendations\n')
        for group_id, rec_tracks in recommendations.items():
            f.write(f'- Group #{group_id} (Input: {track_id})\n')
            for i, track_id in enumerate(rec_tracks, 1):
                track_info = track_details.get(track_id)
                if track_info:
                    f.write(
                        f'{i}. {track_info["artist_names"]} - {track_info["track_name"]} [{track_id}]\n')


# Example usage
if __name__ == "__main__":
    ids = [
        '6uunyBNvRyzQl5imkPYdEb',
        '5MAK1nd8R6PWnle1Q1WJvh',
        '1ZyQGXH9dZ4AecevHhKUxi',
        '2xXNLutYAOELYVObYb1C1S',
        '5eAKNw3ftVX16LYECfmEsw',
    ]
    cf_result(ids)
