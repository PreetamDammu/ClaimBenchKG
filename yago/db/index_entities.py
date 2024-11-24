import os
import sys
import argparse
from typing import List, Tuple
import sqlite3

from tqdm import tqdm

from .classes import Item, Property, Claim
from .constants.main import DB_NAME
from .yagodb import YagoDB


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
    
    main(args.db_name)