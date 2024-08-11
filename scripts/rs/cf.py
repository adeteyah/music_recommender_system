import sqlite3
import configparser
from collections import Counter

# Read configuration file
config = configparser.ConfigParser()
config.read('config.cfg')

MODEL = 'Collaborative Filtering'
DB = config['rs']['db_path']
OUTPUT_PATH = config['rs']['cf_output']


def get_song_info(cursor, song_ids):
    query = """
        SELECT s.song_id, s.song_name, s.artist_ids, a.artist_name,
               COALESCE(NULLIF(a.artist_genres, ''), 'N/A') as artist_genres
        FROM songs s
        JOIN artists a ON instr(s.artist_ids, a.artist_id) > 0
        WHERE s.song_id IN ({})
    """.format(','.join('?' * len(song_ids)))

    cursor.execute(query, song_ids)
    results = cursor.fetchall()

    # Map song_id to song_info
    song_info_map = {}
    for result in results:
        song_id = result[0]
        if song_id not in song_info_map:
            song_info_map[song_id] = result

    return song_info_map


def get_related_playlists(cursor, artist_name, inputted_ids):
    # Fetch playlists containing any of the inputted songs directly
    cursor.execute("""
        SELECT p.playlist_id, p.playlist_creator_id, p.playlist_top_genres, p.playlist_items
        FROM playlists p
        WHERE EXISTS (
            SELECT 1
            FROM (
                SELECT song_id
                FROM songs
                WHERE song_id IN ({})
            ) AS input_songs
            WHERE instr(p.playlist_items, input_songs.song_id) > 0
        )
    """.format(','.join('?' * len(inputted_ids))), inputted_ids)

    playlists = cursor.fetchall()

    # Fetch playlists containing songs by the specific artist
    cursor.execute("""
        SELECT DISTINCT p.playlist_id, p.playlist_creator_id, p.playlist_top_genres, p.playlist_items
        FROM playlists p
        JOIN songs s ON instr(p.playlist_items, s.song_id) > 0
        JOIN artists a ON s.artist_ids = a.artist_id
        WHERE a.artist_name = ?
    """, (artist_name,))

    artist_related_playlists = cursor.fetchall()

    # Combine both queries results
    related_playlists = playlists + artist_related_playlists
    return related_playlists


def extract_songs_from_playlists(related_playlists, song_info_map, inputted_ids):
    song_count = Counter()

    for playlist_id, playlist_creator_id, playlist_top_genres, playlist_items in related_playlists:
        playlist_items_list = playlist_items.split(',')
        for song_id in playlist_items_list:
            song_info = song_info_map.get(song_id)
            if song_info:
                if song_id in inputted_ids:
                    # Count +2 for same inputted song ID
                    song_count[(song_id, song_info[3], song_info[1])] += 2
                else:
                    song_count[(song_id, song_info[3], song_info[1])
                               ] += 1  # Count +1 for other songs

    return song_count


def cf(ids):
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    # 1. INPUTTED IDS
    song_info_map = get_song_info(cursor, ids)
    inputted_ids = set(ids)

    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        f.write('\nINPUTTED IDS\n')
        for idx, song_id in enumerate(ids, 1):
            info = song_info_map.get(song_id)
            if info:
                song_name, artist_ids, artist_name, artist_genres = info[1], info[2], info[3], info[4]
                f.write(f"{idx}. https://open.spotify.com/track/{song_id} {
                        artist_name} - {song_name} | Genre: {artist_genres}\n")

        # 2. RELATED PLAYLISTS
        f.write('\nRELATED PLAYLISTS\n')
        for idx, song_id in enumerate(ids, 1):
            info = song_info_map.get(song_id)
            if info:
                artist_name = info[3]
                f.write(f"\nFor Input Song: {
                        artist_name} - {song_info_map[song_id][1]}\n")
                related_playlists = get_related_playlists(
                    cursor, artist_name, inputted_ids)
                if not related_playlists:
                    f.write("No related playlists found.\n")
                else:
                    for playlist_idx, (playlist_id, playlist_creator_id, playlist_top_genres, playlist_items) in enumerate(related_playlists, 1):
                        f.write(f"{playlist_idx}. https://open.spotify.com/playlist/{playlist_id} by https://open.spotify.com/user/{
                                playlist_creator_id}, Top Genres: {playlist_top_genres}, Items: {', '.join(playlist_items.split(','))}\n")

        # 3. SONG RECOMMENDATION
        f.write('\nSONG RECOMMENDATION\n')
        for idx, song_id in enumerate(ids, 1):
            info = song_info_map.get(song_id)
            if info:
                artist_name = info[3]
                f.write(f"\nRecommendations for Input Song: {
                        artist_name} - {song_info_map[song_id][1]}\n")
                related_playlists = get_related_playlists(
                    cursor, artist_name, inputted_ids)
                song_count = extract_songs_from_playlists(
                    related_playlists, song_info_map, inputted_ids)

                if not song_count:
                    f.write("No song recommendations found.\n")
                else:
                    sorted_songs = sorted(song_count.items(),
                                          key=lambda x: x[1], reverse=True)
                    song_artist_counter = {}

                    for rec_idx, ((rec_song_id, rec_artist_name, rec_song_name), count) in enumerate(sorted_songs, 1):
                        if rec_artist_name not in song_artist_counter:
                            song_artist_counter[rec_artist_name] = 0

                        if song_artist_counter[rec_artist_name] < 2:
                            f.write(f"{rec_idx}. https://open.spotify.com/track/{rec_song_id} {
                                    rec_artist_name} - {rec_song_name} | Count: {count}\n")
                            song_artist_counter[rec_artist_name] += 1

    conn.close()
    print(f'Result for {MODEL} stored at {OUTPUT_PATH}')


if __name__ == "__main__":
    ids = ['6EIMUjQ7Q8Zr2VtIUik4He',
           '30Z12rJpW0M0u8HMFpigTB', '3wlLknnMtD8yZ0pCtCeeK4']
    cf(ids)
