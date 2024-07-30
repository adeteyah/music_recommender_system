import sqlite3
import configparser
from collections import Counter

config = configparser.ConfigParser()
config.read('config.cfg')

songs_db_path = config['db']['songs_db']
playlists_db_path = config['db']['playlists_db']


def update_track_weight(cursor, track_id):
    query = """
        INSERT INTO tracks (track_id, track_count_in_playlist) VALUES (?, 1)
        ON CONFLICT(track_id) DO UPDATE SET track_count_in_playlist = track_count_in_playlist + 1
    """
    cursor.execute(query, (track_id,))


def delete_empty_playlist_feature(cursor):
    query = "DELETE FROM playlists WHERE playlist_most_artist_id IS NULL"
    cursor.execute(query)


def calculate_track_genres(cursor_songs, track_ids):
    genres = []
    for track_id in track_ids:
        cursor_songs.execute("""
            SELECT artist_ids FROM tracks WHERE track_id = ?
        """, (track_id,))
        artist_ids = cursor_songs.fetchone()
        if artist_ids:
            for artist_id in artist_ids[0].split(','):
                cursor_songs.execute("""
                    SELECT artist_genres FROM artists WHERE artist_id = ?
                """, (artist_id,))
                artist_genres = cursor_songs.fetchone()
                if artist_genres:
                    genres.extend(artist_genres[0].split(','))
    genre_counts = Counter(genres)
    top_genres = [genre for genre, count in genre_counts.most_common(20)]
    return ",".join(top_genres)


def calculate_track_moods(cursor_songs, track_id):
    cursor_songs.execute("""
        SELECT acousticness, danceability, energy, instrumentalness, liveness, loudness, speechiness, valence
        FROM tracks WHERE track_id = ?
    """, (track_id,))
    features = cursor_songs.fetchone()
    if features:
        moods = {
            'happy': features[7],  # valence
            'energetic': features[2],  # energy
            'danceable': features[1],  # danceability
            'acoustic': features[0]  # acousticness
        }
        return ",".join([k for k, v in moods.items() if v > 0.5])
    return ""


def fill_playlists_table():
    with sqlite3.connect(playlists_db_path) as conn_playlists, \
            sqlite3.connect(songs_db_path) as conn_songs:

        cursor_playlists = conn_playlists.cursor()
        cursor_songs = conn_songs.cursor()

        cursor_playlists.execute(
            "SELECT playlist_id, playlist_items FROM items")
        playlists = cursor_playlists.fetchall()

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
                'genres': [],
                'moods': []
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
                    (duration_ms, popularity, acousticness, danceability, energy,
                     instrumentalness, key, liveness, loudness, mode,
                     speechiness, tempo, time_signature, valence, artist_ids) = track_info

                    min_max_values['duration_ms'].append(duration_ms)
                    min_max_values['popularity'].append(popularity)
                    min_max_values['acousticness'].append(acousticness)
                    min_max_values['danceability'].append(danceability)
                    min_max_values['energy'].append(energy)
                    min_max_values['instrumentalness'].append(instrumentalness)
                    min_max_values['key'].append(key)
                    min_max_values['liveness'].append(liveness)
                    min_max_values['loudness'].append(loudness)
                    min_max_values['mode'].append(mode)
                    min_max_values['speechiness'].append(speechiness)
                    min_max_values['tempo'].append(tempo)
                    min_max_values['time_signature'].append(time_signature)
                    min_max_values['valence'].append(valence)
                    min_max_values['artist_ids'].extend(artist_ids.split(','))

                    # Fetch genres for each artist in the track
                    for artist_id in artist_ids.split(','):
                        cursor_songs.execute(
                            "SELECT artist_genres FROM artists WHERE artist_id = ?", (artist_id,))
                        artist_genres = cursor_songs.fetchone()
                        if artist_genres:
                            min_max_values['genres'].extend(
                                artist_genres[0].split(','))

                    # Calculate track moods and add to min_max_values
                    track_moods = calculate_track_moods(cursor_songs, track_id)
                    if track_moods:
                        min_max_values['moods'].extend(track_moods.split(','))

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

                # Get the top 3 most common moods
                mood_counts = Counter(min_max_values['moods'])
                most_moods = ",".join(
                    [mood for mood, count in mood_counts.most_common(3)])

                cursor_playlists.execute("""
                    UPDATE playlists SET
                        min_duration_ms = ?, max_duration_ms = ?, min_popularity = ?, max_popularity = ?, 
                        min_acousticness = ?, max_acousticness = ?, min_danceability = ?, max_danceability = ?, 
                        min_energy = ?, max_energy = ?, min_instrumentalness = ?, max_instrumentalness = ?, 
                        min_key = ?, max_key = ?, min_liveness = ?, max_liveness = ?, 
                        min_loudness = ?, max_loudness = ?, min_mode = ?, max_mode = ?, 
                        min_speechiness = ?, max_speechiness = ?, min_tempo = ?, max_tempo = ?, 
                        min_time_signature = ?, max_time_signature = ?, min_valence = ?, max_valence = ?, 
                        playlist_most_artist_id = ?, playlist_most_genres = ?, playlist_most_moods = ?, 
                        fetched_track_count = ?
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
                    min(min_max_values['energy']), max(
                        min_max_values['energy']),
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
                    min(min_max_values['valence']), max(
                        min_max_values['valence']),
                    most_artist_id, most_genres, most_moods, len(
                        track_ids), playlist_id
                ))
            else:
                print(f"No track information found for playlist {playlist_id}")

        delete_empty_playlist_feature(cursor_playlists)
        conn_playlists.commit()


def update_tracks_table():
    with sqlite3.connect(songs_db_path) as conn_songs, \
            sqlite3.connect(playlists_db_path) as conn_playlists:

        cursor_songs = conn_songs.cursor()
        cursor_playlists = conn_playlists.cursor()

        cursor_songs.execute("SELECT track_id FROM tracks")
        tracks = cursor_songs.fetchall()

        for track_id, in tracks:
            cursor_playlists.execute("""
                SELECT playlist_items FROM items WHERE playlist_items LIKE ?
            """, (f'%{track_id}%',))
            playlists_containing_track = cursor_playlists.fetchall()

            if playlists_containing_track:
                playlist_ids = [playlist_items.split(
                    ',') for playlist_items, in playlists_containing_track]
                flattened_playlist_ids = [
                    item for sublist in playlist_ids for item in sublist]
                track_genres = calculate_track_genres(
                    cursor_songs, flattened_playlist_ids)
                track_moods = calculate_track_moods(cursor_songs, track_id)

                cursor_songs.execute("""
                    UPDATE tracks SET
                        track_count_in_playlist = ?,
                        track_genres = ?,
                        track_moods = ?
                    WHERE track_id = ?
                """, (len(playlists_containing_track), track_genres, track_moods, track_id))

        conn_songs.commit()


if __name__ == "__main__":
    fill_playlists_table()
    update_tracks_table()
    print("DONE")
