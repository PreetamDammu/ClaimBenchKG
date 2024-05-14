"""Sampler."""
from collections import Counter
import sqlite3
from typing import Set, List, Optional, Tuple

import numpy as np

from openai import OpenAI


def sample(
    cursor: sqlite3.Cursor,
    n_hops: int,
    c: float,
    bad_prop_ids: Set[str] = set(),
    bad_item_ids: Set[str] = set(),
    log: Optional[List[str]] = None,
) -> Tuple[List[Tuple[str, ...]], ...]:
    """Samples.

    Args:
    - cursor: the sqlite3 cursor to the db
    - n_hops: number of hops
    - c: constant for the sampling
    - bad_prop_ids: property ids to avoid sampling
    - bad_item_ids: item ids to avoid sampling
    - log: where to store logging messages
    
    Returns:
    - tuple of:
        - list of sampled items
        - list of properties connecting them
    """
    if log is None:
        # no logging will be returned
        log = []

    # get random initial item
    cursor.execute('''
        SELECT * FROM items WHERE item_id IN (SELECT item_id FROM items ORDER BY RANDOM() LIMIT 1)
    ''')
    initial_item = cursor.fetchone()

    path = [initial_item]
    item_ids = set([initial_item[0]])
    prev_id = initial_item[0]
    properties = []
    prop_ids = set()

    # get path
    for _ in range(n_hops):
        # get all outgoing claims
        cursor.execute('''
            SELECT * FROM claims WHERE subject_id = ?
        ''', (prev_id,))
        outgoing_claims = [claim for claim in cursor.fetchall() if claim[2] not in prop_ids] # remove duplicate claims
        outgoing_claims = [claim for claim in outgoing_claims if claim[2] not in bad_prop_ids] # remove bad claims
        # exclude any properties which point to multiple items
        counts = Counter([claim[2] for claim in outgoing_claims])
        orig = len(outgoing_claims) # TODO: remove
        outgoing_claims = [claim for claim in outgoing_claims if counts[claim[2]] <= 1] # remove bad claims
        log.append(f'removed {orig - len(outgoing_claims)} claims via duplicates')

        # get outgoing items
        outgoing_items = []
        # we reverse so we can delete without idx issues
        # TODO: change to increase speed
        for i, claim in reversed(list(enumerate(outgoing_claims))):
            cursor.execute('''
                SELECT * FROM items where item_id = ?
            ''', (claim[3],))
            item = cursor.fetchone()
            # ensure no duplicates - TODO: add other filters
            if item[0] in item_ids or item[0] in bad_item_ids:
                log.append('deleted: ' + str(outgoing_claims[i]))
                del outgoing_claims[i]
            else:
                outgoing_items.insert(0, item)

        # get probs
        in_deg = np.array([item[3] for item in outgoing_items]) ** -c
        probs = in_deg / np.sum(in_deg)

        # sample
        if not len(probs):
            log.append('no possible next hops')
            return path, properties
        idx = np.random.choice(a=len(probs), p=probs)
        path.append(outgoing_items[idx])
        prev_id = outgoing_items[idx][0]
        # add all items to item_ids (heuristic to prevent double hops)
        item_ids.update([item[0] for item in outgoing_items])

        # get property
        cursor.execute('''
            SELECT * FROM properties WHERE property_id = ?
        ''', (outgoing_claims[idx][2],))
        properties.append(cursor.fetchone())
        prop_ids.add(outgoing_claims[idx][2])
    return path, properties


def generate(path: List[Tuple[str, ...]], properties: List[Tuple[str, ...]]) -> str:
    """Generate a question from a sample.

    Args:
    - path: a sampled path
    - properties: sampled properties

    Returns:
    - question generated from GPT-4
    """
    example = []
    example.append(f'Starting item: {path[0][1]}')
    for i, prop in enumerate(properties):
        example.append(f'Hop {i+1}: {prop[1]}')
    sample = '\n'.join(example)
    prompt = """
You will be given a starting item and a sequence of relationships, as hops, leading to an answer. You need to convert this information into a question, asking what the final item would be after all of the hops. Only respond with the question, nothing else.

Note that the hops follow, in the sequence:

STARTING ITEM -> hop1 -> hop2 -> ... -> hopn -> FINAL ITEM

Ensure that your question asks about the final items with the proper hop relationship directions and orderings.

For instance, given the starting item: "Barack Obama" and the hops "Born in state", "Capital city", you might respond: "What is the capital of the state which Barack Obama was born in?"

Sample:
""" + sample
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




