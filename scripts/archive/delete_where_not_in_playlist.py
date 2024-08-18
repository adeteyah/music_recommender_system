import sqlite3
import pandas as pd

# Define file paths
db_file = 'data/main.db'
csv_file = 'data/playlist_items_ids.csv'

# Read the CSV file to get the list of song_ids to keep
df = pd.read_csv(csv_file, header=None, names=['song_id'])
song_ids_to_keep = df['song_id'].tolist()

# Connect to the SQLite database
conn = sqlite3.connect(db_file)
cursor = conn.cursor()

# Check the number of rows in the songs table before deletion
cursor.execute("SELECT COUNT(*) FROM songs")
initial_count = cursor.fetchone()[0]
print(f"Initial number of songs: {initial_count}")

# Check the number of song_ids to keep
print(f"Number of song_ids in CSV: {len(song_ids_to_keep)}")

# Create a temporary table to store song_ids to keep
cursor.execute(
    "CREATE TEMPORARY TABLE IF NOT EXISTS temp_song_ids (song_id TEXT)")
cursor.executemany("INSERT INTO temp_song_ids (song_id) VALUES (?)", [
                   (id,) for id in song_ids_to_keep])

# Perform the deletion using the temporary table
query = """
DELETE FROM songs
WHERE song_id NOT IN (
    SELECT song_id FROM temp_song_ids
)
"""
cursor.execute(query)

# Drop the temporary table
cursor.execute("DROP TABLE temp_song_ids")

# Commit the changes and check the number of rows after deletion
conn.commit()

cursor.execute("SELECT COUNT(*) FROM songs")
final_count = cursor.fetchone()[0]
print(f"Final number of songs: {final_count}")

# Close the connection
conn.close()
