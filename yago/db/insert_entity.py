"""This file extracts all entities from the YAGO ttl files and inserts them into the database."""

import os
import argparse
from typing import List, Tuple
import sqlite3

from classes import Item, Property, Claim
from constants.main import DB_NAME
from yagodb import YagoDB

TTL_PATH = os.path.join(os.path.dirname(__file__), 'yago-facts.ttl')

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
    if len(entities) != 3:
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
    if len(entities) != 3:
        return False
    return True

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
    return entities[0], entities[1], entities[2]