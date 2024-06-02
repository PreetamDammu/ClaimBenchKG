"""Random walk sampling from a Wikidata5m graph.

- Use `parse_graph.py` to generate the data pickle
- `c` is a hyperparameter representing the dampening of common nodes sampling
    - `c` = 1 will have each node weighed by inverse in-degree
    - `c` = 0 is uniform sampling
- Run `python random_sample.py -h` to get all options
- For 3-hop paths on my Macbook Air, ~10 examples are generated per second
"""

import csv
import pickle
import random
from argparse import ArgumentParser
from typing import List, Set, Tuple

import networkx as nx
import numpy as np


def sample(
    G: nx.DiGraph,
    n_hops: int,
    c: float,
    bad_prop_ids: Set[str] = set(),
    bad_item_ids: Set[str] = set(),
) -> Tuple[List[Tuple[str, ...]], ...]:
    """Samples.

    Args:
    - G: NetworkX DiGraph
    - n_hops: number of hops
    - c: constant for the sampling
    - bad_prop_ids: property ids to avoid sampling
    - bad_item_ids: item ids to avoid sampling

    Returns:
    - tuple of:
        - list of sampled items
        - list of properties connecting them
    """
    # get random initial item
    initial_item = random.choice(list(G.nodes))

    path = [initial_item]
    item_ids = set([initial_item])
    prev_id = initial_item
    properties = []
    prop_ids = set()

    # get path
    for _ in range(n_hops):
        # get all outgoing claims
        outgoing_claims = [
            claim
            for claim in G.out_edges(prev_id, data=True)
            if claim[2]["id"] not in prop_ids and claim[2]["id"] not in bad_prop_ids
        ]  # remove duplicate and bad relations

        outgoing_claims = [
            claim
            for claim in outgoing_claims
            if claim[1] not in item_ids and claim[1] not in bad_item_ids
        ]  # remove duplicate and bad items

        # ensure we aren't at a dead end
        if not outgoing_claims:
            # HACK: restart - just call itself again
            return sample(
                G,
                n_hops,
                c,
                bad_prop_ids,
                bad_item_ids,
            )

        # get probs
        in_deg = np.array(
            [x[1] for x in G.in_degree([claim[1] for claim in outgoing_claims])]
        )
        in_deg = in_deg**-c
        probs = in_deg / np.sum(in_deg)

        # sample
        idx = np.random.choice(a=len(probs), p=probs)
        path.append(outgoing_claims[idx][1])
        prev_id = outgoing_claims[idx][1]

        # update
        item_ids.update([item[1] for item in outgoing_claims])
        properties.append(outgoing_claims[idx][2]["id"])
        prop_ids.add(outgoing_claims[idx][2]["id"])

    return path, properties


def main(args):
    with open(args.pickle, "rb") as f:
        G, _ = pickle.load(f)

    with open(args.out_file, "w") as f:
        writer = csv.writer(f)
        for i in range(args.n_samples):
            try:
                items, relations = sample(G, 3, 0.3)
                writer.writerow(items + relations)
                if args.print_every > 0 and (i + 1) % args.print_every == 0:
                    print(f"iteration: {i+1}")
            except Exception as e:
                print(e)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("pickle", type=str, help="pickled data file")
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
    parser.add_argument(
        "--print-every", type=int, default=-1, help="how often to print updates"
    )
    args = parser.parse_args()
    main(args)
