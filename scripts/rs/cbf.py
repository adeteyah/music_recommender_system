import sqlite3
import configparser

# Read configuration file
config = configparser.ConfigParser()
config.read('config.cfg')

MODEL = 'Content-based Filtering'
DB = config['rs']['db_path']
OUTPUT_PATH = config['rs']['cbf_output']
N_RESULT = int(config['rs']['n_result'])
CBF_FEATURES = config['rs']['cbf_features'].split(', ')


def get_song_info(conn, song_id, features):
    features_sql = ', '.join(features)
    query = f"""
        SELECT s.song_id, s.song_name, s.artist_ids, a.artist_name, a.artist_genres,
               {features_sql}
        FROM songs s
        JOIN artists a ON s.artist_ids = a.artist_id
        WHERE s.song_id = ?
    """
    cursor = conn.cursor()
    cursor.execute(query, (song_id,))
    return cursor.fetchone()


def read_inputted_ids(ids, conn, features):
    song_info_list = []
    for song_id in ids:
        song_info = get_song_info(conn, song_id, features)
        if song_info:
            song_info_list.append(song_info)
    return song_info_list


def cbf(ids):
    conn = sqlite3.connect(DB)
    features = ['s.' + feature for feature in CBF_FEATURES]
    songs_info = read_inputted_ids(ids, conn, features)

    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        f.write('INPUTTED IDS\n')
        for idx, song_info in enumerate(songs_info, start=1):
            base_info = song_info[:5]
            audio_features = song_info[5:]

            song_id, song_name, artist_ids, artist_name, artist_genres = base_info
            song_url = f"https://open.spotify.com/track/{song_id}"
            features_str = ', '.join(
                [f"{CBF_FEATURES[i]}: {audio_features[i]}" for i in range(len(audio_features))])

            line = (f"{idx}. {song_url} {artist_name} - {song_name} | "
                    f"Genres: {artist_genres} | "
                    f"{features_str}\n")
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
