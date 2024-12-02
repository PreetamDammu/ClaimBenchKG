"""
This file extracts all properties from the YAGO ttl files and inserts them into the database along with their counts.
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

TTL_PATH = os.path.join(os.path.dirname(__file__), 'data/yago-facts.ttl')
TTL_ALL_PATH = os.path.join(os.path.dirname(__file__), 'data/yago-beyond-wikipedia.ttl')

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

def insert_properties(properties: List[Tuple[str, str]], db: YagoDB) -> int:
    """
    Insert the properties into the database.

    Parameters:
    ----------
    properties: List[Tuple[str, str]]
        The properties to be inserted.

    db: YagoDB
        The database object.

    Returns:
    --------
    int
        The number of properties inserted.
    """
    properties = [Property(*property_) for property_ in properties]
    try:
        return db.insert_properties_with_counts(properties)
    except Exception as e:
        # error_file.write(f'Error inserting properties:\n')
        return 0

def read_ttl_line(line: str, prefix_dict: dict) -> Tuple[str, str, str]:
    """
    Read a line of the ttl file and return the entities and property.
    Also, if the line contains a prefix, insert the prefix into a json file, 
        and insert the prefix into the prefix_dict.

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
        prefix = entities[1].replace(':', '')
        prefix_dict[prefix] = entities[2].replace('>', '').replace('<', '')
        # Insert the prefix into a json file
        with open(PREFIX_PATH, 'a') as f:
            f.write(f"{prefix}: {prefix_dict[prefix]}\n")
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

    def createEntityLabel(entity: str) -> str:
        entity_string_list = entity.split(':')
        if len(entity_string_list) == 1:
            return entity
        if entity_string_list[0] not in prefix_dict:
            return entity
        return f"{prefix_dict[entity_string_list[0]]}{entity_string_list[1]}"

    prefix_dict = dict()

    count = 0
    properties_count = 0
    properties_set = dict()
    with open(ttl_path, 'r') as f:
        for line in tqdm(f):
            entities = read_ttl_line(line, prefix_dict)
            if not entities:
                continue
            
            count += 1
            if entities[1] not in properties_set:
                properties_set[entities[1]] = 1
            else:
                properties_set[entities[1]] += 1
            
            if count == batch_length:
                # Insert properties
                properties_list = list([property_, None, count]
                                    for (property_, count) in properties_set.items())
                res = insert_properties(properties_list, db)
                properties_set = dict()
                properties_count += res if res else 0
                print(f'Rows {count}. Inserted {batch_length} properties. Total: {properties_count}')
            # if count == TOTAL:
            #     return
        
        if properties_set:
            properties_list = list([property_, None, count] for (property_, count) in properties_set.items())
            res = insert_properties(properties_list, db)
            properties_count += res if res else 0

        print(f'Done. Rows {count}. Total: {properties_count}')

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
    args.ttl_path = TTL_ALL_PATH
    main(args.ttl_path, args.db_name, args.batch_length)
    error_file.close()