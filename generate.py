"""Generate QA examples from Wikidata5m.

Requires Wikidata5m sqlite3 db locally and a .env file with 'AZURE_OPENAI_KEY'
and 'AZURE_OPENAI_ENDPOINT' set. See the Azure instance for reference.

Writes generated samples to a CSV file with the header format:
GENERATED_QUESTION, ITEM_1, ITEM_2, ..., ITEM_N_HOPS+1, PROP_1, PROP_2, PROP_N_HOPS

Usage: `python3 generate.py DATABASE OUT_FILE N_SAMPLES [args]`

- Use `python3 generate.py -h` for additional help.
- Examples:
    - Simple generation of 10 examples: `python3 generate.py knowledge_graph.db out.csv 10`
    - Generate with 4 hops and c=0.5:
      `python3 generate.py knowledge_graph.db out.csv 5 --n-hops 4 --c 0.5`
"""

import csv
import sqlite3
from argparse import ArgumentParser
from collections import Counter
from typing import List, Optional, Set, Tuple

import numpy as np
from dotenv import dotenv_values
from openai import AzureOpenAI, OpenAI


def sample(
    cursor: sqlite3.Cursor,
    n_hops: int,
    c: float,
    bad_prop_ids: Set[str] = set(),
    bad_item_ids: Set[str] = set(),
    log: Optional[List[str]] = None,
) -> Tuple[List[Tuple[str, ...]], ...]:
    """Samples.

    Args:
    - cursor: the sqlite3 cursor to the db
    - n_hops: number of hops
    - c: constant for the sampling
    - bad_prop_ids: property ids to avoid sampling
    - bad_item_ids: item ids to avoid sampling
    - log: where to store logging messages

    Returns:
    - tuple of:
        - list of sampled items
        - list of properties connecting them
    """
    if log is None:
        # no logging will be returned
        log = []

    # get random initial item
    cursor.execute(
        """
        SELECT * FROM items WHERE item_id IN (SELECT item_id FROM items ORDER BY RANDOM() LIMIT 1)
    """
    )
    initial_item = cursor.fetchone()

    path = [initial_item]
    item_ids = set([initial_item[0]])
    prev_id = initial_item[0]
    properties = []
    prop_ids = set()

    # get path
    for _ in range(n_hops):
        # get all outgoing claims
        cursor.execute(
            """
            SELECT * FROM claims WHERE subject_id = ?
        """,
            (prev_id,),
        )
        outgoing_claims = [
            claim for claim in cursor.fetchall() if claim[2] not in prop_ids
        ]  # remove duplicate claims
        outgoing_claims = [
            claim for claim in outgoing_claims if claim[2] not in bad_prop_ids
        ]  # remove bad claims
        # exclude any properties which point to multiple items
        counts = Counter([claim[2] for claim in outgoing_claims])
        orig = len(outgoing_claims)  # HACK: for logging
        outgoing_claims = [
            claim for claim in outgoing_claims if counts[claim[2]] <= 1
        ]  # remove bad claims
        log.append(f"removed {orig - len(outgoing_claims)} claims via duplicates")

        # get outgoing items
        outgoing_items = []
        # we reverse so we can delete without idx issues
        # TODO: change to increase speed if it is a problem
        for i, claim in reversed(list(enumerate(outgoing_claims))):
            cursor.execute(
                """
                SELECT * FROM items where item_id = ?
            """,
                (claim[3],),
            )
            item = cursor.fetchone()
            if item[0] in item_ids or item[0] in bad_item_ids:
                log.append("deleted: " + str(outgoing_claims[i]))
                del outgoing_claims[i]
            else:
                outgoing_items.insert(0, item)

        # get probs
        in_deg = np.array([item[3] for item in outgoing_items]) ** -c
        probs = in_deg / np.sum(in_deg)

        # sample
        if not len(probs):
            log.append("no possible next hops")
            return path, properties
        idx = np.random.choice(a=len(probs), p=probs)
        path.append(outgoing_items[idx])
        prev_id = outgoing_items[idx][0]
        # add all items to item_ids (heuristic to prevent double hops)
        item_ids.update([item[0] for item in outgoing_items])

        # get property
        cursor.execute(
            """
            SELECT * FROM properties WHERE property_id = ?
        """,
            (outgoing_claims[idx][2],),
        )
        properties.append(cursor.fetchone())
        prop_ids.add(outgoing_claims[idx][2])
    return path, properties


