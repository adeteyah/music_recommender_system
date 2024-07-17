
import sqlite3
import os
import pandas as pd
import configparser
import time

config = configparser.ConfigParser()
config.read('config.cfg')

raw_path = config['dir']['raw']
transformed_path = config['dir']['transformed']

songs_db_path = config['db']['songs_db']
playlists_db_path = config['db']['playlists_db']


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


def fill_playlist_db():
    for filename in os.listdir(transformed_path):
        if filename.endswith('.csv'):
            file_path = os.path.join(transformed_path, filename)
            creator_id, playlist_id = filename.split(
                '_')[0], filename.split('_')[1].split('.')[0]

            df = pd.read_csv(file_path)

            # Example: Inserting track data into 'tracks' table
            track_data = [
                {
                    "track_id": row['spotify_id'],
                    "track_name": "",  # You might fetch track names from Spotify API
                    "artist_ids": ",".join(row['artists_id'].split(','))
                }
                for _, row in df.iterrows()
            ]
            insert_data_into_db(songs_db_path, 'tracks', track_data)

            # Example: Inserting artist data into 'artists' table
            artists = set()
            for _, row in df.iterrows():
                for artist_id in row['artists_id'].split(','):
                    artists.add(artist_id)

            artist_data = [
                {
                    "artist_id": artist_id,
                    "artist_name": "",  # You might fetch artist names from Spotify API
                    "artist_genres": ""
                }
                for artist_id in artists
            ]
            insert_data_into_db(songs_db_path, 'artists', artist_data)

            # Inserting playlist metadata into 'playlists' table
            playlist_data = {
                "creator_id": creator_id,
                "playlist_id": playlist_id,
                "playlist_track_count": len(df)
            }
            insert_data_into_db(playlists_db_path,
                                'playlists', [playlist_data])


def fill_songs_db_with_spotify():
    # TODO
    pass


def choose_process():
    print("Choose a process to run:")
    print("1. Transform raw CSV files")
    print("2. Insert data into database")
    print("3. Fill playlist database")
    print("4. Fill songs database with Spotify data")
    choice = input("Enter your choice (1, 2, 3, or 4): ")

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
        fill_playlist_db()
        print("Playlist DB filled with current data.")
    elif choice == '4':
        fill_songs_db_with_spotify()
        print("Songs DB filled with Spotify data.")
    else:
        print("Invalid choice. Please enter '1', '2', '3', or '4'.")


if __name__ == "__main__":
    choose_process()
