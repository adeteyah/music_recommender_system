import sqlite3
import configparser
from collections import Counter

# Read configuration file
config = configparser.ConfigParser()
config.read('config.cfg')

MODEL = 'Collaborative Filtering'
DB = config['rs']['db_path']
OUTPUT_PATH = config['rs']['cf_output']
N_RESULT = int(config['rs']['cbf_n_result'])


def get_song_info(conn, song_id):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT s.song_id, s.song_name, s.artist_ids, a.artist_name, a.artist_genres
        FROM songs s
        JOIN artists a ON s.artist_ids = a.artist_id
        WHERE s.song_id = ?
    """, (song_id,))
    return cursor.fetchone()


def get_playlists_by_song(conn, song_id):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT playlist_id FROM playlists
        WHERE playlist_items LIKE ?
    """, ('%' + song_id + '%',))
    return [row[0] for row in cursor.fetchall()]


def get_playlists_by_genre(conn, genre):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT playlist_id FROM playlists
        WHERE playlist_top_genres LIKE ?
    """, ('%' + genre + '%',))
    return [row[0] for row in cursor.fetchall()]


def get_playlists_by_artist(conn, artist_id):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT playlist_id FROM playlists
        WHERE playlist_top_artist_ids LIKE ?
    """, ('%' + artist_id + '%',))
    return [row[0] for row in cursor.fetchall()]


def get_songs_from_playlists(conn, playlist_ids):
    cursor = conn.cursor()
    playlist_items = []
    for playlist_id in playlist_ids:
        cursor.execute("""
            SELECT playlist_items FROM playlists
            WHERE playlist_id = ?
        """, (playlist_id,))
        playlist_items.extend(cursor.fetchone()[0].split(","))
    return playlist_items


def get_top_songs(song_ids, exclude_ids):
    count = Counter(song_ids)
    top_songs = [(song_id, count) for song_id,
                 count in count.most_common() if song_id not in exclude_ids]
    return top_songs[:N_RESULT]


def read_inputted_ids(ids, conn):
    songs_info = []
    for song_id in ids:
        song_info = get_song_info(conn, song_id)
        if song_info:
            playlists = get_playlists_by_song(conn, song_id)
            songs_info.append((*song_info, playlists))
    return songs_info


def cf(ids):
    conn = sqlite3.connect(DB)
    songs_info = read_inputted_ids(ids, conn)
    inputted_ids = set(id for id, *_ in songs_info)

    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        f.write("# SEARCH BY SONG_ID:\n")
        for i, song in enumerate(songs_info, 1):
            song_id, song_name, artist_ids, artist_name, artist_genres, playlists = song
            genres_str = artist_genres if artist_genres else "N/A"
            playlists_str = ", ".join(playlists)
            f.write(f"{i}. {
                    artist_name} - {song_name} https://open.spotify.com/track/{song_id} ({genres_str})\n")
            f.write(f"Song found in: {playlists_str}\n")

            # Top N_RESULT Songs
            playlist_items = get_songs_from_playlists(conn, playlists)
            top_songs = get_top_songs(playlist_items, inputted_ids)
            f.write(f"\nTop {N_RESULT} by Song ID:\n")
            for song_id, count in top_songs:
                song_info = get_song_info(conn, song_id)
                if song_info:
                    _, song_name, _, _, _ = song_info
                    f.write(
                        f"- https://open.spotify.com/track/{song_id} {song_name} | Count: {count}\n")
            f.write('\n')

        # SEARCH BY ARTIST_GENRE
        f.write("\n# SEARCH BY ARTIST_GENRE:\n")
        genres = set()
        for _, _, artist_ids, _, artist_genres, _ in songs_info:
            genres.update(artist_genres.split(", ") if artist_genres else [])
        for genre in genres:
            playlists_by_genre = get_playlists_by_genre(conn, genre)
            playlist_items = get_songs_from_playlists(conn, playlists_by_genre)
            top_songs = get_top_songs(playlist_items, inputted_ids)
            f.write(f"\nTop {N_RESULT} by Genre '{genre}':\n")
            for song_id, count in top_songs:
                song_info = get_song_info(conn, song_id)
                if song_info:
                    _, song_name, _, _, _ = song_info
                    f.write(
                        f"- https://open.spotify.com/track/{song_id} {song_name} | Count: {count}\n")
            f.write('\n')

        # SEARCH BY ARTIST_ID
        f.write("\n# SEARCH BY ARTIST_ID:\n")
        artist_ids_set = set()
        for _, _, artist_ids, _, _, _ in songs_info:
            artist_ids_set.add(artist_ids)
        for artist_id in artist_ids_set:
            playlists_by_artist = get_playlists_by_artist(conn, artist_id)
            playlist_items = get_songs_from_playlists(
                conn, playlists_by_artist)
            top_songs = get_top_songs(playlist_items, inputted_ids)
            f.write(f"\nTop {
                    N_RESULT} by Artist ID 'https://open.spotify.com/artist/{artist_id}':\n")
            for song_id, count in top_songs:
                song_info = get_song_info(conn, song_id)
                if song_info:
                    _, song_name, _, _, _ = song_info
                    f.write(
                        f"- https://open.spotify.com/track/{song_id} {song_name} | Count: {count}\n")
            f.write('\n')

    conn.close()
    print('Result for', MODEL, 'stored at', OUTPUT_PATH)


if __name__ == "__main__":
    ids = [
        '1BxfuPKGuaTgP7aM0Bbdwr',
        '4xqrdfXkTW4T0RauPLv3WA',
        '7JIuqL4ZqkpfGKQhYlrirs',
        '5dTHtzHFPyi8TlTtzoz1J9',
        '4cluDES4hQEUhmXj6TXkSo',
        '4ZtFanR9U6ndgddUvNcjcG',
        '2QjOHCTQ1Jl3zawyYOpxh6',
        '0nJW01T7XtvILxQgC5J7Wh',
        '7nQoDLkzCcoIpKPQt3eCdN',
        '72MEldEAmz3WMJ2MkII3kP',
    ]
    cf(ids)
