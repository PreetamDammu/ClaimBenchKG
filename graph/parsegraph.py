"""Script to convert Wikidata5m download to pickled NetworkX graph and aliases.

- Converts to a NetworkX DiGraph and dictionary of relation aliases.
- Wikidata5m download: https://deepgraphlearning.github.io/project/wikidata5m
- We use the transductive train split for claims!
"""

import argparse
import pickle

import networkx as nx


def main(args):
    G = nx.DiGraph()

    # add all nodes
    with open(args.entity_file, "r") as f:
        for line in f:
            splits = line[:-1].split("\t")
            G.add_nodes_from([(splits[0], {"alias": ",".join(splits[1:])})])

    # get relation aliases
    aliases = {}
    with open(args.relation_file, "r") as f:
        for line in f:
            splits = line[:-1].split("\t")
            aliases[splits[0]] = ",".join(splits[1:])

    # add claims to graph
    with open(args.claim_file, "r") as f:
        for line in f:
            s, p, o = line[:-1].split("\t")
            if p in aliases:  # skip claims with a non-existent relation
                G.add_edges_from([(s, o, {"id": p})])

    # save the graph and aliases!
    with open(args.out_file, "wb") as f:
        pickle.dump((G, aliases), f)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("entity_file", type=str, help="file of Wikidata5m entities")
    parser.add_argument("relation_file", type=str, help="file of Wikidata5m relations")
    parser.add_argument("claim_file", type=str, help="file of Wikidata5m claims")
    parser.add_argument("out_file", type=str, help="location to store pickled output")
    args = parser.parse_args()
    main(args)
