import sqlite3
import configparser
from collections import defaultdict, Counter

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
    return cursor.fetchone()


def read_inputted_ids(cursor, ids):
    songs_info = []
    artists = set()
    for song_id in ids:
        info = get_song_info(cursor, song_id)
        if info:
            songs_info.append(info)
            artists.add(info[3])  # Add artist_name to the artists set
    return songs_info, artists


def get_related_playlists(cursor, artists):
    cursor.execute("""
        SELECT p.playlist_id, p.playlist_creator_id, p.playlist_top_genres, p.playlist_items
        FROM playlists p
    """)
    playlists = cursor.fetchall()

    related_playlists = []
    for playlist in playlists:
        playlist_id, playlist_creator_id, playlist_top_genres, playlist_items = playlist
        playlist_items_list = playlist_items.split(',')

        # Find playlists that contain songs by any of the input artists
        artist_names = set()
        for song_id in playlist_items_list:
            song_info = get_song_info(cursor, song_id)
            if song_info and song_info[3] in artists:
                artist_names.add(song_info[3])

        if artist_names:
            related_playlists.append(
                (playlist_id, playlist_creator_id, playlist_top_genres,
                 playlist_items_list, list(artist_names))
            )
    return related_playlists


def categorize_playlists(related_playlists, inputted_ids):
    categorized_playlists = defaultdict(list)

    for playlist_id, playlist_creator_id, playlist_top_genres, playlist_items, artist_names in related_playlists:
        for song_id in playlist_items:
            if song_id in inputted_ids:
                categorized_playlists[song_id].append(
                    (playlist_id, playlist_creator_id,
                     playlist_top_genres, playlist_items, artist_names)
                )

    return categorized_playlists


def extract_songs_from_playlists(categorized_playlists, cursor, inputted_ids):
    song_count_by_input = defaultdict(Counter)

    for input_id, playlists in categorized_playlists.items():
        for _, _, _, playlist_items, _ in playlists:
            for song_id in playlist_items:
                if song_id not in inputted_ids:
                    song_info = get_song_info(cursor, song_id)
                    if song_info:
                        _, song_name, _, artist_name, _ = song_info
                        song_count_by_input[input_id][(
                            song_id, artist_name, song_name)] += 1

    return song_count_by_input


def cf(ids):
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    songs_info, artists = read_inputted_ids(cursor, ids)
    inputted_ids = {song_id for song_id, *_ in songs_info}
    related_playlists = get_related_playlists(cursor, artists)
    categorized_playlists = categorize_playlists(
        related_playlists, inputted_ids)
    songs_by_input = extract_songs_from_playlists(
        categorized_playlists, cursor, inputted_ids)

    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        f.write('\nINPUTTED IDS\n')
        for idx, (song_id, song_name, artist_ids, artist_name, artist_genres) in enumerate(songs_info, 1):
            f.write(f"{idx}. https://open.spotify.com/track/{song_id} {
                    artist_name} - {song_name} | Genre: {artist_genres}\n")

        f.write('\nRELATED PLAYLISTS\n')
        for idx, (playlist_id, playlist_creator_id, playlist_top_genres, playlist_items, artist_names) in enumerate(related_playlists, 1):
            f.write(f"{idx}. Playlist ID: {playlist_id}, Creator ID: {playlist_creator_id}, Top Genres: {
                    playlist_top_genres}, Items: {', '.join(playlist_items)}, Artists: {', '.join(set(artist_names))}\n")

        f.write('\nCATEGORIZED PLAYLISTS\n')
        for input_id, playlists in categorized_playlists.items():
            song_name = next(
                (s[1] for s in songs_info if s[0] == input_id), "Unknown")
            f.write(f"{input_id} - {song_name}\n")
            unique_artists_written = set()
            for playlist_id, playlist_creator_id, playlist_top_genres, playlist_items, artist_names in playlists:
                artist_names_str = ', '.join(
                    set(artist_names) - unique_artists_written)
                if artist_names_str:
                    f.write(f"  - Playlist ID: {playlist_id}, Creator ID: {playlist_creator_id}, Top Genres: {
                            playlist_top_genres}, Artists: {artist_names_str}\n")
                    unique_artists_written.update(artist_names)

        f.write('\nSONGS FROM CATEGORIZED PLAYLISTS\n')
        for input_id, songs in songs_by_input.items():
            song_name = next(
                (s[1] for s in songs_info if s[0] == input_id), "Unknown")
            f.write(f"{input_id} - {song_name}\n")
            sorted_songs = sorted(
                songs.items(), key=lambda x: x[1], reverse=True)
            unique_artists_written = set()
            for (song_id, artist_name, song_name), count in sorted_songs:
                if artist_name not in unique_artists_written:
                    f.write(f"  - https://open.spotify.com/track/{song_id} {
                            artist_name} - {song_name} | Count: {count}\n")
                    unique_artists_written.add(artist_name)

    conn.close()
    print(f'Result for {MODEL} stored at {OUTPUT_PATH}')


if __name__ == "__main__":
    ids = [
        '1BxfuPKGuaTgP7aM0Bbdwr',
        '4xqrdfXkTW4T0RauPLv3WA',
        '7JIuqL4ZqkpfGKQhYlrirs',
    ]
    cf(ids)
