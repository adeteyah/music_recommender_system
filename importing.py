import sqlite3
import pandas as pd
import os

# File to store the last processed batch
PROGRESS_FILE = r'C:\Users\Adeteyah\Documents\progress.txt'


def save_progress(start):
    with open(PROGRESS_FILE, 'w') as f:
        f.write(str(start))


def load_progress():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, 'r') as f:
            return int(f.read().strip())
    return 0


def import_data(batch_size=1000):
    # Load progress
    start_from = load_progress()

    # Connect to the source database
    source_conn = sqlite3.connect(
        r'C:\Users\Adeteyah\Documents\source_tracks.db')

    # Read data from source tables
    audio_features_df = pd.read_sql_query(
        "SELECT * FROM audio_features", source_conn)
    track_information_df = pd.read_sql_query(
        "SELECT * FROM track_information", source_conn)
    source_conn.close()

    # Create combined DataFrame for tracks
    tracks_df = pd.merge(track_information_df,
                         audio_features_df, on='spotify_id')
    tracks_df.rename(columns={
        'spotify_id': 'track_id',
        'artist_names': 'artist_ids'
    }, inplace=True)

    # Connect to the destination database (songs)
    songs_conn = sqlite3.connect(
        r'C:\Users\Adeteyah\Documents\music_recommender_system\data\db\songs_details.db')

    # Process tracks in batches
    total_tracks = len(tracks_df)
    for start in range(start_from, total_tracks, batch_size):
        end = start + batch_size
        batch_df = tracks_df.iloc[start:end]
        print(f'Processing tracks {start} to {end} out of {total_tracks}')

        for index, row in batch_df.iterrows():
            try:
                row.to_frame().T.to_sql('tracks', songs_conn, if_exists='append', index=False)
            except sqlite3.IntegrityError:
                # Update existing record if track_id already exists
                update_query = """
                UPDATE tracks
                SET
                    track_name = ?,
                    artist_ids = ?,
                    duration_ms = ?,
                    popularity = ?,
                    acousticness = ?,
                    danceability = ?,
                    energy = ?,
                    instrumentalness = ?,
                    key = ?,
                    liveness = ?,
                    loudness = ?,
                    mode = ?,
                    speechiness = ?,
                    tempo = ?,
                    time_signature = ?,
                    valence = ?
                WHERE
                    track_id = ?
                """
                songs_conn.execute(update_query, (
                    row['track_name'], row['artist_ids'], row['duration_ms'], row['popularity'],
                    row['acousticness'], row['danceability'], row['energy'], row['instrumentalness'],
                    row['key'], row['liveness'], row['loudness'], row['mode'], row['speechiness'],
                    row['tempo'], row['time_signature'], row['valence'], row['track_id']
                ))
                songs_conn.commit()

        # Save progress
        save_progress(end)

    # Insert artists data in batches
    artists_df = track_information_df[['artist_names']].drop_duplicates()
    artists_df['artist_id'] = artists_df['artist_names']
    artists_df.rename(columns={'artist_names': 'artist_name'}, inplace=True)
    artists_df['artist_genres'] = ''  # Placeholder if genres are not available

    total_artists = len(artists_df)
    for start in range(0, total_artists, batch_size):
        end = start + batch_size
        batch_df = artists_df.iloc[start:end]
        print(f'Processing artists {start} to {end} out of {total_artists}')

        for index, row in batch_df.iterrows():
            try:
                row.to_frame().T.to_sql('artists', songs_conn, if_exists='append', index=False)
            except sqlite3.IntegrityError:
                # Update existing record if artist_id already exists
                update_query = """
                UPDATE artists
                SET artist_name = ?, artist_genres = ?
                WHERE artist_id = ?
                """
                songs_conn.execute(update_query, (
                    row['artist_name'], row['artist_genres'], row['artist_id']
                ))
                songs_conn.commit()

    songs_conn.close()

    # Connect to the playlists database
    playlists_conn = sqlite3.connect(
        r'C:\Users\Adeteyah\Documents\music_recommender_system\data\db\playlists_details.db')

    # Example DataFrame for playlists
    playlists_df = pd.DataFrame({
        'playlist_id': [],
        'creator_id': [],
        'playlist_track_count': [],
        'min_duration_ms': [],
        'max_duration_ms': [],
        'min_popularity': [],
        'max_popularity': [],
        'min_acousticness': [],
        'max_acousticness': [],
        'min_danceability': [],
        'max_danceability': [],
        'min_energy': [],
        'max_energy': [],
        'min_instrumentalness': [],
        'max_instrumentalness': [],
        'min_key': [],
        'max_key': [],
        'min_liveness': [],
        'max_liveness': [],
        'min_loudness': [],
        'max_loudness': [],
        'min_mode': [],
        'max_mode': [],
        'min_speechiness': [],
        'max_speechiness': [],
        'min_tempo': [],
        'max_tempo': [],
        'min_time_signature': [],
        'max_time_signature': [],
        'min_valence': [],
        'max_valence': [],
        'most_artist_id': [],
        'most_genres': []
    })

    # Insert data into the playlists table in a batch (example; real logic may differ)
    print('Processing playlists data')
    playlists_df.to_sql('playlists', playlists_conn,
                        if_exists='append', index=False)

    playlists_conn.close()

    # Remove progress file after completion
    if os.path.exists(PROGRESS_FILE):
        os.remove(PROGRESS_FILE)


# Run the import function
import_data()
