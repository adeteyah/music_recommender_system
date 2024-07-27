import sqlite3
import configparser

# Read the configuration file
config = configparser.ConfigParser()
config.read('config.cfg')

db_playlist = config['db']['playlists_db']
db_songs = config['db']['songs_db']

# Connect to the databases
conn_playlist = sqlite3.connect(db_playlist)
cur_playlist = conn_playlist.cursor()
conn_songs = sqlite3.connect(db_songs)
cur_songs = conn_songs.cursor()

# Function to split data into train and test sets


def split_data(conn, cur, table_name, train_table, test_table, id_column):
    # Count total records
    cur.execute(f"SELECT COUNT(*) FROM {table_name}")
    total_records = cur.fetchone()[0]

    # Calculate the number of records for training (80%)
    train_limit = int(total_records * 0.8)

    # Insert 80% of records into the training table
    cur.execute(f"""
        INSERT INTO {train_table}
        SELECT *
        FROM {table_name}
        ORDER BY RANDOM()
        LIMIT {train_limit}
    """)
    conn.commit()

    # Insert the remaining 20% of records into the testing table
    cur.execute(f"""
        INSERT INTO {test_table}
        SELECT *
        FROM {table_name}
        WHERE {id_column} NOT IN (SELECT {id_column} FROM {train_table})
    """)
    conn.commit()


# Split items data
split_data(conn_playlist, cur_playlist, 'items',
           'items_to_train', 'items_to_test', 'playlist_id')

# Split tracks data
split_data(conn_songs, cur_songs, 'tracks',
           'tracks_to_train', 'tracks_to_test', 'track_id')

# Close the database connections
conn_playlist.close()
conn_songs.close()
