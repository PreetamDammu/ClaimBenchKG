
from wikidata.client import Client

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