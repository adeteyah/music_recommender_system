import sqlite3
import configparser

# Read configuration file
config = configparser.ConfigParser()
config.read('config.cfg')

MODEL = 'Content-based Filtering'
DB = config['rs']['db_path']
OUTPUT_PATH = config['rs']['cbf_output']
N_RESULT = int(config['rs']['cbf_n_result'])

# Extract features to use from config
CBF_FEATURES = config['rs']['cbf_features'].split(',')


def get_song_info(conn, song_id):
    cursor = conn.cursor()
    features_select = ', '.join(f's.{feature}' for feature in CBF_FEATURES)
    cursor.execute(f"""
        SELECT s.song_id, s.song_name, s.artist_ids, a.artist_name, a.artist_genres,
               {features_select}
        FROM songs s
        JOIN artists a ON s.artist_ids = a.artist_id
        WHERE s.song_id = ?
    """, (song_id,))
    return cursor.fetchone()


def read_inputted_ids(ids, conn):
    songs_info = []
    for song_id in ids:
        song_info = get_song_info(conn, song_id)
        if song_info:
            songs_info.append(song_info)
    return songs_info


def cbf(ids):
    conn = sqlite3.connect(DB)
    songs_info = read_inputted_ids(ids, conn)

    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        for index, song in enumerate(songs_info, start=1):
            song_id, song_name, artist_id, artist_name, artist_genres, *features = song

            f.write(f"{index}. {
                    artist_name} - {song_name} https://open.spotify.com/track/{song_id}\n")
            feature_lines = []
            for feature in CBF_FEATURES:
                feature_value = features[CBF_FEATURES.index(feature)]
                feature_lines.append(
                    f"{feature.capitalize()}: {feature_value}")
            f.write(", ".join(feature_lines) + "\n")
            f.write(f"Genres: {artist_genres}\n\n")

    print('Result for', MODEL, 'stored at', OUTPUT_PATH)


if __name__ == "__main__":
    ids = [
        '1BxfuPKGuaTgP7aM0Bbdwr',
        '4xqrdfXkTW4T0RauPLv3WA',
        '7JIuqL4ZqkpfGKQhYlrirs',
        '5dTHtzHFPyi8TlTtzoz1J9',
        '4cluDES4hQEUhmXj6TXkSo',
    ]
    cbf(ids)
