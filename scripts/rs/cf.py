import sqlite3
import configparser
from collections import Counter

# Read configuration file
config = configparser.ConfigParser()
config.read('config.cfg')

MODEL = 'Collaborative Filtering'
DB = config['rs']['db_path']
OUTPUT_PATH = config['rs']['cf_output']


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


def extract_songs_from_playlists(related_playlists, cursor, inputted_ids):
    song_count = Counter()

    for playlist_id, playlist_creator_id, playlist_top_genres, playlist_items in related_playlists:
        for song_id in playlist_items:
            song_info = get_song_info(cursor, song_id)
            if song_info:
                if song_id in inputted_ids:
                    # Count +2 for same inputted song ID
                    song_count[(song_id, song_info[3], song_info[1])] += 2
                elif song_id not in inputted_ids:
                    song_count[(song_id, song_info[3], song_info[1])
                               ] += 1  # Count +1 for other songs

    return song_count


def cf(ids):
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    # 1. INPUTTED IDS
    songs_info = read_inputted_ids(cursor, ids)
    inputted_ids = {song_id for song_id, *_ in songs_info}
    inputted_songs = {(artist_name, song_name)
                      for _, _, _, artist_name, song_name in songs_info}

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
            song_count = extract_songs_from_playlists(
                related_playlists, cursor, inputted_ids)

            if not song_count:
                f.write("No song recommendations found.\n")
            else:
                sorted_songs = sorted(song_count.items(),
                                      key=lambda x: x[1], reverse=True)
                artist_song_count = {}  # Dictionary to track song counts per artist
                for rec_idx, ((rec_song_id, rec_artist_name, rec_song_name), count) in enumerate(sorted_songs, 1):
                    if (rec_song_id not in inputted_ids and
                        (rec_artist_name, rec_song_name) not in inputted_songs and
                            rec_artist_name not in artist_song_count):
                        artist_song_count[rec_artist_name] = 0
                    if (rec_song_id not in inputted_ids and
                        (rec_artist_name, rec_song_name) not in inputted_songs and
                            artist_song_count[rec_artist_name] < 2):
                        f.write(f"{rec_idx}. https://open.spotify.com/track/{rec_song_id} {
                                rec_artist_name} - {rec_song_name} | Count: {count}\n")
                        artist_song_count[rec_artist_name] += 1

    conn.close()
    print(f'Result for {MODEL} stored at {OUTPUT_PATH}')


if __name__ == "__main__":

    ids = ['6EIMUjQ7Q8Zr2VtIUik4He',
           '30Z12rJpW0M0u8HMFpigTB', '3wlLknnMtD8yZ0pCtCeeK4']
    cf(ids)
