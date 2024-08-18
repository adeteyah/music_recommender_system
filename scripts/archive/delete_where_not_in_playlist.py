import sqlite3
import pandas as pd

# Define file paths
db_file = 'data/main.db'
csv_file = 'data/playlist_items_ids.csv'

# Read the CSV file to get the list of song_ids to keep
df = pd.read_csv(csv_file, header=None, names=['song_id'])
song_ids_to_keep = df['song_id'].tolist()

# Define the batch size
batch_size = 500  # Adjust as needed

# Connect to the SQLite database
conn = sqlite3.connect(db_file)
cursor = conn.cursor()

# Perform batch deletion
for i in range(0, len(song_ids_to_keep), batch_size):
    batch = song_ids_to_keep[i:i + batch_size]
    placeholders = ','.join('?' for _ in batch)
    query = f"DELETE FROM songs WHERE song_id NOT IN ({placeholders})"
    cursor.execute(query, batch)

# Commit the changes and close the connection
conn.commit()
conn.close()
