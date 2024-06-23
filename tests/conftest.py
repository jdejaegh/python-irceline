import json
from unittest.mock import Mock, AsyncMock

import aiohttp


def get_api_data(fixture: str, plain=False) -> str | dict:
    with open(f'tests/fixtures/{fixture}', 'r') as file:
        if plain:
            return file.read()
        return json.load(file)


def get_mock_session(json_file=None, text_file=None):
    # Create the mock response
    mock_response = Mock()
    if json_file is not None:
        mock_response.json = AsyncMock(return_value=get_api_data(json_file))
    if text_file is not None:
        mock_response.text = AsyncMock(return_value=get_api_data(text_file, plain=True))

    mock_response.status = 200
    mock_response.headers = dict()

    # Create the mock session
    mock_session = Mock(aiohttp.ClientSession)
    mock_session.request = AsyncMock(return_value=mock_response)
    return mock_session


def create_mock_response(*args, **kwargs):
    etag = 'my-etag-here'
    mock_response = Mock()
    if '20240619' not in kwargs.get('url', ''):
        mock_response.status = 404
        mock_response.raise_for_status = Mock(side_effect=aiohttp.ClientResponseError(Mock(), Mock()))
    elif etag in kwargs.get('headers', {}).get('If-None-Match', ''):
        mock_response.text = AsyncMock(return_value='')
        mock_response.status = 304
    else:
        mock_response.text = AsyncMock(return_value=get_api_data('forecast.csv', plain=True))
        mock_response.status = 200

    if '20240619' in kwargs.get('url', ''):
        mock_response.headers = {'ETag': etag}
    else:
        mock_response.headers = dict()
    return mock_response


def get_mock_session_many_csv():
    mock_session = Mock(aiohttp.ClientSession)
    mock_session.request = AsyncMock(side_effect=create_mock_response)
    return mock_session
