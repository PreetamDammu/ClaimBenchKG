"""Exploratory testing of Wikidata5m random walk sampling."""
from wikidata5m.utils import WikidataDB, get_openai_response
from wikidata5m.samplers import RandomWalk
from wikidata5m.filters import BadPropertyFilter


DB_PATH = 'db/knowledge_graph.db'
NUM_CLAIMS = 3
NUM_EXAMPLES = 5


def main():
    db = WikidataDB(DB_PATH)
    sampler = RandomWalk(
        db,
        NUM_CLAIMS,
        property_filters=[BadPropertyFilter()],
        # reversed=True,
    )

    for _ in range(NUM_EXAMPLES):
        claims = sampler.sample()
        if len(claims) == 0:
            print('*' * 80)
            print('SKIPPED EXAMPLE')
            print('*' * 80)
            print()
            continue
        example = []
        example.append(f'Starting item: {db.get_item(claims[0].subject_id)}')
        print('-' * 80)
        print(f'Starting item: {db.get_item(claims[0].subject_id)}')
        for i, claim in enumerate(claims):
            print('-' * 80)
            c = db.get_property(claim.property_id)
            example.append(f'Hop {i+1}: {c}')
            print(f'Hop {i+1}: {c}')
            print(f'Intermediate item {i+1}: {db.get_item(claim.target_id)}')
        sample = '\n'.join(example)
        print('-' * 80)
        print(f'Target item: {db.get_item(claims[-1].target_id)}')
        print('-' * 80)
        prompt = """
You will be given a starting item and a sequence of relationships, as hops, leading to an answer. You need to convert this information into a question, asking what the final item would be after all of the hops.

Note that the hops follow, in the sequence:

STARTING ITEM -> hop1 -> hop2 -> ... -> hopn -> FINAL ITEM

Ensure that your question asks about the final items with the proper hop relationship directions and orderings.

For instance, given the starting item: "Barack Obama" and the hops "Born in state", "Capital city", you might respond: "What is the capital of the state which Barack Obama was born in?"

Sample:
""" + sample
        print(get_openai_response(prompt))
        print('-' * 80)
        print()

if __name__ == '__main__':
    main()
