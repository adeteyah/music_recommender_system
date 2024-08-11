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
    cursor.execute("""
        SELECT s.song_id, s.song_name, s.artist_ids, a.artist_name, a.artist_genres,
               s.acousticness, s.danceability, s.energy, s.instrumentalness, 
               s.key, s.liveness, s.loudness, s.mode, s.speechiness, s.tempo, 
               s.time_signature, s.valence
        FROM songs s
        JOIN artists a ON s.artist_ids = a.artist_id
        WHERE s.song_id = ?
    """, (song_id,))
    return cursor.fetchone()


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


def format_song_info(song_info, count):
    song_id, song_name, artist_ids, artist_name, artist_genres, acousticness, danceability, energy, instrumentalness, key, liveness, loudness, mode, speechiness, tempo, time_signature, valence = song_info
    return f"https://open.spotify.com/track/{song_id} {artist_name} - {song_name} | Genre: {artist_genres} | Acousticness: {acousticness}, Danceability: {danceability}, Energy: {energy}, Instrumentalness: {instrumentalness}, Key: {key}, Liveness: {liveness}, Loudness: {loudness}, Mode: {mode}, Speechiness: {speechiness}, Tempo: {tempo}, Time Signature: {time_signature}, Valence: {valence} | COUNT: {count}"


def read_inputted_ids(ids, conn):
    return [get_song_info(conn, song_id) for song_id in ids]


def cf(ids):
    conn = sqlite3.connect(DB)
    songs_info = read_inputted_ids(ids, conn)

    with open(OUTPUT_PATH, 'w', encoding='utf-8') as file:
        file.write('INPUTTED IDS\n')
        for i, song_info in enumerate(songs_info, 1):
            formatted_info = format_song_info(song_info, count=1)
            file.write(f"{i}. {formatted_info}\n")

            # Add FOUND IN section
            file.write(f"\nFOUND IN:\n")
            playlists = get_playlists_for_song(conn, song_info[0])
            playlist_ids = [playlist_id for playlist_id, _, _ in playlists]
            for j, (playlist_id, playlist_creator_id, _) in enumerate(playlists, 1):
                file.write(f"{j}. {playlist_id} by {playlist_creator_id}\n")

            # Add SONGS RECOMMENDATION section
            if playlist_ids:
                file.write(f"\nSONGS RECOMMENDATION\n")
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
                        # Artist name from get_song_info
                        artist_name = song_recommendation_info[3]
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
    ids = [
        '1BxfuPKGuaTgP7aM0Bbdwr',
        '4xqrdfXkTW4T0RauPLv3WA',
        '7JIuqL4ZqkpfGKQhYlrirs',
        '5dTHtzHFPyi8TlTtzoz1J9',
    ]
    cf(ids)
