import re

def extract_session_id(session_str):
    match = re.search(r"/sessions/(.*)/contexts/", session_str)

    if match:
        extracted_str = match.group(1)
        return extracted_str
    
    return ""

def get_str_from_food_dict(food_dict):
    return ", ".join([f"{int(value)} {key}" for key, value in food_dict.items()])