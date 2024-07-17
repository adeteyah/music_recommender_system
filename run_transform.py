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

    batch_size = 10
    offset = 0
    total_tracks_updated = 0
    total_artists_updated = 0

    # fill code

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
