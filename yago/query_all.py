"""
Query the YAGO knowledge graph.
"""
import os
import sys
import random
import requests
import argparse
from typing import List, Set

from .db.yagodb import YagoDB
from .db.constants.main import YAGO_ALL_ENTITY_COUNT, YAGO_FACTS_ENTITY_COUNT
from .db.functions.entity import get_random_entities_query

from .utils.constants import YAGO_ENTITY_STORE_DB_PATH, YAGO_PREFIXES_PATH, YAGO_ENDPOINT_URL
from .utils.functions import get_prefixes, get_url_from_prefix_and_id, get_triples_query, get_triples_multiple_subjects_query

"""
Note: Call this file from ClaimbenchKG as follows:
python -m yago.query
"""

PREFIXES = get_prefixes(yago_prefixes_path=YAGO_PREFIXES_PATH)

def query_kg(yago_endpoint_url: str, query_sparql: str) -> List[str]:
    """Query the YAGO knowledge graph.

    Args:
    - yago_endpoint_url: The YAGO endpoint URL
    - query_sparql: The SPARQL query

    Returns:
    - The response
    """
    headers = {
        "Content-Type": "application/sparql-query",
        "Accept": "application/sparql-results+json",
    }

    response = requests.post(yago_endpoint_url, headers=headers, data=query_sparql)
    if response.status_code == 200:
        response_json = response.json()  # Prints the JSON result
        return response_json
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
    random_entity = query_random_entities(yago_db)

    subject = get_url_from_prefix_and_id(PREFIXES, random_entity[0][0])

    walk = [subject]
    for _ in range(depth):
        print(walk)
        triple = query_triple(YAGO_ENDPOINT_URL, f"<{walk[-1]}>")
        if triple is None:
            break
        walk.append(triple["predicate"]["value"])
        walk.append(triple["object"]["value"])
    return walk

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Query the YAGO knowledge graph.")

    yago_db = YagoDB(YAGO_ENTITY_STORE_DB_PATH)

    # query = get_triples_query(entity_id="<http://yago-knowledge.org/resource/2Mass_J14070720-0234401_Q80666561>")
    # response = query_kg(YAGO_ENDPOINT_URL, query)
    # print(response)

    # query1 = get_random_entities_query(num_of_entities=3)
    # entities = yago_db.query(query1)
    # entity_list = [f"<{entity[1]}>" for entity in entities]
    entity_list = ["<http://yago-knowledge.org/resource/2Mass_J14070720-0234401_Q80666561>", 
    "<http://yago-knowledge.org/resource/Mgc_13393_Q83004058>"]

    query2 = get_triples_multiple_subjects_query(entities=entity_list, filter_literals=True)
    print(query2)
    response = query_kg(YAGO_ENDPOINT_URL, query2)
    print(response)

    # walk = random_walk(yago_db)
    # print(walk)