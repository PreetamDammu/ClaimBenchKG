"""
This file extracts all entities from the YAGO ttl files and inserts them into the database.

Currently, it only inserts the subject of the triple into the database.
"""

import os
import sys
import argparse
from typing import List, Tuple
import sqlite3

from tqdm import tqdm

from .classes import Item, Property, Claim
from .constants.main import DB_NAME
from .yagodb import YagoDB

TTL_PATH = os.path.join(os.path.dirname(__file__), 'yago-facts.ttl')
PREFIX_PATH = os.path.join(os.path.dirname(__file__), 'yago-prefixes.txt')
ERROR_PATH = os.path.join(os.path.dirname(__file__), 'error.txt')

error_file = None # open(ERROR_PATH, 'a')

def check_prefix(entities: List[str]) -> bool:
    """
    Check if the entities of a line contains a prefix.

    Parameters:
    ----------
    entities: List[str]
        The entities of the line
    
    Returns:
    --------
    bool
        True if the line contains a prefix, False otherwise.
    """
    if len(entities) != 4:
        return False
    if entities[0] == '@prefix':
        return True
    return False

def check_triple(entities: List[str]) -> bool:
    """
    Check if the line contains a triple.
    A simple check at the moment, just checking if the line contains 3 entities.
    The logic may be updated in the future.
    
    Parameters:
    ----------
    entities: List[str]
        The entities of the line
    
    Returns:
    --------
    bool
        True if the line contains a triple, False otherwise.
    """
    if len(entities) != 4:
        return False
    return True

def insert_entities(entities: List[Tuple[str, str, str]], db: YagoDB) -> int:
    """
    Insert the entities into the database.

    Parameters:
    ----------
    entities: List[Tuple[str, str, str]]
        The entities to be inserted.

    db: YagoDB
        The database object.

    Returns:
    --------
    int
        The number of entities inserted.
    """
    items = [Item(*entity) for entity in entities]
    try:
        return db.insert_items(items)
    except Exception as e:
        # error_file.write(f'Error inserting items:\n')
        return 0

def read_ttl_line(line: str) -> Tuple[str, str, str]:
    """
    Read a line of the ttl file and return the entities.

    Parameters:
    ----------
    line: str
        The line to be read.
    
    Returns:
    --------
    Tuple[str, str, str]
        The entities of the line.
    """
    entities = line.split()
    # print(entities)
    if check_prefix(entities):
        # Insert the prefix into a json file
        with open(PREFIX_PATH, 'a') as f:
            f.write(line)
        return None
    if check_triple(entities):
        return entities
    return None

def read_ttl_file(ttl_path: str, db: YagoDB, batch_length: int) -> None:
    """
    Read the file in chunks and insert the entities into the database.
    Insert the entities in batches of `batch_length`.

    Parameters:
    ----------
    ttl_path: str
        The path to the ttl file.
    
    db: YagoDB
        The database object.

    batch_length: int
        The number of entities to be inserted in a batch.
        Currently, not in use for anything except logging.
    """
    # For Dev
    TOTAL = 10

    count = 0
    entities_set = set()
    with open(ttl_path, 'r') as f:
        for line in tqdm(f):
            entities = read_ttl_line(line)
            if not entities:
                continue
            
            entities_set.add(entities[0])
            if len(entities_set) == batch_length:
                entities_list = list([entity, None, None] for entity in entities_set)

                res = insert_entities(entities_list, db)
                entities_set = set()
                count += res if res else 0
                print(f'Inserted {batch_length} entities. Total: {count}')
            
            # if count == TOTAL:
            #     return
        
        if entities_set:
            entities_list = list([entity, None, None] for entity in entities_set)
            res = insert_entities(entities_list, db)
            count += res if res else 0

        print(f'Inserted {count} entities.')

def main(ttl_path: str, db_name: str, batch_length: int) -> None:
    """
    Main function to insert entities into the database.

    Parameters:
    ----------
    ttl_path: str
        The path to the ttl file.
    
    db_name: str
        The name of the database.
    
    batch_length: int
        The number of entities to be inserted in a batch.
    """
    db = YagoDB(db_name)
    read_ttl_file(ttl_path, db, batch_length)

if __name__=="__main__":
    parser = argparse.ArgumentParser(description='Insert entities into the Yago database.')
    parser.add_argument('--ttl_path', type=str, default=TTL_PATH, help='Path to the ttl file.')
    parser.add_argument('--db_name', type=str, default=DB_NAME, help='Name of the database.')
    parser.add_argument('--batch_length', type=int, default=1000000, help='Number of entities to be inserted in a batch.')
    args = parser.parse_args()
    
    error_file = open(ERROR_PATH, 'a')
    main(args.ttl_path, args.db_name, args.batch_length)
    error_file.close()