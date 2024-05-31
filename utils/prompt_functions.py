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

def get_prompt_HIT_test(triplet_text):
    prompt = f'''
    Triplet format: (subject, relation, object)
    Use the given triplet and correspoding description provided below to generate two questions:
    Q1) Whose answer is the object node of the triplet.
    Q2) Whose answer is not the object node of the triplet, considering the triplet as a fact.
    
    Return the two questions, their labels, along with the rationale for each generated question.
    Valid labels are: "Supported" and "Refuted".

    Structure your response as a JSON object with the following keys:
    - "Q1": Question whose answer is the object node of the triplet.
    - "Rationale_Q1": Rationale for Q1.
    - "Label_Q1": Label for Q1.
    - "Q2": Question whose answer is NOT the object node of the triplet.
    - "Rationale_Q2": Rationale for Q2.
    - "Label_Q2": Label for Q2.


    The triplets and corresponding descriptions provided in brackets are as follows:
    {triplet_text}
    '''
    return prompt.replace('    ', '')

def get_abstraction_mcq_prompt(question, answer, options):
    prompt = f'''
    Given the following question and a valid answer, identify all suitable candidates from the provided options that can also serve as valid answers to the question. Note that there may be multiple correct answers. Only select options that provide a direct answer to the question and adequately satisfy the information sought.

    Question:
    {question}

    Valid Answer:
    {answer}

    Options:
    {options}

    Respond with a JSON object containing a list of the selected options under the key 'answer'. If no suitable options are present, return an empty list.
    '''

    return prompt.replace('    ', '')


def get_abstraction_mcq_prompt_v2(question, answer, options):
    prompt = f'''
    Given the following question and a valid answer, identify all suitable candidates from the provided options that can also serve as valid answers to the question. Note that there may be multiple correct answers. 
    Only select options that provide a specific and informative answer to the question, or closely related concepts, similar in nature to the valid answer provided.

    Question:
    {question}

    Valid Answer:
    {answer}

    Options:
    {options}

    Respond with a JSON object containing a list of the selected options under the key 'answer'. If no suitable options are present, return an empty list.
    '''

    return prompt.replace('    ', '')