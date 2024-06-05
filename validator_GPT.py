
from utils.prompt_functions import generate_verification_prompt_v1
import numpy as np
import pandas as pd
from tqdm import tqdm


from utils.openai_helpers import query_openai_model_batch_save
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
np.save(f'outputs/annotator_results/prompts_{fname}.npy', prompts_dict)
prompts_list = list(prompts_dict.values())


processed_responses = query_openai_model_batch_save(prompts_list, model_name='gpt-4o', max_workers=10, save_interval=100, 
                                                    save_path=f"outputs/annotator_results/{fname}_results_temp")
processed_responses = dict(sorted(processed_responses.items()))
np.save(f"outputs/annotator_results/{fname}_results_all", processed_responses)
print("Saved all responses!")