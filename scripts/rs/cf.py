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
        JOIN artists a ON s.artist_ids = a.artist_id
        WHERE s.song_id = ?
    """, (song_id,))
    result = cursor.fetchone()
    if result:
        # Extract the first artist_id from artist_ids (assuming artist_ids is a comma-separated list)
        artist_ids = result[2].split(',')
        first_artist_id = artist_ids[0] if artist_ids else None
        cursor.execute("""
            SELECT a.artist_name, a.artist_genres
            FROM artists a
            WHERE a.artist_id = ?
        """, (first_artist_id,))
        artist_info = cursor.fetchone()
        if artist_info:
            return (result[0], result[1], first_artist_id, artist_info[0], artist_info[1])
    return result


def read_inputted_ids(cursor, ids):
    cursor.execute("""
        SELECT s.song_id, s.song_name, s.artist_ids
        FROM songs s
        WHERE s.song_id IN ({})
    """.format(','.join('?' for _ in ids)), ids)

    results = cursor.fetchall()
    songs_info = []
    for song_id, song_name, artist_ids in results:
        info = get_song_info(cursor, song_id)
        if info:
            songs_info.append(info)
    print(f"DEBUG: Retrieved {len(songs_info)
                              } songs from the database for input IDs: {ids}")
    return songs_info


def get_related_playlists(cursor, artist_name, inputted_ids):
    related_playlists = []

    # Use a query to fetch playlists containing any of the inputted songs directly
    for song_id in inputted_ids:
        cursor.execute("""
            SELECT p.playlist_id, p.playlist_creator_id, p.playlist_top_genres, p.playlist_items
            FROM playlists p
            WHERE p.playlist_items LIKE ?
        """, (f'%{song_id}%',))

        playlists = cursor.fetchall()

        # Add playlists that match the song ID
        for playlist_id, playlist_creator_id, playlist_top_genres, playlist_items in playlists:
            playlist_items_list = playlist_items.split(',') if isinstance(
                playlist_items, str) else playlist_items

            related_playlists.append(
                (playlist_id, playlist_creator_id,
                 playlist_top_genres, playlist_items_list)
            )

    # Add playlists containing songs by the specific artist
    cursor.execute("""
        SELECT p.playlist_id, p.playlist_creator_id, p.playlist_top_genres, p.playlist_items
        FROM playlists p
        JOIN songs s ON instr(p.playlist_items, s.song_id) > 0
        WHERE s.artist_ids IN (
            SELECT a.artist_id
            FROM artists a
            WHERE a.artist_name = ?
        )
    """, (artist_name,))

    artist_related_playlists = cursor.fetchall()

    for playlist_id, playlist_creator_id, playlist_top_genres, playlist_items in artist_related_playlists:
        playlist_items_list = playlist_items.split(',') if isinstance(
            playlist_items, str) else playlist_items

        related_playlists.append(
            (playlist_id, playlist_creator_id,
             playlist_top_genres, playlist_items_list)
        )

    return related_playlists


def extract_songs_from_playlists(related_playlists, cursor, inputted_ids):
    song_count = Counter()

    for playlist_id, playlist_creator_id, playlist_top_genres, playlist_items in related_playlists:
        playlist_items_list = playlist_items if isinstance(
            playlist_items, list) else playlist_items.split(',')

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
            print(f"DEBUG: Writing song info for {
                  song_id} - {song_name} by {artist_name}")

        # 2. RELATED PLAYLISTS
        f.write('\nRELATED PLAYLISTS\n')
        for idx, (song_id, song_name, artist_ids, artist_name, artist_genres) in enumerate(songs_info, 1):
            f.write(f"\nFor Input Song: {artist_name} - {song_name}\n")
            related_playlists = get_related_playlists(
                cursor, artist_name, inputted_ids)
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
            related_playlists = get_related_playlists(
                cursor, artist_name, inputted_ids)
            song_count = extract_songs_from_playlists(
                related_playlists, cursor, inputted_ids)

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
