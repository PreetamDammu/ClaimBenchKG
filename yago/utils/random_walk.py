"""
This module contains utility functions to implement random walk on the YAGO knowledge graph.
"""
import os
import sys
import random
import requests
import argparse
from typing import List, Set

import numpy as np
import pandas as pd

# A temporary solution to import from parent directory lol
# until the package is properly installable
if __name__=='__main__':
    if __package__ is None:
        from os import path
        sys.path.insert(0, path.dirname( path.dirname( path.abspath(__file__) ) ) )
        from db.yagodb import YagoDB
        from db.constants.main import YAGO_ALL_ENTITY_COUNT, YAGO_FACTS_ENTITY_COUNT
        from db.functions.entity import get_random_entities_query
        from kg.query import get_triples_multiple_subjects_query, query_kg, get_triples_from_response
        sys.path.insert(0, path.dirname( path.abspath(__file__) ) )
        from constants import YAGO_ENTITY_STORE_DB_PATH, YAGO_PREFIXES_PATH, YAGO_ENDPOINT_URL
        from prefix import get_prefixes, get_url_from_prefix_and_id
    else:
        from ..db.yagodb import YagoDB
        from ..db.constants.main import YAGO_ALL_ENTITY_COUNT, YAGO_FACTS_ENTITY_COUNT
        from ..db.functions.entity import get_random_entities_query
        from ..kg.query import get_triples_multiple_subjects_query, query_kg, get_triples_from_response
        from .constants import YAGO_ENTITY_STORE_DB_PATH, YAGO_PREFIXES_PATH, YAGO_ENDPOINT_URL
        from .prefix import get_prefixes, get_url_from_prefix_and_id
else:
    from db.yagodb import YagoDB
    from db.constants.main import YAGO_ALL_ENTITY_COUNT, YAGO_FACTS_ENTITY_COUNT
    from db.functions.entity import get_random_entities_query
    from kg.query import get_triples_multiple_subjects_query, query_kg, get_triples_from_response
    from utils.constants import YAGO_ENTITY_STORE_DB_PATH, YAGO_PREFIXES_PATH, YAGO_ENDPOINT_URL
    from utils.prefix import get_prefixes, get_url_from_prefix_and_id

SPARQL_COLUMNS_DICT = {
    "subject": "subject",
    "predicate": "predicate",
    "object": "object"
}

def random_walks_multiple(yago_db: YagoDB, *, num_of_entities: int = 10, depth: int = 3) -> pd.DataFrame:
    """
    Random walks on the YAGO knowledge graph.

    Parameters:
    ----------
    yago_db: YagoDB
        The YagoDB object
    
    num_of_entities: int
        Number of entities to start the random walk with

    depth: int
        Depth of the random walk

    Returns:
    ----------
    entities_df: pd.DataFrame
        The dataframe of entities and their neighbors
        Schema: entity0, predicate1, entity1, predicate2, entity2, ...
    """
    query1 = get_random_entities_query(num_of_entities=num_of_entities)
    entities = yago_db.query(query1)
    entities_df = pd.DataFrame([f"{entity[1]}" for entity in entities], columns=["entity0"])

    for i in range(depth - 1):
        entities_single_hop = single_hop_multiple_entities(yago_db, entities_df)
        entities_df[[f"predicate{i+1}", f"entity{i+1}"]] = entities_single_hop

    return entities_df

def single_hop_multiple_entities(yago_db: YagoDB, entities_df: pd.DataFrame, *,
    yago_endpoint_url = YAGO_ENDPOINT_URL) -> pd.DataFrame:
    """
    Single-hop random walk on the YAGO knowledge graph.
    Takes a dataframe of entities and returns a dataframe of entities and their neighbors.
    """
    query2 = get_triples_multiple_subjects_query(
        entities=[f"<{entity}>" for entity in entities_df["entity0"].tolist()], 
        columns_dict=SPARQL_COLUMNS_DICT
    )
    response = query_kg(yago_endpoint_url, query2)
    triples = get_triples_from_response(response)
    entities_hop_1 = entities_df.apply(
        lambda row: sample_triple_for_entity_as_list(triples_df=triples, entity=row["entity0"]), 
        axis=1, result_type="expand").rename(columns={0: "predicate1", 1: "entity1"})
    return entities_hop_1

def sample_triple_for_entity_as_list(triples_df: pd.DataFrame, entity: str, *, 
    sparql_columns_dict: dict = SPARQL_COLUMNS_DICT) -> List[str]:
    """
    Samples triples for a given entity.
    """
    if entity is None:
        return [None, None]
    matched_triples_df = triples_df[triples_df[sparql_columns_dict["subject"]] == entity]\
        [[sparql_columns_dict["predicate"], sparql_columns_dict["object"]]]
    if len(matched_triples_df) == 0:
        return [None, None]
    sampled_triple = matched_triples_df.sample(n=1, replace=False).iloc[0]
    return [sampled_triple[sparql_columns_dict["predicate"]], sampled_triple[sparql_columns_dict["object"]]]

if __name__=='__main__':
    parser = argparse.ArgumentParser(description="Random walks on the YAGO knowledge graph.")
    parser.add_argument("--num_of_entities", type=int, default=10, help="Number of entities to start the random walk with.")
    parser.add_argument("--depth", type=int, default=3, help="Depth of the random walk.")
    args = parser.parse_args()

    yago_db = YagoDB(db_name=YAGO_ENTITY_STORE_DB_PATH)
    random_walks_df = random_walks_multiple_v1(yago_db, num_of_entities=args.num_of_entities, depth=args.depth)
    print(random_walks_df)