import sqlite3
import configparser
from collections import Counter, defaultdict

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
    query = """
        SELECT s.song_id, s.song_name, s.artist_ids, a.artist_name, a.artist_genres
        FROM songs s
        JOIN artists a ON a.artist_id = (
            SELECT substr(s.artist_ids, 1, instr(s.artist_ids || ',', ',') - 1)
        )
        WHERE s.song_id IN ({})
    """.format(','.join('?' for _ in ids))

    cursor.execute(query, ids)
    return cursor.fetchall()


def get_related_playlists(cursor, artist_name, inputted_ids):
    cursor.execute("""
        SELECT p.playlist_id, p.playlist_creator_id, p.playlist_top_genres, p.playlist_items
        FROM playlists p
        WHERE EXISTS (
            SELECT 1 FROM songs s WHERE s.song_id IN ({}) AND instr(p.playlist_items, s.song_id) > 0
        )
        OR p.playlist_items LIKE ?
    """.format(','.join('?' for _ in inputted_ids)), (*inputted_ids, f'%{artist_name}%'))

    return cursor.fetchall()


def extract_songs_from_playlists(related_playlists, cursor, inputted_ids):
    song_count = Counter()

    for playlist_id, playlist_creator_id, playlist_top_genres, playlist_items in related_playlists:
        playlist_items_list = playlist_items.split(',')

        for song_id in playlist_items_list:
            song_info = get_song_info(cursor, song_id)
            if song_info:
                if song_id in inputted_ids:
                    # Count +2 for same inputted song ID
                    song_count[(song_id, song_info[3], song_info[1])] += 2
                else:
                    # Count +1 for other songs
                    song_count[(song_id, song_info[3], song_info[1])] += 1

    return song_count


def cf(ids):
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    # 1. INPUTTED IDS
    songs_info = read_inputted_ids(cursor, ids)
    inputted_ids = {song_id for song_id, *_ in songs_info}

    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        f.write('\nINPUTTED IDS\n')
        for idx, (song_id, song_name, artist_ids, artist_name, artist_genres) in enumerate(songs_info, 1):
            f.write(f"{idx}. https://open.spotify.com/track/{song_id} {
                    artist_name} - {song_name} | Genre: {artist_genres}\n")

        # 2. RELATED PLAYLISTS
        f.write('\nRELATED PLAYLISTS\n')

        # Gather all related playlists in a single pass
        all_related_playlists = {}
        for _, song_name, artist_ids, artist_name, _ in songs_info:
            related_playlists = get_related_playlists(
                cursor, artist_name, inputted_ids)
            for playlist_id, playlist_creator_id, playlist_top_genres, playlist_items in related_playlists:
                if playlist_id not in all_related_playlists:
                    all_related_playlists[playlist_id] = (
                        playlist_creator_id, playlist_top_genres, playlist_items.split(','))

        if not all_related_playlists:
            f.write("No related playlists found.\n")
        else:
            for playlist_idx, (playlist_id, (playlist_creator_id, playlist_top_genres, playlist_items)) in enumerate(all_related_playlists.items(), 1):
                f.write(f"{playlist_idx}. https://open.spotify.com/playlist/{playlist_id} by https://open.spotify.com/user/{
                        playlist_creator_id}, Top Genres: {playlist_top_genres}, Items: {', '.join(playlist_items)}\n")

        # 3. SONG RECOMMENDATION
        f.write('\nSONG RECOMMENDATION\n')

        # Reuse the related playlists to extract songs
        song_count = extract_songs_from_playlists(
            all_related_playlists.values(), cursor, inputted_ids)

        if not song_count:
            f.write("No song recommendations found.\n")
        else:
            # Filter and sort the songs
            artist_song_limit = defaultdict(int)
            limited_songs = []

            sorted_songs = sorted(song_count.items(),
                                  key=lambda x: x[1], reverse=True)
            for ((rec_song_id, rec_artist_name, rec_song_name), count) in sorted_songs:
                # Limit to 2 songs per artist
                if artist_song_limit[rec_artist_name] < 2:
                    limited_songs.append(
                        (rec_song_id, rec_artist_name, rec_song_name, count))
                    artist_song_limit[rec_artist_name] += 1

            # Write the limited songs to the output with proper enumeration
            for rec_idx, (rec_song_id, rec_artist_name, rec_song_name, count) in enumerate(limited_songs, 1):
                f.write(f"{rec_idx}. https://open.spotify.com/track/{rec_song_id} {
                        rec_artist_name} - {rec_song_name} | Count: {count}\n")

    conn.close()
    print(f'Result for {MODEL} stored at {OUTPUT_PATH}')


if __name__ == "__main__":
    ids = ['6EIMUjQ7Q8Zr2VtIUik4He',
           '30Z12rJpW0M0u8HMFpigTB', '3wlLknnMtD8yZ0pCtCeeK4']
    cf(ids)
