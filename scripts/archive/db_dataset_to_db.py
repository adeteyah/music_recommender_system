import sqlite3

# Define your database file
db_file = 'data/main.db'

# Define the mapping of columns from dataset_1 to songs
column_mapping = {
    'id': 'song_id',
    'name': 'song_name',
    'artist_ids': 'artist_ids',
    'acousticness': 'acousticness',
    'danceability': 'danceability',
    'energy': 'energy',
    'instrumentalness': 'instrumentalness',
    'key': 'key',
    'liveness': 'liveness',
    'loudness': 'loudness',
    'mode': 'mode',
    'speechiness': 'speechiness',
    'tempo': 'tempo',
    'time_signature': 'time_signature',
    'valence': 'valence'
}

# Function to import data


def import_data(db_file, column_mapping):
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()

        # Build the SELECT statement
        select_columns = ', '.join(column_mapping.keys())
        select_sql = f"SELECT {select_columns} FROM dataset_1"

        # Fetch data from dataset_1
        cursor.execute(select_sql)
        data = cursor.fetchall()

        # Build the INSERT statement with OR IGNORE
        insert_columns = ', '.join(column_mapping.values())
        placeholders = ', '.join(['?'] * len(column_mapping))
        insert_sql = f"INSERT OR IGNORE INTO songs ({insert_columns}) VALUES ({
            placeholders})"

        # Insert data into songs
        for row in data:
            cursor.execute(insert_sql, row)

        # Commit the transaction
        conn.commit()
        print("Data has been successfully imported from dataset_1 to songs.")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Close the database connection
        conn.close()


# Call the function with the specified variables
import_data(db_file, column_mapping)
