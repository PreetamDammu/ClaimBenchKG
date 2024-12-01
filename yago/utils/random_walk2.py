"""
This module contains RandomWalk2 class.
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

class RandomWalk2:
    def __init__(self, yago_db: YagoDB, *, yago_endpoint_url = YAGO_ENDPOINT_URL,
        sparql_columns_dict: dict = SPARQL_COLUMNS_DICT):
        """
        Initialize the RandomWalk2 object.

        Parameters:
        ----------
        yago_db: YagoDB
            The YagoDB object

        yago_endpoint_url: str
            The YAGO endpoint URL

        sparql_columns_dict: dict
            The SPARQL columns dictionary
        """
        self.yago_db = yago_db
        self.yago_endpoint_url = yago_endpoint_url
        self.sparql_columns_dict = sparql_columns_dict




    def sample_triple_for_entity_by_count_as_list(triples_with_object_prob_df: pd.DataFrame, entity: str) -> List[str]:
        """
        Samples triples for a given entity.
        Uses the count of the entities to weight the sampling.

        Parameters:
        ----------
        triples_with_object_prob_df: pd.DataFrame
            The dataframe of triples with object count

        entity: str
            The entity to sample triples for

        Returns:
        ----------
        sampled_triple: List[str]
            The sampled triple as a list (predicate, object)
        """
        if entity is None:
            return [None, None]
        
        matched_triples_columns = [self.sparql_columns_dict["predicate"], self.sparql_columns_dict["object"], 
            self.sparql_columns_dict["object_count"]]
        matched_triples_df = triples_with_object_prob_df[triples_df[sparql_columns_dict["subject"]] == entity][matched_triples_columns]
        if len(matched_triples_df) == 0:
            return [None, None]
        
        sampled_triple = matched_triples_df.sample(n=1, replace=False, weights=self.sparql_columns_dict["object_count"]).iloc[0]
        return [self.sampled_triple[sparql_columns_dict["predicate"]], 
            self.sampled_triple[sparql_columns_dict["object"]]]