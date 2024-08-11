import sqlite3
import configparser
from collections import defaultdict

# Read configuration file
config = configparser.ConfigParser()
config.read('config.cfg')

MODEL = 'Collaborative Filtering + Content-based Filtering'
DB = config['rs']['db_path']
OUTPUT_PATH = config['rs']['cf_cbf_output']


def get_song_info(cursor, song_id):
    cursor.execute("""
        SELECT s.song_id, s.song_name, s.artist_ids, a.artist_name, a.artist_genres
        FROM songs s
        JOIN artists a ON a.artist_id = (
            SELECT substr(s.artist_ids, 1, instr(s.artist_ids || ',', ',') - 1)
        )
        WHERE s.song_id = ?
    """, (song_id,))
    return cursor.fetchone()


def get_audio_features(cursor, song_id):
    cursor.execute("""
        SELECT danceability, energy, key, loudness, mode, speechiness, acousticness, instrumentalness, liveness, valence, tempo
        FROM audio_features
        WHERE song_id = ?
    """, (song_id,))
    return cursor.fetchone()


def read_inputted_ids(cursor, ids):
    cursor.execute("""
        SELECT s.song_id, s.song_name, s.artist_ids, a.artist_name, a.artist_genres
        FROM songs s
        JOIN artists a ON a.artist_id = (
            SELECT substr(s.artist_ids, 1, instr(s.artist_ids || ',', ',') - 1)
        )
        WHERE s.song_id IN ({})
    """.format(','.join('?' for _ in ids)), ids)

    return cursor.fetchall()


def get_related_playlists(cursor, artist_name):
    cursor.execute("""
        SELECT p.playlist_id, p.playlist_creator_id, p.playlist_top_genres, p.playlist_items
        FROM playlists p
    """)
    playlists = cursor.fetchall()

    related_playlists = []
    for playlist_id, playlist_creator_id, playlist_top_genres, playlist_items in playlists:
        playlist_items_list = playlist_items.split(',')

        # Find playlists that contain songs by the specific artist
        artist_names = set()
        for song_id in playlist_items_list:
            song_info = get_song_info(cursor, song_id)
            if song_info and song_info[3] == artist_name:
                artist_names.add(song_info[3])

        if artist_names:
            related_playlists.append(
                (playlist_id, playlist_creator_id,
                 playlist_top_genres, playlist_items_list)
            )
    return related_playlists


def extract_songs_from_playlists(related_playlists, cursor, inputted_ids, inputted_songs):
    song_count = defaultdict(int)
    song_id_map = {}

    for playlist_id, playlist_creator_id, playlist_top_genres, playlist_items in related_playlists:
        for song_id in playlist_items:
            song_info = get_song_info(cursor, song_id)
            if song_info:
                song_name, artist_name = song_info[1], song_info[3]

                # Skip variations of the input songs
                if (song_id not in inputted_ids) and (song_name, artist_name) not in inputted_songs:
                    # Accumulate count for songs with the same name and artist
                    song_count[(song_name, artist_name)] += 1
                    # Store one of the song IDs for this song
                    if (song_name, artist_name) not in song_id_map:
                        song_id_map[(song_name, artist_name)] = song_id

    return song_count, song_id_map


def cf_cbf(ids):
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    # 1. INPUTTED IDS
    songs_info = read_inputted_ids(cursor, ids)
    inputted_ids = {song_id for song_id, *_ in songs_info}
    inputted_songs = {(song_name, artist_name) for song_id, song_name,
                      artist_ids, artist_name, artist_genres in songs_info}

    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        f.write('\nINPUTTED IDS\n')
        for idx, (song_id, song_name, artist_ids, artist_name, artist_genres) in enumerate(songs_info, 1):
            f.write(f"{idx}. https://open.spotify.com/track/{song_id} {
                    artist_name} - {song_name} | Genre: {artist_genres}\n")

        # 2. RELATED PLAYLISTS
        f.write('\nRELATED PLAYLISTS\n')
        for idx, (song_id, song_name, artist_ids, artist_name, artist_genres) in enumerate(songs_info, 1):
            f.write(f"\nFor Input Song: {artist_name} - {song_name}\n")
            related_playlists = get_related_playlists(cursor, artist_name)
            if not related_playlists:
                f.write("No related playlists found.\n")
            else:
                for playlist_idx, (playlist_id, playlist_creator_id, playlist_top_genres, playlist_items) in enumerate(related_playlists, 1):
                    f.write(f"{playlist_idx}. https://open.spotify.com/playlist/{playlist_id} by https://open.spotify.com/user/{
                            playlist_creator_id}, Top Genres: {playlist_top_genres}, Items: {', '.join(playlist_items)}\n")

        # 3. SONG RECOMMENDATION
        f.write('\nSONG RECOMMENDATION\n')
        for idx, (song_id, song_name, artist_ids, artist_name, artist_genres) in enumerate(songs_info, 1):
            f.write(f"\nRecommendations for Input Song: {
                    artist_name} - {song_name}\n")
            related_playlists = get_related_playlists(cursor, artist_name)
            song_count, song_id_map = extract_songs_from_playlists(
                related_playlists, cursor, inputted_ids, inputted_songs)

            if not song_count:
                f.write("No song recommendations found.\n")
            else:
                sorted_songs = sorted(song_count.items(),
                                      key=lambda x: x[1], reverse=True)
                artist_song_count = {}  # Dictionary to track song counts per artist
                for rec_idx, ((rec_song_name, rec_artist_name), count) in enumerate(sorted_songs, 1):
                    if rec_artist_name not in artist_song_count:
                        artist_song_count[rec_artist_name] = 0
                    if artist_song_count[rec_artist_name] < 2:
                        # Retrieve the stored song ID from song_id_map
                        rec_song_id = song_id_map[(
                            rec_song_name, rec_artist_name)]

                        # Get audio features
                        audio_features = get_audio_features(
                            cursor, rec_song_id)
                        if audio_features:
                            features_str = ', '.join([f"{feat}: {val:.2f}" for feat, val in zip(
                                ['Danceability', 'Energy', 'Key', 'Loudness', 'Mode', 'Speechiness', 'Acousticness', 'Instrumentalness', 'Liveness', 'Valence', 'Tempo'], audio_features)])
                        else:
                            features_str = "No audio features available"

                        f.write(f"{rec_idx}. https://open.spotify.com/track/{rec_song_id} {
                                rec_artist_name} - {rec_song_name} | Count: {count} | Features: {features_str}\n")
                        artist_song_count[rec_artist_name] += 1

    conn.close()
    print(f'Result for {MODEL} stored at {OUTPUT_PATH}')


if __name__ == "__main__":
    ids = ['6EIMUjQ7Q8Zr2VtIUik4He',
           '30Z12rJpW0M0u8HMFpigTB', '3wlLknnMtD8yZ0pCtCeeK4']
    cf_cbf(ids)
