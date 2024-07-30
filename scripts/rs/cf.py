import sqlite3
import random
import configparser

# Read configuration
config = configparser.ConfigParser()
config.read('config.cfg')

db_playlist_path = config['db']['playlists_db']
db_songs_path = config['db']['songs_db']
output_path = config['output']['cf_output']
n_recommend = int(config['rs']['n_recommend'])


def get_playlist_containing_tracks(track_ids):
    query = f"""
    SELECT DISTINCT playlist_id
    FROM items
    WHERE playlist_items LIKE '%{"%' OR playlist_items LIKE '%".join(track_ids)}%'
    """
    with sqlite3.connect(db_playlist_path) as conn:
        return [row[0] for row in conn.execute(query).fetchall()]


def get_tracks_from_playlists(playlist_ids):
    query = f"""
    SELECT DISTINCT i.playlist_items
    FROM items i
    WHERE i.playlist_id IN ({','.join('?' * len(playlist_ids))})
    """
    with sqlite3.connect(db_playlist_path) as conn:
        return [row[0] for row in conn.execute(query, playlist_ids).fetchall()]


def get_track_details(track_ids):
    query = f"""
    SELECT t.track_id, t.track_name, a.artist_name
    FROM tracks t
    JOIN artists a ON t.artist_ids LIKE '%' || a.artist_id || '%'
    WHERE t.track_id IN ({','.join('?' * len(track_ids))})
    """
    with sqlite3.connect(db_songs_path) as conn:
        return conn.execute(query, track_ids).fetchall()


def recommend_songs(input_track_ids):
    # Step 1: Find playlists containing inputted track IDs
    matched_playlists = get_playlist_containing_tracks(input_track_ids)

    # Step 2: Recommend other songs in the matched playlists
    playlist_tracks = get_tracks_from_playlists(matched_playlists)
    all_tracks = set(
        track for sublist in playlist_tracks for track in sublist.split(','))

    # Remove input tracks from recommendations
    recommended_tracks = all_tracks.difference(set(input_track_ids))

    # Step 3: Apply penalty to prevent the same artist from showing up again
    track_details = get_track_details(recommended_tracks)
    artist_penalty = {detail[2]: 0 for detail in track_details}  # Artist names

    final_recommendations = []
    for detail in track_details:
        if artist_penalty[detail[2]] < 0.5:
            final_recommendations.append(detail)
            artist_penalty[detail[2]] += 0.5

    # Step 4: Sort songs randomly
    random.shuffle(final_recommendations)

    # Limit the number of recommendations
    final_recommendations = final_recommendations[:n_recommend]

    return final_recommendations, matched_playlists


def save_recommendations(input_track_ids, recommendations, matched_playlists):
    with open(output_path, 'w') as f:
        f.write("# Inputted IDs\n")
        for track_id in input_track_ids:
            f.write(f"{track_id}\n")

        f.write("\n# Categorizing IDs (Categorize by MATCHED PLAYLIST)\n")
        playlist_groups = {}
        for track_id in input_track_ids:
            playlist_groups[track_id] = []
            for playlist_id in matched_playlists:
                if track_id in playlist_id:
                    playlist_groups[track_id].append(playlist_id)

        for i, (group, playlists) in enumerate(playlist_groups.items(), 1):
            f.write(f"1. Group #{i} : {', '.join(group)}\n")
            for playlist_id in playlists:
                f.write(f"   a. {playlist_id}\n")

        for i, rec in enumerate(recommendations, 1):
            f.write(f"\n# Group #{i}\n")
            for detail in rec:
                f.write(f"{detail[2]} - {detail[1]} [{detail[0]}]\n")


if __name__ == "__main__":
    input_track_ids = [
        '6uunyBNvRyzQl5imkPYdEb',
        '5MAK1nd8R6PWnle1Q1WJvh',
        '1ZyQGXH9dZ4AecevHhKUxi',
        '2xXNLutYAOELYVObYb1C1S',
        '5eAKNw3ftVX16LYECfmEsw',
    ]

    recommendations, matched_playlists = recommend_songs(input_track_ids)
    save_recommendations(input_track_ids, recommendations, matched_playlists)
