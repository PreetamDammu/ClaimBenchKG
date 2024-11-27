"""
Query the YAGO knowledge graph.
"""
import os
import sys
import random
import requests
from typing import List, Set

from db.yagodb import YagoDB
from db.constants.main import YAGO_ALL_ENTITY_COUNT, YAGO_FACTS_ENTITY_COUNT

"""
Note: Call this file from ClaimbenchKG as follows:
python -m yago.query
"""


YAGO_ENTITY_STORE_DB_PATH = os.path.join(os.path.dirname(__file__), "db/yago.db")
YAGO_ENTITY_LENGTH = YAGO_FACTS_ENTITY_COUNT

YAGO_PREFIXES_PATH = os.path.join(os.path.dirname(__file__), "db/yago-prefixes.txt")

YAGO_ENDPOINT_URL = "http://localhost:9999/bigdata/sparql"

def get_prefixes() -> str:
    """Get the prefixes for the YAGO knowledge graph.

    Returns:
    - The prefixes
    """
    prefixes = dict()
    with open(YAGO_PREFIXES_PATH, "r") as f:
        for prefix in f:
            prefix_list = prefix.split()
            if len(prefix_list) != 2:
                continue
            if prefix_list[0].endswith(":"):
                prefix_list[0] = prefix_list[0][:-1]
            if prefix_list[1].startswith("<") and prefix_list[1].endswith(">"):
                prefix_list[1] = prefix_list[1][1:-1]
            prefixes[prefix_list[0]] = prefix_list[1]
    return prefixes

PREFIXES = get_prefixes()

def query_random_entity(yago_db: YagoDB) -> str:
    """Query a random entity from the YAGO knowledge graph.

    Returns:
    - The ID of a random entity
    """
    query = """
    SELECT item_id FROM items ORDER BY RANDOM() LIMIT 1
    """
    results = yago_db.query(query)
    return results[0][0]

def query_triple(yago_endpoint_url: str, subject: str, *, 
                 filter_literals: bool = True) -> List[str]:
    """Query a triple from the YAGO knowledge graph.

    Args:
    - subject: The subject of the triple
    - filter_literals: Whether to filter out literals

    Returns:
    - The triple
    """
    headers = {
        "Content-Type": "application/sparql-query",
        "Accept": "application/sparql-results+json",
    }

    query = f"""
    SELECT ?predicate ?object WHERE {{
        {subject} ?predicate ?object
        {   "FILTER isIRI(?object)" if filter_literals else "" }
    }}
    """

    response = requests.post(yago_endpoint_url, headers=headers, data=query)
    if response.status_code == 200:
        response_json = response.json()  # Prints the JSON result
        # Randomly select a triple
        if len(response_json["results"]["bindings"]) == 0:
            return None
        triple = random.choice(response_json["results"]["bindings"])
        # triple = response_json["results"]["bindings"][0]
        return triple
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None

def random_walk(self, depth: int = 3) -> List[str]:
    """Random walk on the YAGO knowledge graph.

    Args:
    - depth: Depth of the walk

    Returns:
    - A list of node IDs visited during the walk
    """
    random_entity = query_random_entity(yago_db)

    subject = random_entity
    if not (random_entity.startswith("<") and random_entity.endswith(">")):
        subject_list = random_entity.split(":")
        if len(subject_list) == 2 and subject_list[0] in PREFIXES:
            subject = f"{PREFIXES[subject_list[0]]}{subject_list[1]}"
        else:
            subject = f"{subject}"

    walk = [subject]
    for _ in range(depth):
        triple = query_triple(YAGO_ENDPOINT_URL, f"<{walk[-1]}>")
        if triple is None:
            break
        walk.append(triple["predicate"]["value"])
        walk.append(triple["object"]["value"])
    return walk

if __name__ == "__main__":
    yago_db = YagoDB(YAGO_ENTITY_STORE_DB_PATH)

    # query_triple(YAGO_ENDPOINT_URL, random_entity)

    walk = random_walk(yago_db)
    print(walk)