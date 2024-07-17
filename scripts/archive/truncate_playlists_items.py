import sqlite3
import pandas as pd

# Database file path
db_path = r'C:\Users\Adeteyah\Documents\music_recommender_system\data\db\playlists_details.db'

# Connect to the SQLite database
conn = sqlite3.connect(db_path)

# Load data into pandas DataFrame
items_df = pd.read_sql_query("SELECT * FROM items", conn)

# Function to truncate playlist items to 50


def truncate_items(playlist_items):
    items_list = playlist_items.split(',')
    if len(items_list) > 50:
        items_list = items_list[:50]
    return ','.join(items_list)


# Apply truncation to the 'playlist_items' column
items_df['playlist_items'] = items_df['playlist_items'].apply(truncate_items)

# Update the database
for index, row in items_df.iterrows():
    conn.execute("UPDATE items SET playlist_items = ? WHERE playlist_id = ?",
                 (row['playlist_items'], row['playlist_id']))

# Commit the changes and close the connection
conn.commit()
conn.close()

print("Playlists have been truncated to a maximum of 50 items each.")
