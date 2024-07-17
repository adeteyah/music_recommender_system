import sqlite3
import time
import subprocess
import sys
from pathlib import Path

start = time.time()


def install_directories():
    directories = [
        "data/cache",
        "data/raw",
        "data/transformed"
    ]

    files = [
        "data/cache/fetched_users.txt",  # store scraped users
        "data/cache/fetched_artists.txt",  # store scraped artists
        "data/cache/artists_table_cache.csv",  # store cache when fill songs db
        "data/cache/tracks_table_cache.csv",  # store cache when fill playlists db
        "data/db/playlists_details.db",  # store playlist characteristic
        "data/db/songs_details.db",  # store title and artists id, artist name and genres
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
    track_name TEXT,
    artist_ids TEXT
);

CREATE INDEX IF NOT EXISTS idx_tracks_track_id ON tracks (track_id);
"""

playlist_schema = """
CREATE TABLE IF NOT EXISTS playlists (
    playlist_id TEXT PRIMARY KEY,
    creator_id TEXT,
    playlist_track_count INTEGER
);

CREATE INDEX IF NOT EXISTS idx_playlist_id ON playlists (playlist_id);
CREATE INDEX IF NOT EXISTS idx_creator_id ON playlists (creator_id);
"""

create_database("data/db/songs_details.db", songs_schema)
create_database("data/db/playlists_details.db", playlist_schema)


def install_packages(packages):
    for package in packages:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", package])


if __name__ == "__main__":
    install_directories()
    packages = ["configparser", "requests", "spotipy", "pandas"]
    install_packages(packages)

end = time.time()
print("\nExecution time: ", end - start)
