import time
import sqlite3
import configparser
import spotipy
import requests
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.exceptions import SpotifyException
from bs4 import BeautifulSoup
import re
import os
from collections import Counter
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.tag import pos_tag

# Load configuration
config = configparser.ConfigParser()
config.read('config.cfg')

SPOTIPY_CLIENT_ID = config['spotify']['client_id']
SPOTIPY_CLIENT_SECRET = config['spotify']['client_secret']
GENIUS_API_TOKEN = config['genius']['api_token']
DELAY_TIME = float(config['api']['delay_time'])

user_ids = ['angelakatarina1001', '2oxec3r349m2x7mdwl9u0k7xi', '88qhmnsnyewlgfh4reytf1bqo', '31ryqvo6cyfciehwvqkjtwa3nt44', '31xyna5wagkylrcwc6wiio4tu5ji', '21vzd5cyqwwmnc4usgf24yzjy', 'piwz3bc0dmv9z1wduk24z2nn7',
            '314vs32d6vzvjnxxto7ye4x6tneu', '317t2q2dztovfc2yzufh5ktt5jee', '31pvgypjnvjxyooliqcyarhfeahu', '12162238821', '3154bolg6t7edowci4kbhgwx447u', 'hae3zzfwdxlqb7jhwyxghvqd1']  # Add Spotify user IDs here

