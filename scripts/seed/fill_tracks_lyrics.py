import sqlite3
import requests
import configparser
from bs4 import BeautifulSoup
import re
import os
import time
from collections import Counter
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# Load configuration
config = configparser.ConfigParser()
config.read('config.cfg')

GENIUS_API_TOKEN = config['genius']['api_token']
songs_db_path = config['db']['songs_db']
fetched_lyrics_path = 'data/cache/fetched_lyrics.txt'

headers = {
    'Authorization': f'Bearer {GENIUS_API_TOKEN}'
}

stop_words = set(stopwords.words('english'))


def get_lyrics_url(song_title, artist_name):
    search_url = "https://api.genius.com/search"
    params = {'q': f"{song_title} {artist_name}"}
    retries = 3
    while retries > 0:
        response = requests.get(search_url, headers=headers, params=params)
        if response.status_code == 200:
            try:
                response_data = response.json()
                break
            except requests.exceptions.JSONDecodeError:
                print("Error decoding JSON, retrying...")
                retries -= 1
                time.sleep(1)
        else:
            print(f"Error fetching URL for {song_title} by {
                  artist_name}: {response.status_code}")
            retries -= 1
            time.sleep(1)
    else:
        print(f"Failed to fetch URL after retries for {
              song_title} by {artist_name}")
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
    retries = 3
    while retries > 0:
        response = requests.get(url)
        if response.status_code == 200:
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
        else:
            print(f"Error fetching lyrics from URL {
                  url}: {response.status_code}")
            retries -= 1
            time.sleep(1)
    print(f"Failed to fetch lyrics after retries from URL {url}")
    return None


def clean_lyrics(lyrics):
   # Remove bracketed sections and replace with a space
    lyrics = re.sub(r'\[.*?\]', ' ', lyrics)
    # Insert a newline before an uppercase letter that is in the middle of a word
    lyrics = re.sub(r'(?<=[a-z])(?=[A-Z])', '\n', lyrics)
    # Ensure there is a space after punctuation marks
    lyrics = re.sub(r'([?.!,])', r'\1 ', lyrics)
    # Replace multiple spaces with a single space to clean up any extra spaces left by the replacement
    lyrics = re.sub(r'\s+', ' ', lyrics)
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


def extract_keywords(lyrics):
    words = word_tokenize(lyrics)
    words = [word.lower() for word in words if word.isalpha()]
    filtered_words = [word for word in words if word not in stop_words]
    tagged_words = nltk.pos_tag(filtered_words)
    nouns = [word for word, pos in tagged_words if pos.startswith('NN')]

    # Count the most common nouns
    noun_counts = Counter(nouns)
    most_common_nouns = noun_counts.most_common(50)
    keywords = [word for word, count in most_common_nouns]

    return ', '.join(keywords)


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

                    # Append the track ID to the fetched lyrics file
                    with open(fetched_lyrics_path, 'a') as f:
                        f.write(f"{track_id}\n")

                    fetched_track_ids.add(track_id)
                else:
                    print(f"Lyrics not found for {cleaned_track_name}")
            else:
                print(f"Lyrics URL not found for {cleaned_track_name}")


if __name__ == "__main__":
    fetch_and_store_lyrics()
    print("Finished fetching and storing lyrics.")
