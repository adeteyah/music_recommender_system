import sqlite3
import configparser

# Read configuration file
config = configparser.ConfigParser()
config.read('config.cfg')

MODEL = 'Content-based Filtering'
DB = config['rs']['db_path']
OUTPUT_PATH = config['rs']['cbf_output']
CBF_FEATURES = config['rs']['cbf_features'].split(', ')
REAL_BOUND_VAL = float(config['rs']['cbf_real_bound'])
INTEGER_BOUND_VAL = int(config['rs']['cbf_integer_bound'])

# Define which features are integers
INTEGER_FEATURES = {'tempo', 'time_signature', 'key', 'mode'}


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


def calculate_similarity(song_features, input_features):
    return sum(abs(song_feature - input_feature) for song_feature, input_feature in zip(song_features, input_features))


def get_similar_audio_features(conn, features, input_audio_features, inputted_ids, inputted_songs):
    feature_conditions = [
        f"{feature.split('.')[-1]} BETWEEN {input_audio_features[i] - (REAL_BOUND_VAL if feature.split('.')[-1] not in INTEGER_FEATURES else INTEGER_BOUND_VAL)
                                            } AND {input_audio_features[i] + (REAL_BOUND_VAL if feature.split('.')[-1] not in INTEGER_FEATURES else INTEGER_BOUND_VAL)}"
        for i, feature in enumerate(features)
    ]
    conditions_sql = ' AND '.join(feature_conditions)

    features_sql = ', '.join(features)
    query = f"""
        SELECT s.song_id, s.song_name, s.artist_ids, a.artist_name, a.artist_genres,
               {features_sql}
        FROM songs s
        JOIN artists a ON s.artist_ids = a.artist_id
        WHERE {conditions_sql}
    """
    cursor = conn.cursor()
    cursor.execute(query)
    songs = cursor.fetchall()

    # Filter out inputted IDs and ensure only one song per artist, excluding same artist and song names
    seen_artists = set()
    seen_song_artist_names = {(info[3], info[1]) for info in inputted_songs}
    filtered_songs = [
        song for song in songs
        if song[0] not in inputted_ids and (song[3], song[1]) not in seen_song_artist_names and song[2] not in seen_artists
    ]
    for song in filtered_songs:
        seen_artists.add(song[2])

    # Sort songs by similarity
    filtered_songs.sort(key=lambda song: calculate_similarity(
        song[5:], input_audio_features))
    return filtered_songs


def cbf(ids):
    conn = sqlite3.connect(DB)
    features = ['s.' + feature for feature in CBF_FEATURES]
    songs_info = [get_song_info(conn, song_id, features) for song_id in ids]

    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        f.write('INPUTTED IDS\n')
        input_audio_features_list = []
        inputted_ids_set = set(ids)

        for idx, song_info in enumerate(songs_info, start=1):
            if not song_info:
                continue

            base_info = song_info[:5]
            audio_features = song_info[5:]
            input_audio_features_list.append(audio_features)
            song_url = f"https://open.spotify.com/track/{base_info[0]}"
            features_str = ', '.join(
                [f"{CBF_FEATURES[i]}: {audio_features[i]}" for i in range(len(audio_features))])
            line = (f"{idx}. {song_url} {base_info[3]} - {base_info[1]} | "
                    f"Genres: {base_info[4]} | {features_str}\n")
            f.write(line)

        # SIMILAR AUDIO FEATURES
        f.write('\nSIMILAR AUDIO FEATURES\n')
        for input_audio_features, song_info in zip(input_audio_features_list, songs_info):
            header = f"{song_info[3]} - {song_info[1]
                                         } | Genres: {song_info[4]}"
            f.write(f"\n{header}\n")
            similar_songs_info = get_similar_audio_features(
                conn, features, input_audio_features, inputted_ids_set, songs_info)
            for idx, song_info in enumerate(similar_songs_info, start=1):
                base_info = song_info[:5]
                audio_features = song_info[5:]
                song_url = f"https://open.spotify.com/track/{base_info[0]}"
                features_str = ', '.join(
                    [f"{CBF_FEATURES[i]}: {audio_features[i]}" for i in range(len(audio_features))])
                line = (f"{idx}. {song_url} {base_info[3]} - {base_info[1]} | "
                        f"Genres: {base_info[4]} | {features_str}\n")
                f.write(line)

    conn.close()
    print('Result for', MODEL, 'stored at', OUTPUT_PATH)


if __name__ == "__main__":
    ids = ['1yKAqZoi8xWGLCf5vajroL',
           '5VGlqQANWDKJFl0MBG3sg2', '0lP4HYLmvowOKdsQ7CVkuq']
    cbf(ids)
