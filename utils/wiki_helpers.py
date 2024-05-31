
from wikidata.client import Client
import logging

logging.basicConfig(level=logging.ERROR,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[logging.FileHandler("wiki_client_logs.txt"),
                              logging.StreamHandler()])
logger = logging.getLogger()
client = Client()

def get_label_for_qid(qid):
    try:
        entity = client.get(qid, load=True)
        label = str(entity.label)
        desc = str(entity.description)
        return label, desc

    except Exception as e:
        print(f"Error: {str(e)}")
        return None
    
def get_info_for_qid(qid):
    try:
        entity = client.get(qid, load=True)
        label = str(entity.label)
        desc = str(entity.description)
        aliases = entity.attributes.get('aliases', {}).get('en', [])

        # Extract English aliases
        english_aliases = [alias['value'] for alias in aliases]
        return label, desc, english_aliases

    except Exception as e:
        print(f"Error: {str(e)}")
        return None
    
def get_triplet_labels(triplet):

    subjQID = triplet[0] 
    predicateQID = triplet[1] 
    objQID = triplet[2] 

    try:
        subjLabel, subj_desc = get_label_for_qid(subjQID)
        predicateLabel, pred_desc = get_label_for_qid(predicateQID)
        objLabel, obj_desc = get_label_for_qid(objQID)
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

    tripletNames = (subjLabel, predicateLabel, objLabel)
    tripletDesc = (subj_desc, pred_desc, obj_desc)
    return tripletNames, tripletDesc

def get_label(qid, language='en'):
    entity = client.get(qid, load=True)
    if entity.label:
        if language in entity.label:
            return entity.label[language]
        else:

            return next(iter(entity.label.values()))
    return qid

def get_abstraction_nodes(qid, property_dict):
    try:
        entity = client.get(qid, load=True)
    except Exception as e:
        logger.error(f"Error fetching entity for QID {qid}: {e}")
        return {}

    abstraction_nodes = {}

    def fetch_related_nodes(entity, properties):
        related_nodes = []
        try:
            for pid in properties.values():
                if pid in entity.data['claims']:
                    related_entities = entity.data['claims'][pid]
                    related_nodes.extend(
                        related_entity['mainsnak']['datavalue']['value']['id']
                        for related_entity in related_entities
                    )
        except KeyError as e:
            logger.error(f"KeyError in fetching related nodes for properties {properties}: {e}")
        except Exception as e:
            logger.error(f"Error in fetching related nodes for properties {properties}: {e}")
        return related_nodes

    try:
        for category, relations in property_dict.items():
            abstraction_nodes[category] = {}
            for relation_type, properties in relations.items():
                abstraction_nodes[category][relation_type] = fetch_related_nodes(entity, properties)
    except KeyError as e:
        logger.error(f"KeyError in processing property_dict {property_dict}: {e}")
    except Exception as e:
        logger.error(f"Error in processing property_dict {property_dict}: {e}")

    return abstraction_nodes

# Function to convert abstraction QIDs to labels
def convert_abstraction_qids_to_labels(abstraction_nodes, language='en'):
    abstraction_nodes_names = {}
    mapping_label_to_qid = {}
    try:
        for category, relations in abstraction_nodes.items():
            abstraction_nodes_names[category] = {}
            for relation_type, qids in relations.items():
                labels = [get_label(qid, language) for qid in qids]
                abstraction_nodes_names[category][relation_type] = labels
                mapping_label_to_qid.update({label: qid for label, qid in zip(labels, qids)})
    except KeyError as e:
        logger.error(f"KeyError in abstraction_nodes {abstraction_nodes}: {e}")
    except Exception as e:
        logger.error(f"Error in abstraction_nodes {abstraction_nodes}: {e}")
    return abstraction_nodes_names, mapping_label_to_qid
