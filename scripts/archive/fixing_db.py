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


def fix_artist_ids_format():
    logger.info('Fixing artist_ids format in songs table')
    cursor.execute('SELECT song_id, artist_ids FROM songs')
    rows = cursor.fetchall()

    for song_id, artist_ids in rows:
        if isinstance(artist_ids, str) and ',' not in artist_ids:
            # If artist_ids is not a comma-separated string, assume it's a list-like format
            # Example: if artist_ids is ['id1', 'id2']
            try:
                # Convert string list representation to actual list
                artist_ids_list = eval(artist_ids)
                if isinstance(artist_ids_list, list):
                    # Join list elements into a comma-separated string
                    corrected_artist_ids = ','.join(artist_ids_list)
                    cursor.execute('''
                        UPDATE songs
                        SET artist_ids = ?
                        WHERE song_id = ?
                    ''', (corrected_artist_ids, song_id))
                    logger.info(f'Updated song_id {
                                song_id} with corrected artist_ids')
            except Exception as e:
                logger.error(f'Error correcting artist_ids for song_id {
                             song_id}: {e}')

    conn.commit()
    logger.info('Finished fixing artist_ids format')


def close_connection():
    conn.close()
    logger.info('Database connection closed')


if __name__ == "__main__":
    try:
        fix_artist_ids_format()
    finally:
        close_connection()
