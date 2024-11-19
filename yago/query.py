"""
Query the YAGO knowledge graph.
"""
import os
import sys
import random
import requests
from typing import List, Set

from db.yagodb import YagoDB

YAGO_ENTITY_STORE_DB_PATH = os.path.join(os.path.dirname(__file__), "db/yago.db")
YAGO_ENTITY_LENGTH = 5600415

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
            if len(prefix_list) != 4:
                continue
            if prefix_list[0] != "@prefix":
                continue
            if prefix_list[1].endswith(":"):
                prefix_list[1] = prefix_list[1][:-1]
            if prefix_list[2].startswith("<") and prefix_list[2].endswith(">"):
                prefix_list[2] = prefix_list[2][1:-1]
            prefixes[prefix_list[1]] = prefix_list[2]
    return prefixes

PREFIXES = get_prefixes()

def query_random_entity(yago_db: YagoDB) -> str:
    """Query a random entity from the YAGO knowledge graph.

    Returns:
    - The ID of a random entity
    """
    query = """
    SELECT item_id FROM items LIMIT 1
    """
    # SELECT item_id FROM items ORDER BY RANDOM() LIMIT 1
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

    # Check if the subject has a prefix or is a full URI
    if not (subject.startswith("<") and subject.endswith(">")):
        subject_list = subject.split(":")
        if len(subject_list) == 2:
            subject = f"<{PREFIXES[subject_list[0]]}{subject_list[1]}>"

    query = f"""
    SELECT ?predicate ?object WHERE {{
        {subject} ?predicate ?object
        {   "FILTER isIRI(?object)" if filter_literals else "" }
    }}
    """

    response = requests.post(yago_endpoint_url, headers=headers, data=query)
    if response.status_code == 200:
        response_json = response.json()  # Prints the JSON result
        for result_bindings in response_json["results"]["bindings"]:
            print(result_bindings)
    else:
        print(f"Error: {response.status_code}")
        print(response.text)

def random_walk(self, depth: int = 3) -> List[str]:
    """Random walk on the YAGO knowledge graph.

    Args:
    - depth: Depth of the walk

    Returns:
    - A list of node IDs visited during the walk
    """
    random_entity = query_random_entity(yago_db)
    for _ in range(depth):
        claims = self.claims_from_subject(walk[-1])
        if not claims:
            break
        claim = random.choice(list(claims))
        walk.append(claim.target_id)
    return walk

if __name__ == "__main__":
    yago_db = YagoDB(YAGO_ENTITY_STORE_DB_PATH)
    random_entity = query_random_entity(yago_db)
    print(random_entity)

    query_triple(YAGO_ENDPOINT_URL, random_entity)