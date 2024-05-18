import pandas as pd
from collections import Counter
from utils.openai_helpers import query_openai_model
from utils.wiki_helpers import get_label_for_qid, get_triplet_labels
from tqdm import tqdm
import json

def getNumber(s):
    s = s.replace('Q', '')
    s = s.replace('P', '')
    try:
        return int(s)
    except ValueError:
        return float(s)

def convert_to_triplets(input_list, numbersOnly = False):
    """
    :param input_list: List of strings formatted as 'head\trelation\ttail\n'
    :return: List of triplets (head, relation, tail)
    """
    # Split each string by the tab character and strip the newline character, then store as a tuple
    triplets = [tuple(item.strip().split('\t')) for item in input_list]
    if numbersOnly:
        triplets = [(getNumber(triplet[0]), getNumber(triplet[1]), getNumber(triplet[2])) for triplet in triplets]
    return triplets

def top_n_entities(triplets, n=None):
    """
    :param triplets: List of triplets (head, relation, tail)
    :param n: Number of top entities to return
    :return: List of tuples (entity, count) for the top n occurring entities
    """
    entities = [triplet[0] for triplet in triplets] + [triplet[2] for triplet in triplets]
    entity_counts = Counter(entities)
    if n is None:
        top_entities = entity_counts.most_common()  # Return all entities sorted by count
    else:
        top_entities = entity_counts.most_common(n)  # Return the top n entities

    return top_entities
    
    return top_entities

def triplets_containing_entity(triplets, qid):
    """
    :param triplets: List of triplets (entity, relation, entity)
    :param qid: The QID of the entity to filter by
    :return: List of triplets that contain the specified QID
    """
    filtered_triplets = [triplet for triplet in triplets if qid in triplet]
    
    return filtered_triplets

def get_labels_and_descriptions_for_triplets(triplets):
    labels_list = []
    descriptions_list = []
    
    for triplet in tqdm(triplets):
        result = get_triplet_labels(triplet)
        
        if result is not None:
            triplet_labels, triplet_descriptions = result
            labels_list.append(triplet_labels)
            descriptions_list.append(triplet_descriptions)
        else:
            print("Failed to get labels and descriptions for triplet:", triplet)
            labels_list.append(("Error", "Error", "Error"))
            descriptions_list.append(("Error", "Error", "Error"))

    return labels_list, descriptions_list

def format_triplets_text(labels_list, descriptions_list):
    formatted_text = []
    
    for labels, descriptions in zip(labels_list, descriptions_list):

        subjLabel, predicateLabel, objLabel = labels
        subj_desc, pred_desc, obj_desc = descriptions
        
        formatted_triplet = f"({subjLabel} ({subj_desc}), {predicateLabel}, {objLabel} ({obj_desc}))"
        formatted_text.append(formatted_triplet)
    
    return "\n".join(formatted_text)