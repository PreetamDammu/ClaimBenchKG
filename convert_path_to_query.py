"""Create LLM prompts from a csv file of sampled Wikidata5m paths.

Will write a JSONL file which can be used with the parallel processing script
from the OpenAI cookbook.
"""

import argparse
import csv
import json
import sqlite3
from typing import List

LLM_PROMPT = """You will be given a starting item and a sequence of relationships, as hops, leading to an answer. You need to convert this information into a question, asking what the final item would be after all of the hops. Only respond with the question, nothing else. The info for each item and property are multiple aliases, but only include on name for each.

Note that the hops follow, in the sequence:

STARTING ITEM -> hop1 -> hop2 -> ... -> hopn -> FINAL ITEM

Ensure that your question asks about the final items with the proper hop relationship directions and orderings. DO NOT include the final item in the question.

For instance, given the starting item: "Barack Obama" and the hops "Born in state", "Capital city", you might respond: "What is the capital of the state which Barack Obama was born in?"

Sample:
"""


def main(args):
    db = sqlite3.connect(args.database)
    curr = db.cursor()
    with open(args.__dict__["in-file"], "r") as in_file:
        reader = csv.reader(in_file)
        with open(args.__dict__["out-file"], "w") as out_file:
            for i, line in enumerate(reader):
                items = [
                    line[0],
                    line[len(line) // 2],
                ]  # we only use first and last item
                properties = line[1 + len(line) // 2 :]
                prop_desc = []
                for prop in properties:
                    curr.execute(
                        "SELECT property_alias FROM properties where property_id = ?",
                        (prop,),
                    )
                    prop_desc.append(curr.fetchone()[0])
                item_desc = []
                for item in items:
                    curr.execute(
                        "SELECT item_alias FROM items where item_id = ?",
                        (item,),
                    )
                    item_desc.append(curr.fetchone()[0])
                prompt = create_prompt(item_desc, prop_desc)
                example = json.dumps(
                    {
                        "model": args.model,
                        "prompt": prompt,
                        "metadata": {
                            "row_id": i + 1,  # we one-index here
                            "in_file": args.__dict__["in-file"],
                        },
                    }
                )
                out_file.write(example + "\n")


def create_prompt(path: List[str], properties: List[str]) -> str:
    """Create a prompt from a sample.

    Args:
    - path: a sampled path of item descriptions
    - properties: sampled path of property descriptions

    Returns:
    - prompt for the sample
    """
    example = []
    example.append(f"Starting item: {path[0]}")
    for i, prop in enumerate(properties):
        example.append(f"Hop {i+1}: {prop}")
    example.append(f"Final item: {path[-1]}")
    sample = "\n".join(example)
    prompt = LLM_PROMPT + sample
    return prompt


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("database", type=str, help="path to Wikidata5m database")
    parser.add_argument("in-file", type=str, help="input csv file")
    parser.add_argument("out-file", type=str, help="output csv file")
    parser.add_argument(
        "--model",
        type=str,
        default="gpt4-turbo-0125",
        help="OpenAI model to use during generation",
    )
    args = parser.parse_args()
    main(args)
