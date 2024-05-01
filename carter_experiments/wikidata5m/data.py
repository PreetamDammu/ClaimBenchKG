"""Data classes for Wikidata5m."""


class Item:
    """Wikidata5m item."""

    def __init__(self, id: str, alias: str, desc: str):
        """Instantiate the item.

        Args:
        - id: ID of the item
        - alias: alias of the item
        - desc: description of the item
        """
        self.id: str = id
        self.alias: str = alias
        self.desc: str = desc

    def __str__(self) -> str:
        return f'Item: {self.id}. {self.alias}'


class Property:
    """Wikidata5m property."""

    def __init__(self, id: str, alias: str):
        """Instantiate the property.

        Args:
        - id: ID of the property
        - alias: alias of the property
        """
        self.id: str = id
        self.alias: str = alias

    def __str__(self) -> str:
        return f'Property: {self.id}. {self.alias}'


class Claim:
    """Wikidata5m claim."""

    def __init__(self, id: int, subject_id: str, property_id: str, target_id: str):
        """Instantiate the claim.

        Args:
        - id: ID of the claim in the database
        - subject: ID of the subject `Item` of the claim
        - property: ID of the `Property` of the claim
        - target: ID of the target `Item` of the claim
        """
        self.id: int = id
        self.subject_id: str = subject_id
        self.property_id: str = property_id
        self.target_id: str = target_id

    def __str__(self) -> str:
        return f'subject: {self.subject_id}, Property: {self.property_id}, Target: {self.target_id}'
