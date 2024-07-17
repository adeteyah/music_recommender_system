import os
import csv
import sqlite3

# Directory where CSV files are located
csv_directory = r'C:\Users\Adeteyah\Documents\music_recommender_system\data\transformed'

# SQLite database file path
db_file = r'C:\Users\Adeteyah\Documents\music_recommender_system\data\db\playlists_details.db'

# Function to connect to SQLite database


def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except sqlite3.Error as e:
        print(e)
    return conn

# Function to insert or update data in database


def insert_or_update_data(conn, playlist_id, playlist_items):
    try:
        cursor = conn.cursor()
        # Insert or update statement
        cursor.execute("INSERT OR REPLACE INTO items (playlist_id, playlist_items) VALUES (?, ?)",
                       (playlist_id, playlist_items))
        conn.commit()
    except sqlite3.Error as e:
        print(e)


# Iterate through each CSV file in the directory
for filename in os.listdir(csv_directory):
    if filename.endswith('.csv'):
        # Extract playlist_id from filename
        playlist_id = filename.split('_')[-1].split('.')[0]

        # Read Spotify IDs from CSV file, skipping header
        spotify_ids = []
        with open(os.path.join(csv_directory, filename), newline='') as csvfile:
            reader = csv.reader(csvfile)
            next(reader)  # Skip header row
            for row in reader:
                if len(row) >= 2:
                    # Assuming first column is spotify_id
                    spotify_id = row[0].strip()
                    spotify_ids.append(spotify_id)

        # Convert spotify_ids to comma-separated string
        playlist_items = ', '.join(spotify_ids)

        # Insert or update data in database
        conn = create_connection(db_file)
        if conn is not None:
            insert_or_update_data(conn, playlist_id, playlist_items)
            conn.close()
        else:
            print("Error! Cannot create the database connection.")

print("Data import completed.")
