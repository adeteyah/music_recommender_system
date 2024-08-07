import sqlite3
import configparser
from collections import Counter

# Read configuration file
config = configparser.ConfigParser()
config.read('config.cfg')

MODEL = 'Content-based Filtering - Collaborative Filtering'
DB = config['rs']['db_path']
OUTPUT_PATH = config['rs']['cbf_cf_output']
N_RESULT = int(config['rs']['n_result'])
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


def read_inputted_ids(ids, conn, features):
    song_info_list = []
    for song_id in ids:
        song_info = get_song_info(conn, song_id, features)
        if song_info:
            song_info_list.append(song_info)
    return song_info_list


def calculate_similarity(song_features, input_features):
    return sum(abs(song_feature - input_feature) for song_feature, input_feature in zip(song_features, input_features))


def get_similar_audio_features(conn, features, input_audio_features, inputted_ids, inputted_songs):
    feature_conditions = []
    for i, feature in enumerate(features):
        feature_name = feature.split('.')[-1]
        lower_bound = input_audio_features[i] - \
            REAL_BOUND_VAL if feature_name not in INTEGER_FEATURES else input_audio_features[
                i] - INTEGER_BOUND_VAL
        upper_bound = input_audio_features[i] + \
            REAL_BOUND_VAL if feature_name not in INTEGER_FEATURES else input_audio_features[
                i] + INTEGER_BOUND_VAL
        feature_conditions.append(f"{feature_name} BETWEEN {
                                  lower_bound} AND {upper_bound}")
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
    filtered_songs = []
    seen_artists = set()
    seen_song_artist_names = {(info[3], info[1]) for info in inputted_songs}
    for song in songs:
        if song[0] in inputted_ids or (song[3], song[1]) in seen_song_artist_names:
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


def get_playlists_containing_song(conn, song_id):
    query = """
        SELECT playlist_id
        FROM playlists
        WHERE playlist_items LIKE ?
    """
    cursor = conn.cursor()
    cursor.execute(query, ('%' + song_id + '%',))
    return [row[0] for row in cursor.fetchall()]


def get_songs_from_playlists(conn, playlist_ids, features):
    if not playlist_ids:
        return []

    features_sql = ', '.join(features)
    query = f"""
        SELECT s.song_id, s.song_name, s.artist_ids, a.artist_name, a.artist_genres,
               {features_sql}
        FROM playlists p
        JOIN songs s ON p.playlist_items LIKE '%' || s.song_id || '%'
        JOIN artists a ON s.artist_ids = a.artist_id
        WHERE p.playlist_id IN ({','.join(['?' for _ in playlist_ids])})
    """
    cursor = conn.cursor()
    cursor.execute(query, playlist_ids)
    return cursor.fetchall()


def cbf_cf(ids):
    conn = sqlite3.connect(DB)
    features = ['s.' + feature for feature in CBF_FEATURES]
    songs_info = read_inputted_ids(ids, conn, features)

    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        f.write('INPUTTED IDS\n')
        input_audio_features_list = []
        inputted_ids_set = set(ids)
        song_headers = []
        all_playlists = {song_id: [] for song_id in ids}

        for idx, song_info in enumerate(songs_info, start=1):
            # song_id, song_name, artist_ids, artist_name, artist_genres
            base_info = song_info[:5]
            audio_features = song_info[5:]
            input_audio_features_list.append(audio_features)
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
        similar_song_playlists = {song_id: [] for song_id in ids}

        for input_idx, (input_audio_features, header) in enumerate(zip(input_audio_features_list, song_headers), start=1):
            f.write(f"\n{header}\n")
            similar_songs_info = get_similar_audio_features(
                conn, features, input_audio_features, inputted_ids_set, songs_info)
            for song_idx, song_info in enumerate(similar_songs_info[:N_RESULT], start=1):
                # song_id, song_name, artist_ids, artist_name, artist_genres
                base_info = song_info[:5]
                audio_features = song_info[5:]

                song_id, song_name, artist_ids, artist_name, artist_genres = base_info
                song_url = f"https://open.spotify.com/track/{song_id}"
                features_str = ', '.join(
                    [f"{CBF_FEATURES[i]}: {audio_features[i]}" for i in range(len(audio_features))])

                line = (f"{song_idx}. {song_url} {artist_name} - {song_name} | "
                        f"Genres: {artist_genres} | "
                        f"{features_str}\n")
                f.write(line)

                # Find playlists containing this song
                playlists = get_playlists_containing_song(conn, song_id)
                if playlists:
                    f.write("Playlists containing this song:\n")
                    for playlist in playlists:
                        f.write(f"- {playlist}\n")
                    similar_song_playlists[ids[input_idx-1]].append(playlists)

        # Collect all playlists containing similar songs for each input ID
        f.write('\nALL PLAYLISTS CONTAINING SIMILAR SONGS\n')
        for idx, song_id in enumerate(ids, start=1):
            f.write(f"\nInput ID {idx} ({song_id}):\n")
            for song_idx, playlists in enumerate(similar_song_playlists[song_id], start=1):
                if playlists:
                    playlist_str = ', '.join(playlists)
                    f.write(f"{song_idx}. {playlist_str}\n")

        # SONGS RECOMMENDATIONS
        f.write('\nSONGS RECOMMENDATIONS\n')
        for idx, song_id in enumerate(ids, start=1):
            f.write(f"\nInput ID {idx} ({song_id}):\n")
            all_playlist_ids = [
                playlist_id for sublist in similar_song_playlists[song_id] for playlist_id in sublist]
            recommended_songs = get_songs_from_playlists(
                conn, all_playlist_ids, features)

            song_counter = Counter()
            song_details = {}
            for song_info in recommended_songs:
                base_info = song_info[:5]
                song_id, song_name, artist_ids, artist_name, artist_genres = base_info
                song_key = (artist_name, song_name, artist_genres)
                song_counter[song_key] += 1
                song_details[song_key] = song_info

            for song_idx, (song_key, count) in enumerate(song_counter.items(), start=1):
                artist_name, song_name, artist_genres = song_key
                audio_features = song_details[song_key][5:]
                features_str = ', '.join(
                    [f"{CBF_FEATURES[i]}: {audio_features[i]}" for i in range(len(audio_features))])
                line = (f"{song_idx}. {artist_name} - {song_name} | "
                        f"Genres: {artist_genres} | "
                        f"Count: {count} | "
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
    cbf_cf(ids)
