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
def get_triples_multiple_subjects_query(entities: List[str] = None, *,
    lang: str = None, filter_literals: bool = True, prefixes: dict, invalid_properties: List[str] = None,
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
    if entities is None:
        entities = []
    if columns_dict is None:
        columns_dict = {}
    
    prefixes = [f"PREFIX {key}: <{value}>" for key, value in prefixes.items()]
    prefix_string = "\n".join(prefixes)

    subject = columns_dict["subject"] if "subject" in columns_dict else "subject"
    predicate = columns_dict["predicate"] if "predicate" in columns_dict else "predicate"
    _object = columns_dict["object"] if "object" in columns_dict else "object"

    filters = []
    if lang:
        filters.append(f"lang(?{_object}) = '{lang}'")
    if filter_literals:
        filters.append(f"isIRI(?{_object})")
    if invalid_properties:
        filters.append(f"?{predicate} not in ({','.join(invalid_properties)})")
    
    query = f"""
    {prefix_string}
    SELECT ?{subject} ?{predicate} ?{_object} WHERE {{
        VALUES ?{subject} {{ {" ".join(entities)} }}
        ?{subject} ?{predicate} ?{_object}
        {f"FILTER ({' && '.join(filters)})" if filters else ""}
    }}
    """
    return query


def get_description_multiple_entities_query(entities: List[str] = None, *,
    columns_dict: dict = None) -> str:
    """
    Generate a query to get the description for a list of entities.

    Parameters:
    ----------
    entities: List[str]
        The list of entities to get the description for

    columns_dict: dict
        The columns dictionary

    Returns:
    ----------
    query: str
        The query to get the description for the entities
    """
    if entities is None:
        entities = []
    if columns_dict is None:
        columns_dict = {}
    subject = columns_dict["subject"] if "subject" in columns_dict else "subject"
    description = columns_dict["description"] if "description" in columns_dict else "description"
    query = f"""
    SELECT ?{subject} ?{description} WHERE {{
        VALUES ?{subject} {{ {" ".join(entities)} }}
        ?{subject} <http://www.w3.org/2000/01/rdf-schema#comment> ?{description}
        filter(lang(?{description}) = 'en')
    }}
    """
    return query


def query_kg(yago_endpoint_url: str, query_sparql: str) -> List[str]:
    """Query the YAGO knowledge graph.

    Parameters:
    ----------
    yago_endpoint_url: str
        The YAGO endpoint URL

    query_sparql: str
        The SPARQL query

    Returns:
    ----------
    response: List[str]
        The response
    """
    headers = {
        "Content-Type": "application/sparql-query",
        "Accept": "application/sparql-results+json",
    }

    try:
        response = requests.post(yago_endpoint_url, headers=headers, data=query_sparql)
        if response.status_code == 200:
            response_json = response.json()  # Prints the JSON result
            return response_json
        else:
            print(f"Error: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error querying the YAGO knowledge graph")
        return None

def get_triples_from_response(response: dict, *,
    columns_dict: dict = None) -> pd.DataFrame:
    """
    Extracts triples from the response of a SPARQL query.
    """
    if columns_dict is None:
        columns_dict = {
            "subject": "subject",
            "predicate": "predicate",
            "object": "object"
        }
    triples = []

    try:
        for row in response["results"]["bindings"]:
            triple = {}
            for key, value in row.items():
                triple[columns_dict[key]] = value["value"]
            triples.append(triple)
        return pd.DataFrame(triples, columns = columns_dict.values())
    except Exception as e:
        return pd.DataFrame(triples, columns = columns_dict.values())

if __name__ == "__main__":
    # Test the functions
    yago_endpoint_url = "http://localhost:9999/bigdata/sparql"
    query = """
    PREFIX yago: <http://yago-knowledge.org/resource/>
    SELECT * WHERE { 
    yago:doctoralAdvisor ?predicate ?object 
    filter(lang(?object) = 'en')
    } 
    LIMIT 10000
    """
    response = query_kg(yago_endpoint_url, query)
    triples_df = get_triples_from_response(response)
    print(type(response))
    print(triples_df.head())
    print(triples_df.shape)
    with open("triples.csv", "w") as f:
        triples_df.to_csv(f, index=False)