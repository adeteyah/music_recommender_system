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
        "data/cache/fetched_users.txt",
        "data/cache/fetched_artists.txt"
        "data/cache/track_details.json"
        "data/cache/artists_details.json"
    ]

    for directory in directories:
        path = Path(directory)
        path.mkdir(parents=True, exist_ok=True)

    for file in files:
        path = Path(file)
        if not path.exists():
            path.touch()


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
