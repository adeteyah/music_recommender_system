import sqlite3
import random
import configparser

# Load configuration
config = configparser.ConfigParser()
config.read('config.cfg')
db_playlist_path = config['db']['playlists_db']
db_songs_path = config['db']['songs_db']
output_path = config['output']['cf_output']
n_recommend = int(config['rs']['n_recommend'])

# Database connections
conn_playlist = sqlite3.connect(db_playlist_path)
conn_songs = sqlite3.connect(db_songs_path)
cursor_playlist = conn_playlist.cursor()
cursor_songs = conn_songs.cursor()


def get_artist_from_track_id(track_id):
    cursor_songs.execute(
        "SELECT artist_ids FROM tracks WHERE track_id = ?", (track_id,))
    result = cursor_songs.fetchone()
    if result:
        return result[0]
    return None


def cf_result(track_ids):
    matched_playlists = {}
    artist_penalty = {}

    # Find playlists containing the inputted track IDs
    for track_id in track_ids:
        cursor_playlist.execute(
            "SELECT playlist_id FROM items WHERE playlist_items LIKE ?", (f'%{track_id}%',))
        playlists = cursor_playlist.fetchall()
        for playlist in playlists:
            playlist_id = playlist[0]
            if playlist_id not in matched_playlists:
                matched_playlists[playlist_id] = []
            matched_playlists[playlist_id].append(track_id)

        # Apply artist penalty
        artist_id = get_artist_from_track_id(track_id)
        if artist_id:
            artist_penalty[artist_id] = 0.5

    # Recommend other songs in the matched playlists
    recommendations = {}
    for playlist_id in matched_playlists:
        cursor_playlist.execute(
            "SELECT playlist_items FROM items WHERE playlist_id = ?", (playlist_id,))
        playlist_items = cursor_playlist.fetchone()[0].split(',')
        for item in playlist_items:
            if item not in track_ids:
                artist_id = get_artist_from_track_id(item)
                if artist_id and artist_id in artist_penalty:
                    continue
                if playlist_id not in recommendations:
                    recommendations[playlist_id] = []
                recommendations[playlist_id].append(item)

    # Sort songs randomly and limit the number of recommendations
    final_recommendations = {}
    for playlist_id in recommendations:
        random.shuffle(recommendations[playlist_id])
        final_recommendations[playlist_id] = recommendations[playlist_id][:n_recommend]

    # Write results to .txt file
    with open(output_path, 'w') as file:
        file.write("# Inputted IDs\n")
        for track_id in track_ids:
            cursor_songs.execute(
                "SELECT track_name, artist_ids FROM tracks WHERE track_id = ?", (track_id,))
            track_name, artist_id = cursor_songs.fetchone()
            cursor_songs.execute(
                "SELECT artist_name FROM artists WHERE artist_id = ?", (artist_id,))
            artist_name = cursor_songs.fetchone()[0]
            file.write(f"{artist_name} - {track_name} [{track_id}]\n")

        file.write("\n# Categorizing IDs (Categorize by MATCHED PLAYLIST)\n")
        for idx, (playlist_id, matched_tracks) in enumerate(matched_playlists.items()):
            file.write(f"Group #{idx + 1} : {', '.join(matched_tracks)}\n")
            cursor_playlist.execute(
                "SELECT creator_id FROM playlists WHERE playlist_id = ?", (playlist_id,))
            creator_id = cursor_playlist.fetchone()[0]
            file.write(f"a. {playlist_id} by {creator_id}\n")

        for idx, (playlist_id, recommended_tracks) in enumerate(final_recommendations.items()):
            file.write(f"\n# Group #{
                       idx + 1} (Input: {', '.join(matched_playlists[playlist_id])})\n")
            for track_id in recommended_tracks:
                cursor_songs.execute(
                    "SELECT track_name, artist_ids FROM tracks WHERE track_id = ?", (track_id,))
                track_name, artist_id = cursor_songs.fetchone()
                cursor_songs.execute(
                    "SELECT artist_name FROM artists WHERE artist_id = ?", (artist_id,))
                artist_name = cursor_songs.fetchone()[0]
                file.write(f"{artist_name} - {track_name} [{track_id}]\n")


if __name__ == "__main__":
    ids = [
        '6uunyBNvRyzQl5imkPYdEb',
        '5MAK1nd8R6PWnle1Q1WJvh',
        '1ZyQGXH9dZ4AecevHhKUxi',
        '2xXNLutYAOELYVObYb1C1S',
        '5eAKNw3ftVX16LYECfmEsw',
    ]
    cf_result(ids)

# Close database connections
conn_playlist.close()
conn_songs.close()
