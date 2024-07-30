import sqlite3
import configparser
import random

# Read the config file
config = configparser.ConfigParser()
config.read('config.cfg')

# Database paths
db_playlist_path = config['db']['playlists_db']
db_songs_path = config['db']['songs_db']
output_path = config['output']['cf_output']
limit_results = int(config['rs']['n_recommend'])


def cf_result(input_ids):
    conn_playlist = sqlite3.connect(db_playlist_path)
    conn_songs = sqlite3.connect(db_songs_path)
    cursor_playlist = conn_playlist.cursor()
    cursor_songs = conn_songs.cursor()

    # Fetch track details for input IDs
    input_tracks = []
    for track_id in input_ids:
        cursor_songs.execute(
            "SELECT track_name, artist_ids FROM tracks WHERE track_id = ?", (track_id,))
        track_data = cursor_songs.fetchone()
        if track_data:
            artist_names = ', '.join(get_artist_names(
                cursor_songs, track_data[1].split(',')))
            input_tracks.append(
                f"{artist_names} - {track_data[0]} [{track_id}]")

    # Find playlists containing input IDs
    matched_playlists = {}
    for track_id in input_ids:
        cursor_playlist.execute(
            "SELECT playlist_id FROM items WHERE playlist_items LIKE ?", (f'%{track_id}%',))
        playlists = cursor_playlist.fetchall()
        for playlist in playlists:
            if playlist[0] not in matched_playlists:
                matched_playlists[playlist[0]] = []
            matched_playlists[playlist[0]].append(track_id)

    # Categorize IDs by matched playlist
    categorized_ids = {}
    for playlist_id, tracks in matched_playlists.items():
        cursor_playlist.execute(
            "SELECT creator_id FROM playlists WHERE playlist_id = ?", (playlist_id,))
        creator_id = cursor_playlist.fetchone()
        if creator_id:
            group_key = f"Group #{len(categorized_ids) + 1}"
            categorized_ids[group_key] = {
                "playlist_id": playlist_id,
                "creator_id": creator_id[0],
                "tracks": tracks
            }

    # Recommend songs for each group
    recommendations = {}
    for group, data in categorized_ids.items():
        cursor_playlist.execute(
            "SELECT playlist_items FROM items WHERE playlist_id = ?", (data['playlist_id'],))
        items = cursor_playlist.fetchone()
        if items:
            playlist_items = items[0].split(',')
            recommended_tracks = list(
                set(playlist_items) - set(data['tracks']))
            random.shuffle(recommended_tracks)
            recommendations[group] = recommended_tracks[:limit_results]

    # Output the results to a text file
    with open(output_path, 'w') as f:
        # Inputted IDs
        f.write("# Inputted IDs\n")
        for i, track in enumerate(input_tracks, 1):
            f.write(f"{i}. {track}\n")

        # Categorizing IDs
        f.write("\n# Categorizing IDs\n")
        for group, data in categorized_ids.items():
            track_indexes = ', '.join(
                [str(input_ids.index(t) + 1) for t in data['tracks']])
            f.write(f"{group} : {track_indexes}\n")
            f.write(f"- [{data['playlist_id']}] by {data['creator_id']}\n")

        # Songs Recommendations
        f.write("\n# Songs Recommendations\n")
        for group, tracks in recommendations.items():
            f.write(f"{group} (Input: {', '.join(
                [str(input_ids.index(t) + 1) for t in categorized_ids[group]['tracks']])})\n")
            for i, track_id in enumerate(tracks, 1):
                cursor_songs.execute(
                    "SELECT track_name, artist_ids FROM tracks WHERE track_id = ?", (track_id,))
                track_data = cursor_songs.fetchone()
                if track_data:
                    artist_names = ', '.join(get_artist_names(
                        cursor_songs, track_data[1].split(',')))
                    f.write(
                        f"{i}. {artist_names} - {track_data[0]} [{track_id}]\n")

    conn_playlist.close()
    conn_songs.close()


def get_artist_names(cursor, artist_ids):
    artist_names = []
    for artist_id in artist_ids:
        cursor.execute(
            "SELECT artist_name FROM artists WHERE artist_id = ?", (artist_id,))
        artist_data = cursor.fetchone()
        if artist_data:
            artist_names.append(artist_data[0])
    return artist_names


if __name__ == "__main__":
    ids = [
        '6uunyBNvRyzQl5imkPYdEb',
        '5MAK1nd8R6PWnle1Q1WJvh',
        '1ZyQGXH9dZ4AecevHhKUxi',
        '2xXNLutYAOELYVObYb1C1S',
        '5eAKNw3ftVX16LYECfmEsw',
    ]
    cf_result(ids)
