import sqlite3
import configparser

# Read configuration file
config = configparser.ConfigParser()
config.read('config.cfg')

MODEL = 'Collaborative Filtering'
DB = config['rs']['db_path']
OUTPUT_PATH = config['rs']['cbf_output']


def cf(input_ids):
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    # Fetch song details for the given input IDs
    inputted_songs = []
    for song_id in input_ids:
        cursor.execute("""
        SELECT s.song_id, s.song_name, s.artist_ids, s.acousticness, s.danceability, s.energy,
               s.instrumentalness, s.key, s.liveness, s.loudness, s.mode, s.speechiness,
               s.tempo, s.time_signature, s.valence, a.artist_name, a.artist_genres
        FROM songs s
        JOIN artists a ON instr(s.artist_ids, a.artist_id) > 0
        WHERE s.song_id = ?
        """, (song_id,))

        row = cursor.fetchone()
        if row:
            song_info = {
                "song_id": row[0],
                "song_name": row[1],
                "artist_name": row[15],
                "artist_genres": row[16],
                "features": row[3:15]
            }
            inputted_songs.append(song_info)

    # Build the formatted input list
    input_results = []
    for song in inputted_songs:
        song_url = f"https://open.spotify.com/track/{song['song_id']}"
        artist_genres = song['artist_genres'].replace(",", ", ")
        features = ", ".join([f"{name}: {value}" for name, value in zip(
            ["Acousticness", "Danceability", "Energy", "Instrumentalness", "Key",
             "Liveness", "Loudness", "Mode", "Speechiness", "Tempo",
             "Time Signature", "Valence"], song["features"]
        )])
        formatted_song = f"{song_url} {
            song['artist_name']} - {song['song_name']} | Genre: {artist_genres} | {features}"
        input_results.append(formatted_song)

    # Fetch playlist details and build recommendations
    cursor.execute("SELECT playlist_id, playlist_items FROM playlists")
    playlists = cursor.fetchall()

    song_occurrences = {}
    for playlist_id, playlist_items in playlists:
        playlist_songs = playlist_items.split(",")
        for song_id in playlist_songs:
            if song_id in song_occurrences:
                song_occurrences[song_id]['count'] += 1
                song_occurrences[song_id]['playlists'].append(playlist_id)
            else:
                cursor.execute("""
                SELECT s.song_id, s.song_name, s.artist_ids, s.acousticness, s.danceability, s.energy,
                       s.instrumentalness, s.key, s.liveness, s.loudness, s.mode, s.speechiness,
                       s.tempo, s.time_signature, s.valence, a.artist_name, a.artist_genres
                FROM songs s
                JOIN artists a ON instr(s.artist_ids, a.artist_id) > 0
                WHERE s.song_id = ?
                """, (song_id,))

                row = cursor.fetchone()
                if row:
                    song_occurrences[song_id] = {
                        "song_name": row[1],
                        "artist_name": row[15],
                        "artist_genres": row[16],
                        "features": row[3:15],
                        "count": 1,
                        "playlists": [playlist_id]
                    }

    # Build the formatted recommendation list
    recommendation_results = []
    for song_id, data in song_occurrences.items():
        song_url = f"https://open.spotify.com/track/{song_id}"
        artist_genres = data['artist_genres'].replace(",", ", ")
        features = ", ".join([f"{name}: {value}" for name, value in zip(
            ["Acousticness", "Danceability", "Energy", "Instrumentalness", "Key",
             "Liveness", "Loudness", "Mode", "Speechiness", "Tempo",
             "Time Signature", "Valence"], data["features"]
        )])
        formatted_song = f"{song_url} {data['artist_name']} - {data['song_name']} | Genre: {
            artist_genres} | {features} | Count: {data['count']} | From: {data['playlists']}"
        recommendation_results.append(formatted_song)

    # Write results to the output file
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as output_file:
        output_file.write("INPUTTED IDS\n")
        for result in input_results:
            output_file.write(f"{result}\n")

        output_file.write("\nSONGS RECOMMENDATION\n")
        for result in recommendation_results:
            output_file.write(f"{result}\n")

    conn.close()
    print('Result for', MODEL, 'stored at', OUTPUT_PATH)


if __name__ == "__main__":
    ids = ['6EIMUjQ7Q8Zr2VtIUik4He',
           '30Z12rJpW0M0u8HMFpigTB', '3wlLknnMtD8yZ0pCtCeeK4']
    cf(ids)