def generate(
    path: List[Tuple[str, ...]],
    properties: List[Tuple[str, ...]],
    client: OpenAI,
    model: str = "gpt4-turbo-0125",
) -> str:
    """Generate a question from a sample.

    Args:
    - path: a sampled path
    - properties: sampled properties
    - client: OpenAI client to generate from
    - model: OpenAI model to use for generation

    Returns:
    - question generated from GPT-4
    """
    example = []
    example.append(f"Starting item: {path[0][1]}")
    for i, prop in enumerate(properties):
        example.append(f"Hop {i+1}: {prop[1]}")
    sample = "\n".join(example)
    prompt = (
        """
You will be given a starting item and a sequence of relationships, as hops, leading to an answer. You need to convert this information into a question, asking what the final item would be after all of the hops. Only respond with the question, nothing else.

Note that the hops follow, in the sequence:

STARTING ITEM -> hop1 -> hop2 -> ... -> hopn -> FINAL ITEM

Ensure that your question asks about the final items with the proper hop relationship directions and orderings.

For instance, given the starting item: "Barack Obama" and the hops "Born in state", "Capital city", you might respond: "What is the capital of the state which Barack Obama was born in?"

Sample: """
        + sample
    )
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model=model,
    )
    response = chat_completion.choices[0].message.content
    if response is None:
        raise Exception("OpenAI response was None")
    return response


def main(args):
    # connect to db
    db = sqlite3.connect(args.database)
    cursor = db.cursor()

    # get Azure OpenAI client
    secrets = dotenv_values(".env")
    api_key = secrets["AZURE_OPENAI_KEY"]
    azure_endpoint = secrets["AZURE_OPENAI_ENDPOINT"]
    if azure_endpoint is None or api_key is None:
        raise Exception(".env values not set - see generate.py header for info")
    client = AzureOpenAI(
        azure_endpoint=azure_endpoint,
        api_key=api_key,
        api_version="2024-02-15-preview",
    )

    n_generated = 0
    with open(args.out_file, "w") as f:
        writer = csv.writer(f)
        header = ["GENERATED_QUESTION"]
        header += [f"ITEM_{i+1}" for i in range(args.n_hops + 1)]
        header += [f"PROP_{i+1}" for i in range(args.n_hops)]
        writer.writerow(header)

        while n_generated < int(args.n_samples):
            log = []
            path, props = sample(
                cursor,
                args.n_hops,
                args.c,
                bad_prop_ids=set(args.bad_props.split(" ")),
                bad_item_ids=set(args.bad_items.split(" ")),
                log=log,
            )

            if "no possible" in log[-1]:
                continue

            out = []
            for item in path:
                out.append(item[0])
            for prop in props:
                out.append(prop[0])

            generation = generate(path, props, client)
            out.insert(0, generation)
            writer.writerow(out)
            n_generated += 1
            print(f"Generated: {n_generated}")


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("database", type=str, help="path to Wikidata5m database")
    parser.add_argument("out_file", type=str, help="path to output csv file")
    parser.add_argument("n_samples", type=int, help="number of samples to generate")
    parser.add_argument(
        "--n-hops", type=int, default=3, help="number of hops per sample"
    )
    parser.add_argument("--c", type=float, default=0.3, help="normalization parameter")
    parser.add_argument(
        "--bad-props",
        type=str,
        default="P31 P1343 P279",
        help="bad properties, space-separated",
    )
    parser.add_argument(
        "--bad-items", type=str, default="", help="bad items, space-separated"
    )
    args = parser.parse_args()
    main(args)
