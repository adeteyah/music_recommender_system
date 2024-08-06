import sqlite3
import configparser
from collections import defaultdict, Counter

# Read configuration file
config = configparser.ConfigParser()
config.read('config.cfg')

MODEL = 'Content-based Filtering'
DB = config['rs']['db_path']
OUTPUT_PATH = config['rs']['cbf_output']
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
            artist_names = set()
            for song_id in playlist_items_list:
                cursor.execute("""
                    SELECT a.artist_name
                    FROM songs s
                    JOIN artists a ON s.artist_ids = a.artist_id
                    WHERE s.song_id = ?
                """, (song_id,))
                artist_info = cursor.fetchone()
                if artist_info:
                    artist_names.add(artist_info[0])

            related_playlists.append(
                (playlist_id, playlist_creator_id, playlist_top_genres, playlist_items_list, list(artist_names)))

    return related_playlists


def categorize_playlists(playlists, inputted_artists):
    artist_to_playlists = {artist: [] for artist in inputted_artists}

    for playlist_id, playlist_creator_id, playlist_top_genres, playlist_items, artist_names in playlists:
        for artist in artist_names:
            if artist in inputted_artists:
                artist_to_playlists[artist].append(
                    (playlist_id, playlist_creator_id, playlist_top_genres, playlist_items, artist_names))

    categorized_playlists = []
    for artist, playlists in artist_to_playlists.items():
        if playlists:  # Only include artists with related playlists
            # Remove duplicate playlists
            unique_playlists = {p[0]: p for p in playlists}.values()
            categorized_playlists.append((artist, list(unique_playlists)))

    return categorized_playlists


def extract_songs_from_playlists(categorized_playlists, conn, inputted_ids):
    artist_song_count = defaultdict(Counter)

    for artist, playlists in categorized_playlists:
        for playlist_id, playlist_creator_id, playlist_top_genres, playlist_items, artist_names in playlists:
            for song_id in playlist_items:
                if song_id not in inputted_ids:
                    song_info = get_song_info(conn, song_id)
                    if song_info:
                        _, song_name, artist_ids, artist_name, _ = song_info
                        artist_song_count[artist][(
                            song_id, artist_name, song_name)] += 1

    return artist_song_count


def format_artist_category(artist, songs_info):
    song_names = [song_name for _, song_name, _, artist_name,
                  _ in songs_info if artist_name == artist]
    if song_names:
        return f"{artist} - {song_names[0]}"
    return artist


def cbf(ids):
    conn = sqlite3.connect(DB)
    songs_info = read_inputted_ids(ids, conn)
    inputted_ids = set(id for id, *_ in songs_info)
    inputted_artists = set(artist_name for _, _, _,
                           artist_name, _ in songs_info)
    related_playlists = get_related_playlists(conn, inputted_ids)
    categorized_playlists = categorize_playlists(
        related_playlists, inputted_artists)
    artist_song_count = extract_songs_from_playlists(
        categorized_playlists, conn, inputted_ids)

    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        f.write('\nRELATED PLAYLISTS\n')
        for idx, playlist in enumerate(related_playlists, 1):
            playlist_id, playlist_creator_id, playlist_top_genres, playlist_items, artist_names = playlist
            playlist_items_str = ', '.join(playlist_items)
            # Ensure unique artist names
            artist_names_str = ', '.join(set(artist_names))
            output_line = f"{idx}. Playlist ID: {playlist_id}, Creator ID: {playlist_creator_id}, Top Genres: {
                playlist_top_genres}, Items: {playlist_items_str}, Artists: {artist_names_str}"
            f.write(output_line + '\n')

        f.write('\nCATEGORIZED PLAYLISTS\n')
        for artist, playlists in categorized_playlists:
            category_name = format_artist_category(artist, songs_info)
            f.write(f'{category_name}\n')
            unique_artists_written = set()
            for playlist in playlists:
                playlist_id, playlist_creator_id, playlist_top_genres, playlist_items, artist_names = playlist
                # Only show unique artists
                artist_names_str = ', '.join(
                    set(artist_names) - unique_artists_written)
                if artist_names_str:  # Only write if there's something to write
                    output_line = f"  - Playlist ID: {playlist_id}, Creator ID: {
                        playlist_creator_id}, Top Genres: {playlist_top_genres}, Artists: {artist_names_str}"
                    f.write(output_line + '\n')
                    # Mark these artists as written
                    unique_artists_written.update(artist_names)

        f.write('\nSONGS FROM CATEGORIZED PLAYLISTS\n')
        for artist, songs in artist_song_count.items():
            category_name = format_artist_category(artist, songs_info)
            f.write(f'{category_name}\n')
            sorted_songs = sorted(
                songs.items(), key=lambda x: x[1], reverse=True)
            unique_artists_written = set()
            for (song_id, artist_name, song_name), count in sorted_songs:
                if artist_name not in unique_artists_written:  # Only write unique artists
                    output_line = f"  - https://open.spotify.com/track/{song_id} {artist_name} - {
                        song_name} | Count: {count}"
                    f.write(output_line + '\n')
                    # Mark this artist as written
                    unique_artists_written.add(artist_name)

    conn.close()
    print('Result for', MODEL, 'stored at', OUTPUT_PATH)


if __name__ == "__main__":
    ids = [
        '1BxfuPKGuaTgP7aM0Bbdwr',
        '4xqrdfXkTW4T0RauPLv3WA',
        '7JIuqL4ZqkpfGKQhYlrirs',
    ]
    cbf(ids)
