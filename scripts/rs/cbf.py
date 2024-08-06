import sqlite3
import configparser

# Read configuration file
config = configparser.ConfigParser()
config.read('config.cfg')

MODEL = 'Content-based Filtering'
DB = config['rs']['db_path']
OUTPUT_PATH = config['rs']['cbf_output']
N_RESULT = int(config['rs']['n_result'])


def get_song_info(conn, song_id):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT s.song_id, s.song_name, s.artist_ids, a.artist_name, a.artist_genres,
               s.acousticness, s.danceability, s.energy, s.instrumentalness,
               s.key, s.liveness, s.loudness, s.mode, s.speechiness,
               s.tempo, s.time_signature, s.valence
        FROM songs s
        JOIN artists a ON s.artist_ids = a.artist_id
        WHERE s.song_id = ?
    """, (song_id,))
    return cursor.fetchone()


def read_inputted_ids(ids, conn):
    song_info_list = []
    for song_id in ids:
        song_info = get_song_info(conn, song_id)
        if song_info:
            song_info_list.append(song_info)
    return song_info_list


def cbf(ids):
    conn = sqlite3.connect(DB)
    songs_info = read_inputted_ids(ids, conn)

    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        f.write('\nINPUTTED IDS\n')
        for song_info in songs_info:
            (song_id, song_name, artist_ids, artist_name, artist_genres,
             acousticness, danceability, energy, instrumentalness,
             key, liveness, loudness, mode, speechiness,
             tempo, time_signature, valence) = song_info

            song_url = f"https://open.spotify.com/track/{song_id}"
            line = (f"{song_url} {artist_name} - {song_name} | "
                    f"Genres: {artist_genres} | "
                    f"acousticness: {acousticness}, "
                    f"danceability: {danceability}, "
                    f"energy: {energy}, "
                    f"instrumentalness: {instrumentalness}, "
                    f"key: {key}, "
                    f"liveness: {liveness}, "
                    f"loudness: {loudness}, "
                    f"mode: {mode}, "
                    f"speechiness: {speechiness}, "
                    f"tempo: {tempo}, "
                    f"time_signature: {time_signature}, "
                    f"valence: {valence}\n")
            f.write(line)

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
