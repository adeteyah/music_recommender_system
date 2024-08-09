import sqlite3
import configparser
import logging

# Setup logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load configuration
config = configparser.ConfigParser()
config.read('config.cfg')

DB = config['rs']['db_path']

# Connect to SQLite database
conn = sqlite3.connect(DB)
cursor = conn.cursor()


def fetch_incorrect_artist_ids():
    logger.info('Fetching rows with incorrectly formatted artist_ids')
    cursor.execute(
        "SELECT song_id, artist_ids FROM songs WHERE artist_ids LIKE '%[%]'")
    return cursor.fetchall()


def correct_artist_ids_format(rows):
    updates = []
    for song_id, artist_ids in rows:
        try:
            # Convert artist_ids from string list format to a comma-separated string
            artist_ids = artist_ids.strip("[]").replace("'", "").split(', ')
            corrected_artist_ids = ','.join(artist_ids)
            updates.append((corrected_artist_ids, song_id))
            logger.info(f'Queued update for song_id {song_id}')
        except Exception as e:
            logger.error(f'Error processing artist_ids for song_id {
                         song_id}: {e}')
    return updates


def batch_update_artist_ids(updates):
    logger.info('Batch updating artist_ids format in songs table')
    batch_size = 100  # Number of updates per batch
    for i in range(0, len(updates), batch_size):
        batch = updates[i:i+batch_size]
        cursor.executemany('''
            UPDATE songs
            SET artist_ids = ?
            WHERE song_id = ?
        ''', batch)
        logger.info(f'Batch updated {len(batch)} records')
        conn.commit()


def close_connection():
    conn.close()
    logger.info('Database connection closed')


if __name__ == "__main__":
    try:
        rows = fetch_incorrect_artist_ids()
        if rows:
            updates = correct_artist_ids_format(rows)
            if updates:
                batch_update_artist_ids(updates)
    finally:
        close_connection()
