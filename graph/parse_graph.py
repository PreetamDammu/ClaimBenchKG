"""Script to convert Wikidata5m download to pickled NetworkX graph and aliases.

- Converts to a NetworkX DiGraph and dictionary of relation aliases.
- Wikidata5m download: https://deepgraphlearning.github.io/project/wikidata5m
- We use the transductive train split for claims!
"""

import argparse
import pickle
import time

import networkx as nx
import pywikibot


def main(args):
    G = nx.DiGraph()
    site = pywikibot.Site("wikidata", "wikidata")
    repo = site.data_repository()

    # add all nodes
    missing_items = set()
    with open(args.entity_file, "r") as f:
        for i, line in enumerate(f):
            id = line.split("\t")[0]
            try:
                item = pywikibot.ItemPage(repo, id)
                item.get()
                name = item.labels["en"]
                aliases = item.aliases.get("en", [])  # have no alias if empty
                G.add_nodes_from([(id, {"name": name, "alias": ",".join(aliases)})])
            except pywikibot.exceptions.NoPageError:
                missing_items.add(id)
            print(i)

    # get relation aliases
    relations = {}
    with open(args.relation_file, "r") as f:
        t = time.time()
        for i, line in enumerate(f):
            id = line.split("\t")[0]
            relations[id] = {}
            if i == 99:
                print(time.time() - t)

    # add claims to graph
    with open(args.claim_file, "r") as f:
        for line in f:
            s, p, o = line[:-1].split("\t")
            if p in relations:  # skip claims with a non-existent relation
                G.add_edges_from([(s, o, {"id": p})])

    # save the graph and aliases!
    with open(args.out_file, "wb") as f:
        pickle.dump((G, relations), f)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("entity_file", type=str, help="file of Wikidata5m entities")
    parser.add_argument("relation_file", type=str, help="file of Wikidata5m relations")
    parser.add_argument("claim_file", type=str, help="file of Wikidata5m claims")
    parser.add_argument("out_file", type=str, help="location to store pickled output")
    args = parser.parse_args()
    main(args)
