import sqlite3
import json
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

# Process transformed data to JSON Database


def load_json(file_path, default_data):
    if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
        return default_data
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)


def save_json(data, file_path):
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def update_json(csv_file, tracks_json, artists_json):
    df = pd.read_csv(csv_file)

    for index, row in df.iterrows():
        track_id = row['spotify_id']
        artist_ids = row['artists_id'].split(',')

        track_exists = False
        for track in tracks_json['tracks']:
            if track['id'] == track_id:
                track_exists = True
                track['artist_ids'].extend(artist_ids)
                track['artist_ids'] = list(set(track['artist_ids']))
                break

        if not track_exists:
            tracks_json['tracks'].append({
                "id": track_id,
                "title": '',
                "artist_ids": artist_ids
            })

        for artist_id in artist_ids:
            artist_exists = False
            for artist in artists_json['artists']:
                if artist['id'] == artist_id:
                    artist_exists = True
                    break

            if not artist_exists:
                artists_json['artists'].append({
                    "id": artist_id,
                    "name": '',
                    "genres": []
                })


playlists_json_path = config['file']['playlists_json']
artists_json_path = config['file']['artists_json']
tracks_json_path = config['file']['tracks_json']

# Initialize default structures
default_tracks_json = {"tracks": []}
default_artists_json = {"artists": []}

tracks_json = load_json(tracks_json_path, default_tracks_json)
artists_json = load_json(artists_json_path, default_artists_json)

for filename in os.listdir(transformed_path):
    if filename.endswith('.csv'):
        file_path = os.path.join(transformed_path, filename)
        update_json(file_path, tracks_json, artists_json)

save_json(tracks_json, tracks_json_path)
save_json(artists_json, artists_json_path)

print(f"Updated JSON files: {tracks_json_path} and {artists_json_path}")

# Create the databases
artists_db_path = config['db']['artists_details.db']
tracks_db_path = config['db']['tracks_details.db']

# Function to parse and insert data into SQLite


def insert_data_into_db(db_path, table_name, data):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    placeholders = ", ".join(["?"] * len(data[0]))
    columns = ", ".join(data[0].keys())
    sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"

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
                    "id": row['spotify_id'],
                    # Assuming the title is the same as spotify_id, you might need to adjust this
                    "title": row['spotify_id'],
                    "artist_ids": json.dumps(row['artists_id'].split(','))
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
                    "id": artist_id,
                    "name": "",
                    "genres": ""
                }
                for artist_id in artists
            ]
            insert_data_into_db(artists_db_path, 'artists', artist_data)


process_transformed_csv(transformed_path, artists_db_path, tracks_db_path)
