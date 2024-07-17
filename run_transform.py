import sqlite3
import os
import time
import pandas as pd
import configparser
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.exceptions import SpotifyException

config = configparser.ConfigParser()
config.read('config.cfg')

songs_db_path = config['db']['songs_db']
playlists_db_path = config['db']['playlists_db']

SPOTIPY_CLIENT_ID = config['spotify']['client_id']
SPOTIPY_CLIENT_SECRET = config['spotify']['client_secret']


client_credentials_manager = SpotifyClientCredentials(
    client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)


def insert_data_into_db(db_path, table_name, data):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    placeholders = ", ".join(["?"] * len(data[0]))
    columns = ", ".join(data[0].keys())
    sql = f"INSERT OR IGNORE INTO {
        table_name} ({columns}) VALUES ({placeholders})"

    for row in data:
        cursor.execute(sql, list(row.values()))

    conn.commit()
    conn.close()


def fill_playlist_db():
    for filename in os.listdir(transformed_path):
        if filename.endswith('.csv'):
            file_path = os.path.join(transformed_path, filename)
            creator_id, playlist_id = filename.split(
                '_')[0], filename.split('_')[1].split('.')[0]

            df = pd.read_csv(file_path)

            track_data = [
                {
                    "track_id": row['spotify_id'],
                    "track_name": "",
                    "artist_ids": ",".join(row['artists_id'].split(','))
                }
                for _, row in df.iterrows()
            ]
            insert_data_into_db(songs_db_path, 'tracks', track_data)

            artists = set()
            for _, row in df.iterrows():
                for artist_id in row['artists_id'].split(','):
                    artists.add(artist_id)

            artist_data = [
                {
                    "artist_id": artist_id,
                    "artist_name": "",
                    "artist_genres": ""
                }
                for artist_id in artists
            ]
            insert_data_into_db(songs_db_path, 'artists', artist_data)

            playlist_data = {
                "creator_id": creator_id,
                "playlist_id": playlist_id,
                "playlist_track_count": len(df)
            }
            insert_data_into_db(playlists_db_path,
                                'playlists', [playlist_data])


def fill_songs_db_with_spotify():
    conn = sqlite3.connect(songs_db_path)
    cursor = conn.cursor()

    # Updating artists
    while True:
        cursor.execute(
            "SELECT * FROM artists WHERE artist_name = '' LIMIT 5")
        artists = cursor.fetchall()
        if not artists:
            break

        for artist in artists:
            artist_id = artist[0]
            try:
                artist_info = sp.artist(artist_id)
                artist_name = artist_info['name']
                artist_genres = ",".join(artist_info['genres'])
                cursor.execute("UPDATE artists SET artist_name = ?, artist_genres = ? WHERE artist_id = ?",
                               (artist_name, artist_genres, artist_id))
                print(f'Updated artist name, genres for {
                      artist_id}: {artist_name}, {artist_genres}')
            except SpotifyException as e:
                print(f"Error fetching artist {artist_id}: {e}")
        time.sleep(5)
        conn.commit()

    # Updating tracks
    while True:
        cursor.execute("SELECT * FROM tracks WHERE track_name = '' LIMIT 5")
        tracks = cursor.fetchall()
        if not tracks:
            break

        for track in tracks:
            track_id = track[0]
            try:
                track_info = sp.track(track_id)
                track_name = track_info['name']
                cursor.execute(
                    "UPDATE tracks SET track_name = ? WHERE track_id = ?", (track_name, track_id))
                print(f'Updated track name for {track_id}: {track_name}')
            except SpotifyException as e:
                print(f"Error fetching track {track_id}: {e}")
        time.sleep(5)
        conn.commit()

    conn.close()
    print("Finished updating tracks and artists with Spotify data.")


def choose_process():
    while True:
        print("\nChoose a process to run:")
        print("1. Fill playlist database")
        print("2. Fill songs database with Spotify data")
        print("3. Exit")
        choice = input("Enter your choice (1 or 2): ")

        if choice == '1':
            fill_playlist_db()
            print("Playlist DB filled with current data.")
        elif choice == '2':
            fill_songs_db_with_spotify()
            print("Songs DB filled with Spotify data.")
        elif choice == '3':
            print("Exiting the program.")
            break
        else:
            print("Invalid choice. Please enter '1' or '2'.")

        return_to_menu = input("Return to menu (Y/N)? ").strip().lower()
        if return_to_menu != 'y':
            print("Exiting the program.")
            break


if __name__ == "__main__":
    choose_process()
