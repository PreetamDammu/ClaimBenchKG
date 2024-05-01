"""Wikidata5m helper code.

See the `README.md` from the parent directory as well.

This helper package structured into a few files. The experiments aren't
contained within this file, but can import these utilties.

Files:
- `data`: data classes for properties, claims, items
- `filters`: filters for removing bad items when sampling
- `samplers`: samplers. Currently I've only got random walk implemented, but
              there's others that would be worth trying (e.g. pick large
              random subset of items, find all claims between those items)
- `utils`: utilities, including database helper and superclass for samplers

I made this a package so that it would be easy to try different experiments and
keep it modular, LMK if this does/doesn't work.
"""
