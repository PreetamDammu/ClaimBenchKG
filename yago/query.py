"""
Query the YAGO knowledge graph.
"""
import os
import sys
import random

from typing import List, Set

from db.yagodb import YagoDB

YAGO_ENTITY_STORE_DB = os.path.join(os.path.dirname(__file__), "db/yago.db")
YAGO_ENTITY_LENGTH = 5600415

YAGO_ENDPOINT_URL = "http://localhost:9999/bigdata/sparql"

def query_yago_entity_store(query: str) -> List[str]:
    """Query the YAGO entity store database.

    Parameters:
    - query: The query to run

    Returns:
    - A list of results
    """
    db = YagoDB(YAGO_ENTITY_STORE_DB)
    results = db.query(query)
    return results


# def random_walk(self) -> List[str]:
#     """Random walk on the YAGO knowledge graph.

#     Returns:
#     - A list of node IDs visited during the walk
#     """
#     walk = [start]
#     for _ in range(depth):
#         claims = self.claims_from_subject(walk[-1])
#         if not claims:
#             break
#         claim = random.choice(list(claims))
#         walk.append(claim.target_id)
#     return walk

if __name__ == "__main__":
    query = """
    SELECT item_id FROM items ORDER BY RANDOM() LIMIT 1
    """
    results = query_yago_entity_store(query)
    print(results)