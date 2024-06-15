import json


def get_api_data(fixture: str) -> dict:
    with open(f'tests/fixtures/{fixture}', 'r') as file:
        return json.load(file)
