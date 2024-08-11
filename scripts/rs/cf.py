import sqlite3
import configparser

# Read configuration file
config = configparser.ConfigParser()
config.read('config.cfg')

MODEL = 'Collaborative Filtering'
DB = config['rs']['db_path']
OUTPUT_PATH = config['rs']['cf_output']


def cf(inputted_ids):
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    results = []
    recommendations = {}

    # Step 1: Process each inputted song ID
    for song_id in inputted_ids:
        # Fetch song details
        cursor.execute("""
            SELECT s.song_id, s.song_name, s.artist_ids, s.acousticness, s.danceability, 
                   s.energy, s.instrumentalness, s.key, s.liveness, s.loudness, 
                   s.mode, s.speechiness, s.tempo, s.time_signature, s.valence,
                   a.artist_name, a.artist_genres
            FROM songs s
            JOIN artists a ON a.artist_id = s.artist_ids
            WHERE s.song_id = ?
        """, (song_id,))
        song = cursor.fetchone()

        if song:
            # Format the song's output
            artist_name = song[15]
            artist_genres = song[16]
            song_info = (f"https://open.spotify.com/track/{song[0]} {artist_name} - {song[1]} | Genre: {artist_genres} "
                         f"| Acousticness: {song[3]}, Danceability: {
                             song[4]}, Energy: {song[5]}, "
                         f"Instrumentalness: {song[6]}, Key: {
                             song[7]}, Liveness: {song[8]}, "
                         f"Loudness: {song[9]}, Mode: {
                             song[10]}, Speechiness: {song[11]}, "
                         f"Tempo: {song[12]}, Time Signature: {song[13]}, Valence: {song[14]}")
            results.append(song_info)

            # Step 2: Find all playlists containing this song
            cursor.execute("""
                SELECT playlist_id, playlist_creator_id, playlist_items
                FROM playlists
                WHERE ? IN (SELECT value FROM json_each(playlist_items))
            """, (song_id,))
            playlists = cursor.fetchall()

            if playlists:
                for playlist in playlists:
                    playlist_info = f"{playlist[0]} by {playlist[1]}"
                    results.append(playlist_info)

                    # Step 3: Collect other songs in these playlists for recommendations
                    playlist_songs = playlist[2].split(',')
                    for other_song_id in playlist_songs:
                        if other_song_id != song_id:
                            if other_song_id not in recommendations:
                                recommendations[other_song_id] = {
                                    'count': 1, 'playlists': [playlist[0]]}
                            else:
                                recommendations[other_song_id]['count'] += 1
                                recommendations[other_song_id]['playlists'].append(
                                    playlist[0])

    # Step 4: Format and append the recommendation results
    for inputted_song_info in results:
        inputted_song_id = inputted_song_info.split()[0].split('/')[-1]
        results.append(f"\nSONGS RECOMMENDATION for {inputted_song_info}")

        for rec_song_id, rec_data in recommendations.items():
            # Fetch recommended song details
            cursor.execute("""
                SELECT s.song_id, s.song_name, s.artist_ids, s.acousticness, s.danceability, 
                       s.energy, s.instrumentalness, s.key, s.liveness, s.loudness, 
                       s.mode, s.speechiness, s.tempo, s.time_signature, s.valence,
                       a.artist_name, a.artist_genres
                FROM songs s
                JOIN artists a ON a.artist_id = s.artist_ids
                WHERE s.song_id = ?
            """, (rec_song_id,))
            rec_song = cursor.fetchone()

            if rec_song:
                rec_artist_name = rec_song[15]
                rec_artist_genres = rec_song[16]
                rec_info = (f"https://open.spotify.com/track/{rec_song[0]} {rec_artist_name} - {rec_song[1]} | "
                            f"Genre: {rec_artist_genres} | Acousticness: {
                                rec_song[3]}, "
                            f"Danceability: {rec_song[4]}, Energy: {
                                rec_song[5]}, Instrumentalness: {rec_song[6]}, "
                            f"Key: {rec_song[7]}, Liveness: {
                                rec_song[8]}, Loudness: {rec_song[9]}, "
                            f"Mode: {rec_song[10]}, Speechiness: {
                                rec_song[11]}, Tempo: {rec_song[12]}, "
                            f"Time Signature: {
                                rec_song[13]}, Valence: {rec_song[14]} "
                            f"| Count: {rec_data['count']} | From: {rec_data['playlists']}")
                results.append(rec_info)

    # Write the results to the output file
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as file:
        for result in results:
            file.write(result + '\n')

    conn.close()
    print(f'Result for {MODEL} stored at {OUTPUT_PATH}')


if __name__ == "__main__":
    ids = ['6EIMUjQ7Q8Zr2VtIUik4He',
           '30Z12rJpW0M0u8HMFpigTB', '3wlLknnMtD8yZ0pCtCeeK4']
    cf(ids)
