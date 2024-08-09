import sqlite3
import configparser
import re

# Read configuration file
config = configparser.ConfigParser()
config.read('config.cfg')

MODEL = 'Content-based Filtering'
DB = config['rs']['db_path']
OUTPUT_PATH = config['rs']['cbf_output']
CBF_FEATURES = config['rs']['cbf_features'].split(', ')
REAL_BOUND_VAL = float(config['rs']['cbf_real_bound'])
MODE_BOUND_VAL = int(config['rs']['cbf_mode_bound'])
TIME_SIGNATURE_BOUND_VAL = int(config['rs']['cbf_time_signature_bound'])
TEMPO_BOUND_VAL = float(config['rs']['cbf_tempo_bound'])

# Define specific bound values for features
SEPARATE_BOUNDS = {
    'mode': MODE_BOUND_VAL,
    'time_signature': TIME_SIGNATURE_BOUND_VAL,
    'tempo': TEMPO_BOUND_VAL
}


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


def normalize_song_name(song_name):
    # Normalize song names by removing any parenthetical text (e.g., "(Remastered)", "(Live)", etc.)
    return re.sub(r'\(.*?\)', '', song_name).strip().lower()


def get_similar_audio_features(conn, features, input_audio_features, inputted_ids, inputted_songs):
    feature_conditions = []
    for i, feature in enumerate(features):
        feature_name = feature.split('.')[-1]
        # Use specific bound if defined, else use general bound
        bound_val = SEPARATE_BOUNDS.get(feature_name, REAL_BOUND_VAL)
        lower_bound = input_audio_features[i] - bound_val
        upper_bound = input_audio_features[i] + bound_val
        feature_conditions.append(f"{feature_name} BETWEEN {
                                  lower_bound} AND {upper_bound}")

    conditions_sql = ' AND '.join(feature_conditions)

    # Extract first two genres from input song genres
    input_genres = inputted_songs[0][4].split(',')[:2]  # Take first two genres
    genre_conditions = ' OR '.join(
        [f"a.artist_genres LIKE '%{genre.strip()}%'" for genre in input_genres])

    # Combine feature conditions with genre filtering
    combined_conditions_sql = f"{conditions_sql} AND ({genre_conditions})"

    features_sql = ', '.join(features)
    query = f"""
        SELECT s.song_id, s.song_name, s.artist_ids, a.artist_name, a.artist_genres,
               {features_sql}
        FROM songs s
        JOIN artists a ON s.artist_ids = a.artist_id
        WHERE {combined_conditions_sql}
    """
    cursor = conn.cursor()
    cursor.execute(query)
    songs = cursor.fetchall()

    # Filter out inputted IDs and ensure only one song per artist, excluding same artist and song names
    seen_artists = set()
    seen_song_artist_names = {(normalize_song_name(info[1]), info[3].lower(
    )) for info in inputted_songs}  # (normalized_song_name, artist_name)
    filtered_songs = []
    seen_song_artist_pairs = set()

    for song in songs:
        song_id, song_name, artist_ids, artist_name, artist_genres = song[:5]
        normalized_name = normalize_song_name(song_name)
        artist_name_lower = artist_name.lower()

        if song_id in inputted_ids or (normalized_name, artist_name_lower) in seen_song_artist_names:
            continue

        # Normalize and use case insensitive comparison
        song_artist_pair = (normalized_name, artist_name_lower)
        if song_artist_pair in seen_song_artist_pairs:
            continue

        filtered_songs.append(song)
        seen_artists.add(artist_ids)
        seen_song_artist_pairs.add(song_artist_pair)

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
