"""Utilities for Wikidata5m."""
from typing import Set, List
from abc import ABC
import sqlite3

from openai import OpenAI

from wikidata5m.data import Item, Property, Claim


class WikidataDB:
    """Class for interacting with a Wikidata5m DB."""
    # TODO: add error handling

    def __init__(self, db_name: str):
        """Instantiate the database helper.

        Args:
        - db_name: Path to the sqlite3 database.
        """
        self._conn = sqlite3.connect(db_name)
        self._curr = self._conn.cursor()

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


class Sampler(ABC):
    """Abstract Base Class for samplers.

    Used to sample a subgraph from Wikidata5m."""

    def sample(self) -> List[Claim]:
        """Sample a subgraph from Wikidata5m."""
        raise NotImplemented()


class ItemFilter(ABC):
    """Filter for `Item`s when sampling."""

    def check(self, item: Item) -> bool:
        """Pass an `Item` through the filter.

        Args:
        - item: the `Item` to pass through the filter

        Returns:
        - boolean if `item` passes the filter
        """
        raise NotImplemented()


class PropertyFilter(ABC):
    """Filter for `Property`s when sampling."""

    def check(self, property: Property) -> bool:
        """Pass a `Propery` through the filter.

        Args:
        - item: the `Property` to pass through the filter

        Returns:
        - boolean if `property` passes the filter
        """
        raise NotImplemented()


def get_openai_response(prompt: str) -> str:
    """Get a GPT-4 response.

    You need the OPENAI_API_KEY env variable set.

    Args:
    - prompt: prompt for the model

    Returns:
    - the model's response to the prompt
    """
    client = OpenAI()
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model="gpt-4-turbo",
    )
    response = chat_completion.choices[0].message.content
    if response is None:
        raise Exception('OpenAI response was None')
    return response
