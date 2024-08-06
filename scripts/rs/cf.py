
import sqlite3
import configparser
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.exceptions import SpotifyException
import time
from collections import Counter

# Load configuration
config = configparser.ConfigParser()
config.read('config.cfg')

DB = config['rs']['db_path']
CLIENT_ID = config['api']['client_id']
CLIENT_SECRET = config['api']['client_secret']
DELAY_TIME = float(config['api']['delay_time'])
N_MINIMUM = int(config['rs']['n_minimum_playlist_songs'])
N_SCRAPE = int(config['rs']['n_scrape'])
OUTPUT_PATH = config['rs']['cf_output']

# Spotify API credentials
client_credentials_manager = SpotifyClientCredentials(
    client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

# Connect to SQLite database
conn = sqlite3.connect(DB)
cursor = conn.cursor()


def get_artist_ids(song_ids):
    cursor.execute(
        "SELECT song_id, artist_ids FROM songs WHERE song_id IN ({})".format(
            ','.join('?' for _ in song_ids)),
        song_ids
    )
    return {row[0]: row[1].split(',') for row in cursor.fetchall()}


def get_playlists_containing_artists(artist_ids):
    cursor.execute(
        "SELECT playlist_id, playlist_top_artist_ids FROM playlists"
    )
    playlists = cursor.fetchall()

    playlist_artist_map = {}
    for playlist_id, top_artist_ids in playlists:
        top_artists = top_artist_ids.split(',')
        common_artists = set(artist_ids).intersection(top_artists)
        if common_artists:
            playlist_artist_map[playlist_id] = common_artists
    return playlist_artist_map


def categorize_input_ids(artist_playlists, input_ids, artist_map):
    categories = {'common': {}, 'individual': {}}

    for input_id, artist_ids in artist_map.items():
        found_playlists = set()
        for artist_id in artist_ids:
            found_playlists.update(artist_playlists.get(artist_id, []))

        if len(found_playlists) > 0:
            common_playlists = list(found_playlists)
            common_artist_ids = list(artist_ids)
            categories['common'][input_id] = {
                'playlists': common_playlists,
                'artists': common_artist_ids
            }
        else:
            categories['individual'][input_id] = list(artist_ids)

    return categories

# add procedural function here if needed


def recommend_songs(input_ids, artist_playlists):
    playlist_ids = set()
    for playlists in artist_playlists.values():
        playlist_ids.update(playlists)

    cursor.execute(
        "SELECT song_id, artist_ids, song_name FROM songs WHERE artist_ids NOT IN ({})".format(
            ','.join('?' for _ in input_ids)
        )
    )
    recommended_songs = []
    for row in cursor.fetchall():
        song_id, artist_ids, song_name = row
        artist_id_list = artist_ids.split(',')
        song_playlists = set()
        for artist_id in artist_id_list:
            song_playlists.update(artist_playlists.get(artist_id, []))
        if song_playlists.intersection(playlist_ids):
            recommended_songs.append({
                'song_id': song_id,
                'song_name': song_name,
                'artist_ids': artist_id_list,
                'playlists': list(song_playlists)
            })

    return recommended_songs


def output_results(categories, recommended_songs, output_path):
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("INPUTTED IDS:\n")
        for category, ids in categories.items():
            f.write(f"Case: {category}\n")
            for input_id, data in ids.items():
                f.write(f"{input_id}:\n")
                for playlist_id in data.get('playlists', []):
                    f.write(f"  - {playlist_id}\n")

        f.write(
            "\nSONGS (Recommend Other Artist is in the playlists_result other than Inputted IDS artist):\n")
        for song in recommended_songs:
            f.write(f"{song['song_id']} {song['song_name']} | Count: {
                    len(song['playlists'])} | From: {', '.join(song['playlists'])}\n")


def cf(song_ids):
    artist_map = get_artist_ids(song_ids)
    artist_playlists = {}
    for artist_ids in artist_map.values():
        for artist_id in artist_ids:
            playlists = get_playlists_containing_artists([artist_id])
            if artist_id not in artist_playlists:
                artist_playlists[artist_id] = set()
            artist_playlists[artist_id].update(playlists.keys())

    categories = categorize_input_ids(artist_playlists, song_ids, artist_map)
    recommended_songs = recommend_songs(song_ids, artist_playlists)
    output_results(categories, recommended_songs, OUTPUT_PATH)


if __name__ == "__main__":
    ids = [
        '1BxfuPKGuaTgP7aM0Bbdwr',
        '4xqrdfXkTW4T0RauPLv3WA',
        '7JIuqL4ZqkpfGKQhYlrirs',
        '5dTHtzHFPyi8TlTtzoz1J9',
        '4cluDES4hQEUhmXj6TXkSo',
        '4ZtFanR9U6ndgddUvNcjcG',
        '2QjOHCTQ1Jl3zawyYOpxh6',
        '0nJW01T7XtvILxQgC5J7Wh',
        '7nQoDLkzCcoIpKPQt3eCdN',
        '72MEldEAmz3WMJ2MkII3kP',
    ]
    cf(ids)
