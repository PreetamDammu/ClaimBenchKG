import urllib.request
import json
import os
from dotenv import dotenv_values

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

def query_endpoint(data, model):       

    body = str.encode(json.dumps(data))
    
    # print(model)
    
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

    try:
        response = urllib.request.urlopen(req)

        result = response.read()
        # print(result)
        return result
    except urllib.error.HTTPError as error:
        print("The request failed with status code: " + str(error.code))

        # Print the headers - they include the requert ID and the timestamp, which are useful for debugging the failure
        print(error.info())
        print(error.read().decode("utf8", 'ignore'))
