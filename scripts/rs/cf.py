import sqlite3
import configparser
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.exceptions import SpotifyException
import time
from collections import defaultdict, Counter

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


def get_playlists_by_song(song_id):
    cursor.execute("""
        SELECT * FROM playlists
        WHERE playlist_items LIKE ?
    """, ('%' + song_id + '%',))
    return cursor.fetchall()


def get_playlists_by_artist(artist_id):
    cursor.execute("""
        SELECT * FROM playlists
        WHERE playlist_top_artist_ids LIKE ?
    """, ('%' + artist_id + '%',))
    return cursor.fetchall()


def get_song_info(song_id):
    cursor.execute("""
        SELECT s.song_id, s.song_name, s.artist_ids, a.artist_name, a.artist_genres
        FROM songs s
        JOIN artists a ON s.artist_ids = a.artist_id
        WHERE s.song_id = ?
    """, (song_id,))
    return cursor.fetchone()


def cf(ids):
    playlists_result = defaultdict(list)
    songs_result = []
    inputted_songs = []
    inputted_artists = set()

    # Gather information for inputted IDs
    for song_id in ids:
        song_info = get_song_info(song_id)
        if song_info:
            song_id, song_name, artist_ids, artist_name, artist_genres = song_info
            inputted_songs.append(f"https://open.spotify.com/track/{song_id} {
                                  artist_name} - {song_name} | Genre: {artist_genres}")
            inputted_artists.add(artist_ids)

    # Find playlists containing the inputted songs and artists
    artist_playlist_map = defaultdict(set)
    for song_id in ids:
        playlists = get_playlists_by_song(song_id)
        for playlist in playlists:
            playlist_id = playlist[0]
            artist_playlist_map[playlist_id].update(inputted_artists)
            creator_id = playlist[1]
            playlist_url = f"https://open.spotify.com/playlist/{playlist_id}"
            creator_url = f"https://open.spotify.com/user/{creator_id}"
            # Assuming this is the number of songs in the playlist
            songs_count = playlist[3]
            playlists_result[frozenset(inputted_artists)].append(
                f"{playlist_url} - {creator_url} | {songs_count} songs from this playlist")

    for artist_id in inputted_artists:
        playlists = get_playlists_by_artist(artist_id)
        for playlist in playlists:
            playlist_id = playlist[0]
            artist_playlist_map[playlist_id].add(artist_id)
            creator_id = playlist[1]
            playlist_url = f"https://open.spotify.com/playlist/{playlist_id}"
            creator_url = f"https://open.spotify.com/user/{creator_id}"
            # Assuming this is the number of songs in the playlist
            songs_count = playlist[3]
            playlists_result[frozenset(artist_playlist_map[playlist_id])].append(
                f"{playlist_url} - {creator_url} | {songs_count} songs from this playlist")

    # Find songs by other artists in the playlists
    for playlist_id in artist_playlist_map:
        artists_in_playlist = artist_playlist_map[playlist_id]
        cursor.execute("""
            SELECT s.song_id, s.song_name, s.artist_ids, a.artist_name, a.artist_genres
            FROM songs s
            JOIN artists a ON s.artist_ids = a.artist_id
            WHERE s.song_id IN (
                SELECT song_id FROM playlists WHERE playlist_id = ?
            ) AND s.artist_ids NOT IN (?)
        """, (playlist_id, ','.join(inputted_artists)))
        songs = cursor.fetchall()
        song_counter = Counter()
        playlist_map = defaultdict(list)

        for song in songs:
            song_id, song_name, artist_ids, artist_name, artist_genres = song
            song_counter[song_id] += 1
            playlist_map[song_id].append(playlist_id)

        for song_id, count in song_counter.items():
            song_info = next(song for song in songs if song[0] == song_id)
            song_id, song_name, artist_ids, artist_name, artist_genres = song_info
            song_url = f"https://open.spotify.com/track/{song_id}"
            playlist_ids = playlist_map[song_id]
            songs_result.append(f"{song_url} {artist_name} - {song_name} | Genre: {
                                artist_genres} | Count: {count} | From: {playlist_ids}")

    # Write to output file
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        f.write("INPUTTED IDS\n")
        for idx, line in enumerate(inputted_songs, start=1):
            f.write(f"{idx}. {line}\n")

        f.write("\nPLAYLIST CATEGORY\n")
        for idx, (artist_ids, playlists) in enumerate(playlists_result.items(), start=1):
            artist_ids_str = ','.join(artist_ids)
            f.write(f"{idx}. ({artist_ids_str})\n")
            for playlist_idx, line in enumerate(playlists, start=1):
                f.write(f"   {playlist_idx}. {line}\n")

        f.write("\nSONGS\n")
        for idx, line in enumerate(songs_result, start=1):
            f.write(f"{idx}. {line}\n")


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
