import sqlite3
import pandas as pd

# Define file paths
db_file = 'data/main.db'
csv_file = 'data/playlist_items_ids.csv'
chunk_size = 900  # Adjust the chunk size if needed

# Load the list of IDs from the CSV file
id_df = pd.read_csv(csv_file, header=None, names=['song_id'])
id_list = id_df['song_id'].tolist()

# Connect to the SQLite database
conn = sqlite3.connect(db_file)
cursor = conn.cursor()

# Function to delete rows in chunks


def delete_in_chunks(id_list, chunk_size):
    for i in range(0, len(id_list), chunk_size):
        chunk = id_list[i:i + chunk_size]
        id_placeholder = ','.join(['?'] * len(chunk))
        delete_query = f"DELETE FROM songs WHERE song_id NOT IN ({
            id_placeholder})"
        cursor.execute(delete_query, chunk)
        print(f"Deleted rows not in chunk {i // chunk_size + 1}")


# Perform the deletion
delete_in_chunks(id_list, chunk_size)

# Commit the changes and close the connection
conn.commit()
conn.close()

print(f"Deletion complete. Rows where song_id is not in {
      csv_file} have been deleted.")
