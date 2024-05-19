from openai import AzureOpenAI
from dotenv import dotenv_values
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
import time
from tqdm import tqdm

secrets = dotenv_values(".env")
personal_api_key = secrets['AZURE_OPENAI_KEY']
azure_endpoint = secrets['AZURE_OPENAI_ENDPOINT']

client = AzureOpenAI(
  azure_endpoint = azure_endpoint, 
  api_key=personal_api_key,  
  api_version="2024-02-15-preview"
)


logging.basicConfig(filename='openai_query.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

def query_openai_model(prompt, model_name = "gpt4-turbo-0125"):
    response = client.chat.completions.create(
        model=model_name, # model = "deployment_name".
        temperature = 0.7,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"{prompt}"}
        ],
        response_format={"type": "json_object"}
    )
    usage = response.usage

    return response.choices[0].message.content, usage

def query_openai_model_with_retries(prompt, model_name="gpt4-turbo-0125", max_retries=5):
    retry_count = 0
    wait_time = 1  # Start with 1 second wait time
    while retry_count < max_retries:
        try:
            response = client.chat.completions.create(
                model=model_name,
                temperature=0.7,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": f"{prompt}"}
                ],
                response_format={"type": "json_object"}
            )
            return response.choices[0].message.content, response.usage
        except Exception as e:
            logging.error(f"Error querying prompt '{prompt}': {e}")
            if "rate limit" in str(e).lower():
                retry_count += 1
                logging.info(f"Rate limit exceeded. Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
                wait_time *= 2  
            else:
                break  
    return None, None

def query_openai_model_batch(prompts, model_name="gpt4-turbo-0125", max_workers=5):
    results = {}
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(query_openai_model, prompt, model_name): i for i, prompt in enumerate(prompts)}
        for future in tqdm(as_completed(futures), total=len(futures), desc="Processing prompts"):
            idx = futures[future]
            try:
                result = future.result()
                results[idx] = result
            except Exception as e:
                logging.error(f"Error processing a future for prompt index {idx}: {e}")
                results[idx] = (None, None)
    return results