from datetime import date
from unittest.mock import call

from src.open_irceline.api import _forecast_base_url, _user_agent
from src.open_irceline.api import IrcelineForecastClient
from src.open_irceline.data import ForecastFeature
from tests.conftest import get_api_data, get_mock_session_many_csv


def test_extract_from_csv():
    data = get_api_data('forecast.csv', plain=True)
    x, y = 50.45, 4.85

    result = IrcelineForecastClient.extract_result_from_csv(x, y, data)
    assert result == 13.0844

    result = IrcelineForecastClient.extract_result_from_csv(23, 4, data)
    assert result is None


async def test_cached_calls():
    session = get_mock_session_many_csv()
    client = IrcelineForecastClient(session)

    _ = await client.get_data(
        timestamp=date(2024, 6, 19),
        features=[ForecastFeature.NO2_MAXHMEAN],
        position=(50.45, 4.85)
    )

    calls = [
        call(method='GET',
             url=f"{_forecast_base_url}/BE_{ForecastFeature.NO2_MAXHMEAN}_20240619_d{i}.csv",
             params=None,
             headers={'User-Agent': _user_agent}
             ) for i in range(5)
    ]

    assert session.request.call_count == 5
    session.request.assert_has_calls(calls)

    _ = await client.get_data(
        timestamp=date(2024, 6, 19),
        features=[ForecastFeature.NO2_MAXHMEAN],
        position=(50.45, 4.85)
    )

    calls += [
        call(method='GET',
             url=f"{_forecast_base_url}/BE_{ForecastFeature.NO2_MAXHMEAN}_20240619_d{i}.csv",
             params=None,
             headers={'User-Agent': _user_agent, 'If-None-Match': 'my-etag-here'}
             ) for i in range(5)
    ]

    assert session.request.call_count == 10
    session.request.assert_has_calls(calls)


async def test_missed_cached_calls():
    session = get_mock_session_many_csv()
    client = IrcelineForecastClient(session)

    r = await client.get_data(
        timestamp=date(2024, 6, 21),
        features=[ForecastFeature.NO2_MAXHMEAN],
        position=(50.45, 4.85)
    )

    calls = list()

    for i in range(5):
        calls += [
            call(method='GET',
                 url=f"{_forecast_base_url}/BE_{ForecastFeature.NO2_MAXHMEAN}_20240621_d{i}.csv",
                 params=None,
                 headers={'User-Agent': _user_agent}
                 ),
            call(method='GET',
                 url=f"{_forecast_base_url}/BE_{ForecastFeature.NO2_MAXHMEAN}_20240620_d{i}.csv",
                 params=None,
                 headers={'User-Agent': _user_agent}
                 )
        ]

    assert session.request.call_count == 10
    session.request.assert_has_calls(calls)

    for value in r.values():
        assert value['value'] is None
