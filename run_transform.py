import json
import os
import pandas as pd
import configparser

config = configparser.ConfigParser()
config.read('config.cfg')

raw_path = config['dir']['raw']
transformed_path = config['dir']['transformed']

playlists_json_path = config['dir']['playlists_json']
artists_json_path = config['dir']['artists_json']
tracks_json_path = config['dir']['tracks_json']

os.makedirs(transformed_path, exist_ok=True)


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

# Load JSON files


def load_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

# Save JSON files


def save_json(data, file_path):
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

# Function to update tracks and artists JSON


def update_json(csv_file, tracks_json, artists_json):
    df = pd.read_csv(csv_file)

    # Update tracks JSON
    for index, row in df.iterrows():
        track_id = row['spotify_id']
        artist_ids = row['artists_id'].split(',')

        # Check if the track already exists in the tracks JSON
        track_exists = False
        for track in tracks_json['tracks']:
            if track['id'] == track_id:
                track_exists = True
                track['artist_ids'].extend(artist_ids)
                track['artist_ids'] = list(
                    set(track['artist_ids']))  # Remove duplicates
                break

        if not track_exists:
            tracks_json['tracks'].append({
                "id": track_id,
                "title": track_id,  # Assuming title is same as track_id, you can modify this
                "artist_ids": artist_ids
            })

        # Update artists JSON
        for artist_id in artist_ids:
            artist_exists = False
            for artist in artists_json['artists']:
                if artist['id'] == artist_id:
                    artist_exists = True
                    break

            if not artist_exists:
                artists_json['artists'].append({
                    "id": artist_id,
                    # Placeholder, as we don't have the actual name
                    "name": f"Artist {artist_id}",
                    "genres": []  # Placeholder, as we don't have the actual genres
                })


# Load JSON data
tracks_json_path = config['dir']['tracks_json']
artists_json_path = config['dir']['artists_json']
tracks_json = load_json(tracks_json_path)
artists_json = load_json(artists_json_path)

# Process each CSV file
for filename in os.listdir(transformed_path):
    if filename.endswith('.csv'):
        file_path = os.path.join(transformed_path, filename)
        update_json(file_path, tracks_json, artists_json)

# Save updated JSON data
save_json(tracks_json, tracks_json_path)
save_json(artists_json, artists_json_path)

print(f"Updated JSON files: {tracks_json_path} and {artists_json_path}")
