import sqlite3
import os
import pandas as pd
import configparser

config = configparser.ConfigParser()
config.read('config.cfg')

raw_path = config['dir']['raw']
transformed_path = config['dir']['transformed']

# Transform raw data


def transform_raw_csv(file_path, output_path):
    df = pd.read_csv(file_path)
    df.drop_duplicates(subset=['spotify_id'], inplace=True)

    num = 5
    if len(df) >= num:
        df.to_csv(output_path, index=False)
        print(f"Saved cleaned data to {output_path}")
    else:
        print(f"Skipped {file_path}, less than {num} tracks.")


for filename in os.listdir(raw_path):
    if filename.endswith('.csv'):
        file_path = os.path.join(raw_path, filename)
        output_path = os.path.join(transformed_path, filename)
        transform_raw_csv(file_path, output_path)

#


# Load the configuration

transformed_path = config['dir']['transformed']
artists_db_path = config['db']['artists_db']
tracks_db_path = config['db']['tracks_db']

# Function to insert data into the database


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

# Function to process the transformed CSV files


def process_transformed_csv(transformed_path, artists_db_path, tracks_db_path):
    for filename in os.listdir(transformed_path):
        if filename.endswith('.csv'):
            file_path = os.path.join(transformed_path, filename)
            df = pd.read_csv(file_path)

            # Insert into tracks_details.db
            track_data = [
                {
                    "track_id": row['spotify_id'],
                    "track_name": "",
                    "artist_ids": ",".join(row['artists_id'].split(','))
                }
                for _, row in df.iterrows()
            ]
            insert_data_into_db(tracks_db_path, 'tracks', track_data)

            # Insert into artists_details.db
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
            insert_data_into_db(artists_db_path, 'artists', artist_data)


# Process the transformed CSV files and insert data into the databases
process_transformed_csv(transformed_path, artists_db_path, tracks_db_path)