client_credentials_manager = SpotifyClientCredentials(
    client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

# SQLite database file paths
playlists_db_path = config['db']['playlists_db']
songs_db_path = config['db']['songs_db']
fetched_lyrics_path = 'data/cache/fetched_lyrics.txt'

headers = {
    'Authorization': f'Bearer {GENIUS_API_TOKEN}'
}


def create_connection(db_file):
    try:
        return sqlite3.connect(db_file)
    except sqlite3.Error as e:
        print(f"Error connecting to database: {e}")
        return None


def insert_track_id_into_lyrics(cursor, track_id):
    cursor.execute(
        "INSERT OR IGNORE INTO lyrics (track_id) VALUES (?)", (track_id,))


def store_playlist_details(cursor, playlist_id, user_id, track_count):
    cursor.execute('''
        INSERT OR IGNORE INTO playlists (playlist_id, creator_id, original_track_count)
        VALUES (?, ?, ?)
    ''', (playlist_id, user_id, track_count))


def store_playlist_items(cursor, playlist_id, track_ids):
    playlist_items = ','.join(track_ids)
    cursor.execute('''
        INSERT OR REPLACE INTO items (playlist_id, playlist_items)
        VALUES (?, ?)
    ''', (playlist_id, playlist_items))


def store_track_details(cursor, track, audio_features):
    cursor.execute('''
        INSERT OR IGNORE INTO tracks (track_id, track_name, artist_ids, duration_ms, popularity, 
        acousticness, danceability, energy, instrumentalness, key, liveness, loudness, mode, 
        speechiness, tempo, time_signature, valence) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        track['id'], track['name'], ",".join(
            [artist['id'] for artist in track['artists']]),
        track['duration_ms'], track['popularity'], audio_features['acousticness'],
        audio_features['danceability'], audio_features['energy'],
        audio_features['instrumentalness'], audio_features['key'],
        audio_features['liveness'], audio_features['loudness'], audio_features['mode'],
        audio_features['speechiness'], audio_features['tempo'],
        audio_features['time_signature'], audio_features['valence']
    ))
    insert_track_id_into_lyrics(cursor, track['id'])


def store_artist_details(cursor, artist, fetched_artist_ids):
    cursor.execute('SELECT 1 FROM artists WHERE artist_id = ?',
                   (artist['id'],))
    if cursor.fetchone():
        fetched_artist_ids.add(artist['id'])
        return

    artist_info = sp.artist(artist['id'])
    cursor.execute('''
        INSERT OR IGNORE INTO artists (artist_id, artist_name, artist_genres) 
        VALUES (?, ?, ?)
    ''', (artist['id'], artist_info['name'], ",".join(artist_info['genres'])))
    fetched_artist_ids.add(artist['id'])


def fetch_and_store_playlist_data(user_id, conn_playlists, conn_songs):
    try:
        offset = 0
        limit = 1
        fetched_playlist_ids = set()
        fetched_artist_ids = set()

        while True:
            playlists = sp.user_playlists(user_id, offset=offset, limit=limit)
            if not playlists['items']:
                break

            for playlist in playlists['items']:
                if playlist['public']:
                    playlist_id = playlist['id']
                    if playlist_id in fetched_playlist_ids:
                        continue

                    fetched_playlist_ids.add(playlist_id)

                    playlist_details = sp.playlist(playlist_id)
                    if playlist_details['tracks']['total'] <= 5:
                        print(f"Skipping playlist {
                              playlist_id}, not enough tracks.")
                        continue

                    cursor = conn_playlists.cursor()
                    store_playlist_details(
                        cursor, playlist_id, user_id, playlist_details['tracks']['total'])

                    track_ids = [track['track']['id'] for track in playlist_details['tracks']
                                 ['items'][:24] if track['track']['id'] is not None]
                    if not track_ids:
                        continue

                    store_playlist_items(cursor, playlist_id, track_ids)
                    conn_playlists.commit()

                    track_data = sp.tracks(track_ids)
                    audio_features_list = sp.audio_features(track_ids)

                    for track, audio_features in zip(track_data['tracks'], audio_features_list):
                        if track is None or audio_features is None:
                            continue

                        if None in [track['id'], track['name'], track['duration_ms'], track['popularity'],
                                    audio_features['acousticness'], audio_features['danceability'],
                                    audio_features['energy'], audio_features['instrumentalness'],
                                    audio_features['key'], audio_features['liveness'],
                                    audio_features['loudness'], audio_features['mode'],
                                    audio_features['speechiness'], audio_features['tempo'],
                                    audio_features['time_signature'], audio_features['valence']]:
                            print(f"Skipping track {
                                  track['id']} due to missing data.")
                            continue

                        cursor = conn_songs.cursor()
                        store_track_details(cursor, track, audio_features)

                        for artist in track['artists']:
                            if artist['id'] not in fetched_artist_ids:
                                store_artist_details(
                                    cursor, artist, fetched_artist_ids)

                        conn_songs.commit()

                    print(f"Saved playlist details for {playlist_id}")
                    time.sleep(DELAY_TIME)

            offset += limit

    except SpotifyException as e:
        if e.http_status == 429:
            print(f"Rate limit exceeded for user: {user_id}")
        else:
            print(f"Spotify error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")


def get_lyrics_url(song_title, artist_name):
    search_url = "https://api.genius.com/search"
    params = {'q': f"{song_title} {artist_name}"}
    response = requests.get(search_url, headers=headers, params=params)

    if response.status_code != 200:
        print(f"Failed to fetch URL for {song_title} by {
              artist_name}. HTTP Status: {response.status_code}")
        return None

    try:
        response_data = response.json()
    except requests.exceptions.JSONDecodeError:
        print(f"Failed to parse JSON for {song_title} by {artist_name}")
        return None

    song_info = None
    if response_data['response']['hits']:
        for hit in response_data['response']['hits']:
            if artist_name.lower() in hit['result']['primary_artist']['name'].lower():
                song_info = hit
                break

    if song_info:
        return song_info['result']['url']
    else:
        return None


def get_lyrics_from_url(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    [h.extract() for h in soup(['script', 'style', 'br'])]

    lyrics = soup.find_all('div', class_='lyrics')
    if lyrics:
        return clean_lyrics(lyrics[0].get_text().strip())

    lyrics = soup.find_all(
        'div', class_=lambda x: x and 'Lyrics__Container' in x)
    if lyrics:
        return clean_lyrics('\n'.join([div.get_text().strip() for div in lyrics]))

    return None


def clean_lyrics(lyrics):
    lyrics = re.sub(r'\[.*?\]', ' ', lyrics)
    lyrics = re.sub(r'(?<=[a-z])(?=[A-Z])', ' ', lyrics)
    lyrics = re.sub(r'([?.!,])', r'\1 ', lyrics)
    lyrics = re.sub(r'\s+', ' ', lyrics)
    return lyrics.strip()


def clean_track_title(track_title):
    patterns = [
        r'\(.*?\)',
        r'\[.*?\]',
        r' - .*$',
        r'\b(remix|remaster(ed)?|version)\b',
        r'\d{4}',
    ]
    for pattern in patterns:
        track_title = re.sub(pattern, '', track_title, flags=re.IGNORECASE)
    return track_title.strip()


def extract_keywords(lyrics, max_keywords=50):
    stop_words = set(stopwords.words('english'))
    words = word_tokenize(lyrics.lower())
    filtered_words = [word for word in words if word.isalnum()
                      and word not in stop_words]
    tagged_words = pos_tag(filtered_words)
    keywords = [word for word, pos in tagged_words if pos in [
        'NN', 'NNS', 'NNP', 'NNPS', 'JJ']]

    most_common_keywords = [word for word, count in Counter(
        keywords).most_common(max_keywords)]
    return ', '.join(most_common_keywords)


def fetch_and_store_lyrics():
    with sqlite3.connect(songs_db_path) as conn:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT tracks.track_id, tracks.track_name, artists.artist_name
            FROM tracks
            JOIN artists ON tracks.artist_ids = artists.artist_id
            LEFT JOIN lyrics ON tracks.track_id = lyrics.track_id
            WHERE lyrics.lyrics IS NULL
        """)

        tracks = cursor.fetchall()

        if os.path.exists(fetched_lyrics_path):
            with open(fetched_lyrics_path, 'r') as f:
                fetched_track_ids = set(f.read().splitlines())
        else:
            fetched_track_ids = set()

        for track_id, track_name, artist_name in tracks:
            if track_id in fetched_track_ids:
                print(f"Skipping {track_name} by {
                      artist_name}, already fetched.")
                continue

            cleaned_track_name = clean_track_title(track_name)
            print(f"Fetching lyrics for {cleaned_track_name} by {artist_name}")
            lyrics_url = get_lyrics_url(cleaned_track_name, artist_name)
            if lyrics_url:
                lyrics = get_lyrics_from_url(lyrics_url)
                if lyrics:
                    keywords = extract_keywords(lyrics)
                    cursor.execute("""
                        INSERT OR REPLACE INTO lyrics (track_id, lyrics, keywords)
                        VALUES (?, ?, ?)
                    """, (track_id, lyrics, keywords))
                    conn.commit()
                    print(f"Lyrics fetched and stored for {
                          cleaned_track_name}")
                else:
                    print(f"Lyrics not found for {cleaned_track_name}")
            else:
                print(f"Lyrics URL not found for {cleaned_track_name}")

            with open(fetched_lyrics_path, 'a') as f:
                f.write(f"{track_id}\n")

            fetched_track_ids.add(track_id)


def main():
    fetched_users_file = config['file']['fetched_users']
    fetched_users = set()

    try:
        with open(fetched_users_file, 'r') as f:
            fetched_users.update(f.read().splitlines())
    except FileNotFoundError:
        pass

    conn_playlists = create_connection(playlists_db_path)
    conn_songs = create_connection(songs_db_path)

    if conn_playlists is None or conn_songs is None:
        print("Error! Cannot create the database connections.")
        return

    for user_id in user_ids:
        if user_id in fetched_users:
            print(f"Skipping {user_id}, already fetched.")
            continue

        fetch_and_store_playlist_data(user_id, conn_playlists, conn_songs)
        fetched_users.add(user_id)

        with open(fetched_users_file, 'a') as f:
            f.write(user_id + '\n')

    fetch_and_store_lyrics()

    conn_playlists.close()
    conn_songs.close()

    print("Playlist scraping and lyrics fetching completed.")


if __name__ == "__main__":
    main()
