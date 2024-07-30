import sqlite3
import configparser

# Load configurations
config = configparser.ConfigParser()
config.read('config.cfg')

db_playlist = config['db']['playlists_db']
db_songs = config['db']['songs_db']

# Connect to the databases
conn_playlist = sqlite3.connect(db_playlist)
cur_playlist = conn_playlist.cursor()
conn_songs = sqlite3.connect(db_songs)
cur_songs = conn_songs.cursor()


def delete_invalid_playlists():
    # Get all track IDs from the tracks table
    cur_songs.execute("SELECT track_id FROM tracks")
    valid_track_ids = set(track_id[0] for track_id in cur_songs.fetchall())

    # Get all playlists
    cur_playlist.execute("SELECT playlist_id, playlist_items FROM items")
    playlists = cur_playlist.fetchall()

    playlists_to_delete = []

    for playlist_id, playlist_items in playlists:
        track_ids = set(playlist_items.split(','))
        if not track_ids.issubset(valid_track_ids):
            playlists_to_delete.append(playlist_id)

    # Delete invalid playlists
    for playlist_id in playlists_to_delete:
        cur_playlist.execute(
            "DELETE FROM items WHERE playlist_id = ?", (playlist_id,))
        cur_playlist.execute(
            "DELETE FROM playlists WHERE playlist_id = ?", (playlist_id,))
        print(f"Deleted playlist with ID: {playlist_id}")

    conn_playlist.commit()


if __name__ == "__main__":
    delete_invalid_playlists()

    # Close the connections
    conn_playlist.close()
    conn_songs.close()
