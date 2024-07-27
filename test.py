import sqlite3
import configparser

# Read configuration
config = configparser.ConfigParser()
config.read('config.cfg')

songs_db_path = config['db']['songs_db']


def insert_track_ids():
    # Connect to the songs database
    conn = sqlite3.connect(songs_db_path)
    cursor = conn.cursor()

    # Retrieve all track_id values from the tracks table
    cursor.execute("SELECT track_id FROM tracks")
    track_ids = cursor.fetchall()

    # Insert track_id values into the lyrics table
    insert_query = "INSERT INTO lyrics (track_id) VALUES (?) ON CONFLICT(track_id) DO NOTHING"

    for track_id in track_ids:
        cursor.execute(insert_query, (track_id[0],))

    # Commit changes and close the connection
    conn.commit()
    conn.close()


if __name__ == "__main__":
    insert_track_ids()
    print("Finished inserting track_ids into lyrics table.")
