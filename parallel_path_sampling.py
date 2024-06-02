"""Sample paths from a DB.

Used for getting question paths before generating questions.
"""

import csv
import sqlite3
from argparse import ArgumentParser
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Optional, Set, Tuple

import numpy as np


def sample(
    db_path: str,
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

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

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
            # HACK: restart - just call itself again
            conn.close()
            return sample(
                db_path,
                n_hops,
                c,
                bad_prop_ids,
                bad_item_ids,
                log,
            )
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

    conn.close()
    return path, properties


def process_and_write_to_csv(
    db_path: str,
    output_csv: str,
    num_samples: int,
    batch_size: int,
    n_workers: int,
    **sample_args
):
    def task(sample_args):
        path, properties = sample(**sample_args)
        return path, properties

    with ThreadPoolExecutor(max_workers=n_workers) as executor:
        futures = []
        for i in range(0, num_samples, batch_size):
            batch_futures = [
                executor.submit(task, {"db_path": db_path, **sample_args})
                for _ in range(min(batch_size, num_samples - i))
            ]
            futures.extend(batch_futures)
            print(len(futures))

            with open(output_csv, "w", newline="") as csvfile:
                csv_writer = csv.writer(csvfile)
                for future in as_completed(futures):
                    try:
                        path, props = future.result()
                        out = []
                        for item in path:
                            out.append(item[0])
                        for prop in props:
                            out.append(prop[0])
                        csv_writer.writerow(out)
                    except KeyboardInterrupt as e:
                        raise e
                    except Exception:
                        pass


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("database", type=str, help="path to Wikidata5m database")
    parser.add_argument("out_file", type=str, help="path to output csv file")
    parser.add_argument("n_samples", type=int, help="number of samples to generate")
    parser.add_argument(
        "--n-hops", type=int, default=3, help="number of hops per sample"
    )
    parser.add_argument(
        "--batch-size", type=int, default=10, help="batch size for generation"
    )
    parser.add_argument(
        "--n-workers", type=int, default=10, help="number of workers in generation"
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

    process_and_write_to_csv(
        args.database,
        args.out_file,
        args.n_samples,
        args.batch_size,
        args.n_workers,
        n_hops=args.n_hops,
        c=args.c,
        bad_prop_ids=set(args.bad_props.split(" ")),
        bad_item_ids=set(args.bad_items.split(" ")),
    )
