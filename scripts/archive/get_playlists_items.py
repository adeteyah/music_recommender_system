import sqlite3
import pandas as pd

# Define your database file
db_file = 'data/main.db'

# Connect to the SQLite database
conn = sqlite3.connect(db_file)

# Query to select all playlist_items from the playlists table
query = "SELECT playlist_items FROM playlists"

# Read the data into a DataFrame
df = pd.read_sql_query(query, conn)

# Close the database connection
conn.close()

# Initialize a set to store unique IDs
unique_ids = set()

# Process each row to extract unique IDs
for row in df['playlist_items']:
    ids = row.split(',')
    unique_ids.update(ids)

# Convert the set of unique IDs to a sorted list
sorted_unique_ids = sorted(unique_ids)

# Create a DataFrame for the CSV output
output_df = pd.DataFrame(sorted_unique_ids, columns=['IDs'])

# Write to CSV
output_df.to_csv('data/playlist_items_ids.csv', index=False, header=False)
