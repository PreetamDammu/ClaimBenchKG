import json

# def generate_verification_prompt_yaml(question, answer):
#    prompt = f"""
# **Prompt Adequacy Verification Test**

# **Objective:** Ensure the question is coherent and the provided answer is suitable and relevant.

# **Instructions:**

# 1. **Read the Question:**
#    - Is the question logical and clear?
#    - Is it unambiguous?
#    - Can it have multiple valid answers?

# 2. **Read the Answer:**
#    - Does the answer directly address the question?

# 3. **Evaluate the Question and Answer Pair:**
#    - Does the answer meet the informational needs of the question?
#    - Is it free from irrelevant information?

# **Example:**

# **Question:** What is the capital of the administrative territorial entity that Kul Mishan is a part of?

# **Expected Answer Characteristics:**
#    - The answer should be a capital city.
#    - It should correspond to the entity that Kul Mishan is part of.

# **Sample Answer Evaluations:**
#    - **"Ardal."** - Suitable, addresses the question.
#    - **"Tehran."** - Suitable if Tehran is the correct capital.
#    - **"Iran."** - Unsuitable, does not specify a capital city.
#    - **"Kul Mishan is in Ardal."** - Suitable but less direct.

# **Sample Multiple Answer Evaluations:**
#    - **"What is the capital city of Washington?"** - Cannot have multiple answers (false).
#    - **"Where did Barack Obama study?"** - Can have multiple answers (true).

# **Verification Checklist:**

# - [ ] The question is logical and clear.
# - [ ] The answer directly addresses the question and meets its informational needs.
# - [ ] The answer is free from irrelevant information.
# - [ ] The question can/cannot have multiple valid answers.

# **Response Format:**
# Provide your evaluation in the following YAML format with fields:
# - "question_valid": true/false
# - "answer_relevance": true/false
# - "multiple_answers_possible": true/false
# - "comments": "Your comments here"

# **Question and Answer to Evaluate:**

# **Question:** {question}

# **Answer:** {answer}

# """
#    return prompt


def generate_selection_prompt(question, valid_answer, options):
    prompt = f"""
**Prompt Validation and Selection Task**

**Objective:** Identify all suitable options from the provided list that can serve as valid answers to the given question. Ensure that each selected option directly addresses the question and meets the informational needs.

**Instructions:**

1. **Read the Question:**
   - Understand the information being sought by the question.

2. **Read the Valid Answer:**
   - Understand the nature of the answer that directly addresses the question and meets its informational needs.

3. **Evaluate the Options:**
   - Select all options that are direct and appropriate answers to the question.
   - Avoid options that are irrelevant or do not adequately satisfy the question.

**Example 1:**

**Question:** What is the occupation of the founder of the university that John Guillim attended?

**Valid Answer:** priest

**Options to Evaluate:**
   - religious occupation
   - cleric
   - rabbi
   - priestess
   - Catholic priest

**Sample Evaluations:**
   - **"religious occupation."** - Unsuitable, vague and not specific.
   - **"cleric."** - Suitable, addresses the question.
   - **"rabbi."** - Suitable if it matches the occupation in context.
   - **"priestess."** - Unsuitable, does not match the valid answer's gender implication.
   - **"Catholic priest."** - Suitable, a specific type of priest.

**Example 2:**

**Question:** What is the location of the headquarters of the regulatory authority of the sport that Kai Gehring plays?

**Valid Answer:** Zürich

**Options to Evaluate:**
   - Zürich District
   - Greater Zurich Area
   - Zurich metropolitan area
   - RZU
   - Zurich
   - city of Switzerland
   - District 2

**Sample Evaluations:**
   - **"Zürich District."** - Suitable, addresses the question.
   - **"Greater Zurich Area."** - Suitable, addresses the question.
   - **"Zurich metropolitan area."** - Suitable, addresses the question.
   - **"RZU."** - Unsuitable, not specific.
   - **"Zurich."** - Suitable, directly addresses the question.
   - **"city of Switzerland."** - Unsuitable, not specific.
   - **"District 2."** - Unsuitable, not specific.

**Verification Checklist:**

- [ ] The valid answer directly addresses the question and meets its informational needs.
- [ ] Selected options are direct and relevant answers.
- [ ] Irrelevant options are excluded.

**Question and Valid Answer:**

**Question:** {question}

**Answer:** {valid_answer}

**Other Options to Select From:** {options}

**Response Format:**
Please provide your evaluation in the JSON format with the field:
- "answers": [list of selected options]
"""
    return prompt

def generate_verification_prompt_v1(question, answer):
   prompt = f"""
**Prompt Adequacy Verification Test**

**Objective:** Ensure the question is coherent and the provided answer is suitable and relevant.

**Instructions:**

1. **Read the Question:**
   - Is the question logical and clear?
   - Is it unambiguous?
   - Can it have multiple valid answers?

2. **Read the Answer:**
   - Does the answer directly address the question?

3. **Evaluate the Question and Answer Pair:**
   - Does the answer meet the informational needs of the question?
   - Is it free from irrelevant information?

**Example:**

**Question:** What is the capital of the administrative territorial entity that Kul Mishan is a part of?

**Expected Answer Characteristics:**
   - The answer should be a capital city.
   - It should correspond to the entity that Kul Mishan is part of.

**Sample Answer Evaluations:**
   - **"Ardal."** - Suitable, addresses the question.
   - **"Tehran."** - Suitable if Tehran is the correct capital.
   - **"Iran."** - Unsuitable, does not specify a capital city.
   - **"Kul Mishan is in Ardal."** - Suitable but less direct.

**Sample Multiple Answer Evaluations:**
   - **"What is the capital city of Washington?"** - Cannot have multiple answers (false).
   - **"Where did Barack Obama study?"** - Can have multiple answers (true).

**Verification Checklist:**

- [ ] The question is logical and clear.
- [ ] The answer directly addresses the question and meets its informational needs.
- [ ] The answer is free from irrelevant information.
- [ ] The question can/cannot have multiple valid answers.

**Response Format:**
Provide your evaluation in the following JSON format:
- "question_valid": true/false
- "answer_relevance": true/false
- "multiple_answers_possible": true/false
- "comments": "Your comments here"

**Question and Answer to Evaluate:**

**Question:** {question}

**Answer:** {answer}

"""
   return prompt


