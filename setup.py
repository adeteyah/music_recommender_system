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
        "data/cache/playlists_details.db",  # store playlist characteristic
        "data/cache/tracks_details.db",  # store title and artists id
        "data/cache/artists_details.db"  # store artist name and genres
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


artist_schema = """
CREATE TABLE IF NOT EXISTS artists (
    artist_id TEXT PRIMARY KEY,
    artist_name TEXT,
    artist_genres TEXT
);
"""

track_schema = """
CREATE TABLE IF NOT EXISTS tracks (
    track_id TEXT PRIMARY KEY,
    track_name TEXT,
    artist_ids TEXT
);
"""

create_database("data/cache/artists_details.db", artist_schema)
create_database("data/cache/tracks_details.db", track_schema)


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
