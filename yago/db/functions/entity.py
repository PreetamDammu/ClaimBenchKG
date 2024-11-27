from typing import List, Set

############################################################################################################
# Functions
def get_random_entities_query(*, 
    num_of_entities: int = 1) -> str:
    """Generate a query to get a fixed number of random entities from the YAGO knowledge graph.

    Parameters:
    ----------
    num_of_entities: int
        The number of entities to query
    
    Returns:
    ----------
    query: str
        The query to get the random entities
    """
    query = f"""
    SELECT item_id, item_label FROM items ORDER BY RANDOM() LIMIT {num_of_entities}
    """
    return query
