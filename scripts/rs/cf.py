import os
import csv

import configparser

config = configparser.ConfigParser()
config.read('config.cfg')


def load_data(directory_path):
    data = []
    for filename in os.listdir(directory_path):
        if filename.endswith(".csv"):
            file_path = os.path.join(directory_path, filename)
            with open(file_path, 'r', newline='') as csvfile:
                csvreader = csv.reader(csvfile)
                for row in csvreader:
                    # You can adjust how you store each row based on your specific needs
                    data.append(row)
    return data


def generate_recommendations():
    pass


def write_recommendations():
    pass


def cf_result(ids):
    return print(f"Getting recommendation from {ids}!")


playlists_data = load_data(config['dir']['transformed'])
print(f"Loaded {len(playlists_data)} rows of data from playlists CSV.")

if __name__ == "__main__":
    ids = ['1uCDg9WDXzG5j1tVqnFNBR']
    cf_result(ids)
