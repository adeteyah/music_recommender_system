import nltk
import sqlite3
import time
import subprocess
import sys
from pathlib import Path

start = time.time()


def install_directories():
    directories = [
        "data/cache",
        "data/db",
        "result/"
    ]

    files = [
        "data/cache/fetched_users.txt",  # store scraped users
        "data/cache/fetched_lyrics.txt",  # store scraped users
        "data/db/playlists_details.db",  # store playlist characteristic
        "data/db/songs_details.db"  # store title and artists id, artist name and genres
    ]

    for directory in directories:
        path = Path(directory)
        path.mkdir(parents=True, exist_ok=True)

    for file in files:
        path = Path(file)
        if not path.exists():
            path.touch()


def create_database(db_path, schema):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.executescript(schema)
    conn.commit()
    conn.close()


songs_schema = """
CREATE TABLE IF NOT EXISTS artists (
    artist_id TEXT PRIMARY KEY,
    artist_name TEXT,
    artist_genres TEXT
);

CREATE INDEX IF NOT EXISTS idx_artists_artist_id ON artists (artist_id);

CREATE TABLE IF NOT EXISTS tracks (
    track_id TEXT PRIMARY KEY,
    artist_ids TEXT,
    track_name TEXT,
    duration_ms INTEGER,
    popularity REAL,
    acousticness REAL,
    danceability REAL,
    energy REAL,
    instrumentalness REAL,
    key INTEGER,
    liveness REAL,
    loudness REAL,
    mode REAL,
    speechiness REAL,
    tempo REAL,
    time_signature INTEGER,
    valence REAL,
    in_playlist_count INTEGER,
    most_related_artist_genres TEXT,

);
CREATE INDEX IF NOT EXISTS idx_tracks_track_id ON tracks (track_id);
"""

playlist_schema = """
CREATE TABLE IF NOT EXISTS playlists (
    playlist_id TEXT PRIMARY KEY,
    creator_id TEXT,
    original_track_count INTEGER,
    fetched_track_count INTEGER,
    min_duration_ms INTEGER,
    max_duration_ms INTEGER,
    min_popularity REAL,
    max_popularity REAL,
    min_acousticness REAL,
    max_acousticness REAL,
    min_danceability REAL,
    max_danceability REAL,
    min_energy REAL,
    max_energy REAL,
    min_instrumentalness REAL,
    max_instrumentalness REAL,
    min_key INTEGER,
    max_key INTEGER,
    min_liveness REAL,
    max_liveness REAL,
    min_loudness REAL,
    max_loudness REAL,
    min_mode INTEGER,
    max_mode INTEGER,
    min_speechiness REAL,
    max_speechiness REAL,
    min_tempo REAL,
    max_tempo REAL,
    min_time_signature INTEGER,
    max_time_signature INTEGER,
    min_valence REAL,
    max_valence REAL,
    most_artist_id TEXT,
    most_genres TEXT
);

CREATE INDEX IF NOT EXISTS idx_playlist_id ON playlists (playlist_id);
CREATE INDEX IF NOT EXISTS idx_creator_id ON playlists (creator_id);

CREATE TABLE IF NOT EXISTS items (
    playlist_id TEXT PRIMARY KEY,
    playlist_items TEXT
);

CREATE INDEX IF NOT EXISTS idx_playlist_id ON items (playlist_id);
CREATE INDEX IF NOT EXISTS idx_playlist_items ON items (playlist_items);
"""


def install_packages(packages):
    for package in packages:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", package])


if __name__ == "__main__":
    install_directories()
    packages = ["configparser", "requests", "spotipy",
                "pandas", "numpy", "matplotlib", "seaborn", "nltk"]
    install_packages(packages)
    create_database("data/db/songs_details.db", songs_schema)
    create_database("data/db/playlists_details.db", playlist_schema)

end = time.time()
print("\nExecution time: ", end - start)
