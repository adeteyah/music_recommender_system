import sqlite3
import configparser

# Read config file
config = configparser.ConfigParser()
config.read('config.cfg')

songs_db_path = config['db']['songs_db']
playlists_db_path = config['db']['playlists_db']

# Connect to the databases
songs_conn = sqlite3.connect(songs_db_path)
playlists_conn = sqlite3.connect(playlists_db_path)

# Fetch all playlists
playlists_cursor = playlists_conn.cursor()
playlists_cursor.execute("SELECT playlist_id FROM playlists")
playlists = playlists_cursor.fetchall()

# Helper function to get min and max values from a list of tuples


def get_min_max(feature_list):
    return min(feature_list), max(feature_list)


# Process each playlist
for playlist in playlists:
    playlist_id = playlist[0]

    # Fetch track_ids for the playlist
    playlists_cursor.execute(
        "SELECT playlist_items FROM items WHERE playlist_id=?", (playlist_id,))
    playlist_items = playlists_cursor.fetchone()
    if not playlist_items:
        continue

    track_ids = playlist_items[0].split(',')

    # Fetch all audio features for tracks in this playlist
    placeholders = ','.join('?' for _ in track_ids)
    songs_cursor = songs_conn.cursor()
    songs_cursor.execute(f"SELECT duration_ms, popularity, acousticness, danceability, energy, instrumentalness, key, liveness, loudness, mode, speechiness, tempo, time_signature, valence FROM tracks WHERE track_id IN ({
                         placeholders})", track_ids)
    track_features = songs_cursor.fetchall()

    if not track_features:
        continue

    # Calculate min and max for each feature
    duration_ms = [track[0] for track in track_features]
    popularity = [track[1] for track in track_features]
    acousticness = [track[2] for track in track_features]
    danceability = [track[3] for track in track_features]
    energy = [track[4] for track in track_features]
    instrumentalness = [track[5] for track in track_features]
    key = [track[6] for track in track_features]
    liveness = [track[7] for track in track_features]
    loudness = [track[8] for track in track_features]
    mode = [track[9] for track in track_features]
    speechiness = [track[10] for track in track_features]
    tempo = [track[11] for track in track_features]
    time_signature = [track[12] for track in track_features]
    valence = [track[13] for track in track_features]

    min_duration_ms, max_duration_ms = get_min_max(duration_ms)
    min_popularity, max_popularity = get_min_max(popularity)
    min_acousticness, max_acousticness = get_min_max(acousticness)
    min_danceability, max_danceability = get_min_max(danceability)
    min_energy, max_energy = get_min_max(energy)
    min_instrumentalness, max_instrumentalness = get_min_max(instrumentalness)
    min_key, max_key = get_min_max(key)
    min_liveness, max_liveness = get_min_max(liveness)
    min_loudness, max_loudness = get_min_max(loudness)
    min_mode, max_mode = get_min_max(mode)
    min_speechiness, max_speechiness = get_min_max(speechiness)
    min_tempo, max_tempo = get_min_max(tempo)
    min_time_signature, max_time_signature = get_min_max(time_signature)
    min_valence, max_valence = get_min_max(valence)

    # Update playlists table with calculated values
    playlists_cursor.execute("""
        UPDATE playlists
        SET min_duration_ms=?, max_duration_ms=?, min_popularity=?, max_popularity=?,
            min_acousticness=?, max_acousticness=?, min_danceability=?, max_danceability=?,
            min_energy=?, max_energy=?, min_instrumentalness=?, max_instrumentalness=?,
            min_key=?, max_key=?, min_liveness=?, max_liveness=?, min_loudness=?, max_loudness=?,
            min_mode=?, max_mode=?, min_speechiness=?, max_speechiness=?, min_tempo=?, max_tempo=?,
            min_time_signature=?, max_time_signature=?, min_valence=?, max_valence=?
        WHERE playlist_id=?
    """, (
        min_duration_ms, max_duration_ms, min_popularity, max_popularity,
        min_acousticness, max_acousticness, min_danceability, max_danceability,
        min_energy, max_energy, min_instrumentalness, max_instrumentalness,
        min_key, max_key, min_liveness, max_liveness, min_loudness, max_loudness,
        min_mode, max_mode, min_speechiness, max_speechiness, min_tempo, max_tempo,
        min_time_signature, max_time_signature, min_valence, max_valence,
        playlist_id
    ))

# Commit the changes and close the connections
playlists_conn.commit()
playlists_conn.close()
songs_conn.close()
