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
    cursor.execute(schema)
    conn.commit()
    conn.close()


songs_schema = """
CREATE TABLE IF NOT EXISTS artists (
    artist_id TEXT PRIMARY KEY,
    artist_name TEXT,
    artist_genres TEXT
);
CREATE TABLE IF NOT EXISTS tracks (
    track_id TEXT PRIMARY KEY,
    track_name TEXT,
    artist_ids TEXT
);
"""

playlist_schema = """
CREATE TABLE IF NOT EXISTS playlists (
    playlist_id TEXT PRIMARY KEY,
    creator_id TEXT,
    playlist_genres TEXT
);
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
