import os
from typing import Set, List
from abc import ABC
import sqlite3
import argparse

from classes import Item, Property, Claim
from constants.main import DB_NAME

class YagoDB:
    """Class for interacting with a Yago DB.
    
    Note: At the moment, we will not be using the logic related to property and claim. 
    We will only be using the logic related to items.
    
    """
    def __init__(self, db_name: str = DB_NAME):
        """Instantiate the database helper."""
        self._conn = sqlite3.connect(db_name)
        self._curr = self._conn.cursor()

    def create_db(self):
        """Create the database."""
        self._curr.execute('''
            CREATE TABLE items (
                item_id TEXT PRIMARY KEY,
                item_label TEXT,
                item_description TEXT
            )
        ''')
        self._curr.execute('''
            CREATE TABLE properties (
                property_id TEXT PRIMARY KEY,
                property_label TEXT,
                property_description TEXT
            )
        ''')
        self._curr.execute('''
            CREATE TABLE claims (
                claim_id INTEGER PRIMARY KEY,
                item_id TEXT,
                property_id TEXT,
                target_id TEXT
            )
        ''')
        self._conn.commit()

    def get_item(self, item_id: str) -> Item:
        """Get an item from the database.

        Args:
        - item_id: ID of the item to be returned

        Returns:
        - The `Item` if it exists
        """
        self._curr.execute('''
            SELECT * FROM items WHERE item_id = ?
        ''', (item_id,))
        row = self._curr.fetchone()
        return Item(*row)
    
    def insert_item(self, item: Item) -> None:
        """Insert an item into the database.

        Args:
        - item: `Item` to be inserted
        """
        self._curr.execute('''
            INSERT INTO items VALUES (?, ?, ?)
        ''', (item.item_id, item.item_label, item.item_description))
        self._conn.commit()
    
    def get_property(self, property_id: str) -> Property:
        """Get a property from the database.

        Args:
        - property_id: ID of the property to be returned

        Returns:
        - The `Property` if it exists
        """
        self._curr.execute('''
            SELECT * FROM properties WHERE property_id = ?
        ''', (property_id,))
        row = self._curr.fetchone()
        return Property(*row)
    
    def get_claim(self, claim_id: int) -> Claim:
        """Get a claim from the database.

        Args:
        - claim_id: ID of the claim to be returned

        Returns:
        - The `Claim` if it exists
        """
        self._curr.execute('''
            SELECT * FROM claims WHERE claim_id = ?
        ''', (claim_id,))
        row = self._curr.fetchone()
        return Claim(*row)
    
    def claims_from_subject(self, subject_id: str) -> Set[Claim]:
        """Get outgoing claims relating to an item.

        Args:
        - subject_id: ID of the `Item` to get outgoing claims from

        Returns:
        - Claims where `item_id` is the subject of the claim
        """
        self._curr.execute('''
            SELECT * FROM claims WHERE subject_id = ?
        ''', (subject_id,))
        return {Claim(*row) for row in self._curr.fetchall()}
    
    def random_item(self) -> Item:
        """Get a random item from the database.

        Returns:
        - Randomly selected `Item`
        """
        self._curr.execute('''
            SELECT * FROM items WHERE item_id IN (SELECT item_id FROM items ORDER BY RANDOM() LIMIT 1)
        ''', ())
        return Item(*self._curr.fetchone())
    
    def claims_from_target(self, target_id: str) -> Set[Claim]:
        """Get incoming claims relating to an item.

        Args:
        - target_id: ID of the `Item` to get incoming claims from

        Returns:
        - Claims where `target_id` is the target of the claim
        """
        self._curr.execute('''
            SELECT * FROM claims WHERE target_id = ?
        ''', (target_id,))
        return {Claim(*row) for row in self._curr.fetchall()}

    def close(self) -> None:
        """Close the connection to the database."""
        self._curr.close()
        self._conn.close()