import json


def json_to_string(file_path):
    """
    Reads a JSON file and returns its contents as a Python object.
    
    :param file_path: The path to the JSON file.
    :return: The JSON object.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Failed to read JSON file {file_path}:", e)
        return None

