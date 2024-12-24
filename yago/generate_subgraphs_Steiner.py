from kg.query import query_kg, query_kg_endpoint, get_triples_from_response
import matplotlib.pyplot as plt
import networkx as nx
import json

from utils.kg_functions import load_json, extract_ids_with_prefix, convert_QID_yagoID
from utils.kg_functions import combine_lists_from_dict, get_yago_direct_neighbors, sparql_to_triples_with_main_entity
from utils.kg_functions import parallel_process_nodes, extract_ids_with_prefix, parallel_convert_QID_yagoID

from utils.subgraph_functions import create_graph_from_triples, build_minimal_subgraph_Steiner, largest_connected_subgraph
from utils.subgraph_functions import edges_to_triples, get_interesting_entities, filter_triples_by_predicates


yago_endpoint_url = "http://localhost:9999/bigdata/sparql"
data = load_json('/home/ubuntu/preetam_experiments/inputs/final_results_train10K_wiki40B.json')
keys = list(data.keys())

exclude_props = ['knowsLanguage', 'location', 'image', 'about', 'comment', 'gtin', 'url', 'label', 'postalCode', 'isbn', 'sameAs', 'mainEntityOfPage', 'leiCode', 'type', 'dateCreated', 'unemploymentRate', 'length', 'description', 'iswcCode', 'iataCode', 'logo', 'alternateName', 'geo', 'subclassOf', 'icaoCode', 'humanDevelopmentIndex', 'sameAs', 'dateCreated', 'startDate', 'endDate', 'follows', 'superEvent']

results = {}
for idx in range(10): #len(keys)):
    
    QID = keys[idx]
    interesting_entities = get_interesting_entities(QID, data[QID]['entities'])

    results = parallel_process_nodes(interesting_entities)
    comb_list = combine_lists_from_dict(results)
    comb_list = filter_triples_by_predicates(comb_list, exclude_props)
    graph = create_graph_from_triples(comb_list)

    subgraph_Steiner = build_minimal_subgraph_Steiner(graph, interesting_entities)
    subgraph_Steiner_largest_connected = largest_connected_subgraph(subgraph_Steiner)

    subgraph_Steiner_triples = edges_to_triples(subgraph_Steiner)
    subgraph_Steiner_largest_connected_triples = edges_to_triples(subgraph_Steiner_largest_connected)
    results[QID] = {'subgraph_Steiner': subgraph_Steiner_triples, 
                    'subgraph_Steiner_length': len(subgraph_Steiner_triples), 
                    'subgraph_Steiner_largest_connected': subgraph_Steiner_largest_connected_triples,
                    'subgraph_Steiner_largest_connected_length': len(subgraph_Steiner_largest_connected_triples)
                    }

#save as JSON
with open('results_subgraphs_Steiner.json', 'w') as f:
    json.dump(results, f)
    

