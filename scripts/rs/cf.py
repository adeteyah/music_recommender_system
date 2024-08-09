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
    return [get_song_info(cursor, song_id) for song_id in ids if get_song_info(cursor, song_id)]


def get_related_playlists(cursor, inputted_ids):
    cursor.execute("""
        SELECT p.playlist_id, p.playlist_creator_id, p.playlist_top_genres, p.playlist_items
        FROM playlists p
    """)
    playlists = cursor.fetchall()

    related_playlists = []
    for playlist in playlists:
        playlist_id, playlist_creator_id, playlist_top_genres, playlist_items = playlist
        playlist_items_list = playlist_items.split(',')

        if any(song_id in inputted_ids for song_id in playlist_items_list):
            artist_names = set(
                get_song_info(cursor, song_id)[3] for song_id in playlist_items_list if get_song_info(cursor, song_id)
            )
            related_playlists.append(
                (playlist_id, playlist_creator_id, playlist_top_genres,
                 playlist_items_list, list(artist_names))
            )
    return related_playlists


def categorize_playlists(playlists):
    artist_to_playlists = defaultdict(list)

    for playlist_id, playlist_creator_id, playlist_top_genres, playlist_items, artist_names in playlists:
        for artist in artist_names:
            artist_to_playlists[artist].append(
                (playlist_id, playlist_creator_id,
                 playlist_top_genres, playlist_items, artist_names)
            )

    return [(artist, list({p[0]: p for p in playlists}.values())) for artist, playlists in artist_to_playlists.items()]


def extract_songs_from_playlists(categorized_playlists, cursor, inputted_ids, inputted_songs):
    artist_song_count = defaultdict(Counter)
    inputted_songs_set = {(artist_name, song_name)
                          for _, song_name, _, artist_name, _ in inputted_songs}

    for artist, playlists in categorized_playlists:
        for _, _, _, playlist_items, _ in playlists:
            for song_id in playlist_items:
                song_info = get_song_info(cursor, song_id)
                if song_info and song_id not in inputted_ids:
                    _, song_name, _, artist_name, _ = song_info
                    if (artist_name, song_name) not in inputted_songs_set:
                        artist_song_count[artist][(
                            song_id, artist_name, song_name)] += 1

    return artist_song_count


def format_artist_category(artist, songs_info):
    song_names = [song_name for _, song_name, _, artist_name,
                  _ in songs_info if artist_name == artist]
    return f"{artist} - {song_names[0]}" if song_names else artist


def cf(ids):
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    songs_info = read_inputted_ids(cursor, ids)
    inputted_ids = {song_id for song_id, *_ in songs_info}
    related_playlists = get_related_playlists(cursor, inputted_ids)
    categorized_playlists = categorize_playlists(related_playlists)
    artist_song_count = extract_songs_from_playlists(
        categorized_playlists, cursor, inputted_ids, songs_info)

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
        for artist, playlists in categorized_playlists:
            category_name = format_artist_category(artist, songs_info)
            f.write(f'{category_name}\n')
            unique_artists_written = set()
            for playlist_id, playlist_creator_id, playlist_top_genres, playlist_items, artist_names in playlists:
                artist_names_str = ', '.join(
                    set(artist_names) - unique_artists_written)
                if artist_names_str:
                    f.write(f"  - https://open.spotify.com/playlist/{playlist_id} by https://open.spotify.com/user/{playlist_creator_id} | Top Genres: {
                            playlist_top_genres} | Artists: {artist_names_str}\n")
                    unique_artists_written.update(artist_names)

        f.write('\nSONGS FROM CATEGORIZED PLAYLISTS\n')
        for artist, songs in artist_song_count.items():
            category_name = format_artist_category(artist, songs_info)
            f.write(f'{category_name}\n')
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
    ids = ['09mEdoA6zrmBPgTEN5qXmN', '7CyPwkp0oE8Ro9Dd5CUDjW',
           '6WzRpISELf3YglGAh7TXcG', '7MXVkk9YMctZqd1Srtv4MB']
    cf(ids)
