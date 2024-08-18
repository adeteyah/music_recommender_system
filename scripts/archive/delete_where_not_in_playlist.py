import sqlite3
import pandas as pd

# Define file paths
db_file = 'data/main.db'
csv_file = 'data/playlist_items_ids.csv'

# Load the list of IDs from the CSV file
id_df = pd.read_csv(csv_file, header=None, names=['song_id'])
id_list = id_df['song_id'].tolist()

# Connect to the SQLite database
conn = sqlite3.connect(db_file)
cursor = conn.cursor()

# Delete rows from the songs table where song_id is not in the CSV file
id_placeholder = ','.join(['?'] * len(id_list))
delete_query = f"DELETE FROM songs WHERE song_id NOT IN ({id_placeholder})"
cursor.execute(delete_query, id_list)

# Commit the changes and close the connection
conn.commit()
conn.close()

print(f"Deleted rows where song_id is not in {csv_file}")
