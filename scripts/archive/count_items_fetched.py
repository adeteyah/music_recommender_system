import sqlite3

# Define the path to the database
db_file = 'data/main.db'

# Connect to the SQLite database
conn = sqlite3.connect(db_file)
cursor = conn.cursor()

# Select all rows from the playlists table
cursor.execute("SELECT playlist_id, playlist_items FROM playlists")
rows = cursor.fetchall()

# Iterate through each row
for row in rows:
    playlist_id = row[0]
    playlist_items = row[1]

    # Count the number of items by splitting the comma-separated string
    if playlist_items:
        item_count = len(playlist_items.split(','))
    else:
        item_count = 0

    # Update the playlist_items_fetched column with the counted items
    cursor.execute(
        "UPDATE playlists SET playlist_items_fetched = ? WHERE playlist_id = ?",
        (item_count, playlist_id)
    )

# Commit the changes and close the connection
conn.commit()
conn.close()
