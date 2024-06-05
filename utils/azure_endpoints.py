import urllib.request
import json
import os
from dotenv import dotenv_values

from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import numpy as np

import time
import logging

logging.basicConfig(filename='azure_endpoint_logger.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Create a logger object
logger = logging.getLogger(__name__)
# Function to log specific messages
def log_message(message):
    logger.log(logging.INFO, message)

secrets = dotenv_values(".env")
mistral_api_key = secrets['AZURE_MISTRAL_KEY']
mistral_endpoint = secrets['AZURE_MISTRAL_ENDPOINT']

phi3_api_key = secrets['AZURE_PHI3_KEY']
phi3_endpoint = secrets['AZURE_PHI3_ENDPOINT']

llama3_8b_api_key = secrets['AZURE_LLAMA3_8B_KEY']
llama3_8b_endpoint = secrets['AZURE_LLAMA3_8B_ENDPOINT']



# Request data goes here
# The example below assumes JSON formatting which may be updated
# depending on the format your endpoint expects.
# More information can be found here:
# https://docs.microsoft.com/azure/machine-learning/how-to-deploy-advanced-entry-script


def create_query_json(prompt, model, temperature=0.2,  max_new_tokens=512):
    
    if model == 'mistral':
        data =  {
        "input_data": {
            "input_string": [
            {
                "role": "user",
                "content": prompt
            }
            ],
            "parameters": {
            "temperature": temperature,
            "max_new_tokens": max_new_tokens
            }
        }
        }
        
    elif model == 'phi3':
        data =  {
        "messages": [
            {
            "role": "user",
            "content": prompt
            }
        ],
        "temperature": temperature,
        "max_new_tokens": max_new_tokens

        }
        
    elif model == 'llama3-8b':
        data =  {
        "input_data": {
            "input_string": [
            {
                "role": "user",
                "content": prompt
            }
            ],
            "parameters": {
            "temperature": temperature,
            "max_new_tokens": max_new_tokens
            }
        }
        }
        
    else:
        raise Exception("Model details not found")
        
    return data

def query_endpoint(prompt, model, temperature=0.2,  max_new_tokens=512):       

    data = create_query_json(prompt, model, temperature, max_new_tokens)
    body = str.encode(json.dumps(data))
    
    # print(data)
    
    if model == 'mistral':
        url = mistral_endpoint
        api_key = mistral_api_key
    elif model == 'phi3':
        url = phi3_endpoint
        api_key = phi3_api_key
        
    elif model == 'llama3-8b':
        url = llama3_8b_endpoint
        api_key = llama3_8b_api_key

    else:
        raise Exception("Model details not found")

    if not api_key:
        raise Exception("A key should be provided to invoke the endpoint")


    headers = {'Content-Type':'application/json', 'Authorization':('Bearer '+ api_key)}

    req = urllib.request.Request(url, body, headers)

    response = urllib.request.urlopen(req)

    result = response.read()

    return result


def query_endpoint_with_retries(prompt, model, temperature=0.2, max_new_tokens=512, max_retries=10):
    retry_count = 0
    wait_time = 1  # Start with 1 second wait time

    while retry_count < max_retries:
        try:
            return query_endpoint(prompt, model, temperature, max_new_tokens)
        except Exception as e:
            retry_count += 1
            if retry_count >= max_retries:
                logging.error(f"Failed after {max_retries} retries: {e}")
                return None
            logging.info(f"Error occurred. Retrying in {wait_time} seconds... (Retry {retry_count}/{max_retries})")
            time.sleep(wait_time)
            wait_time *= 2  # Exponential backoff

    return None

def query_endpoint_batch_save(prompts, model, max_workers=5, save_interval=500, save_path="outputs/results_temp"):
    results = {}
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(query_endpoint_with_retries, prompt, model): i for i, prompt in enumerate(prompts)}
        for i, future in enumerate(tqdm(as_completed(futures), total=len(futures), desc="Processing prompts")):
            idx = futures[future]
            try:
                result = future.result()
                results[idx] = result
            except Exception as e:
                logging.error(f"Error processing a future for prompt index {idx} - {model}: {e}")
                log_message(f"Error processing a future for prompt index {idx} - {model}: {e}")
                results[idx] = None
            
            # Save the results every 'save_interval' iterations
            if (i + 1) % save_interval == 0:
                logging.info(f'Saving intermediate results - {model}, iteration {i+1}')
                log_message(f'Saving intermediate results - {model}, iteration {i+1}')
                np.save(f'{save_path}', results)
                
    # Save final results
    np.save(f'{save_path}'+'_final', results)
    
    return results