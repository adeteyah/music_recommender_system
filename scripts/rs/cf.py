import sqlite3
import configparser
from collections import defaultdict
import re

# Read configuration file
config = configparser.ConfigParser()
config.read('config.cfg')

MODEL = 'Collaborative Filtering'
DB = config['rs']['db_path']
OUTPUT_PATH = config['rs']['cf_output']


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


def format_song_info(song_info, count=None):
    (song_id, song_name, artist_ids, artist_name, artist_genres, acousticness,
     danceability, energy, instrumentalness, key, liveness, loudness, mode,
     speechiness, tempo, time_signature, valence) = song_info

    base_info = (f"https://open.spotify.com/track/{song_id} {artist_name} - {song_name} | "
                 f"Genre: {artist_genres} | Acousticness: {
                     acousticness}, Danceability: {danceability}, "
                 f"Energy: {energy}, Instrumentalness: {
                     instrumentalness}, Key: {key}, "
                 f"Liveness: {liveness}, Loudness: {loudness}, Mode: {mode}, "
                 f"Speechiness: {speechiness}, Tempo: {
                     tempo}, Time Signature: {time_signature}, "
                 f"Valence: {valence}")

    return base_info + (f" | COUNT: {count}" if count is not None else "")


def read_inputted_ids(ids, conn):
    return [get_song_info(conn, song_id) for song_id in ids]


def is_similar_song(song_info, existing_songs):
    song_id, song_name, artist_ids, _, _, _, _, _, _, _, _, _, _, _, _, _ = song_info
    artist_name = existing_songs.get(song_id, {}).get('artist_name', '')
    existing_song_name = existing_songs.get(song_id, {}).get('song_name', '')

    if song_id in existing_songs:
        return True

    for key, info in existing_songs.items():
        if artist_name == info['artist_name'] and song_name == info['song_name']:
            return True
        if artist_name == info['artist_name'] and similar_title(song_name, info['song_name']):
            return True

    return False


def similar_title(title1, title2):
    # Function to check if titles are similar (e.g., same song with different variations like remix, cover, etc.)
    variations = ['remix', 'remaster', 'cover', 'version', 'edit', 'live']
    title1 = title1.lower()
    title2 = title2.lower()

    for var in variations:
        if var in title1 and var in title2:
            return True

    return title1 == title2


def cf(ids):
    conn = sqlite3.connect(DB)
    songs_info = read_inputted_ids(ids, conn)

    # Create a dictionary of inputted songs
    input_songs = {song_info[0]: {
        'song_name': song_info[1],
        'artist_name': song_info[3]
    } for song_info in songs_info if song_info}

    with open(OUTPUT_PATH, 'w', encoding='utf-8') as file:
        file.write('INPUTTED IDS\n')
        for i, song_info in enumerate(songs_info, 1):
            if song_info is None:  # Check if the song was found
                file.write(f"{i}. Song ID not found in the database.\n")
                continue

            formatted_info = format_song_info(song_info)
            file.write(f"{i}. {formatted_info}\n")

            # Add FOUND IN section
            file.write(f"\nFOUND IN:\n")
            playlists = get_playlists_for_song(conn, song_info[0])
            playlist_ids = [playlist_id for playlist_id, _, _ in playlists]
            for j, (playlist_id, playlist_creator_id, _) in enumerate(playlists, 1):
                file.write(f"{j}. {playlist_id} by {playlist_creator_id}\n")

            # Add SONGS RECOMMENDATION section with a specific title
            if playlist_ids:
                file.write(f"\nSONGS RECOMMENDATION FOR {formatted_info}\n")
                recommended_songs = get_songs_from_playlists(
                    conn, playlist_ids)

                # Sort by count in descending order
                sorted_recommended_songs = sorted(
                    recommended_songs.items(), key=lambda x: x[1], reverse=True)

                # Track song count per artist
                artist_song_count = defaultdict(int)
                k = 1
                existing_songs = {}

                for recommended_song_id, count in sorted_recommended_songs:
                    song_recommendation_info = get_song_info(
                        conn, recommended_song_id)
                    if song_recommendation_info:  # Ensure the song exists
                        if not is_similar_song(song_recommendation_info, input_songs):
                            # Artist name from get_song_info
                            artist_name = song_recommendation_info[3]
                            # Allow only 2 songs per artist
                            if artist_song_count[artist_name] < 2:
                                formatted_recommendation = format_song_info(
                                    song_recommendation_info, count)
                                file.write(
                                    f"{k}. {formatted_recommendation}\n")
                                # Increment the count for the artist
                                artist_song_count[artist_name] += 1
                                k += 1
                                existing_songs[recommended_song_id] = {
                                    'song_name': song_recommendation_info[1],
                                    'artist_name': artist_name
                                }
            file.write('\n')

    conn.close()
    print('Result for', MODEL, 'stored at', OUTPUT_PATH)


if __name__ == "__main__":
    ids = ['3wlLknnMtD8yZ0pCtCeeK4',
           '0KpWiHVmIFDTvai20likX4', '30Z12rJpW0M0u8HMFpigTB']
    cf(ids)
