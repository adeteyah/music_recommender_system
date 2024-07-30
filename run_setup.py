import sqlite3
import time
import subprocess
import sys
from pathlib import Path

start = time.time()


def install_directories():
    directories = [
        "data/",
        "result/"
    ]
    for directory in directories:
        path = Path(directory)
        path.mkdir(parents=True, exist_ok=True)


def create_database(db_path, schema, views):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.executescript(schema)
        cursor.executescript(views)
        conn.commit()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        if conn:
            conn.close()


schema = """
CREATE TABLE IF NOT EXISTS artists (
    artist_id TEXT PRIMARY KEY,
    artist_name TEXT,
    artist_genres TEXT
);

CREATE INDEX IF NOT EXISTS idx_artists_artist_name ON artists (artist_name);

CREATE TABLE IF NOT EXISTS songs (
    song_id TEXT PRIMARY KEY,
    song_name TEXT,
    artist_ids TEXT,
    acousticness REAL,
    danceability REAL,
    energy REAL,
    instrumentalness REAL,
    key INTEGER,
    liveness REAL,
    loudness REAL,
    mode INTEGER,
    speechiness REAL,
    tempo REAL,
    time_signature INTEGER,
    valence REAL
);

CREATE INDEX IF NOT EXISTS idx_songs_song_name ON songs (song_name);
CREATE INDEX IF NOT EXISTS idx_songs_artist_ids ON songs (artist_ids);

CREATE TABLE IF NOT EXISTS playlists (
    playlist_id TEXT PRIMARY KEY,
    playlist_creator_id TEXT,
    playlist_original_items INTEGER,
    playlist_items_fetched INTEGER,
    playlist_top_artist_ids TEXT,
    playlist_top_genres TEXT,
    playlist_items TEXT,
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
    max_valence REAL
);

CREATE INDEX IF NOT EXISTS idx_playlists_playlist_creator_id ON playlists (playlist_creator_id);
CREATE INDEX IF NOT EXISTS idx_playlists_playlist_top_artist_ids ON playlists (playlist_top_artist_ids);
"""

views = """
CREATE VIEW IF NOT EXISTS view_song_details AS
SELECT
    s.song_id,
    s.song_name,
    s.artist_ids,
    a.artist_name,
    s.acousticness,
    s.danceability,
    s.energy,
    s.instrumentalness,
    s.key,
    s.liveness,
    s.loudness,
    s.mode,
    s.speechiness,
    s.tempo,
    s.time_signature,
    s.valence
FROM songs s
LEFT JOIN artists a ON s.artist_ids = a.artist_id;
"""


def install_packages(packages):
    for package in packages:
        try:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", package])
        except subprocess.CalledProcessError as e:
            print(f"Error installing package {package}: {e}")


if __name__ == "__main__":
    install_directories()
    packages = ["configparser", "requests", "spotipy",
                "pandas", "numpy", "matplotlib", "seaborn"]
    # install_packages(packages)
    create_database("data/main.db", schema, views)

end = time.time()
print("\nExecution time: ", end - start)
