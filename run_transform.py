import csv
import sqlite3
import os
import pandas as pd
import configparser
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

config = configparser.ConfigParser()
config.read('config.cfg')

raw_path = config['dir']['raw']
transformed_path = config['dir']['transformed']
songs_db_path = config['db']['songs_db']
spotify_client_id = config['spotify']['client_id']
spotify_client_secret = config['spotify']['client_secret']

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=spotify_client_id,
                                                           client_secret=spotify_client_secret))


def transform_raw_csv(file_path, output_path):
    df = pd.read_csv(file_path)
    df.drop_duplicates(subset=['spotify_id'], inplace=True)

    num = 5
    if len(df) >= num:
        df.to_csv(output_path, index=False)
        print(f"Saved cleaned data to {output_path}")
    else:
        print(f"Skipped {file_path}, less than {num} tracks.")


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


def process_transformed_csv(transformed_path, songs_db_path):
    for filename in os.listdir(transformed_path):
        if filename.endswith('.csv'):
            file_path = os.path.join(transformed_path, filename)
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


def fill_database_with_spotify_api(songs_db_path):
    conn = sqlite3.connect(songs_db_path)
    cursor = conn.cursor()

    # Function to update track names
    def update_track_names():
        query = "SELECT track_id FROM tracks WHERE track_name = ''"
        print('Running query...')
        cursor.execute(query)
        print('Fetching all cursor...')
        tracks_to_update = cursor.fetchall()
        updated_tracks = []
        print('Iterating tracks id...')
        for track_id in tracks_to_update:
            try:
                print(f'Fetching track name for {track_id}')
                track_info = sp.track(track_id[0])
                track_name = track_info['name']
                updated_tracks.append((track_id[0], track_name, 1))
            except:
                # Track name not found
                print(f'Track name not found for {track_id}')
                updated_tracks.append((track_id[0], '', 0))
        return updated_tracks

    # Function to update artist names and genres
    def update_artist_info():
        query = "SELECT artist_id FROM artists WHERE artist_name = '' OR artist_genres = ''"
        print('Running query...')
        cursor.execute(query)
        print('Fetching all cursor...')
        artists_to_update = cursor.fetchall()
        updated_artists = []
        print('Iterating artists id...')
        for artist_id in artists_to_update:
            try:
                print(f'Fetching track name for {artist_id}')
                artist_info = sp.artist(artist_id[0])
                artist_name = artist_info['name']
                artist_genres = ",".join(artist_info['genres'])
                updated_artists.append(
                    (artist_id[0], artist_name, artist_genres, 1))
            except:
                # Artist info not found
                print(f'Track name not found for {artist_id}')
                updated_artists.append((artist_id[0], '', '', 0))
        return updated_artists

    # Updating tracks
    tracks_cache = update_track_names()
    with open('data/cache/tracks_table_cache.csv', 'w') as file:
        writer = csv.writer(file)
        writer.writerow(['spotify_id', 'track_name', 'success'])
        writer.writerows(tracks_cache)

    # Updating artists
    artists_cache = update_artist_info()
    with open('data/cache/artists_table_cache.csv', 'w') as file:
        writer = csv.writer(file)
        writer.writerow(['artist_id', 'artist_name',
                        'artist_genres', 'success'])
        writer.writerows(artists_cache)

    # Updating database with successful results
    for track_id, track_name, success in tracks_cache:
        if success == 1:
            cursor.execute(
                "UPDATE tracks SET track_name = ? WHERE track_id = ?", (track_name, track_id))

    for artist_id, artist_name, artist_genres, success in artists_cache:
        if success == 1:
            cursor.execute("UPDATE artists SET artist_name = ?, artist_genres = ? WHERE artist_id = ?",
                           (artist_name, artist_genres, artist_id))

    conn.commit()
    conn.close()

    # Summary
    total_tracks_updated = sum(
        1 for _, _, success in tracks_cache if success == 1)
    total_artists_updated = sum(
        1 for _, _, _, success in artists_cache if success == 1)
    offset = 0  # Assuming no pagination for simplicity

    print(f"Total tracks updated: {total_tracks_updated}")
    print(f"Total artists updated: {total_artists_updated}")
    print(f"Last offset processed: {offset}")


def choose_process():
    print("Choose a process to run:")
    print("1. Transform raw CSV files")
    print("2. Insert data into database")
    print("3. Fill database with Spotify API")
    choice = input("Enter your choice (1, 2, or 3): ")

    if choice == '1':
        for filename in os.listdir(raw_path):
            if filename.endswith('.csv'):
                file_path = os.path.join(raw_path, filename)
                output_path = os.path.join(transformed_path, filename)
                transform_raw_csv(file_path, output_path)
        print("Transformation process completed.")
    elif choice == '2':
        process_transformed_csv(transformed_path, songs_db_path)
        print("Data insertion process completed.")
    elif choice == '3':
        fill_database_with_spotify_api(songs_db_path)
        print("Database filled with Spotify API data.")
    else:
        print("Invalid choice. Please enter '1', '2', or '3'.")


if __name__ == "__main__":
    choose_process()
