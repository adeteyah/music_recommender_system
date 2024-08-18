import sqlite3

# Define the database file
db_file = 'data/main.db'

# Connect to the SQLite database
conn = sqlite3.connect(db_file)
cursor = conn.cursor()

# Fetch all rows with the playlist_items column
cursor.execute("SELECT rowid, playlist_items FROM songs")
rows = cursor.fetchall()

# Loop through the rows and update the playlist_items_fetched column
for row in rows:
    rowid = row[0]
    playlist_items = row[1]

    # Count the number of items in the playlist_items column
    if playlist_items:
        item_count = len(playlist_items.split(','))
    else:
        item_count = 0  # In case playlist_items is empty or None

    # Update the playlist_items_fetched column with the count
    cursor.execute(
        "UPDATE songs SET playlist_items_fetched = ? WHERE rowid = ?", (item_count, rowid))

# Commit the changes and close the connection
conn.commit()
conn.close()
