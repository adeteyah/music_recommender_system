import sqlite3
import configparser
import random

config = configparser.ConfigParser()
config.read('config.cfg')

db_playlist = config['db']['playlists_db']
db_songs = config['db']['songs_db']
output_path = config['output']['cf_output']
n_recommend = int(config['rs']['n_recommend'])

# Connect to the databases
conn_playlist = sqlite3.connect(db_playlist)
cur_playlist = conn_playlist.cursor()
conn_songs = sqlite3.connect(db_songs)
cur_songs = conn_songs.cursor()

# add more functions here


def write_result():
    with open(output_path, 'w', encoding='utf-8') as file:  # Specify UTF-8 encoding
        file.write("Inputted IDs:\n")
        # For Loop
        file.write("\nEliminated Inputs:\n")
        # For Loop
        file.write("\nUsed Inputs:\n")
        # For Loop
        file.write("\nMatched Playlists:\n")
        # For Loop
        file.write("\nSongs Recommendation:\n")
        # For Loop

    print(f'CF Result written to: {output_path}')


def cf_result(ids):
    pass


if __name__ == "__main__":
    ids = [
        '1FWsomP9StpCcXNWmJk8Cl',
        '1RMJOxR6GRPsBHL8qeC2ux',
        '2LBqCSwhJGcFQeTHMVGwy3',
        '2eAvDnpXP5W0cVtiI0PUxV',
    ]
    cf_result(ids)
