from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import sqlite3
import configparser
from collections import defaultdict

# Configuration setup
config = configparser.ConfigParser()
config.read('config.cfg')

# Constants
MODEL = 'Collaborative Filtering'
DB = config['rs']['db_path']
OUTPUT_PATH = config['rs']['cf_output']
SONGS_PER_ARTIST = int(config['hp']['songs_per_artist'])
ALL_GENRES = config['hp']['cf_genres']


def get_song_info(conn, song_id):
    """Fetch song details and associated artist details from the database."""
    cursor = conn.cursor()

    # Fetch song details
    cursor.execute("""
        SELECT s.song_id, s.song_name, s.artist_ids, 
               s.acousticness, s.danceability, s.energy, s.instrumentalness, 
               s.key, s.liveness, s.loudness, s.mode, s.speechiness, s.tempo, 
               s.time_signature, s.valence
        FROM songs s
        WHERE s.song_id = ?
    """, (song_id,))
    song_details = cursor.fetchone()

    if not song_details:
        return None

    song_id, song_name, artist_ids, acousticness, danceability, energy, instrumentalness, key, liveness, loudness, mode, speechiness, tempo, time_signature, valence = song_details
    first_artist_id = artist_ids.split(',')[0]  # Use the first artist ID

    # Fetch artist details
    cursor.execute("""
        SELECT artist_name, artist_genres
        FROM artists
        WHERE artist_id = ?
    """, (first_artist_id,))
    artist_details = cursor.fetchone()

    if not artist_details:
        return None

    artist_name, artist_genres = artist_details

    return (song_id, song_name, artist_ids, artist_name, artist_genres,
            acousticness, danceability, energy, instrumentalness, key,
            liveness, loudness, mode, speechiness, tempo, time_signature,
            valence)


def get_playlists_for_song(conn, song_id):
    """Retrieve playlists that contain the given song ID."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT playlist_id, playlist_creator_id, playlist_items
        FROM playlists
        WHERE playlist_items LIKE ?
    """, (f'%{song_id}%',))
    return cursor.fetchall()


def get_songs_from_playlists(conn, playlist_ids):
    """Count the occurrences of each song across the specified playlists."""
    song_counts = defaultdict(int)
    cursor = conn.cursor()

    for playlist_id in playlist_ids:
        cursor.execute("""
            SELECT playlist_items
            FROM playlists
            WHERE playlist_id = ?
        """, (playlist_id,))
        items = cursor.fetchone()[0].split(',')
        for song_id in items:
            song_counts[song_id] += 1

    return song_counts


def get_song_vector(song_info):
    """Convert song details into a vector combining numeric features and genre encoding."""
    _, _, _, _, artist_genres, acousticness, danceability, energy, instrumentalness, key, liveness, loudness, mode, speechiness, tempo, time_signature, valence = song_info

    # Numeric features
    numeric_features = np.array([
        danceability, energy,
        loudness, valence
    ])

    # Genre encoding
    genre_vector = np.zeros(len(ALL_GENRES))
    for genre in artist_genres.split(","):
        genre = genre.strip().lower()
        if genre in ALL_GENRES:
            genre_vector[ALL_GENRES.index(genre)] = 1

    return np.concatenate([numeric_features, genre_vector])


def format_song_info(song_info, count=None, similarity=None):
    """Format song details for output, including optional count and similarity."""
    song_id, song_name, _, artist_name, artist_genres, acousticness, danceability, energy, instrumentalness, key, liveness, loudness, mode, speechiness, tempo, time_signature, valence = song_info

    formatted_info = (
        f"https://open.spotify.com/track/{
            song_id} {artist_name} - {song_name} | "
        f"Genres: {artist_genres} | Acousticness: {
            acousticness}, Danceability: {danceability}, "
        f"Energy: {energy}, Instrumentalness: {instrumentalness}, Key: {key}, "
        f"Liveness: {liveness}, Loudness: {loudness}, Mode: {mode}, "
        f"Speechiness: {speechiness}, Tempo: {
            tempo}, Time Signature: {time_signature}, "
        f"Valence: {valence}"
    )

    if count is not None:
        formatted_info += f" | Count: {count}"
    if similarity is not None:
        formatted_info += f" | Cosine Sim: {similarity:.4f}"

    return formatted_info


def read_inputted_ids(ids, conn):
    """Fetch details for all inputted song IDs."""
    return [get_song_info(conn, song_id) for song_id in ids]


def cf(ids):
    """Collaborative filtering function to recommend songs based on input song IDs."""
    conn = sqlite3.connect(DB)
    songs_info = read_inputted_ids(ids, conn)

    input_vectors = [get_song_vector(song_info)
                     for song_info in songs_info if song_info]
    input_song_ids = set(song_info[0] for song_info in songs_info if song_info)
    input_song_titles_artists = {
        (song_info[1], song_info[3]) for song_info in songs_info if song_info}

    with open(OUTPUT_PATH, 'w', encoding='utf-8') as file:
        file.write('INPUTTED IDS\n')
        for i, song_info in enumerate(songs_info, 1):
            if song_info is None:
                file.write(f"{i}. Song ID not found in the database.\n")
                continue

            formatted_info = format_song_info(song_info)
            file.write(f"{i}. {formatted_info}\n")

            playlists = get_playlists_for_song(conn, song_info[0])
            playlist_ids = [playlist_id for playlist_id, _, _ in playlists]

            if playlist_ids:
                file.write(f"\nSONGS RECOMMENDATION: {formatted_info}\n")
                recommended_songs = get_songs_from_playlists(
                    conn, playlist_ids)

                similarities = []
                for recommended_song_id, count in recommended_songs.items():
                    if count > 1:
                        recommended_song_info = get_song_info(
                            conn, recommended_song_id)
                        if recommended_song_info:
                            rec_vector = get_song_vector(recommended_song_info)
                            similarity = cosine_similarity(
                                np.array(input_vectors), rec_vector.reshape(
                                    1, -1)
                            ).mean()
                            similarities.append(
                                (recommended_song_id, similarity, count))

                sorted_recommended_songs = sorted(
                    similarities, key=lambda x: x[1], reverse=True)

                artist_song_count = defaultdict(int)
                k = 1
                for recommended_song_id, similarity, count in sorted_recommended_songs:
                    song_recommendation_info = get_song_info(
                        conn, recommended_song_id)
                    if song_recommendation_info:
                        song_title = song_recommendation_info[1]
                        artist_name = song_recommendation_info[3]

                        if (recommended_song_id in input_song_ids or
                                (song_title, artist_name) in input_song_titles_artists):
                            continue

                        if artist_song_count[artist_name] < SONGS_PER_ARTIST:
                            formatted_recommendation = format_song_info(
                                song_recommendation_info, count=count, similarity=similarity)
                            file.write(f"{k}. {formatted_recommendation}\n")
                            artist_song_count[artist_name] += 1
                            k += 1
            file.write('\n')

    conn.close()
    print(f'Result for {MODEL} stored at {OUTPUT_PATH}')


if __name__ == "__main__":
    ids = ['2kJwzbxV2ppxnQoYw4GLBZ',
           '3Sbova9DAY3pc9GTAACT4b', '5O2P9iiztwhomNh8xkR9lJ']
    cf(ids)
