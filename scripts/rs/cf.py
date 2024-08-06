import sqlite3
import configparser
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
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


def get_artist_details(artist_ids):
    artist_details = {}
    for artist_id in artist_ids.split(','):
        artist = sp.artist(artist_id)
        artist_details[artist_id] = {
            'name': artist['name'],
            'genres': ', '.join(artist['genres'])
        }
    return artist_details


def get_song_details(song_ids):
    song_details = {}
    for song_id in song_ids:
        song = sp.track(song_id)
        artist_details = get_artist_details(song['artists'][0]['id'])
        song_details[song_id] = {
            'name': song['name'],
            'artist_name': song['artists'][0]['name'],
            'genres': artist_details[song['artists'][0]['id']]['genres']
        }
    return song_details


def get_playlists_by_songs(song_ids):
    cursor.execute("SELECT playlist_id, playlist_items FROM playlists")
    playlists = cursor.fetchall()

    song_to_playlists = {}
    for song_id in song_ids:
        song_to_playlists[song_id] = []

    for playlist_id, playlist_items in playlists:
        items = playlist_items.split(',')
        for song_id in song_ids:
            if song_id in items:
                song_to_playlists[song_id].append(playlist_id)

    return song_to_playlists


def categorize_playlists(song_to_playlists):
    playlist_categories = {}
    all_playlists = set()

    for song_id, playlists in song_to_playlists.items():
        for playlist in playlists:
            if playlist not in playlist_categories:
                playlist_categories[playlist] = []
            playlist_categories[playlist].append(song_id)
            all_playlists.add(playlist)

    return playlist_categories, all_playlists


def format_output(song_details, playlist_categories, all_playlists):
    output = []
    categorized_playlists = {}

    for playlist_id, songs in playlist_categories.items():
        artists = set()
        for song_id in songs:
            song = song_details[song_id]
            artists.add(song['artist_name'])
        categorized_playlists[playlist_id] = artists

    for idx, (playlist_id, artists) in enumerate(categorized_playlists.items(), 1):
        output.append(f"PLAYLIST CATEGORY ({idx}) {
                      artists} (Category Playlist that contains artists of inputted ids)")
        cursor.execute(
            "SELECT playlist_creator_id, playlist_top_genres, playlist_items FROM playlists WHERE playlist_id = ?", (playlist_id,))
        playlist = cursor.fetchone()

        creator_id = playlist[0]
        top_genres = playlist[1]
        playlist_items = playlist[2].split(',')
        song_count = len(
            [item for item in playlist_items if item in song_details])

        output.append(f"https://open.spotify.com/playlist/{playlist_id} - https://open.spotify.com/user/{
                      creator_id} | Genres: {top_genres} | {song_count} songs from this playlist")

    for song_id, details in song_details.items():
        playlists = [
            playlist_id for playlist_id in all_playlists if song_id in playlist_categories[playlist_id]]
        output.append(f"https://open.spotify.com/track/{song_id} {details['artist_name']} - {
                      details['name']} | Genre: {details['genres']} | Count: {len(playlists)} | From: {playlists}")

    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        f.write('\n'.join(output))


def cf(input_ids):
    song_details = get_song_details(input_ids)
    song_to_playlists = get_playlists_by_songs(input_ids)
    playlist_categories, all_playlists = categorize_playlists(
        song_to_playlists)
    format_output(song_details, playlist_categories, all_playlists)


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
