import json

def get_prompt_v1(triplet_text):
    prompt = f'''
    Use the triplets and their descriptions provided below to generate a coherent paragraph.
    You may use only a subset of the triplets if you wish. The focus is to generate a paragraph that is natural, coherent and informative.

    Return the paragraph generated, and a mapping for each triplet to the claim in the paragraph that it was used to generate.

    Structure your response as a JSON object with the following keys:
    - "mapping": A dictionary mapping each claim in the paragraph to the triplet or set of triplets that were used to generate it.
    - "paragraph": The paragraph generated

    The triplets and their descriptions provided in brackets are as follows:
    {triplet_text}
    '''
    return prompt.replace('    ', '')


def get_prompt_v2(triplet_text):
    prompt = f'''
    Use the triplets and their descriptions provided below to generate a coherent paragraph.
    You may use only a subset of the triplets if you wish. The focus is to generate a paragraph that is natural, coherent and informative.

    
    Return the paragraph generated, and a mapping for each triplet to the claim in the paragraph that it was used to generate.

    Structure your response as a JSON object with the following keys:
    - "mapping": A dictionary mapping each claim in the paragraph to the triplet or set of triplets that were used to generate it.
    - "paragraph": The paragraph generated

    NOTE: The mapping only needs to be at the level of the triplet, not the individual entities within the triplet. 
    For example, if the paragraph contains the claim "The capital of France is Paris", the mapping should indicate that this claim was generated using the triplet ("France", "capital", "Paris").
    Both the subject and object entities should be mentioned in the corresponding claim in the paragraph.

    The triplets and their descriptions provided in brackets are as follows:
    {triplet_text}
    '''
    return prompt.replace('    ', '')

# create more variants here for different prompts, testing, ..etc.