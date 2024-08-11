import sqlite3
import configparser
from collections import defaultdict

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


def cf(ids):
    conn = sqlite3.connect(DB)
    songs_info = read_inputted_ids(ids, conn)

    # Prepare to track excluded songs
    input_song_ids = set(song_info[0] for song_info in songs_info if song_info)
    input_song_titles_artists = {
        (song_info[1], song_info[3]) for song_info in songs_info if song_info}

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
                file.write(f"{j}. https://open.spotify.com/playlist/{
                           playlist_id} by https://open.spotify.com/user/{playlist_creator_id}\n")

            # Add SONGS RECOMMENDATION section with a specific title
            if playlist_ids:
                file.write(f"\nSONGS RECOMMENDATION: {formatted_info}\n")
                recommended_songs = get_songs_from_playlists(
                    conn, playlist_ids)

                # Sort by count in descending order
                sorted_recommended_songs = sorted(
                    recommended_songs.items(), key=lambda x: x[1], reverse=True)

                # Track song count per artist
                artist_song_count = defaultdict(int)
                k = 1
                for recommended_song_id, count in sorted_recommended_songs:
                    song_recommendation_info = get_song_info(
                        conn, recommended_song_id)
                    if song_recommendation_info:  # Ensure the song exists
                        song_title = song_recommendation_info[1]
                        artist_name = song_recommendation_info[3]

                        # Skip songs that are input songs or have the same title and artist as input songs
                        if (recommended_song_id in input_song_ids or
                                (song_title, artist_name) in input_song_titles_artists):
                            continue

                        # Allow only 2 songs per artist
                        if artist_song_count[artist_name] < 2:
                            formatted_recommendation = format_song_info(
                                song_recommendation_info, count)
                            file.write(f"{k}. {formatted_recommendation}\n")
                            # Increment the count for the artist
                            artist_song_count[artist_name] += 1
                            k += 1
            file.write('\n')

    conn.close()
    print('Result for', MODEL, 'stored at', OUTPUT_PATH)


if __name__ == "__main__":
    ids = ['3wlLknnMtD8yZ0pCtCeeK4',
           '0KpWiHVmIFDTvai20likX4', '30Z12rJpW0M0u8HMFpigTB']
    cf(ids)
