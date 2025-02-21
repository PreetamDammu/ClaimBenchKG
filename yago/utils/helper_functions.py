import json
import os
from tqdm import tqdm

import re

def decode_underscored_unicode(s: str) -> str:
    """
    Decodes any underscores of the form: _uXXXX_ into their corresponding
    Unicode character. Then replaces all remaining underscores with spaces.

    """
    
    # 1. Replace patterns like "_uXXXX_" with the corresponding Unicode character
    pattern = r"_u([0-9A-Fa-f]{4})_"  # matches something like _u002E_ or _u00A9_
    
    def unicode_replacer(match):
        hex_code = match.group(1)  # the part after 'u' and before the next underscore
        return chr(int(hex_code, 16))  # convert the hex code to an integer, then to a Unicode character

    s = re.sub(pattern, unicode_replacer, s)

    # 2. Replace remaining underscores with spaces
    s = s.replace("_", " ")
    
    # 3. Strip extra whitespace
    return s.strip()

def read_and_merge_json(directory_path):
    """
    Reads all JSON files in the given directory and merges them into a single dictionary.

    Args:
        directory_path (str): Path to the directory containing JSON files.

    Returns:
        dict: A dictionary containing merged content from all JSON files.
    """
    merged_data = {}
    
    files_list = os.listdir(directory_path)
    print(files_list)
    print(f"Found {len(files_list)} files in {directory_path}")

    for file_name in files_list:
        if file_name.endswith('.json'):
            file_path = os.path.join(directory_path, file_name)
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                    if isinstance(data, dict):
                        merged_data.update(data)
                    else:
                        raise ValueError(f"File {file_name} does not contain a JSON object.")
            except Exception as e:
                print(f"Error reading file {file_name}: {e}")

    return merged_data

def save_json_to_disk(data, output_path):
    """
    Saves the given data as a JSON file to the specified output path.

    Args:
        data (dict): Data to save as a JSON file.
        output_path (str): Path where the JSON file will be saved.

    Returns:
        None
    """
    try:
        with open(output_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=4, ensure_ascii=False)
        print(f"Merged JSON data saved to {output_path}")
    except Exception as e:
        print(f"Error saving JSON data to {output_path}: {e}")

def check_unwanted_facts(triples, threshold=20):
    """
    Checks if the percentage of unwanted facts in the list of triples is below the given threshold.

    Parameters:
        triples (list of tuples): A list of triples in the form (subject, predicate, object).
        threshold (float): The maximum allowable percentage of unwanted facts.

    Returns:
        bool: True if the percentage of unwanted facts is below the threshold, False otherwise.
    """
    # Define unwanted predicates
    unwanted_predicates = {
        'http://schema.org/gender',
        'http://schema.org/inLanguage',
        'http://schema.org/birthPlace',
        'http://schema.org/deathPlace',
        'http://yago-knowledge.org/resource/neighbors'
        
    }

    # Count total triples and unwanted triples
    total_triples = len(triples)
    unwanted_count = sum(1 for _, predicate, _ in triples if predicate in unwanted_predicates)
    
    # Calculate percentage of unwanted facts
    if total_triples == 0:
        return True  # If there are no triples, percentage of unwanted facts is trivially below threshold
    
    unwanted_percentage = (unwanted_count / total_triples) * 100
    
    

    filter_flag = unwanted_percentage > threshold
    return filter_flag, unwanted_percentage

def process_dataframe_unwanted(df, threshold=20):
    """
    Processes the DataFrame to compute unwanted facts and stores results in new columns.

    Parameters:
        df (pd.DataFrame): The input DataFrame with a column 'subgraph_Steiner_largest_connected'.
        threshold (float): The threshold percentage for unwanted facts.

    Returns:
        pd.DataFrame: The updated DataFrame with new columns for filter flag and unwanted percentage.
    """
    # Initialize progress bar
    tqdm.pandas(desc="Processing rows")
    
    # Apply the function to the DataFrame column
    results = df['subgraph_Steiner_largest_connected'].progress_apply(lambda x: check_unwanted_facts(x, threshold))
    
    # Unpack results into new columns
    df['unwanted_filter_flag'], df['unwanted_percentage'] = zip(*results)
    
    return df


def save_as_jsonl(data, file_path):
    """
    Saves a list of dictionaries to a .jsonl file.

    Args:
        data (list): A list of dictionaries to be saved.
        file_path (str): Path to the output .jsonl file.

    Raises:
        ValueError: If the data is not a list of dictionaries.
    """
    if not isinstance(data, list) or not all(isinstance(item, dict) for item in data):
        raise ValueError("Input data must be a list of dictionaries.")

    with open(file_path, 'w') as file:
        for entry in data:
            file.write(json.dumps(entry) + '\n')
            
def read_jsonl_file(file_path):
    """
    Reads a JSON Lines (JSONL) file where each line is a separate JSON object.
    Returns a list of Python dictionaries (or other data structures if the JSON
    objects are not strictly dictionaries).
    
    :param file_path: Path to the .jsonl file
    :return: A list of deserialized JSON objects
    """
    data = []
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            if line:  # Skip any empty lines
                data.append(json.loads(line))
    return data