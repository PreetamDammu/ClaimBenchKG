"""Samplers for Wikidata5m."""
from typing import Iterable, List
import random

from wikidata5m.utils import Sampler, ItemFilter, PropertyFilter, WikidataDB
from wikidata5m.data import Claim


class RandomWalk(Sampler):
    """Random Walk (with optional restart) Sampler."""

    def __init__(
        self,
        db: WikidataDB,
        num_claims: int,
        restart_prob: float = 0.0,
        item_filters: Iterable[ItemFilter] = [],
        property_filters: Iterable[PropertyFilter] = [],
        reversed: bool = False,
    ):
        """Initialize the sampler.

        Args:
        - db: `WikidataDB` connected to the database
        - num_claims: number of claims to return
        - restart_prob: probability of restarting on the random walk, defaults
          to `0.0`
        - item_filters: filters for sampling new items
        - property_filters: filters for sampling new properties
        - reversed: if the edges should be sampled in forward or reversed order
        """
        self._db = db
        self._num_claims = num_claims
        self._rp = restart_prob
        self._item_filters = item_filters
        self._property_filters = property_filters
        self._reversed = reversed

    def sample(self) -> List[Claim]:
        """Sample via Random Walk with given params.

        Returns:
        - `List` of sampled `Claims`
        """
        while True:
            curr_item = self._db.random_item()
            if all([f.check(curr_item) for f in self._item_filters]):
                break
        claims = []
        while len(claims) < self._num_claims:
            if self._reversed:
                linked_claims = list(self._db.claims_from_target(curr_item.id))
            else:
                linked_claims = list(self._db.claims_from_subject(curr_item.id))
            random.shuffle(linked_claims)
            no_valid_claim = True # TODO: better handling
            for sample_claim in linked_claims:
                sample_item = self._db.get_item(sample_claim.target_id)
                sample_prop = self._db.get_property(sample_claim.property_id)
                if all([f.check(sample_item) for f in self._item_filters]) and all([f.check(sample_prop) for f in self._property_filters]):
                    claims.append(sample_claim)
                    curr_item = sample_item
                    no_valid_claim = False
                    break
            if no_valid_claim:
                break
        if self._reversed:
            claims = list(reversed(claims))
        return claims
