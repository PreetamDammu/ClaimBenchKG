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
    """
    RandomWalk2 class.
    It takes into account the number of facts an entity is involved in to weight the sampling.
    It also returns the description of the entities and predicates.

    NOTE: Most of the functions work with entity_labels instead of entity_ids.
    """
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


    def single_hop_batch(self, entities_df: pd.DataFrame, entity_column_label: str, *,
        entities_hop_1_cols: dict = None) -> pd.DataFrame:
        """
        Single-hop random walk on the YAGO knowledge graph.
        Takes a dataframe of entities and returns a dataframe of entities and their neighbors.

        Parameters:
        ----------
        entities_df: pd.DataFrame
            The dataframe of entities
        
        entity_column_label: str
            The entity column label from which to perform the single hop

        entities_hop_1_cols: dict
            The dictionary of columns to use for the returned entities in the first hop

        Returns:
        ----------
        entities_df: pd.DataFrame
            The dataframe of entities and their neighbors
        """
        if entities_hop_1_cols is None:
            entities_hop_1_cols = {0: "predicate1", 1: "entity1"}
        
        # First, get the triples for the entities
        query2 = get_triples_multiple_subjects_query(
            entities=[f"<{entity}>" for entity in entities_df[entity_column_label].tolist()], 
            columns_dict=sparql_columns_dict
        )
        response = query_kg(yago_endpoint_url, query2)
        triples = get_triples_from_response(response)

        # Get the counts for the objects
        triples_object_counts = self.get_counts_for_entities(entity_series=triples[sparql_columns_dict["object"]],
            entity_column_label=sparql_columns_dict["object"], count_label=sparql_columns_dict["object_count"])
        ## The counts returned by get_counts_for_entities align with the triples
        triples[sparql_columns_dict["object_count"]] = triples_object_counts[sparql_columns_dict["object_count"]].values

        # Finally, use the objects and their counts to get one entity each for the first hop
        entities_hop_1 = entities_df.apply(
            lambda row: self.sample_triple_for_entity_by_count(triples_with_object_prob_df=triples,
                entity=row[entity_column_label]),
            axis=1, result_type="expand").rename(columns=entities_hop_1_cols)
        return entities_hop_1


    def get_counts_for_entities(self, entity_series: pd.Series, entity_column_label: str, *,
        count_label: str = 'count') -> pd.DataFrame:
        """
        Get the counts for the entities.

        Parameters:
        ----------
        entity_series: pd.Series
            The series of entities (entity labels)

        entity_column_label: str
            The entity column label to use in the returned dataframe

        count_label: str
            The count label to use in the returned dataframe

        Returns:
        ----------
        counts_df: pd.DataFrame
            The dataframe of entities and their counts
        """
        entity_labels = entity_series.tolist()
        query = get_entity_count_from_label_multiple_query(entity_labels=entity_labels)
        entity_counts = self.yago_db.query(query)
        entity_counts_df = pd.DataFrame(entity_counts, columns=["entity_id", entity_column_label, count_label])
        entity_counts_df = entity_series.to_frame(name=entity_column_label)\
            .merge(entity_counts_df, left_on=entity_column_label, right_on=entity_column_label, how="left")
        entity_counts_df[[count_label]].fillna(0, inplace=True)
        return entity_counts_df[[entity_column_label, count_label]]

    def sample_triple_for_entity_by_count(self, triples_with_object_prob_df: pd.DataFrame, entity: str) -> List[str]:
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

if __name__=='__main__':
    yago_db = YagoDB(db_name=YAGO_ENTITY_STORE_DB_PATH)
    random_walk = RandomWalk2(yago_db=yago_db)
    entities_df = random_walk.random_walk(num_of_entities=5, depth=3)
    print(entities_df)