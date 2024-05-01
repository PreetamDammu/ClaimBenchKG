"""Filters for sampling from Wikidata5m.

Ideally we'll add more filters if they makes sense.
"""
from wikidata5m.utils import Property, PropertyFilter


class BadPropertyFilter(PropertyFilter):
    """Filter for manually-picked bad properties."""

    def check(self, property: Property) -> bool:
        id = property.id
        return id not in [
            'P31', # Instance of. Too vague
            'P279', # Subclass of. Also vague
        ]

# TODO: other filters
# - prevent superclass property
# - filter elements with too little/many incoming links
#     - could also filter only with a probability
