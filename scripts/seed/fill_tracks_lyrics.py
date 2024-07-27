import sqlite3
import requests
import configparser
from bs4 import BeautifulSoup
import re
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

# Load configuration
config = configparser.ConfigParser()
config.read('config.cfg')

GENIUS_API_TOKEN = config['genius']['api_token']
songs_db_path = config['db']['songs_db']
fetched_lyrics_path = 'data/cache/fetched_lyrics.txt'

headers = {
    'Authorization': f'Bearer {GENIUS_API_TOKEN}'
}


def get_lyrics_url(song_title, artist_name):
    search_url = "https://api.genius.com/search"
    params = {'q': f"{song_title} {artist_name}"}
    response = requests.get(search_url, headers=headers, params=params)
    response_data = response.json()

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
    # Remove bracketed sections and replace with new lines
    lyrics = re.sub(r'\[.*?\]', '\n', lyrics)
    # Replace multiple newlines with a single newline
    lyrics = re.sub(r'\n+', '\n', lyrics)
    return lyrics.strip()


def clean_track_title(track_title):
    # Patterns to remove from the track title
    patterns = [
        r'\(.*?\)',          # Anything in parentheses
        r'\[.*?\]',          # Anything in square brackets
        r' - .*$',           # Anything after ' - '
        # Words like 'remix', 'remastered', etc.
        r'\b(remix|remaster(ed)?|version)\b',
        r'\d{4}',            # Any 4-digit year
    ]
    for pattern in patterns:
        track_title = re.sub(pattern, '', track_title, flags=re.IGNORECASE)
    return track_title.strip()


def fetch_and_store_lyrics():
    with sqlite3.connect(songs_db_path) as conn:
        cursor = conn.cursor()

        # Fetch tracks that need lyrics
        cursor.execute("""
            SELECT tracks.track_id, tracks.track_name, artists.artist_name
            FROM tracks
            JOIN artists ON tracks.artist_ids = artists.artist_id
            LEFT JOIN lyrics ON tracks.track_id = lyrics.track_id
            WHERE lyrics.lyrics IS NULL
        """)

        tracks = cursor.fetchall()

        # Read fetched track IDs
        if os.path.exists(fetched_lyrics_path):
            with open(fetched_lyrics_path, 'r') as f:
                fetched_track_ids = set(f.read().splitlines())
        else:
            fetched_track_ids = set()

        def fetch_lyrics(track):
            track_id, track_name, artist_name = track
            if track_id in fetched_track_ids:
                return None

            cleaned_track_name = clean_track_title(track_name)
            print(f"Fetching lyrics for {cleaned_track_name} by {artist_name}")
            lyrics_url = get_lyrics_url(cleaned_track_name, artist_name)
            if lyrics_url:
                lyrics = get_lyrics_from_url(lyrics_url)
                if lyrics:
                    keywords = ', '.join(
                        [word for word in track_name.split()] + [word for word in artist_name.split()])
                    return (track_id, lyrics, keywords)
                else:
                    print(f"Lyrics not found for {cleaned_track_name}")
            else:
                print(f"Lyrics URL not found for {cleaned_track_name}")
            return None

        results = []
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(fetch_lyrics, track)
                       for track in tracks]
            for future in as_completed(futures):
                result = future.result()
                if result:
                    results.append(result)
                    fetched_track_ids.add(result[0])

        # Insert fetched lyrics into database in a single transaction
        cursor.executemany("""
            INSERT OR REPLACE INTO lyrics (track_id, lyrics, keywords)
            VALUES (?, ?, ?)
        """, results)
        conn.commit()

        # Update fetched lyrics file
        with open(fetched_lyrics_path, 'a') as f:
            for track_id in fetched_track_ids:
                f.write(f"{track_id}\n")


if __name__ == "__main__":
    fetch_and_store_lyrics()
    print("Finished fetching and storing lyrics.")
