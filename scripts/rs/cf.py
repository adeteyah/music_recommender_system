import sqlite3
import configparser
import random
from collections import defaultdict

# Read config
config = configparser.ConfigParser()
config.read('config.cfg')

db_playlist = config['db']['playlists_db']
db_songs = config['db']['songs_db']
output_path = config['output']['cf_output']
n_recommend = int(config['rs']['n_recommend'])

# Connect to the databases
conn_playlist = sqlite3.connect(db_playlist)
cur_playlist = conn_playlist.cursor()
conn_songs = sqlite3.connect(db_songs)
cur_songs = conn_songs.cursor()


def fetch_track_details(track_ids):
    track_details = {}
    query = f"SELECT track_id, track_name, artist_ids FROM tracks WHERE track_id IN ({
        ','.join(['?']*len(track_ids))})"
    cur_songs.execute(query, track_ids)
    for row in cur_songs.fetchall():
        track_details[row[0]] = {'track_name': row[1], 'artist_ids': row[2]}
    return track_details


def fetch_artist_details(artist_ids):
    artist_details = {}
    query = f"SELECT artist_id, artist_name FROM artists WHERE artist_id IN ({
        ','.join(['?']*len(artist_ids))})"
    cur_songs.execute(query, artist_ids)
    for row in cur_songs.fetchall():
        artist_details[row[0]] = row[1]
    return artist_details


def fetch_playlists_containing_tracks(track_ids):
    playlists = defaultdict(list)
    query = f"SELECT playlist_id, playlist_items FROM items"
    cur_playlist.execute(query)
    for row in cur_playlist.fetchall():
        playlist_id = row[0]
        playlist_items = row[1].split(',')
        matching_items = set(track_ids).intersection(set(playlist_items))
        if matching_items:
            playlists[playlist_id] = matching_items
    return playlists


def fetch_playlist_details(playlist_ids):
    playlist_details = {}
    query = f"SELECT playlist_id, creator_id FROM playlists WHERE playlist_id IN ({
        ','.join(['?']*len(playlist_ids))})"
    cur_playlist.execute(query, playlist_ids)
    for row in cur_playlist.fetchall():
        playlist_details[row[0]] = row[1]
    return playlist_details


def recommend_songs_from_playlists(playlists, exclude_ids):
    track_counts = defaultdict(int)
    for items in playlists.values():
        for item in items:
            if item not in exclude_ids:
                track_counts[item] += 1
    sorted_tracks = sorted(track_counts.items(),
                           key=lambda x: x[1], reverse=True)
    recommended_tracks = sorted_tracks[:n_recommend]
    return [track_id for track_id, count in recommended_tracks], track_counts


def write_result(unqualified, qualified, playlist_matches, recommendations, track_details, artist_details, track_counts, playlist_details):
    with open(output_path, 'w', encoding='utf-8') as file:
        file.write("Unqualified IDs (Doesn't match):\n")
        for track_id in unqualified:
            artists = ', '.join(
                artist_details[aid] for aid in track_details[track_id]['artist_ids'].split(','))
            file.write(f"1. {
                       artists} - {track_details[track_id]['track_name']} [http://open.spotify.com/track/{track_id}]\n")

        file.write("\nQualified IDs (Found match):\n")
        for track_id in qualified:
            artists = ', '.join(
                artist_details[aid] for aid in track_details[track_id]['artist_ids'].split(','))
            file.write(f"1. {
                       artists} - {track_details[track_id]['track_name']} [http://open.spotify.com/track/{track_id}]\n")

        file.write("\nQualified Playlist:\n")
        for playlist_id, match_ids in playlist_matches.items():
            creator_id = playlist_details[playlist_id]
            ids_str = ', '.join(match_ids)
            file.write(
                f"- Qualified ID {ids_str} found @ {playlist_id} by {creator_id}\n")

        file.write("\nRecommended Songs:\n")
        for track_id in recommendations:
            artists = ', '.join(
                artist_details[aid] for aid in track_details[track_id]['artist_ids'].split(','))
            file.write(f"1. {artists} - {track_details[track_id]['track_name']} [http://open.spotify.com/track/{
                       track_id}] | Count: {track_counts[track_id]}\n")


def cf_result(ids):
    # Fetch track details
    track_details = fetch_track_details(ids)
    artist_ids = set(aid for t in track_details.values()
                     for aid in t['artist_ids'].split(','))
    artist_details = fetch_artist_details(list(artist_ids))

    # Fetch playlists containing the inputted track IDs
    playlists = fetch_playlists_containing_tracks(ids)

    # Separate qualified and unqualified IDs
    qualified_ids = set()
    unqualified_ids = set(ids)
    playlist_matches = defaultdict(list)

    for playlist_id, matching_items in playlists.items():
        if len(matching_items) > 1:
            qualified_ids.update(matching_items)
            unqualified_ids.difference_update(matching_items)
            playlist_matches[playlist_id] = matching_items

    # Fetch playlist details
    playlist_details = fetch_playlist_details(list(playlist_matches.keys()))

    # Recommend other songs in the qualified playlists
    recommendations, track_counts = recommend_songs_from_playlists(
        playlists, ids)

    # Write the result
    write_result(list(unqualified_ids), list(qualified_ids), playlist_matches,
                 recommendations, track_details, artist_details, track_counts, playlist_details)


if __name__ == "__main__":
    ids = [
        '1FWsomP9StpCcXNWmJk8Cl',
        '1RMJOxR6GRPsBHL8qeC2ux',
        '2LBqCSwhJGcFQeTHMVGwy3',
        '2eAvDnpXP5W0cVtiI0PUxV',
    ]
    cf_result(ids)

# Close connections
conn_playlist.close()
conn_songs.close()
