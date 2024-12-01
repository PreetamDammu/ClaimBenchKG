"""
This module contains utility functions to implement random walk on the YAGO knowledge graph.
This is the second version of the random walk algorithm.
It takes into account the number of facts an entity is involved in to weight the sampling.
It also returns the description of the entities and predicates.

NOTE: Most of the functions work with entity_labels instead of entity_ids.
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
        from db.functions.entity import get_random_entities_query, get_entity_count_from_label_multiple_query
        from kg.query import get_triples_multiple_subjects_query, query_kg, get_triples_from_response
        sys.path.insert(0, path.dirname( path.abspath(__file__) ) )
        from constants import YAGO_ENTITY_STORE_DB_PATH, YAGO_PREFIXES_PATH, YAGO_ENDPOINT_URL
        from prefix import get_prefixes, get_url_from_prefix_and_id
    else:
        from ..db.yagodb import YagoDB
        from ..db.constants.main import YAGO_ALL_ENTITY_COUNT, YAGO_FACTS_ENTITY_COUNT
        from ..db.functions.entity import get_random_entities_query, get_entity_count_from_label_multiple_query
        from ..kg.query import get_triples_multiple_subjects_query, query_kg, get_triples_from_response
        from .constants import YAGO_ENTITY_STORE_DB_PATH, YAGO_PREFIXES_PATH, YAGO_ENDPOINT_URL
        from .prefix import get_prefixes, get_url_from_prefix_and_id
else:
    from db.yagodb import YagoDB
    from db.constants.main import YAGO_ALL_ENTITY_COUNT, YAGO_FACTS_ENTITY_COUNT
    from db.functions.entity import get_random_entities_query, get_entity_count_from_label_multiple_query
    from kg.query import get_triples_multiple_subjects_query, query_kg, get_triples_from_response
    from utils.constants import YAGO_ENTITY_STORE_DB_PATH, YAGO_PREFIXES_PATH, YAGO_ENDPOINT_URL
    from utils.prefix import get_prefixes, get_url_from_prefix_and_id

SPARQL_COLUMNS_DICT = {
    "subject": "subject",
    "predicate": "predicate",
    "object": "object",
    "object_count": "object_count"
}

def random_walks_multiple(yago_db: YagoDB, *, num_of_entities: int = 10, depth: int = 3,
    yago_endpoint_url = YAGO_ENDPOINT_URL, sparql_columns_dict: dict = SPARQL_COLUMNS_DICT) -> pd.DataFrame:
    """
    Random walks on the YAGO knowledge graph.
    This algorithm weights the neighbouring entities based on the number of facts they are involved in.
    This algorithm also returns the description of the entities and predicates.

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
    random_entities_query = get_random_entities_query(num_of_entities=num_of_entities)
    entities = yago_db.query(random_entities_query)
    entities_df = pd.DataFrame([f"{entity[1]}" for entity in entities], columns=["entity0"])    

    for i in range(depth - 1):
        entities_single_hop = single_hop_multiple_entities(yago_db, entities_df)
        entities_df[[f"predicate{i+1}", f"entity{i+1}"]] = entities_single_hop

    return entities_df

def single_hop_multiple_entities(yago_db: YagoDB, entities_df: pd.DataFrame, entity_column_label: str, *,
    yago_endpoint_url = YAGO_ENDPOINT_URL, sparql_columns_dict: dict = SPARQL_COLUMNS_DICT,
    entities_hop_1_cols: dict = None) -> pd.DataFrame:
    """
    Single-hop random walk on the YAGO knowledge graph.
    Takes a dataframe of entities and returns a dataframe of entities and their neighbors.
    """
    # First, get the triples for the entities
    query2 = get_triples_multiple_subjects_query(
        entities=[f"<{entity}>" for entity in entities_df[entity_column_label].tolist()], 
        columns_dict=sparql_columns_dict
    )
    response = query_kg(yago_endpoint_url, query2)
    triples = get_triples_from_response(response)

    # Get the counts for the objects
    triples_object_counts = get_counts_for_entities(yago_db=yago_db,
        entity_series=triples[sparql_columns_dict["object"]], entity_column_label=sparql_columns_dict["object"],
        count_label=sparql_columns_dict["object_count"])

    ## The counts returned by get_counts_for_entities align with the triples 
    triples[sparql_columns_dict["object_count"]] = triples_object_counts[sparql_columns_dict["object_count"]].values

    if entities_hop_1_cols is None:
        entities_hop_1_cols = {0: "predicate1", 1: "entity1"}

    entities_hop_1 = entities_df.apply(
        lambda row: sample_triple_for_entity_by_count_as_list(triples_df=triples, entity=row[entity_column_label],
            sparql_columns_dict=sparql_columns_dict), 
        axis=1, result_type="expand").rename(columns=entities_hop_1_cols)
    return entities_hop_1

def get_counts_for_entities(yago_db: YagoDB, entity_series: pd.Series, entity_column_label: str, *, 
    count_label = "count") -> pd.DataFrame:
    """
    Get the count of the entities from the YAGO knowledge graph.
    """
    entity_count_query = get_entity_count_from_label_multiple_query(entity_labels=entity_series)
    entity_counts = yago_db.query(entity_count_query)
    entity_counts_df = pd.DataFrame(entity_counts, columns=["entity_id", entity_column_label, count_label])
    entity_counts_df = entity_series.to_frame(name=entity_column_label)\
        .merge(entity_counts_df, left_on=entity_column_label, right_on=entity_column_label, how="left")
    return entity_counts_df[[entity_column_label, count_label]]

def sample_triple_for_entity_by_count_as_list(triples_with_object_prob_df: pd.DataFrame, entity: str, *,
    sparql_columns_dict: dict = SPARQL_COLUMNS_DICT, ) -> List[str]:
    """
    Samples triples for a given entity.
    Uses the count of the entities to weight the sampling.
    """
    if entity is None:
        return [None, None]
    matched_triples_df = triples_with_object_prob_df[triples_df[sparql_columns_dict["subject"]] == entity]\
        [[sparql_columns_dict["predicate"], sparql_columns_dict["object"], sparql_columns_dict["object_count"]]]
    if len(matched_triples_df) == 0:
        return [None, None]
    sampled_triple = matched_triples_df.sample(n=1, replace=False, weights=sparql_columns_dict["object_count"]).iloc[0]
    return [sampled_triple[sparql_columns_dict["predicate"]], sampled_triple[sparql_columns_dict["object"]]]