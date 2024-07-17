import os
import csv
import configparser

config = configparser.ConfigParser()
config.read('config.cfg')

db_playlist = config['db']['playlists_db']
db_songs = config['db']['songs_db']


def load_data(src):
    pass


def generate_recommendations(ids):
    pass


def cf_result(ids):
    pass


if __name__ == "__main__":
    ids = ['4XTP6QLsMZ1GQe0c1i1Oze']
    result = cf_result(ids)
    print(result)
