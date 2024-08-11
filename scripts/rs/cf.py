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
    query = """
        SELECT s.song_id, s.song_name, s.artist_ids, a.artist_name, 
               COALESCE(NULLIF(a.artist_genres, ''), 'N/A') as artist_genres
        FROM songs s
        JOIN artists a ON instr(s.artist_ids, a.artist_id) > 0
        WHERE s.song_id = ?
    """
    cursor.execute(query, (song_id,))
    results = cursor.fetchall()

    # If multiple artists, select the one with valid artist_genres
    if results:
        for result in results:
            if result[4] != 'N/A':  # Check if artist_genres is not "N/A"
                print(f"DEBUG: Found song info for {
                      song_id} - {result[1]} by {result[3]} with valid genres")
                return result

        # If none of the artists had a valid genre, return the first one with "N/A"
        print(f"DEBUG: Found song info for {
              song_id} - {results[0][1]} by {results[0][3]} but all genres are 'N/A'")
        return results[0]
    else:
        print(f"DEBUG: No song info found for {song_id}")
        return None


def read_inputted_ids(cursor, ids):
    songs_info = []
    for song_id in ids:
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
            playlist_items_list = playlist_items.split(',')

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
        playlist_items_list = playlist_items.split(',')

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
