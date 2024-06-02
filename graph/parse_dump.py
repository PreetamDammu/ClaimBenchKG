"""Parse a Wikidata dump to get names and descriptions.

- Dump can be found at `https://dumps.wikimedia.org/wikidatawiki/entities/`
  under: `latest-truthy.nt*`
"""

from argparse import ArgumentParser
import time


def main(args):
    with open(args.out_file, 'w') as out_file:
        with open(args.dump, 'r') as dump:
            allowed = 0
            per = 10000000
            t = time.time()
            for i, line in enumerate(dump):
                if 'http://schema.org/name' in line or 'http://schema.org/description' in line:
                    if '@en ' in line:
                        allowed += 1
                        out_file.write(line)
                if (i+1) % per == 0:
                    print(f'examples: {i+1}, allowed ratio: {(allowed / per):.8f}')
                    print(f'took: {(time.time() - t):.2f} seconds')
                    t = time.time()
                    allowed = 0

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('dump', type=str, help='wikidata truthy dump')
    parser.add_argument('out_file', type=str, help='out file for parsed data')
    args = parser.parse_args()
    main(args)
