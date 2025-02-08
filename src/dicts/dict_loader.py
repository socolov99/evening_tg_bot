import csv
import json
import os

DIRECTORY_PATH = os.path.dirname(os.path.abspath(__file__))


def read_json(file_name):
    with open(f'{DIRECTORY_PATH}/{file_name}') as json_file:
        return json.load(json_file)


def read_csv(file_name):
    with open(f'{DIRECTORY_PATH}/{file_name}') as csv_file:
        return csv.reader(csv_file)


MONTH_NAMES_DICT = read_json('month_names.json')
