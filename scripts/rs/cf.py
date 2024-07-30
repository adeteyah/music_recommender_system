import sqlite3
import configparser
from collections import defaultdict


def cf_result(input_ids):
    # Load config
    config = configparser.ConfigParser()
    config.read('config.cfg')

    db_playlist_path = config['db']['playlists_db']
    db_songs_path = config['db']['songs_db']
    output_path = config['output']['cf_output']
    n_recommend = int(config['rs']['n_recommend'])

    # Connect to the databases
    conn_playlist = sqlite3.connect(db_playlist_path)
    conn_songs = sqlite3.connect(db_songs_path)

    cur_playlist = conn_playlist.cursor()
    cur_songs = conn_songs.cursor()

    # Step 1: Fetch inputted track details
    track_details = {}
    for track_id in input_ids:
        cur_songs.execute("""
            SELECT t.track_id, t.track_name, a.artist_name
            FROM tracks t
            JOIN artists a ON a.artist_id = t.artist_ids
            WHERE t.track_id = ?
        """, (track_id,))
        result = cur_songs.fetchone()
        if result:
            track_details[track_id] = result

    # Step 2: Categorize input IDs by matched playlists
    playlist_groups = defaultdict(list)
    for track_id in input_ids:
        cur_playlist.execute("""
            SELECT playlist_id
            FROM items
            WHERE playlist_items LIKE ?
        """, ('%' + track_id + '%',))
        playlists = cur_playlist.fetchall()
        for playlist in playlists:
            playlist_groups[playlist[0]].append(track_id)

    matched_playlists = {k: v for k,
                         v in playlist_groups.items() if len(v) > 1}

    # Step 3: Recommend other songs from the matched playlists
    recommendations = defaultdict(lambda: defaultdict(int))
    for playlist_id, track_ids in matched_playlists.items():
        cur_playlist.execute("""
            SELECT playlist_items
            FROM items
            WHERE playlist_id = ?
        """, (playlist_id,))
        result = cur_playlist.fetchone()
        if result:
            playlist_items = result[0].split(',')
            for item in playlist_items:
                if item not in input_ids:
                    recommendations[playlist_id][item] += 1

    # Step 4: Apply penalty to artists
    penalized_artists = set([track_details[tid][2]
                            for tid in input_ids if tid in track_details])

    # Step 5: Sort and limit recommendations
    sorted_recommendations = {}
    for playlist_id, tracks in recommendations.items():
        sorted_tracks = sorted(
            tracks.items(), key=lambda x: x[1], reverse=True)
        sorted_recommendations[playlist_id] = sorted_tracks[:n_recommend]

    # Step 6: Store result in a text file
    with open(output_path, 'w', encoding='utf-8') as f:
        # Inputted IDs
        f.write("# Inputted IDs\n")
        for i, track_id in enumerate(input_ids, 1):
            if track_id in track_details:
                track_id, track_name, artist_name = track_details[track_id]
                f.write(f"{i}. {artist_name} - {track_name} [{track_id}]\n")

        # Categorizing IDs
        f.write("\n# Categorizing IDs\n")
        group_id = 1
        for playlist_id, track_ids in matched_playlists.items():
            f.write(f"1. Group #{group_id} : {
                    ', '.join(map(str, track_ids))}\n")
            cur_playlist.execute("""
                SELECT playlist_id, creator_id
                FROM playlists
                WHERE playlist_id = ?
            """, (playlist_id,))
            result = cur_playlist.fetchone()
            if result:
                f.write(f"- [{result[0]}] by {result[1]}\n")
            group_id += 1

        # Songs Recommendations
        f.write("\n# Songs Recommendations\n")
        for playlist_id, tracks in sorted_recommendations.items():
            group_id = list(matched_playlists.keys()).index(playlist_id) + 1
            f.write(f"Group {group_id} (Input: {', '.join(
                map(str, matched_playlists[playlist_id]))})\n")
            for i, (track_id, count) in enumerate(tracks, 1):
                cur_songs.execute("""
                    SELECT t.track_id, t.track_name, a.artist_name
                    FROM tracks t
                    JOIN artists a ON a.artist_id = t.artist_ids
                    WHERE t.track_id = ?
                """, (track_id,))
                result = cur_songs.fetchone()
                if result:
                    track_id, track_name, artist_name = result
                    f.write(
                        f"{i}. {artist_name} - {track_name} [{track_id}] | Count: {count}\n")

    # Print
    print('Result: ', output_path)


if __name__ == "__main__":
    ids = [
        '4SqWKzw0CbA05TGszDgMlc',
        '0yc6Gst2xkRu0eMLeRMGCX',
        '086myS9r57YsLbJpU0TgK9',
        '26WgejlZUG6TxLo8djVxUp',
        '0mL82sxCRjrs3br407IdJh',
        '13sOb9V6Y3uCnRxY9HIZqP',
        '1Y0HqJ0WOyfUX5AvvGlQKF',
        '5FVd6KXrgO9B3JPmC8OPst',
        '3JjnGLK8IxkNLvo8Lb3KOM',
        '4xqrdfXkTW4T0RauPLv3WA',
        '0ROj512WvJ1eqeELd7MEdJ',
        '0BxE4FqsDD1Ot4YuBXwAPp',
        '1w3azB0VuRFp79AduIwrIy',
        '3p4hRhMcb6ch8OLtATMaLw',
        '4EWBhKf1fOFnyMtUzACXEc',
        '4R2kfaDFhslZEMJqAFNpdd',
        '2bdVgAQgosGUJoViVDNeOV',
    ]
    cf_result(ids)
