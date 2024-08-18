import sqlite3

# Define the path to the database
db_file = 'data/main.db'

# Connect to the SQLite database
conn = sqlite3.connect(db_file)
cursor = conn.cursor()

# Select all rows from the playlists table
cursor.execute("SELECT playlist_id, playlist_top_artist_ids FROM playlists")
rows = cursor.fetchall()

# Iterate through each row
for row in rows:
    playlist_id = row[0]
    playlist_top_artist_ids = row[1]

    # Check if playlist_top_artist_ids has only one artist ID
    if playlist_top_artist_ids:
        artist_ids = playlist_top_artist_ids.split(',')
        if len(artist_ids) == 1:
            # Delete the row where there's only one artist ID
            cursor.execute(
                "DELETE FROM playlists WHERE playlist_id = ?", (playlist_id,))

# Commit the changes and close the connection
conn.commit()
conn.close()
