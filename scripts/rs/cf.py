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
        '5XeFesFbtLpXzIVDNQP22n',
        '2UgCs0i0rNHUH2jKE5NZHE',
        '1fDFHXcykq4iw8Gg7s5hG9',
        '6ilc4vQcwMPlvAHFfsTGng',
        '4SqWKzw0CbA05TGszDgMlc',
        '0yc6Gst2xkRu0eMLeRMGCX',
        '1dGr1c8CrMLDpV6mPbImSI',
        '1FWsomP9StpCcXNWmJk8Cl',
        '1RMJOxR6GRPsBHL8qeC2ux',
        '2LBqCSwhJGcFQeTHMVGwy3',
        '2eAvDnpXP5W0cVtiI0PUxV',
        '086myS9r57YsLbJpU0TgK9',
        '26WgejlZUG6TxLo8djVxUp',
        '3afkJSKX0EAMsJXTZnDXXJ',
        '4kfjA6WfgKBt7I7YKuDCkU',
        '56tKRucMdMNuslADmaxN9L',
        '5CZ40GBx1sQ9agT82CLQCT',
        '5xuL74G1vQhSGn7WC3L3QL',
        '7bWHFauPVNfMYUVZnAXbo9',
        '22Nd3GuO7sHopPjdKccRcq',
        '2iOgTijjnxjtz7723Xs4sp',
        '5suV1gtfD3kGj5A3teIVtV',
        '3AJwUDP919kvQ9QcozQPxg',
        '0mL82sxCRjrs3br407IdJh',
        '13sOb9V6Y3uCnRxY9HIZqP',
        '1Y0HqJ0WOyfUX5AvvGlQKF',
        '5FVd6KXrgO9B3JPmC8OPst',
        '3JjnGLK8IxkNLvo8Lb3KOM',
        '4xqrdfXkTW4T0RauPLv3WA',
        '0ROj512WvJ1eqeELd7MEdJ',
        '0SpkyS1Q4MD8GaVcP5YjT4',
        '3hUxzQpSfdDqwM3ZTFQY0K',
        '630DpnzdfjdVqv2yLfPbAX',
        '7D0RhFcb3CrfPuTJ0obrod',
        '78Sw5GDo6AlGwTwanjXbGh',
        '2dIBMHByUGcNPzmYBJ6OAj',
        '2tGvwE8GcFKwNdAXMnlbfl',
        '3M0lSi5WW79CXQamgSBIjx',
        '73jVPicY2G9YHmzgjk69ae',
        '1dQQ2QlnvXUehsRUrukKmf',
        '3vkCueOmm7xQDoJ17W1Pm3',
        '7CyPwkp0oE8Ro9Dd5CUDjW',
        '01beCqR9wsVnwzkAJZyTqq',
        '0BxE4FqsDD1Ot4YuBXwAPp',
        '1w3azB0VuRFp79AduIwrIy',
        '3p4hRhMcb6ch8OLtATMaLw',
        '4EWBhKf1fOFnyMtUzACXEc',
        '4R2kfaDFhslZEMJqAFNpdd',
        '51lPx6ZCSalL2kvSrDUyJc',
        '7nQoDLkzCcoIpKPQt3eCdN',
        '3cKM7UXBZmgjEgEBTkaIlU',
        '1BxfuPKGuaTgP7aM0Bbdwr',
        '22bPsP2jCgbLUvh82U0Z3M',
        '26cvTWJq2E1QqN4jyH2OTU',
        '3W4U7TEgILGpq0EmquurtH',
        '3pCt2wRdBDa2kCisIdHWgF',
        '5O2P9iiztwhomNh8xkR9lJ',
        '6ueq4MrVEcvUwe8E80SPar',
        '7MXVkk9YMctZqd1Srtv4MB',
        '1drRDlIBhcYUOaeMssBpEr',
        '3sqrvkNC6IPTIXvvbx9Arw',
        '4Ssi6tKwrTHi5qvDndrZRP',
        '7iTF9T1jum3Km6H6WMZpDC',
        '7ivYWXqrPLs66YwakDuSim',
        '18UsAG7SfOQ5sxJEdjAMH0',
        '1Fid2jjqsHViMX6xNH70hE',
        '5MIpcd16T59wFeqAChSYwC',
        '04S1pkp1VaIqjg8zZqknR5',
        '1NZs6n6hl8UuMaX0UC0YTz',
        '1ZPVEo8RfmrEz8YAD5n6rW',
        '2AT8iROs4FQueDv2c8q2KE',
        '2LlOeW5rVcvl3QcPNPcDus',
        '4HBZA5flZLE435QTztThqH',
        '4dtmj7X21gunWoQf98hW5L',
        '0X2bh8NVQ8svDQIn2AdCbW',
        '0otRX6Z89qKkHkQ9OqJpKt',
        '2wAiFWjRupWmnDkQcu91MF',
        '3Eb5sztvEMa0Mqnb8DUAlU',
        '3hRV0jL3vUpRrcy398teAU',
        '5EcGSkkNBMAWOePvLgKde1',
        '7zFXmv6vqI4qOt4yGf3jYZ',
        '0ug5NqcwcFR2xrfTkc7k8e',
        '1fzAuUVbzlhZ1lJAx9PtY6',
        '2EfZf8CglKPgpa96criANN',
        '2hHeGD57S0BcopfVcmehdl',
        '3TgMcrV32NUKjEG2ujn9eh',
        '5drW6PGRxkE6MxttzVLNk5',
        '09mEdoA6zrmBPgTEN5qXmN',
        '1HNkqx9Ahdgi1Ixy2xkKkL',
        '1SKPmfSYaPsETbRHaiA18G',
        '1qrpoAMXodY6895hGKoUpA',
        '2xlV2CuWgpPyE9e0GquKDN',
        '4reIsHKw5hUj4pV8zzMjLA',
        '5TpPSTItCwtZ8Sltr3vdzm',
        '68HocO7fx9z0MgDU0ZPHro',
        '6HU7h9RYOaPRFeh0R3UeAr',
        '77sMIMlNaSURUAXq5coCxE',
        '0M3HkE321xpCbCYqVKzr1q',
        '1acVBP8BcK6LTeNeFjfxnh',
        '2bdVgAQgosGUJoViVDNeOV',
    ]
    cf_result(ids)
