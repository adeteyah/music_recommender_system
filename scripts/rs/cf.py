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
    playlists_result = []
    songs_result = []

    for song_id in ids:
        playlists = get_playlists_by_song(song_id)
        for playlist in playlists:
            playlist_id = playlist[0]
            creator_id = playlist[1]
            playlist_url = f"https://open.spotify.com/playlist/{playlist_id}"
            creator_url = f"https://open.spotify.com/user/{creator_id}"
            # Assuming this is the number of songs in the playlist
            songs_count = playlist[3]
            playlists_result.append(
                f"{playlist_url} - {creator_url} | {songs_count} songs from this playlist")

    for artist_id in ids:
        playlists = get_playlists_by_artist(artist_id)
        for playlist in playlists:
            playlist_id = playlist[0]
            creator_id = playlist[1]
            playlist_url = f"https://open.spotify.com/playlist/{playlist_id}"
            creator_url = f"https://open.spotify.com/user/{creator_id}"
            # Assuming this is the number of songs in the playlist
            songs_count = playlist[3]
            playlists_result.append(
                f"{playlist_url} - {creator_url} | {songs_count} songs from this playlist")

    for song_id in ids:
        song_info = get_song_info(song_id)
        if song_info:
            song_id, song_name, artist_ids, artist_name, artist_genres = song_info
            playlists = get_playlists_by_song(song_id)
            playlist_ids = [playlist[0] for playlist in playlists]
            count = len(playlist_ids)
            song_url = f"https://open.spotify.com/track/{song_id}"
            songs_result.append(f"{song_url} {artist_name} - {song_name} | Genre: {
                                artist_genres} | Count: {count} | From: {playlist_ids}")

    with open(OUTPUT_PATH, 'w') as f:
        f.write("PLAYLIST\n")
        for line in playlists_result:
            f.write(line + "\n")
        f.write("\nSONGS\n")
        for line in songs_result:
            f.write(line + "\n")


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
