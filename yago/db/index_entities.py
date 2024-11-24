import os
import sys
import argparse
from typing import List, Tuple
import sqlite3

from tqdm import tqdm

from .classes import Item, Property, Claim
from .constants.main import DB_NAME
from .yagodb import YagoDB

TTL_PATH = os.path.join(os.path.dirname(__file__), 'data/yago-facts-sample.ttl')

PREFIX_PATH = os.path.join(os.path.dirname(__file__), 'yago-prefixes.txt')
ERROR_PATH = os.path.join(os.path.dirname(__file__), 'error.txt')

error_file = None # open(ERROR_PATH, 'a')

def create_index_on_items_table(connection, cursor, item_column: str):
    query = f'CREATE INDEX {item_column}_index ON items({item_column});'
    cursor.execute(query)
    connection.commit()
    cursor.close()

def main(db_name: str):
    yago_db = YagoDB(db_name)
    connection = yago_db.getConnection()
    cursor = yago_db.getCursor()
    create_index_on_items_table(connection, cursor, 'item_label')

if __name__=="__main__":
    parser = argparse.ArgumentParser(description='Insert entities into the Yago database.')
    parser.add_argument('--db_name', type=str, default=DB_NAME, help='Name of the database.')
    args = parser.parse_args()
    
    error_file = open(ERROR_PATH, 'a')
    main(args.db_name)
    error_file.close()