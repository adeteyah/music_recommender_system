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


def get_similar_audio_features(conn, features, input_audio_features, inputted_ids, input_genres):
    feature_conditions = []
    for i, feature in enumerate(features):
        feature = feature.split('.')[-1]
        lower_bound = input_audio_features[i] - 0.1
        upper_bound = input_audio_features[i] + 0.1
        feature_conditions.append(
            f"{feature} BETWEEN {lower_bound} AND {upper_bound}")
    conditions_sql = ' AND '.join(feature_conditions)

    genre_conditions = ' OR '.join(
        [f"a.artist_genres LIKE '%{genre}%'" for genre in input_genres])

    features_sql = ', '.join(features)
    query = f"""
        SELECT s.song_id, s.song_name, s.artist_ids, a.artist_name, a.artist_genres,
               {features_sql}
        FROM songs s
        JOIN artists a ON s.artist_ids = a.artist_id
        WHERE ({conditions_sql}) AND ({genre_conditions})
    """
    cursor = conn.cursor()
    cursor.execute(query)
    songs = cursor.fetchall()

    # Filter out inputted IDs and ensure only one song per artist
    filtered_songs = []
    seen_artists = set()
    for song in songs:
        if song[0] in inputted_ids:
            continue
        artist_id = song[2]
        if artist_id in seen_artists:
            continue
        seen_artists.add(artist_id)
        filtered_songs.append(song)

    # Sort songs by similarity
    filtered_songs.sort(key=lambda song: calculate_similarity(
        song[5:], input_audio_features))
    return filtered_songs


def read_inputted_ids(ids, conn, features):
    song_info_list = []
    for song_id in ids:
        song_info = get_song_info(conn, song_id, features)
        if song_info:
            song_info_list.append(song_info)
    return song_info_list


def calculate_similarity(song_features, input_features):
    return sum(abs(song_feature - input_feature) for song_feature, input_feature in zip(song_features, input_features))


def cbf(ids):
    conn = sqlite3.connect(DB)
    features = ['s.' + feature for feature in CBF_FEATURES]
    songs_info = read_inputted_ids(ids, conn, features)

    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        f.write('INPUTTED IDS\n')
        input_audio_features_list = []
        inputted_ids_set = set(ids)
        song_headers = []
        input_genres_list = []
        for idx, song_info in enumerate(songs_info, start=1):
            # song_id, song_name, artist_ids, artist_name, artist_genres
            base_info = song_info[:5]
            audio_features = song_info[5:]
            input_audio_features_list.append(audio_features)
            input_genres_list.append(song_info[4].split(', '))
            song_headers.append(
                f"{song_info[3]} - {song_info[1]} | Genres: {song_info[4]}")

            song_id, song_name, artist_ids, artist_name, artist_genres = base_info
            song_url = f"https://open.spotify.com/track/{song_id}"
            features_str = ', '.join(
                [f"{CBF_FEATURES[i]}: {audio_features[i]}" for i in range(len(audio_features))])

            line = (f"{idx}. {song_url} {artist_name} - {song_name} | "
                    f"Genres: {artist_genres} | "
                    f"{features_str}\n")
            f.write(line)

        # SIMILAR AUDIO FEATURES
        f.write('\nSIMILAR AUDIO FEATURES\n')
        for input_audio_features, header, input_genres in zip(input_audio_features_list, song_headers, input_genres_list):
            f.write(f"\n{header}\n")
            similar_songs_info = get_similar_audio_features(
                conn, features, input_audio_features, inputted_ids_set, input_genres)
            for idx, song_info in enumerate(similar_songs_info[:N_RESULT], start=1):
                # song_id, song_name, artist_ids, artist_name, artist_genres
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
