import sqlite3
import configparser

# Read configuration file
config = configparser.ConfigParser()
config.read('config.cfg')

MODEL = 'Content-based Filtering'
DB = config['rs']['db_path']
OUTPUT_PATH = config['rs']['cbf_output']


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
        SELECT p.playlist_id, p.playlist_creator_id
        FROM playlists p
        WHERE instr(p.playlist_items, ?) > 0
    """, (song_id,))
    return cursor.fetchall()


def format_song_info(song_info):
    song_id, song_name, artist_ids, artist_name, artist_genres, acousticness, danceability, energy, instrumentalness, key, liveness, loudness, mode, speechiness, tempo, time_signature, valence = song_info

    return f"https://open.spotify.com/track/{song_id} {artist_name} - {song_name} | Genre: {artist_genres} | Acousticness: {acousticness}, Danceability: {danceability}, Energy: {energy}, Instrumentalness: {instrumentalness}, Key: {key}, Liveness: {liveness}, Loudness: {loudness}, Mode: {mode}, Speechiness: {speechiness}, Tempo: {tempo}, Time Signature: {time_signature}, Valence: {valence}"


def format_playlist_relations(playlists):
    if not playlists:
        return "No relations found."
    return "\n".join(f"{playlist_id} by {playlist_creator_id}" for playlist_id, playlist_creator_id in playlists)


def read_inputted_ids(ids, conn):
    songs_info = [get_song_info(conn, song_id) for song_id in ids]
    playlists_info = {}
    for song_info in songs_info:
        song_id = song_info[0]
        playlists_info[song_id] = get_playlists_for_song(conn, song_id)
    return songs_info, playlists_info


def cbf(ids):
    conn = sqlite3.connect(DB)
    songs_info, playlists_info = read_inputted_ids(ids, conn)

    with open(OUTPUT_PATH, 'w', encoding='utf-8') as file:
        file.write('INPUTTED IDS\n')
        for i, song_info in enumerate(songs_info, 1):
            formatted_info = format_song_info(song_info)
            file.write(f"{i}. {formatted_info}\n")
            file.write("RELATIONS\n")
            song_id = song_info[0]
            relations = format_playlist_relations(playlists_info[song_id])
            file.write(f"{relations}\n\n")

    conn.close()
    print('Result for', MODEL, 'stored at', OUTPUT_PATH)


if __name__ == "__main__":
    ids = [
        '1BxfuPKGuaTgP7aM0Bbdwr',
        '4xqrdfXkTW4T0RauPLv3WA',
        '7JIuqL4ZqkpfGKQhYlrirs',
        '5dTHtzHFPyi8TlTtzoz1J9',
    ]
    cbf(ids)