def generate_selection_prompt(question, valid_answer, options):
    prompt = f"""
**Prompt Validation and Selection Task**

**Objective:** Identify all suitable options from the provided list that can serve as valid answers to the given question. Ensure that each selected option directly addresses the question and meets the informational needs.

**Instructions:**

1. **Read the Question:**
   - Understand the information being sought by the question.

2. **Read the Valid Answer:**
   - Understand the nature of the answer that directly addresses the question and meets its informational needs.

3. **Evaluate the Options:**
   - Select all options that are direct and appropriate answers to the question.
   - Avoid options that are irrelevant or do not adequately satisfy the question.

**Example:**

**Question:** What is the occupation of the founder of the university that John Guillim attended?

**Valid Answer:** priest

**Options to Evaluate:**
   - religious occupation
   - cleric
   - rabbi
   - priestess
   - Catholic priest

**Sample Evaluations:**
   - **"religious occupation."** - Unsuitable, vague and not specific.
   - **"cleric."** - Suitable, addresses the question.
   - **"rabbi."** - Suitable if it matches the occupation in context.
   - **"priestess."** - Unsuitable, does not match the valid answer's gender implication.
   - **"Catholic priest."** - Suitable, a specific type of priest.

**Verification Checklist:**

- [ ] The valid answer directly addresses the question and meets its informational needs.
- [ ] Selected options are direct and relevant answers.
- [ ] Irrelevant options are excluded.

**Question and Valid Answer:**

**Question:** {question}

**Answer:** {valid_answer}

**Other Options to Select From:** {options}

**Response Format:**
Provide only your evaluation in the following JSON format:
- "answers": [list of selected options]
"""
    return prompt


def generate_verification_prompt_v1(question, answer):
    prompt = f"""
**Prompt Adequacy Verification Test**

**Objective:** Verify that the question is clear and the answer appropriately addresses it.

**Instructions:**

1. **Evaluate the Question:**
   - Is the question clear and logical?
   - Is it unambiguous?

2. **Evaluate the Answer:**
   - Does it directly address the question?
   - Is it free from irrelevant information?
   - Does it provide a complete response?

**Example for Understanding:**

**Example Question:** What is the capital of the administrative territorial entity that Kul Mishan is a part of?

**Expected Answer Characteristics:**
   - The answer should be the name of a capital city.
   - It should correctly correspond to the administrative territorial entity that Kul Mishan is a part of.

**Sample Answer Evaluations:**
   - **"Ardal."** - Suitable, addresses the question, provides relevant information.
   - **"Tehran."** - Suitable if Tehran is indeed the capital of the entity that Kul Mishan is a part of.
   - **"Iran."** - Unsuitable, does not specify the capital.
   - **"Kul Mishan is in Ardal."** - Suitable, but less direct.

**Verification Checklist:**
- [ ] The question is logical and clear.
- [ ] The answer directly addresses the question.

**Question and Answer to Evaluate:**

**Question:** {question}

**Answer:** {answer}

**Response Format:**
Provide your evaluation in the following JSON format:
- "question_valid": true/false
- "answer_relevance": true/false
- "comments": "Your comments here"
"""
    return prompt






def generate_verification_prompt_old(question, answer):
    prompt = f"""
**Prompt Adequacy Verification Test**

**Objective:** Ensure the question is coherent, and the provided answer is a suitable and relevant response that addresses the informational needs of the question.

**Instructions:**

1. **Read the Question:**
   - Does the question make logical sense?
   - Is the question clear and unambiguous?

2. **Read the Answer:**
   - Does the answer directly address the question?

3. **Evaluate the Question and Answer Pair:**
   - Does the answer fulfill the informational needs implied by the question?
   - Is the answer free from irrelevant information?
   - Does the answer provide a complete response to the question?

**Example:**

**Question:** What is the capital of the administrative territorial entity that Kul Mishan is a part of?

**Expected Answer Characteristics:**
   - The answer should be the name of a capital city.
   - It should correctly correspond to the administrative territorial entity that Kul Mishan is a part of.

**Sample Answer Evaluations:**
   - **"Ardal."** - Suitable, addresses the question, provides relevant information.
   - **"Tehran."** - Suitable if Tehran is indeed the capital of the entity that Kul Mishan is a part of.
   - **"Iran."** - Unsuitable, does not specify the capital.
   - **"Kul Mishan is in Ardal."** - Suitable, but less direct.

**Verification Checklist:**

- [ ] The question is logical and clear.
- [ ] The answer directly addresses the question.

**Question:** {question}

**Answer:** {answer}

**Response Format:**
Please provide your evaluation in the following JSON format:
- "question_valid": true/false,
- "answer_relevance": true/false,
- "comments": "Your comments here"
"""
    return prompt

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