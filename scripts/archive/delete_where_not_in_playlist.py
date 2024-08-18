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

# Print out some of the song_ids to keep for verification
print("Sample song_ids to keep:", song_ids_to_keep[:10])

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

# Commit the changes and close the connection
conn.commit()
conn.close()
