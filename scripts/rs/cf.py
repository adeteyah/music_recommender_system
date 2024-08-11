import sqlite3
import configparser
from collections import Counter

# Read configuration file
config = configparser.ConfigParser()
config.read('config.cfg')

MODEL = 'Collaborative Filtering'
DB = config['rs']['db_path']
OUTPUT_PATH = config['rs']['cf_output']


def get_songs_info(cursor, song_ids):
    placeholders = ','.join('?' for _ in song_ids)
    query = f"""
        SELECT s.song_id, s.song_name, s.artist_ids, a.artist_name, a.artist_genres
        FROM songs s
        JOIN artists a ON s.artist_ids = a.artist_id
        WHERE s.song_id IN ({placeholders})
    """
    cursor.execute(query, song_ids)
    return cursor.fetchall()


def get_related_playlists(cursor, artist_names, inputted_ids):
    placeholders_artists = ','.join('?' for _ in artist_names)
    placeholders_ids = ','.join('?' for _ in inputted_ids)

    # Query for playlists containing the inputted songs
    cursor.execute(f"""
        SELECT p.playlist_id, p.playlist_creator_id, p.playlist_top_genres, p.playlist_items
        FROM playlists p
        WHERE p.playlist_items LIKE '%' || ? || '%'
    """, (f'{placeholders_ids}',))
    playlists_song = cursor.fetchall()

    # Query for playlists containing songs by the specific artists
    cursor.execute(f"""
        SELECT p.playlist_id, p.playlist_creator_id, p.playlist_top_genres, p.playlist_items
        FROM playlists p
        JOIN songs s ON instr(p.playlist_items, s.song_id) > 0
        WHERE s.artist_ids IN ({placeholders_artists})
    """, artist_names)
    playlists_artist = cursor.fetchall()

    # Combine and deduplicate playlists
    all_playlists = playlists_song + playlists_artist
    seen = set()
    related_playlists = []
    for playlist in all_playlists:
        if playlist[0] not in seen:
            seen.add(playlist[0])
            related_playlists.append(playlist)

    return related_playlists


def extract_songs_from_playlists(related_playlists, cursor, inputted_ids):
    song_count = Counter()

    for playlist_id, playlist_creator_id, playlist_top_genres, playlist_items in related_playlists:
        for song_id in playlist_items.split(','):
            if song_id in inputted_ids:
                song_count[song_id] += 2
            else:
                song_info = get_song_info(cursor, song_id)
                if song_info:
                    song_count[(song_info[0], song_info[3], song_info[1])] += 1

    return song_count


def cf(ids):
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    # 1. INPUTTED IDS
    songs_info = get_songs_info(cursor, ids)
    inputted_ids = [song_id for song_id, *_ in songs_info]
    artist_names = [artist_name for _, _, _, artist_name, _ in songs_info]

    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        f.write('\nINPUTTED IDS\n')
        for idx, (song_id, song_name, artist_ids, artist_name, artist_genres) in enumerate(songs_info, 1):
            f.write(f"{idx}. https://open.spotify.com/track/{song_id} {
                    artist_name} - {song_name} | Genre: {artist_genres}\n")

        # 2. RELATED PLAYLISTS
        f.write('\nRELATED PLAYLISTS\n')
        related_playlists = get_related_playlists(
            cursor, artist_names, inputted_ids)
        if not related_playlists:
            f.write("No related playlists found.\n")
        else:
            for playlist_idx, (playlist_id, playlist_creator_id, playlist_top_genres, playlist_items) in enumerate(related_playlists, 1):
                f.write(f"{playlist_idx}. https://open.spotify.com/playlist/{playlist_id} by https://open.spotify.com/user/{
                        playlist_creator_id}, Top Genres: {playlist_top_genres}, Items: {playlist_items}\n")

        # 3. SONG RECOMMENDATION
        f.write('\nSONG RECOMMENDATION\n')
        song_count = extract_songs_from_playlists(
            related_playlists, cursor, inputted_ids)

        if not song_count:
            f.write("No song recommendations found.\n")
        else:
            sorted_songs = sorted(song_count.items(),
                                  key=lambda x: x[1], reverse=True)
            for rec_idx, ((rec_song_id, rec_artist_name, rec_song_name), count) in enumerate(sorted_songs, 1):
                f.write(f"{rec_idx}. https://open.spotify.com/track/{rec_song_id} {
                        rec_artist_name} - {rec_song_name} | Count: {count}\n")

    conn.close()
    print(f'Result for {MODEL} stored at {OUTPUT_PATH}')


if __name__ == "__main__":
    ids = ['1yKAqZoi8xWGLCf5vajroL',
           '5VGlqQANWDKJFl0MBG3sg2', '0lP4HYLmvowOKdsQ7CVkuq']
    cf(ids)
