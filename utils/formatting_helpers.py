import re
import json

def convert_to_json_object(original_string, model):
       
    if model == 'phi3':
        model_type = 'serverless'
    elif model == 'mistral':
        model_type = 'dedicated'
    elif model == 'llama3-8b':
        model_type = 'dedicated'
    else:
        raise Exception("Model details not found")
    
    if model_type == 'serverless':
        try:
            cleaned_string = original_string.replace('```json', '').replace('\n', '').replace('```', '') 
            # cleaned_string = original_string.replace("```json", "")
            cleaned_string = cleaned_string.strip("```json\n")
            # Use regex to strip the unwanted parts
            cleaned_string = re.sub(r"(^'```json\n|\n```'$)", '', cleaned_string).strip()

            # Further clean the string by removing additional newlines or surrounding quotes
            cleaned_string = cleaned_string.strip()

            # Convert string to JSON object
            json_object = json.loads(cleaned_string)
            return json_object
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            return None
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return None
    elif model_type == 'dedicated':
        try:
            json_object = json.loads(original_string)
            result = json.loads(json_object['output'])
            return result
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            return None
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return None
        
    else:
        print("Model details not found")
        return None