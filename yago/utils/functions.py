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

def get_url_from_prefix_and_id(prefixes: dict, entity_id: str) -> str:
    """Get the URL from the prefixes and entity ID.

    Args:
    - prefixes: The prefixes
    - entity_id: The entity ID

    Returns:
    - The URL
    """
    if not (entity_id.startswith("<") and entity_id.endswith(">")):
        entity_list = entity_id.split(":")
        if len(entity_list) == 2 and entity_list[0] in prefixes:
            entity_id = f"{prefixes[entity_list[0]]}{entity_list[1]}"
        else:
            entity_id = f"{entity_id}"
    return entity_id

def get_triples_query(entity_id: str) -> str:
    """Get the triples query for the entity ID.

    Args:
    - entity_id: The entity ID

    Returns:
    - The triples query
    """
    query = f"""
    SELECT ?predicate ?object WHERE {{
        {entity_id} ?predicate ?object
    }}
    """
    return query


# SparQL functions
def get_triples_multiple_subjects_query(*,
    entities: List[str] = [], filter_literals: bool = True) -> str:
    """
    Generate a query to get the triples for a list of entities.

    Parameters:
    ----------
    entities: List[str]
        The list of entities to get the triples for

    filter_literals: bool
        Whether to filter out literals

    Returns:
    ----------
    query: str
        The query to get the triples for the entities
    """
    query = f"""
    SELECT ?subject ?predicate ?object WHERE {{
        VALUES ?subject {{ {" ".join(entities)} }}
        ?subject ?predicate ?object
        {   "FILTER isIRI(?object)" if filter_literals else "" }
    }}
    """
    return query