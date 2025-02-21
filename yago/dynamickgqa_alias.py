"""
This script is used to generate answer alias file for DynamicKGQA dataset.
"""
import json
import argparse
from datasets import load_dataset
from SPARQLWrapper import SPARQLWrapper, JSON

HF_PATH = "preetam7/dynamic_kgqa"
JSON_FILE = "./dynamickgqa/dynamickgqa_test.json"
ALIAS_OUTPUT_FILE = "./dynamickgqa/dynamickgqa_test_alias.jsonl"
ANSWER_URI_KEY = "answer_uri"

SPARQLPATH = "http://localhost:9999/bigdata/sparql"

PREFIXES = {
    "yago": "http://yago-knowledge.org/resource/",
    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "xsd": "http://www.w3.org/2001/XMLSchema#",
    "ontolex": "http://www.w3.org/ns/lemon/ontolex#",
    "dct": "http://purl.org/dc/terms/",
    "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
    "owl": "http://www.w3.org/2002/07/owl#",
    "wikibase": "http://wikiba.se/ontology#",
    "skos": "http://www.w3.org/2004/02/skos/core#",
    "schema": "http://schema.org/",
    "cc": "http://creativecommons.org/ns#",
    "geo": "http://www.opengis.net/ont/geosparql#",
    "prov": "http://www.w3.org/ns/prov#",
    "wd": "http://www.wikidata.org/entity/",
    "data": "https://www.wikidata.org/wiki/Special:EntityData/",
    "sh": "http://www.w3.org/ns/shacl#",
    "s": "http://www.wikidata.org/entity/statement/",
    "ref": "http://www.wikidata.org/reference/",
    "v": "http://www.wikidata.org/value/",
    "wdt": "http://www.wikidata.org/prop/direct/",
    "wpq": "http://www.wikidata.org/prop/quant/",
    "wdtn": "http://www.wikidata.org/prop/direct-normalized/",
    "p": "http://www.wikidata.org/prop/",
    "ps": "http://www.wikidata.org/prop/statement/",
    "psv": "http://www.wikidata.org/prop/statement/value/",
    "psn": "http://www.wikidata.org/prop/statement/value-normalized/",
    "pq": "http://www.wikidata.org/prop/qualifier/",
    "pqv": "http://www.wikidata.org/prop/qualifier/value/",
    "pqn": "http://www.wikidata.org/prop/qualifier/value-normalized/",
    "pr": "http://www.wikidata.org/prop/reference/",
    "prv": "http://www.wikidata.org/prop/reference/value/",
    "prn": "http://www.wikidata.org/prop/reference/value-normalized/",
    "wdno": "http://www.wikidata.org/prop/novalue/",
    "ys": "http://yago-knowledge.org/schema#"
}

def execurte_sparql(sparql_query, sparql_path = SPARQLPATH):
    sparql = SPARQLWrapper(sparql_path)
    sparql.setQuery(sparql_query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    return results["results"]["bindings"]

def get_prefix_string() -> str:
    """
    Returns the prefixes as a substring of the SPARQL format.
    """
    prefix_list = [f"PREFIX {key}: <{value}>" for key, value in PREFIXES.items()]
    prefix_string = "\n".join(prefix_list)
    return prefix_string

PREFIX_STRING = get_prefix_string()

def get_label_query(answers):
    """
    Uses the Sparql query to get the label of the answer.
    """
    answers = [f"<{answer}>" for answer in answers]
    query = f"""
    {PREFIX_STRING}
    SELECT ?answer ?label WHERE {{
        VALUES ?answer {{ {" ".join(answers)} }}
        ?answer rdfs:label ?label
        FILTER(lang(?label) = "en")
    }}
    """
    return query

def get_alias_query(answers):
    """
    Uses the Sparql query to get the alias of the answer.
    """
    answers = [f"<{answer}>" for answer in answers]
    query = f"""
    {PREFIX_STRING}
    SELECT ?answer ?alias WHERE {{
        VALUES ?answer {{ {" ".join(answers)} }}
        ?answer schema:alternateName ?alias
        FILTER(lang(?alias) = "en")
    }}
    """
    return query


def main():
    # Load json dataset
    with open(JSON_FILE, "r") as f:
        data = json.load(f)
    
    answers = []
    threshold = 10
    for index, item in enumerate(data):
        answers.append(item[ANSWER_URI_KEY])
        if (index + 1) % threshold == 0:
            # First, get the labels
            label_query = get_label_query(answers)
            label_results = execurte_sparql(label_query)
            labels_and_aliases = {}

            for label_result in label_results:
                answer = label_result["answer"]["value"]
                label = label_result["label"]["value"]
                labels_and_aliases[answer] = {"label": label, "aliases": []}

            # Then, get the aliases
            alias_query = get_alias_query(answers)
            alias_results = execurte_sparql(alias_query)

            for alias_result in alias_results:
                answer = alias_result["answer"]["value"]
                alias = alias_result["alias"]["value"]
                if labels_and_aliases.get(answer) is None: continue
                labels_and_aliases[answer]["aliases"].append(alias)

            final_labels_and_aliases = {}
            for answer, label_and_aliases in labels_and_aliases.items():
                aliases = label_and_aliases.get("aliases")
                if aliases is None or len(aliases) == 0: continue
                final_labels_and_aliases[label_and_aliases["label"]] = aliases

            # Save to the output jsonl file
            with open(ALIAS_OUTPUT_FILE, "a+") as f:
                for label, alias in final_labels_and_aliases.items():
                    f.write(json.dumps({label: alias}) + "\n")

            answers = []
            print(f"Processed {index + 1} answers")

if __name__ == "__main__":
    main()