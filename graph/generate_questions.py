"""Generate QA examples from Wikidata5m.

- Requires data pickle db locally and a .env file with 'AZURE_OPENAI_KEY' and
  'AZURE_OPENAI_ENDPOINT' set. See the Azure instance for reference.
- Writes generated samples to a CSV file with format: INPUT_LINE_NUMER, QUESTION, PROMPT
    - 0-indexed
- Usage: `python3 generate.py DATA_PICKLE OUT_FILE N_SAMPLES [args]`
- Use `python3 generate.py -h` for additional help.
"""

import pickle
import time
from argparse import ArgumentParser
from typing import Dict, List
import csv
from concurrent.futures import ThreadPoolExecutor

from dotenv import dotenv_values
from openai import AzureOpenAI, OpenAI, RateLimitError


PROMPT = """You will be given a starting item and a sequence of relationships, as hops, leading to an answer. Convert this information into a question, asking what the final item would be after all of the hops. Only respond with the question, nothing else. Do not include the final item in the question. Try to keep the questions coherent and intelligible.

Note that the hops follow, in the sequence:

STARTING ITEM -> hop1 -> hop2 -> ... -> hopn -> FINAL ITEM

Ensure that your question asks about the final items with the proper hop relationship directions and orderings.

For instance, given the starting item: "Barack Obama" and the hops "Born in state", "Capital city", you might respond: "What is the capital of the state which Barack Obama was born in?"

Sequence:
"""

def main(args):
    # get Azure OpenAI client
    print('creating OpenAI client')
    secrets = dotenv_values(".env")
    api_key = secrets["AZURE_OPENAI_KEY"]
    azure_endpoint = secrets["AZURE_OPENAI_ENDPOINT"]
    if azure_endpoint is None or api_key is None:
        raise Exception(".env values not set")
    client = AzureOpenAI(
        azure_endpoint=azure_endpoint,
        api_key=api_key,
        api_version="2024-02-15-preview",
    )

    print('loading pickled data')
    with open(args.pickle_file, "rb") as f:
        _, aliases = pickle.load(f)

    with open(args.sample_file, 'r') as in_file:
        reader = csv.reader(in_file)
        with open(args.out_file, 'w') as out_file:
            writer = csv.writer(out_file)
            t = time.time()
            arguments = []
            for i, line in enumerate(reader):
                try:
                    n_items = args.n_hops + 1
                    items = line[:n_items]
                    props = line[n_items:2 * n_items - 1]
                    arguments.append((i, items, props, aliases, client))
                    if (i+1) % args.batch_size == 0:
                        with ThreadPoolExecutor() as executor:
                            futures = executor.map(lambda x: generate(*x), arguments)
                            for future in futures:
                                if future is not None:
                                    writer.writerow(future)
                        arguments = []
                        print(f'iter: {i+1}, {time.time() - t}')
                        t = time.time()
                except Exception as e:
                    print(f'exception: {e}')
            with ThreadPoolExecutor() as executor:
                futures = executor.map(lambda x: generate(*x), arguments)
                for future in futures:
                    if future is not None:
                        writer.writerow((future))


def generate(
    i: int,
    items: List[str],
    props: List[str],
    aliases: Dict[str, Dict[str, str]],
    client: OpenAI,
    max_requests: int = 5,
    ):
    example = PROMPT
    example += f'STARTING ITEM: name: {aliases[items[0]]["name"]}\n'
    for i, hop in enumerate(props):
        example += f'HOP {i+1}: name: {aliases[hop]["name"]}, description: {aliases[hop].get("description", "")}\n'
    example += f'FINAL ITEM: name: {aliases[items[-1]]["name"]}'

    attempts = 1
    while True:
        response = openai_request(example, client)
        if response['response'] is not None:
            return i, response['response'], example
        elif response['status'] == 'ratelimit':
            if attempts == max_requests:
                return None
            time.sleep(2 ** attempts)
        else:
            return None


def openai_request(prompt, client, model='gpt4-turbo-0125'):
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model=model,
        )
    except RateLimitError:
        return {'response': None, 'status': 'ratelimit'}
    try:
        response = chat_completion.choices[0].message.content
        return {'response': response, 'status': None}
    except Exception as e:
        return {'response': None, 'status': e}


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('pickle_file', type=str, help='pickled data file')
    parser.add_argument('sample_file', type=str, help='sampled path file')
    parser.add_argument('out_file', type=str, help='output file')
    parser.add_argument('n_hops', type=int, help='number of hops in sampled file')
    parser.add_argument('--batch_size', type=int, default=100, help='number of examples per batched request')
    args = parser.parse_args()
    main(args)
