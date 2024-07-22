import sqlite3
import configparser
from collections import Counter

config = configparser.ConfigParser()
config.read('config.cfg')

songs_db_path = config['db']['songs_db']
playlists_db_path = config['db']['playlists_db']


def update_track_weight(cursor, track_id):
    query = "INSERT INTO track_weights (track_id, weight) VALUES (?, 1) ON CONFLICT(track_id) DO UPDATE SET weight = weight + 1"
    cursor.execute(query, (track_id,))


def fill_playlists_table():
    conn_playlists = sqlite3.connect(playlists_db_path)
    cursor_playlists = conn_playlists.cursor()

    cursor_playlists.execute("SELECT playlist_id, playlist_items FROM items")
    playlists = cursor_playlists.fetchall()

    conn_songs = sqlite3.connect(songs_db_path)
    cursor_songs = conn_songs.cursor()

    for playlist_id, playlist_items in playlists:
        track_ids = playlist_items.split(',')

        min_max_values = {
            'duration_ms': [],
            'popularity': [],
            'acousticness': [],
            'danceability': [],
            'energy': [],
            'instrumentalness': [],
            'key': [],
            'liveness': [],
            'loudness': [],
            'mode': [],
            'speechiness': [],
            'tempo': [],
            'time_signature': [],
            'valence': [],
            'artist_ids': [],
            'genres': []
        }

        for track_id in track_ids:
            cursor_songs.execute("""
                SELECT duration_ms, popularity, acousticness, danceability, energy,
                instrumentalness, key, liveness, loudness, mode,
                speechiness, tempo, time_signature, valence, artist_ids
                FROM tracks
                WHERE track_id = ?
            """, (track_id,))
            track_info = cursor_songs.fetchone()

            if track_info:
                min_max_values['duration_ms'].append(track_info[0])
                min_max_values['popularity'].append(track_info[1])
                min_max_values['acousticness'].append(track_info[2])
                min_max_values['danceability'].append(track_info[3])
                min_max_values['energy'].append(track_info[4])
                min_max_values['instrumentalness'].append(track_info[5])
                min_max_values['key'].append(track_info[6])
                min_max_values['liveness'].append(track_info[7])
                min_max_values['loudness'].append(track_info[8])
                min_max_values['mode'].append(track_info[9])
                min_max_values['speechiness'].append(track_info[10])
                min_max_values['tempo'].append(track_info[11])
                min_max_values['time_signature'].append(track_info[12])
                min_max_values['valence'].append(track_info[13])
                min_max_values['artist_ids'].extend(track_info[14].split(','))

                # Fetch genres for each artist in the track
                for artist_id in track_info[14].split(','):
                    cursor_songs.execute(
                        "SELECT artist_genres FROM artists WHERE artist_id = ?", (artist_id,))
                    artist_genres = cursor_songs.fetchone()
                    if artist_genres:
                        min_max_values['genres'].extend(
                            artist_genres[0].split(','))

                # Update track weight
                update_track_weight(cursor_playlists, track_id)

        if min_max_values['duration_ms']:
            # Get the most common artist ID
            most_artist_id = max(
                set(min_max_values['artist_ids']), key=min_max_values['artist_ids'].count)

            # Get the top 5 most common genres
            genre_counts = Counter(min_max_values['genres'])
            most_genres = ",".join(
                [genre for genre, count in genre_counts.most_common(5)])

            cursor_playlists.execute("""
                UPDATE playlists SET
                    min_duration_ms = ?, max_duration_ms = ?, min_popularity = ?, max_popularity = ?, 
                    min_acousticness = ?, max_acousticness = ?, min_danceability = ?, max_danceability = ?, 
                    min_energy = ?, max_energy = ?, min_instrumentalness = ?, max_instrumentalness = ?, 
                    min_key = ?, max_key = ?, min_liveness = ?, max_liveness = ?, 
                    min_loudness = ?, max_loudness = ?, min_mode = ?, max_mode = ?, 
                    min_speechiness = ?, max_speechiness = ?, min_tempo = ?, max_tempo = ?, 
                    min_time_signature = ?, max_time_signature = ?, min_valence = ?, max_valence = ?, 
                    most_artist_id = ?, most_genres = ?, fetched_track_count = ?
                WHERE playlist_id = ?
            """, (
                min(min_max_values['duration_ms']), max(
                    min_max_values['duration_ms']),
                min(min_max_values['popularity']), max(
                    min_max_values['popularity']),
                min(min_max_values['acousticness']), max(
                    min_max_values['acousticness']),
                min(min_max_values['danceability']), max(
                    min_max_values['danceability']),
                min(min_max_values['energy']), max(min_max_values['energy']),
                min(min_max_values['instrumentalness']), max(
                    min_max_values['instrumentalness']),
                min(min_max_values['key']), max(min_max_values['key']),
                min(min_max_values['liveness']), max(
                    min_max_values['liveness']),
                min(min_max_values['loudness']), max(
                    min_max_values['loudness']),
                min(min_max_values['mode']), max(min_max_values['mode']),
                min(min_max_values['speechiness']), max(
                    min_max_values['speechiness']),
                min(min_max_values['tempo']), max(min_max_values['tempo']),
                min(min_max_values['time_signature']), max(
                    min_max_values['time_signature']),
                min(min_max_values['valence']), max(min_max_values['valence']),
                most_artist_id, most_genres, len(track_ids), playlist_id
            ))
        else:
            print(f"No track information found for playlist {playlist_id}")

    conn_playlists.commit()
    conn_playlists.close()
    conn_songs.close()

    print("Finished updating playlists with audio feature data.")


if __name__ == "__main__":
    fill_playlists_table()

print("Scrape completed.")
