import sqlite3
import pandas as pd
from collections import Counter

# Connect to the SQLite database
conn = sqlite3.connect('data/main.db')

# Load data into pandas DataFrames
songs_df = pd.read_sql_query("SELECT * FROM songs", conn)
playlists_df = pd.read_sql_query("SELECT * FROM playlists", conn)
artists_df = pd.read_sql_query("SELECT * FROM artists", conn)

# Function to predict artist genres based on playlists


def predict_artist_genres(artist_id, songs_df, playlists_df):
    # Step 1: Find all song_ids associated with the artist_id
    artist_songs = songs_df[songs_df['artist_ids'].str.contains(
        artist_id, na=False)]
    song_ids = artist_songs['song_id'].tolist()

    # Step 2: Find all playlists that contain any of the song_ids
    matching_playlists = playlists_df[playlists_df['playlist_items'].apply(
        lambda x: any(song_id in x.split(',') for song_id in song_ids)
    )]

    # Step 3: Gather all genres from playlist_top_genres of matching playlists
    all_genres = []
    for genres in matching_playlists['playlist_top_genres'].dropna():
        all_genres.extend(genres.split(','))

    # Step 4: Count the frequency of each genre and select the most common
    if all_genres:
        genre_counts = Counter(all_genres)
        most_common_genre = genre_counts.most_common(1)[0][0]
        return ','.join([genre for genre, _ in genre_counts.most_common()])
    else:
        return None

# Function to update artist_genres in the database


def update_artist_genres():
    # Reconnect to the database to update
    conn = sqlite3.connect('data/main.db')
    cursor = conn.cursor()

    # Iterate through artists with empty or NULL artist_genres
    for index, artist in artists_df.iterrows():
        if pd.isnull(artist['artist_genres']) or artist['artist_genres'].strip() == '':
            artist_id = artist['artist_id']
            predicted_genre = predict_artist_genres(
                artist_id, songs_df, playlists_df)

            if predicted_genre:
                # Update the artist_genres in the database
                cursor.execute(
                    "UPDATE artists SET artist_genres = ? WHERE artist_id = ?", (predicted_genre, artist_id))
                print(f"Updated {artist_id} with genres {predicted_genre}")

    # Commit changes and close the connection
    conn.commit()
    conn.close()


# Run the update function
update_artist_genres()
