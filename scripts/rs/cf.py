import sqlite3
import configparser
from collections import defaultdict

# Read configuration file
config = configparser.ConfigParser()
config.read('config.cfg')

MODEL = 'Collaborative Filtering'
DB = config['rs']['db_path']
OUTPUT_PATH = config['rs']['cf_output']


def fetch_artist_data(cursor):
    cursor.execute("""
        SELECT artist_id, artist_name, artist_genres
        FROM artists
    """)
    return cursor.fetchall()


def fetch_song_data(cursor):
    cursor.execute("""
        SELECT s.song_id, s.song_name, s.artist_ids
        FROM songs s
    """)
    return cursor.fetchall()


def fetch_related_playlists(cursor):
    cursor.execute("""
        SELECT p.playlist_id, p.playlist_creator_id, p.playlist_top_genres, p.playlist_items
        FROM playlists p
    """)
    return cursor.fetchall()


def cf(ids):
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    # Cache artist data and song data
    artist_data = {artist_id: (artist_name, artist_genres)
                   for artist_id, artist_name, artist_genres in fetch_artist_data(cursor)}
    song_data = {song_id: (song_name, artist_ids)
                 for song_id, song_name, artist_ids in fetch_song_data(cursor)}

    # INPUTTED IDS
    songs_info = [(song_id, song_data[song_id][0], song_data[song_id]
                   [1], artist_data[song_data[song_id][1].split(',')[0]][0],
                   artist_data[song_data[song_id][1].split(',')[0]][1])
                  for song_id in ids]
    inputted_ids = {song_id for song_id, *_ in songs_info}
    inputted_songs = {(song_name, artist_name)
                      for song_id, song_name, artist_ids, artist_name, artist_genres in songs_info}

    related_playlists = fetch_related_playlists(cursor)

    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        f.write('\nINPUTTED IDS\n')
        for idx, (song_id, song_name, artist_ids, artist_name, artist_genres) in enumerate(songs_info, 1):
            f.write(
                f"{idx}. https://open.spotify.com/track/{song_id} {artist_name} - {song_name} | Genre: {artist_genres}\n")

        f.write('\nRELATED PLAYLISTS\n')
        song_count = defaultdict(int)
        song_id_map = {}

        for idx, (song_id, song_name, artist_ids, artist_name, artist_genres) in enumerate(songs_info, 1):
            f.write(f"\nFor Input Song: {artist_name} - {song_name}\n")
            found_related = False
            for playlist_id, playlist_creator_id, playlist_top_genres, playlist_items in related_playlists:
                playlist_items_list = playlist_items.split(',')
                if any(song_data.get(song_id)[1].split(',')[0] == artist_name for song_id in playlist_items_list):
                    found_related = True
                    f.write(
                        f"https://open.spotify.com/playlist/{playlist_id} by https://open.spotify.com/user/{playlist_creator_id}, Top Genres: {playlist_top_genres}, Items: {', '.join(playlist_items_list)}\n")

                    for song_id in playlist_items_list:
                        if song_id not in inputted_ids:
                            song_name, artist_ids = song_data[song_id]
                            artist_name = artist_data[artist_ids.split(',')[
                                0]][0]
                            if (song_name, artist_name) not in inputted_songs:
                                song_count[(song_name, artist_name)] += 1
                                if (song_name, artist_name) not in song_id_map:
                                    song_id_map[(
                                        song_name, artist_name)] = song_id

            if not found_related:
                f.write("No related playlists found.\n")

        f.write('\nSONG RECOMMENDATION\n')
        sorted_songs = sorted(song_count.items(),
                              key=lambda x: x[1], reverse=True)
        artist_song_count = {}

        for rec_idx, ((rec_song_name, rec_artist_name), count) in enumerate(sorted_songs, 1):
            if rec_artist_name not in artist_song_count:
                artist_song_count[rec_artist_name] = 0
            if artist_song_count[rec_artist_name] < 2:
                rec_song_id = song_id_map[(rec_song_name, rec_artist_name)]
                f.write(
                    f"{rec_idx}. https://open.spotify.com/track/{rec_song_id} {rec_artist_name} - {rec_song_name} | Count: {count}\n")
                artist_song_count[rec_artist_name] += 1

    conn.close()
    print(f'Result for {MODEL} stored at {OUTPUT_PATH}')


if __name__ == "__main__":
    ids = ['6EIMUjQ7Q8Zr2VtIUik4He',
           '30Z12rJpW0M0u8HMFpigTB', '3wlLknnMtD8yZ0pCtCeeK4']
    cf(ids)
