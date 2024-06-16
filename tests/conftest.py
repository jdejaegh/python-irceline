import json


def get_api_data(fixture: str, plain=False) -> str | dict:
    with open(f'tests/fixtures/{fixture}', 'r') as file:
        if plain:
            return file.read()
        return json.load(file)
