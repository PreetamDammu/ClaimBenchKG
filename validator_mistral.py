from utils.azure_endpoints import query_endpoint_batch_save, query_endpoint
from utils.prompt_functions import generate_verification_prompt_v1
from utils.preprocess_functions import get_labels_and_descriptions_for_triplets
from utils.wiki_helpers import get_info_for_qid
import numpy as np
import pandas as pd
import json
from tqdm import tqdm

model_name = 'mistral'

fname = '26K_3_hop'
df = pd.read_csv(f'/home/azureuser/cloudfiles/code/Users/preetams/dump/{fname}.csv')

prompts_dict = {}

for i in tqdm(range(len(df))):
    row = df.iloc[i]
    question = row['QUESTION']
    answer = row['ANSWER_NAME']
    path = row['ANSWER_NAME']
    
    prompt = generate_verification_prompt_v1(question, answer)
    prompts_dict[i] = prompt

prompts_dict = dict(sorted(prompts_dict.items()))
np.save(f'outputs/annotator_results/prompts_{fname}_{model_name}.npy', prompts_dict)
prompts_list = list(prompts_dict.values())

processed_responses = query_endpoint_batch_save(prompts_list, model=model_name, max_workers=3, save_interval=100, 
                                                    save_path=f"outputs/annotator_results/{fname}_{model_name}_results_temp")


processed_responses = dict(sorted(processed_responses.items()))
np.save(f"outputs/annotator_results/{fname}_{model_name}_results_all", processed_responses)
print("Saved all responses!")