############################################################################################################
# Importing necessary libraries
from typing import List, Set
import requests

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
    entities: List[str] = [], filter_literals: bool = True,
    columns_dict: dict) -> str:
    """
    Generate a query to get the triples for a list of entities.

    Parameters:
    ----------
    entities: List[str]
        The list of entities to get the triples for

    filter_literals: bool
        Whether to filter out literals

    columns_dict: dict
        The columns dictionary
    Returns:
    ----------
    query: str
        The query to get the triples for the entities
    """
    if columns_dict is None:
        columns_dict = {}
    subject = columns_dict["subject"] if "subject" in columns_dict else "subject"
    predicate = columns_dict["predicate"] if "predicate" in columns_dict else "predicate"
    _object = columns_dict["object"] if "object" in columns_dict else "object"
    query = f"""
    SELECT ?{subject} ?{predicate} ?{_object} WHERE {{
        VALUES ?{subject} {{ {" ".join(entities)} }}
        ?{subject} ?{predicate} ?{_object}
        {   f"FILTER isIRI(?{_object})" if filter_literals else "" }
    }}
    """
    return query

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