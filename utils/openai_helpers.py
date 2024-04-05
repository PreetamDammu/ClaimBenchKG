from openai import AzureOpenAI
from dotenv import dotenv_values

secrets = dotenv_values(".env")
personal_api_key = secrets['AZURE_OPENAI_KEY']
azure_endpoint = secrets['AZURE_OPENAI_ENDPOINT']

client = AzureOpenAI(
  azure_endpoint = azure_endpoint, 
  api_key=personal_api_key,  
  api_version="2024-02-15-preview"
)

def query_openai_model(prompt, model_name = "gpt4-turbo-0125"):
    response = client.chat.completions.create(
        model=model_name, # model = "deployment_name".
        temperature = 0.7,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"{prompt}"}
        ]
    )
    usage = response.usage

    return response.choices[0].message.content, usage


