import sqlite3
import configparser
import re

# Read configuration file
config = configparser.ConfigParser()
config.read('config.cfg')

MODEL = 'Content-based Filtering'
DB = config['rs']['db_path']
OUTPUT_PATH = config['rs']['cbf_output']
CBF_FEATURES = config['hp']['cbf_features'].split(', ')
REAL_BOUND_VAL = float(config['hp']['cbf_real_bound'])
MODE_BOUND_VAL = int(config['hp']['cbf_mode_bound'])
TIME_SIGNATURE_BOUND_VAL = int(config['hp']['cbf_time_signature_bound'])
TEMPO_BOUND_VAL = float(config['hp']['cbf_tempo_bound'])
SONGS_PER_ARTIST = int(config['hp']['songs_per_artist'])

# Define specific bound values for features
SEPARATE_BOUNDS = {
    'mode': MODE_BOUND_VAL,
    'time_signature': TIME_SIGNATURE_BOUND_VAL,
    'tempo': TEMPO_BOUND_VAL
}


def get_song_info(conn, song_id, features):
    features_sql = ', '.join(features)
    query = f"""
        SELECT s.song_id, s.song_name, s.artist_ids, {features_sql}
        FROM songs s
        WHERE s.song_id = ?
    """
    cursor = conn.cursor()
    cursor.execute(query, (song_id,))
    return cursor.fetchone()


def get_artist_info(conn, artist_id):
    query = f"""
        SELECT artist_name, artist_genres
        FROM artists
        WHERE artist_id = ?
    """
    cursor = conn.cursor()
    cursor.execute(query, (artist_id,))
    return cursor.fetchone()


def calculate_similarity(song_features, input_features):
    return sum(abs(song_feature - input_feature) for song_feature, input_feature in zip(song_features, input_features))


def normalize_song_name(song_name):
    return re.sub(r'\(.*?\)', '', song_name).strip().lower()


def get_similar_audio_features(conn, features, input_audio_features, inputted_ids, inputted_songs, mandatory_genres):
    feature_conditions = []
    for i, feature in enumerate(features):
        feature_name = feature.split('.')[-1]
        bound_val = SEPARATE_BOUNDS.get(feature_name, REAL_BOUND_VAL)
        lower_bound = input_audio_features[i] - bound_val
        upper_bound = input_audio_features[i] + bound_val
        feature_conditions.append(f"{feature_name} BETWEEN {
                                  lower_bound} AND {upper_bound}")

    conditions_sql = ' AND '.join(feature_conditions)

    # Ensure genre conditions are combined with OR logic
    genre_conditions = ' OR '.join(
        [f"a.artist_genres LIKE '%{genre.strip()}%'" for genre in mandatory_genres])

    combined_conditions_sql = f"{conditions_sql} AND ({genre_conditions})"
    features_sql = ', '.join(features)

    query = f"""
        SELECT s.song_id, s.song_name, s.artist_ids, {features_sql}
        FROM songs s
        JOIN artists a ON s.artist_ids = a.artist_id
        WHERE {combined_conditions_sql}
    """
    cursor = conn.cursor()
    cursor.execute(query)
    songs = cursor.fetchall()

    seen_artists = {}
    seen_song_artist_names = {(normalize_song_name(
        info[1]), info[2].lower()) for info in inputted_songs}
    filtered_songs = []
    seen_song_artist_pairs = set()

    for song in songs:
        song_id, song_name, artist_ids = song[:3]
        normalized_name = normalize_song_name(song_name)
        if song_id in inputted_ids or (normalized_name, artist_ids) in seen_song_artist_names:
            continue

        song_artist_pair = (normalized_name, artist_ids)
        if song_artist_pair in seen_song_artist_pairs:
            continue

        if artist_ids in seen_artists:
            if seen_artists[artist_ids] >= SONGS_PER_ARTIST:
                continue
            seen_artists[artist_ids] += 1
        else:
            seen_artists[artist_ids] = 1

        filtered_songs.append(song)
        seen_song_artist_pairs.add(song_artist_pair)

    filtered_songs.sort(key=lambda song: calculate_similarity(
        song[3:], input_audio_features))
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

            song_id, song_name, artist_ids, *audio_features = song_info
            input_audio_features_list.append(audio_features)
            song_url = f"https://open.spotify.com/track/{song_id}"
            features_str = ', '.join(
                [f"{CBF_FEATURES[i]}: {audio_features[i]}" for i in range(len(audio_features))])

            artist_info = get_artist_info(conn, artist_ids.split(
                ',')[0]) if artist_ids else ('N/A', 'N/A')
            artist_name = artist_info[0] if artist_info[0] else 'N/A'
            genres = artist_info[1] if artist_info[1] else 'N/A'

            line = (f"{idx}. {song_url} {artist_name} - {song_name if song_name else 'N/A'} | "
                    f"Genres: {genres} | {features_str}\n")
            f.write(line)

        f.write('\nSONGS RECOMMENDATION\n')
        for input_audio_features, song_info in zip(input_audio_features_list, songs_info):
            artist_info = get_artist_info(conn, song_info[2].split(
                ',')[0]) if song_info[2] else ('N/A', 'N/A')
            artist_name = artist_info[0] if artist_info[0] else 'N/A'
            genres = artist_info[1] if artist_info[1] else 'N/A'

            header = f"{artist_name} - {song_info[1]} | Genres: {genres}"
            f.write(f"\n{header}\n")

            # Split the genres and pass them to the function
            mandatory_genres = genres.split(',') if genres != 'N/A' else []
            if mandatory_genres:
                similar_songs_info = get_similar_audio_features(
                    conn, features, input_audio_features, inputted_ids_set, songs_info, mandatory_genres)
                for idx, song in enumerate(similar_songs_info, start=1):
                    song_id, song_name, artist_ids, *audio_features = song
                    song_url = f"https://open.spotify.com/track/{song_id}"
                    features_str = ', '.join(
                        [f"{CBF_FEATURES[i]}: {audio_features[i]}" for i in range(len(audio_features))])

                    artist_info = get_artist_info(conn, artist_ids.split(
                        ',')[0]) if artist_ids else ('N/A', 'N/A')
                    artist_name = artist_info[0] if artist_info[0] else 'N/A'
                    genres = artist_info[1] if artist_info[1] else 'N/A'

                    line = (f"{idx}. {song_url} {artist_name} - {song_name if song_name else 'N/A'} | "
                            f"Genres: {genres} | {features_str}\n")
                    f.write(line)

    conn.close()
    print('Result for', MODEL, 'stored at', OUTPUT_PATH)


if __name__ == "__main__":
    ids = ['3wlLknnMtD8yZ0pCtCeeK4', '6EIMUjQ7Q8Zr2VtIUik4He',
           '30Z12rJpW0M0u8HMFpigTB']
    cbf(ids)
