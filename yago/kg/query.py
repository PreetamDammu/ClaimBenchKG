"""
This module contains utility functions for the Yago Knowledge Graph.
"""
############################################################################################################
# Importing necessary libraries
from typing import List, Set
import requests
import pandas as pd

############################################################################################################
# Functions

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

def get_triples_from_response(response: dict, *,
    sparql_columns_dict: dict = None) -> pd.DataFrame:
    """
    Extracts triples from the response of a SPARQL query.
    """
    if sparql_columns_dict is None:
        sparql_columns_dict = {
            "subject": "subject",
            "predicate": "predicate",
            "object": "object"
        }
    triples = []
    for row in response["results"]["bindings"]:
        triple = {}
        for key, value in row.items():
            triple[sparql_columns_dict[key]] = value["value"]
        triples.append(triple)
    return pd.DataFrame(triples)

if __name__ == "__main__":
    # Test the functions
    yago_endpoint_url = "http://yago-knowledge.org/sparql"
    # query = get_triples_multiple_subjects_query(entities=["<http://yago-knowledge.org/resource/Barack_Obama>"], 
    #     columns_dict={"subject": "s", "predicate": "p", "object": "o"})
    # response = query_kg(yago_endpoint_url, query)
    # triples = get_triples_from_response(response)
    print(yago_endpoint_url)