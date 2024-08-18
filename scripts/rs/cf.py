from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import sqlite3
import configparser
from collections import defaultdict

# Read configuration file
config = configparser.ConfigParser()
config.read('config.cfg')

MODEL = 'Collaborative Filtering'
DB = config['rs']['db_path']
OUTPUT_PATH = config['rs']['cf_output']
SONGS_PER_ARTIST = int(config['hp']['songs_per_artist'])


def get_song_info(conn, song_id):
    cursor = conn.cursor()

    # Query to get song details
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

    # Extract the artist_ids and use only the first one
    song_id, song_name, artist_ids, acousticness, danceability, energy, instrumentalness, key, liveness, loudness, mode, speechiness, tempo, time_signature, valence = song_details
    first_artist_id = artist_ids.split(',')[0]  # Get the first artist ID

    # Query to get artist details
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
    cursor = conn.cursor()
    cursor.execute("""
        SELECT playlist_id, playlist_creator_id, playlist_items
        FROM playlists
        WHERE playlist_items LIKE ?
    """, (f'%{song_id}%',))
    return cursor.fetchall()


def get_songs_from_playlists(conn, playlist_ids):
    song_counts = defaultdict(int)
    for playlist_id in playlist_ids:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT playlist_items
            FROM playlists
            WHERE playlist_id = ?
        """, (playlist_id,))
        items = cursor.fetchone()[0].split(',')
        for song_id in items:
            song_counts[song_id] += 1
    return song_counts


def format_song_info(song_info, count=None, similarity=None):
    (song_id, song_name, artist_ids, artist_name, artist_genres, acousticness,
     danceability, energy, instrumentalness, key, liveness, loudness, mode,
     speechiness, tempo, time_signature, valence) = song_info

    base_info = (f"https://open.spotify.com/track/{song_id} {artist_name} - {song_name} | "
                 f"Genres: {artist_genres} | Acousticness: {
                     acousticness}, Danceability: {danceability}, "
                 f"Energy: {energy}, Instrumentalness: {
                     instrumentalness}, Key: {key}, "
                 f"Liveness: {liveness}, Loudness: {loudness}, Mode: {mode}, "
                 f"Speechiness: {speechiness}, Tempo: {
                     tempo}, Time Signature: {time_signature}, "
                 f"Valence: {valence}")

    # Add count and similarity to the output if they are provided
    if count is not None:
        base_info += f" | COUNT: {count}"
    if similarity is not None:
        base_info += f" | SIMILARITY: {similarity:.4f}"

    return base_info


def read_inputted_ids(ids, conn):
    return [get_song_info(conn, song_id) for song_id in ids]


def get_song_vector(song_info):
    # Extract relevant features and create a feature vector
    return np.array([
        song_info[5],  # acousticness
        song_info[6],  # danceability
        song_info[7],  # energy
        song_info[8],  # instrumentalness
        song_info[9],  # key
        song_info[10],  # liveness
        song_info[11],  # loudness
        song_info[12],  # mode
        song_info[13],  # speechiness
        song_info[14],  # tempo
        song_info[15]  # valence
    ])


def cf(ids):
    conn = sqlite3.connect(DB)
    songs_info = read_inputted_ids(ids, conn)

    # Get feature vectors for input songs
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

                # Calculate cosine similarity for each recommended song
                similarities = []
                for recommended_song_id in recommended_songs:
                    recommended_song_info = get_song_info(
                        conn, recommended_song_id)
                    if recommended_song_info:
                        rec_vector = get_song_vector(recommended_song_info)
                        similarity = cosine_similarity(
                            np.array(input_vectors), rec_vector.reshape(1, -1)
                            # Calculate mean similarity across all input songs
                        ).mean()
                        similarities.append((recommended_song_id, similarity))

                # Sort by similarity in descending order
                sorted_recommended_songs = sorted(
                    similarities, key=lambda x: x[1], reverse=True)

                # Track song count per artist
                artist_song_count = defaultdict(int)
                k = 1
                for recommended_song_id, similarity in sorted_recommended_songs:
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
                                song_recommendation_info, similarity)
                            file.write(f"{k}. {formatted_recommendation}\n")
                            artist_song_count[artist_name] += 1
                            k += 1
            file.write('\n')

    conn.close()
    print('Result for', MODEL, 'stored at', OUTPUT_PATH)


if __name__ == "__main__":
    ids = ['3wlLknnMtD8yZ0pCtCeeK4',
           '0KpWiHVmIFDTvai20likX4', '30Z12rJpW0M0u8HMFpigTB']
    cf(ids)
