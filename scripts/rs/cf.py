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
        SELECT s.song_id, s.song_name, GROUP_CONCAT(a.artist_name), GROUP_CONCAT(a.artist_genres)
        FROM songs s
        JOIN song_artists sa ON s.song_id = sa.song_id
        JOIN artists a ON sa.artist_id = a.artist_id
        WHERE s.song_id = ?
        GROUP BY s.song_id
    """, (song_id,))
    return cursor.fetchone()


def read_inputted_ids(cursor, ids):
    cursor.execute("""
        SELECT s.song_id, s.song_name, GROUP_CONCAT(a.artist_name), GROUP_CONCAT(a.artist_genres)
        FROM songs s
        JOIN song_artists sa ON s.song_id = sa.song_id
        JOIN artists a ON sa.artist_id = a.artist_id
        WHERE s.song_id IN ({})
        GROUP BY s.song_id
    """.format(','.join('?' for _ in ids)), ids)

    results = cursor.fetchall()
    print(f"DEBUG: Retrieved {len(results)
                              } songs from the database for input IDs: {ids}")
    return results


def get_related_playlists(cursor, artist_name, inputted_ids):
    cursor.execute("""
        SELECT p.playlist_id, p.playlist_creator_id, p.playlist_top_genres, p.playlist_items
        FROM playlists p
        WHERE EXISTS (
            SELECT 1 FROM songs s
            JOIN song_artists sa ON s.song_id = sa.song_id
            JOIN artists a ON sa.artist_id = a.artist_id
            WHERE s.song_id IN ({}) AND a.artist_name = ?
        )
        OR p.playlist_items LIKE ?
    """.format(','.join('?' for _ in inputted_ids)), (*inputted_ids, artist_name, f'%{artist_name}%'))

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
                    song_count[(song_id, song_info[2], song_info[3])] += 2
                else:
                    # Count +1 for other songs
                    song_count[(song_id, song_info[2], song_info[3])] += 1

    return song_count


def cf(ids):
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    # 1. INPUTTED IDS
    songs_info = read_inputted_ids(cursor, ids)
    inputted_ids = {song_id for song_id, *_ in songs_info}

    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        f.write('\nINPUTTED IDS\n')
        for idx, (song_id, song_name, artist_names, artist_genres) in enumerate(songs_info, 1):
            f.write(f"{idx}. https://open.spotify.com/track/{song_id} {
                    artist_names} - {song_name} | Genre: {artist_genres}\n")
            print(f"DEBUG: Writing song info for {
                  song_id} - {song_name} by {artist_names}")

        # 2. RELATED PLAYLISTS
        f.write('\nRELATED PLAYLISTS\n')
        for idx, (song_id, song_name, artist_names, artist_genres) in enumerate(songs_info, 1):
            f.write(f"\nFor Input Song: {artist_names} - {song_name}\n")
            related_playlists = get_related_playlists(
                cursor, artist_names, inputted_ids)
            if not related_playlists:
                f.write("No related playlists found.\n")
            else:
                for playlist_idx, (playlist_id, playlist_creator_id, playlist_top_genres, playlist_items) in enumerate(related_playlists, 1):
                    f.write(f"{playlist_idx}. https://open.spotify.com/playlist/{playlist_id} by https://open.spotify.com/user/{
                            playlist_creator_id}, Top Genres: {playlist_top_genres}, Items: {', '.join(playlist_items.split(','))}\n")

        # 3. SONG RECOMMENDATION
        f.write('\nSONG RECOMMENDATION\n')
        for idx, (song_id, song_name, artist_names, artist_genres) in enumerate(songs_info, 1):
            f.write(f"\nRecommendations for Input Song: {
                    artist_names} - {song_name}\n")
            related_playlists = get_related_playlists(
                cursor, artist_names, inputted_ids)
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
