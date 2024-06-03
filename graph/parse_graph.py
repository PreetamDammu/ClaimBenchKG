"""Script to convert Wikidata5m download to pickled NetworkX graph and aliases.

- Converts to a NetworkX DiGraph and dictionary of relation aliases.
- Use `parse_dump.py` to parse a Wikidata dump before running this script
- Wikidata5m download: https://deepgraphlearning.github.io/project/wikidata5m
- We use the "raw" (wikidata5m_all_triplet.txt) split for claims!
"""

import argparse
import pickle

import networkx as nx


def main(args):
    # add claims to graph
    print('adding claims to graph')
    G = nx.DiGraph()
    elements = set()
    with open(args.claim_file, "r") as f:
        for line in f:
            s, p, o = line[:-1].split("\t")
            elements.add(s)
            elements.add(o)
            elements.add(p)
            G.add_edges_from([(s, o, {"id": p})])

    # get names and descriptions
    print('getting names and descriptions')
    data = {}
    with open(args.parsed_dump, 'r') as f:
        for i, line in enumerate(f):
            splits = line.split('>')
            key = splits[0][32:]
            field = splits[1][20:]
            value = splits[-1][2:-7].encode('utf-8').decode('unicode_escape')
            if key in elements:
                props = data.get(key, {})
                props[field] = value
                data[key] = props
            if (i+1) % args.print_every == 0:
                print(f'{((i+1) / 1000000):.1f}M lines parsed')
    
    # remove any properties or aliases which don't have a name
    bad_edges = set()
    removed = 0
    for e in elements:
        if e not in data:
            if e[0] == 'P':
                bad_edges.add(e)
            elif e[0] == 'Q':
                removed += 1
                G.remove_node(e)
            else:
                raise Exception('Element which starts with not P or Q')
    print(f'removed {removed} nodes')

    to_remove = set()
    removed = 0
    for u, v, data in G.edges(data=True):
        if data['id'] in bad_edges:
            to_remove.add((u, v))
    for u, v in to_remove:
        removed += 1
        G.remove_edge(u, v)
    print(f'removed {removed} edges')

    # save the graph and aliases!
    print('saving data!')
    with open(args.out_file, "wb") as f:
        pickle.dump((G, data), f)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('parsed_dump', type=str, help='parsed dump of wikidata')
    parser.add_argument("claim_file", type=str, help="file of Wikidata5m claims")
    parser.add_argument("out_file", type=str, help="location to store pickled output")
    parser.add_argument('--print_every', type=int, default=1000000, help='how often to printupdates')
    args = parser.parse_args()
    main(args)
