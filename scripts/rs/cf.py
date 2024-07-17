import os
import csv
import configparser

config = configparser.ConfigParser()
config.read('config.cfg')

src = config['dir']['transformed']


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
