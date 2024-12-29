import logging
import os
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
from kg.query import query_kg, query_kg_endpoint, get_triples_from_response
from utils.kg_functions import (load_json, extract_ids_with_prefix, convert_QID_yagoID, 
                                combine_lists_from_dict, get_yago_direct_neighbors, 
                                sparql_to_triples_with_main_entity, parallel_process_nodes)

from utils.subgraph_functions import (create_graph_from_triples, build_minimal_subgraph_Steiner, 
                                      largest_connected_subgraph, edges_to_triples, 
                                      get_interesting_entities, filter_triples_by_predicates)

# Split variable for dynamic input/output locations
split = "train"  # Can be "train", "test", or "validation"

# Setup logging
log_location = '/home/ubuntu/preetam_experiments/logs/'
os.makedirs(log_location, exist_ok=True)

logging.basicConfig(
    filename=os.path.join(log_location, f'processing_{split}_multi.log'),
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logging.info("Starting multithreaded KG processing.")


input_location = f'/home/ubuntu/preetam_experiments/inputs/{split}/intermediates'
output_location = f'/home/ubuntu/preetam_experiments/outputs/{split}'
output_intermediate_location = f'/home/ubuntu/preetam_experiments/outputs/{split}/intermediate'

os.makedirs(output_location, exist_ok=True)
os.makedirs(output_intermediate_location, exist_ok=True)

exclude_props = ['knowsLanguage', 'location', 'image', 'about', 'comment', 'gtin', 'url', 'label', 
                 'postalCode', 'isbn', 'sameAs', 'mainEntityOfPage', 'leiCode', 'type', 'dateCreated', 
                 'unemploymentRate', 'length', 'description', 'iswcCode', 'iataCode', 'logo', 
                 'alternateName', 'geo', 'subclassOf', 'icaoCode', 'humanDevelopmentIndex', 'dateCreated', 
                 'startDate', 'endDate', 'follows', 'superEvent']

# Function to process a single QID
def process_qid(QID, data):
    try:
        # print(f"Processing QID: {QID}")
        # print(data)
        # print(data[QID])
        interesting_entities = get_interesting_entities(QID, data[QID]) #['entities']
        results = parallel_process_nodes(interesting_entities)
        comb_list = combine_lists_from_dict(results)
        comb_list = filter_triples_by_predicates(comb_list, exclude_props)
        graph = create_graph_from_triples(comb_list)

        subgraph_Steiner = build_minimal_subgraph_Steiner(graph, interesting_entities)
        subgraph_Steiner_largest_connected = largest_connected_subgraph(subgraph_Steiner)

        subgraph_Steiner_triples = edges_to_triples(subgraph_Steiner)
        subgraph_Steiner_largest_connected_triples = edges_to_triples(subgraph_Steiner_largest_connected)

        result = {
            'subgraph_Steiner': subgraph_Steiner_triples,
            'subgraph_Steiner_length': len(subgraph_Steiner_triples),
            'subgraph_Steiner_largest_connected': subgraph_Steiner_largest_connected_triples,
            'subgraph_Steiner_largest_connected_length': len(subgraph_Steiner_largest_connected_triples)
        }

        return QID, result

    except Exception as e:
        logging.error(f"Error processing QID {QID}: {e}")
        return QID, None

# Process all QIDs in a single file
def process_all_qids(keys, data, output_file_name, save_interval=1000):
    final_results = {}

    with ThreadPoolExecutor() as executor:
        futures = {executor.submit(process_qid, QID, data): QID for QID in keys}

        for idx, future in enumerate(tqdm(as_completed(futures), total=len(keys), desc="Processing QIDs")):
            QID = futures[future]
            try:
                result = future.result()
                if result[1] is not None:
                    final_results[result[0]] = result[1]
            except Exception as e:
                logging.error(f"Exception in future for QID {QID}: {e}")

            # Save intermediate results every `save_interval` (rewrite same file)
            if (idx + 1) % save_interval == 0:
                intermediate_path = os.path.join(output_intermediate_location, 'intermediate_results.json')
                with open(intermediate_path, 'w') as f:
                    json.dump(final_results, f)
                logging.info(f"Rewrote intermediate results to {intermediate_path}")

    # Save final results for this file
    final_path = os.path.join(output_location, output_file_name)
    with open(final_path, 'w') as f:
        json.dump(final_results, f)
    logging.info(f"Final results saved to {final_path}")

# Process all JSON files in the input folder
def process_files_in_folder(input_folder, save_interval=500):
    json_files = [f for f in os.listdir(input_folder) if f.endswith('.json')]
    total_files = len(json_files)

    logging.info(f"Found {total_files} JSON files to process.")

    for file_idx, json_file in enumerate(json_files, start=1):
        try:
            file_path = os.path.join(input_folder, json_file)
            logging.info(f"Processing file {file_idx}/{total_files}: {json_file}")

            data = load_json(file_path)
            keys = list(data.keys())
            
            # print(data)
            # print(data[keys[0]])
            # break

            output_file_name = json_file.replace('.json', '_results.json')
            process_all_qids(keys, data, output_file_name, save_interval=save_interval)

            logging.info(f"Completed processing for file: {json_file}")

        except Exception as e:
            logging.error(f"Error processing file {json_file}: {e}")

# Execute processing
process_files_in_folder(input_location, save_interval=500)
