import sqlite3
import requests
import configparser
from bs4 import BeautifulSoup

# Load configuration
config = configparser.ConfigParser()
config.read('config.cfg')

GENIUS_API_TOKEN = config['genius']['api_token']
songs_db_path = config['db']['songs_db']

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
        return lyrics[0].get_text().strip()

    lyrics = soup.find_all(
        'div', class_=lambda x: x and 'Lyrics__Container' in x)
    if lyrics:
        return '\n'.join([div.get_text().strip() for div in lyrics])

    return None


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

        for track_id, track_name, artist_name in tracks:
            print(f"Fetching lyrics for {track_name} by {artist_name}")
            lyrics_url = get_lyrics_url(track_name, artist_name)
            if lyrics_url:
                lyrics = get_lyrics_from_url(lyrics_url)
                if lyrics:
                    keywords = ', '.join(
                        [word for word in track_name.split()] + [word for word in artist_name.split()])
                    cursor.execute("""
                        INSERT OR REPLACE INTO lyrics (track_id, lyrics, keywords)
                        VALUES (?, ?, ?)
                    """, (track_id, lyrics, keywords))
                    conn.commit()
                    print(f"Lyrics fetched and stored for {track_name}")
                else:
                    print(f"Lyrics not found for {track_name}")
            else:
                print(f"Lyrics URL not found for {track_name}")


if __name__ == "__main__":
    fetch_and_store_lyrics()
    print("Finished fetching and storing lyrics.")
