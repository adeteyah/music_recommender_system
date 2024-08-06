import sqlite3
import configparser

# Read configuration file
config = configparser.ConfigParser()
config.read('config.cfg')

MODEL = 'Collaborative Filtering'
DB = config['rs']['db_path']
OUTPUT_PATH = config['rs']['cf_output']
N_RESULT = int(config['rs']['n_result'])


def get_song_info(conn, song_id):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT s.song_id, s.song_name, s.artist_ids, a.artist_name, a.artist_genres
        FROM songs s
        JOIN artists a ON s.artist_ids = a.artist_id
        WHERE s.song_id = ?
    """, (song_id,))
    return cursor.fetchone()


def read_inputted_ids(ids, conn):
    songs_info = []
    for song_id in ids:
        info = get_song_info(conn, song_id)
        if info:
            songs_info.append(info)
    return songs_info


def get_related_playlists(conn, inputted_ids):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.playlist_id, p.playlist_creator_id, p.playlist_top_genres, p.playlist_items
        FROM playlists p
    """)
    playlists = cursor.fetchall()

    related_playlists = []
    for playlist in playlists:
        playlist_id, playlist_creator_id, playlist_top_genres, playlist_items = playlist
        # Assuming playlist_items is a comma-separated string of song_ids
        playlist_items_list = playlist_items.split(',')

        # Check if any inputted IDs are in the playlist
        if any(song_id in inputted_ids for song_id in playlist_items_list):
            artist_names = []
            for song_id in playlist_items_list:
                cursor.execute("""
                    SELECT a.artist_name
                    FROM songs s
                    JOIN artists a ON s.artist_ids = a.artist_id
                    WHERE s.song_id = ?
                """, (song_id,))
                artist_info = cursor.fetchone()
                if artist_info:
                    artist_names.append(artist_info[0])

            related_playlists.append(
                (playlist_id, playlist_creator_id, playlist_top_genres, playlist_items_list, artist_names))

    return related_playlists


def cf(ids):
    conn = sqlite3.connect(DB)
    songs_info = read_inputted_ids(ids, conn)
    inputted_ids = set(id for id, *_ in songs_info)
    related_playlists = get_related_playlists(conn, inputted_ids)

    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        f.write('INPUTTED IDS\n')
        for idx, song_info in enumerate(songs_info, 1):
            song_id, song_name, artist_ids, artist_name, artist_genres = song_info
            output_line = f"{idx}. https://open.spotify.com/track/{song_id} {
                artist_name} - {song_name} | Genre: {artist_genres}"
            f.write(output_line + '\n')

        f.write('\nRELATED PLAYLISTS\n')
        for idx, playlist in enumerate(related_playlists, 1):
            playlist_id, playlist_creator_id, playlist_top_genres, playlist_items, artist_names = playlist
            playlist_items_str = ', '.join(playlist_items)
            artist_names_str = ', '.join(artist_names)
            output_line = f"{idx}. Playlist ID: {playlist_id}, Creator ID: {playlist_creator_id}, Top Genres: {
                playlist_top_genres}, Items: {playlist_items_str}, Artists: {artist_names_str}"
            f.write(output_line + '\n')

    conn.close()
    print('Result for', MODEL, 'stored at', OUTPUT_PATH)


if __name__ == "__main__":
    ids = [
        '1BxfuPKGuaTgP7aM0Bbdwr',
        '4xqrdfXkTW4T0RauPLv3WA',
        '7JIuqL4ZqkpfGKQhYlrirs',
    ]
    cf(ids)
