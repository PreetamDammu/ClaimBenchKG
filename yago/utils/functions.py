############################################################################################################
# Importing necessary libraries
from typing import List, Set

from ..db.yagodb import YagoDB

############################################################################################################
# Functions
def get_prefixes(yago_prefixes_path: str) -> str:
    """Get the prefixes for the YAGO knowledge graph.

    Returns:
    - The prefixes
    """
    prefixes = dict()
    with open(yago_prefixes_path, "r") as f:
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

def query_random_entities(yago_db: YagoDB, *, 
    num_of_entities: int = 1) -> List[str]:
    """Query a fixed number of random entities from the YAGO knowledge graph.

    Parameters:
    ----------
    yago_db: YagoDB
        The YAGO database

    num_of_entities: int
        The number of entities to query
    Returns:
    ----------
    A list of random entities
    """
    query = f"""
    SELECT item_id, item_label FROM items ORDER BY RANDOM() LIMIT {num_of_entities}
    """
    results = yago_db.query(query)
    return results