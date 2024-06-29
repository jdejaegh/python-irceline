from datetime import date, timedelta, datetime

import pytest
from freezegun import freeze_time

from src.open_irceline.api import IrcelineForecastClient, IrcelineRioClient
from src.open_irceline.belaqi import belaqi_index_forecast_daily, belaqi_index_rio_hourly, belaqi_index_hourly, \
    belaqi_index_daily
from src.open_irceline.data import BelAqiIndex
from tests.conftest import get_mock_session_many_csv, get_mock_session


@pytest.mark.parametrize("pm10, pm25, o3, no2, expected", [
    (5, 2, 25, 5, BelAqiIndex.EXCELLENT),
    (15, 5, 50, 12, BelAqiIndex.VERY_GOOD),
    (30, 9, 70, 18, BelAqiIndex.GOOD),
    (40, 13, 80, 25, BelAqiIndex.FAIRLY_GOOD),
    (55, 18, 100, 35, BelAqiIndex.MODERATE),
    (70, 25, 130, 43, BelAqiIndex.POOR),
    (90, 45, 160, 48, BelAqiIndex.VERY_POOR),
    (100, 55, 200, 55, BelAqiIndex.BAD),
    (130, 70, 230, 70, BelAqiIndex.VERY_BAD),
    (150, 80, 250, 80, BelAqiIndex.HORRIBLE),
    (150, 80, 300, 80, BelAqiIndex.HORRIBLE),
    (95, 5, 25, 5, BelAqiIndex.VERY_POOR),
    (145, 5, 25, 5, BelAqiIndex.HORRIBLE),
    (5, 55, 25, 5, BelAqiIndex.BAD),
    (5, 85, 25, 5, BelAqiIndex.HORRIBLE),
    (5, 5, 190, 5, BelAqiIndex.BAD),
    (5, 5, 260, 5, BelAqiIndex.HORRIBLE),
    (5, 5, 25, 65, BelAqiIndex.VERY_BAD),
    (5, 5, 25, 85, BelAqiIndex.HORRIBLE),
    (45, 15, 150, 10, BelAqiIndex.POOR),
    (20, 25, 180, 15, BelAqiIndex.VERY_POOR),
    (10, 7, 250, 70, BelAqiIndex.HORRIBLE),
    (110, 3, 30, 25, BelAqiIndex.BAD),
    (5, 0, 0, 0, BelAqiIndex.EXCELLENT),
    (15, 0, 0, 0, BelAqiIndex.VERY_GOOD),
    (30, 0, 0, 0, BelAqiIndex.GOOD),
    (40, 0, 0, 0, BelAqiIndex.FAIRLY_GOOD),
    (55, 0, 0, 0, BelAqiIndex.MODERATE),
    (70, 0, 0, 0, BelAqiIndex.POOR),
    (90, 0, 0, 0, BelAqiIndex.VERY_POOR),
    (100, 0, 0, 0, BelAqiIndex.BAD),
    (130, 0, 0, 0, BelAqiIndex.VERY_BAD),
    (150, 0, 0, 0, BelAqiIndex.HORRIBLE),
    (0, 2, 0, 0, BelAqiIndex.EXCELLENT),
    (0, 5, 0, 0, BelAqiIndex.VERY_GOOD),
    (0, 9, 0, 0, BelAqiIndex.GOOD),
    (0, 13, 0, 0, BelAqiIndex.FAIRLY_GOOD),
    (0, 18, 0, 0, BelAqiIndex.MODERATE),
    (0, 25, 0, 0, BelAqiIndex.POOR),
    (0, 45, 0, 0, BelAqiIndex.VERY_POOR),
    (0, 55, 0, 0, BelAqiIndex.BAD),
    (0, 70, 0, 0, BelAqiIndex.VERY_BAD),
    (0, 80, 0, 0, BelAqiIndex.HORRIBLE),
    (0, 0, 25, 0, BelAqiIndex.EXCELLENT),
    (0, 0, 50, 0, BelAqiIndex.VERY_GOOD),
    (0, 0, 70, 0, BelAqiIndex.GOOD),
    (0, 0, 80, 0, BelAqiIndex.FAIRLY_GOOD),
    (0, 0, 100, 0, BelAqiIndex.MODERATE),
    (0, 0, 130, 0, BelAqiIndex.POOR),
    (0, 0, 160, 0, BelAqiIndex.VERY_POOR),
    (0, 0, 200, 0, BelAqiIndex.BAD),
    (0, 0, 230, 0, BelAqiIndex.VERY_BAD),
    (0, 0, 250, 0, BelAqiIndex.HORRIBLE),
    (0, 0, 0, 5, BelAqiIndex.EXCELLENT),
    (0, 0, 0, 12, BelAqiIndex.VERY_GOOD),
    (0, 0, 0, 18, BelAqiIndex.GOOD),
    (0, 0, 0, 25, BelAqiIndex.FAIRLY_GOOD),
    (0, 0, 0, 35, BelAqiIndex.MODERATE),
    (0, 0, 0, 43, BelAqiIndex.POOR),
    (0, 0, 0, 48, BelAqiIndex.VERY_POOR),
    (0, 0, 0, 55, BelAqiIndex.BAD),
    (0, 0, 0, 70, BelAqiIndex.VERY_BAD),
    (0, 0, 0, 80, BelAqiIndex.HORRIBLE)
])
def test_belaqi_index_hourly(pm10, pm25, o3, no2, expected):
    assert belaqi_index_hourly(pm10, pm25, o3, no2) == expected


@pytest.mark.parametrize("pm10, pm25, o3, no2, expected_index", [
    (5, 0, 0, 0, BelAqiIndex.EXCELLENT),
    (15, 0, 0, 0, BelAqiIndex.VERY_GOOD),
    (25, 0, 0, 0, BelAqiIndex.GOOD),
    (35, 0, 0, 0, BelAqiIndex.FAIRLY_GOOD),
    (45, 0, 0, 0, BelAqiIndex.MODERATE),
    (60, 0, 0, 0, BelAqiIndex.POOR),
    (70, 0, 0, 0, BelAqiIndex.VERY_POOR),
    (80, 0, 0, 0, BelAqiIndex.BAD),
    (100, 0, 0, 0, BelAqiIndex.VERY_BAD),
    (101, 0, 0, 0, BelAqiIndex.HORRIBLE),
    (0, 2.5, 0, 0, BelAqiIndex.EXCELLENT),
    (0, 5, 0, 0, BelAqiIndex.VERY_GOOD),
    (0, 7.5, 0, 0, BelAqiIndex.GOOD),
    (0, 10, 0, 0, BelAqiIndex.FAIRLY_GOOD),
    (0, 15, 0, 0, BelAqiIndex.MODERATE),
    (0, 25, 0, 0, BelAqiIndex.POOR),
    (0, 35, 0, 0, BelAqiIndex.VERY_POOR),
    (0, 40, 0, 0, BelAqiIndex.BAD),
    (0, 50, 0, 0, BelAqiIndex.VERY_BAD),
    (0, 51, 0, 0, BelAqiIndex.HORRIBLE),
    (0, 0, 30, 0, BelAqiIndex.EXCELLENT),
    (0, 0, 60, 0, BelAqiIndex.VERY_GOOD),
    (0, 0, 70, 0, BelAqiIndex.GOOD),
    (0, 0, 80, 0, BelAqiIndex.FAIRLY_GOOD),
    (0, 0, 100, 0, BelAqiIndex.MODERATE),
    (0, 0, 130, 0, BelAqiIndex.POOR),
    (0, 0, 160, 0, BelAqiIndex.VERY_POOR),
    (0, 0, 190, 0, BelAqiIndex.BAD),
    (0, 0, 220, 0, BelAqiIndex.VERY_BAD),
    (0, 0, 221, 0, BelAqiIndex.HORRIBLE),
    (0, 0, 0, 5, BelAqiIndex.EXCELLENT),
    (0, 0, 0, 10, BelAqiIndex.VERY_GOOD),
    (0, 0, 0, 15, BelAqiIndex.GOOD),
    (0, 0, 0, 20, BelAqiIndex.FAIRLY_GOOD),
    (0, 0, 0, 25, BelAqiIndex.MODERATE),
    (0, 0, 0, 30, BelAqiIndex.POOR),
    (0, 0, 0, 35, BelAqiIndex.VERY_POOR),
    (0, 0, 0, 40, BelAqiIndex.BAD),
    (0, 0, 0, 50, BelAqiIndex.VERY_BAD),
    (0, 0, 0, 51, BelAqiIndex.HORRIBLE),
    (3, 1, 20, 4, BelAqiIndex.EXCELLENT),
    (10, 3, 50, 8, BelAqiIndex.VERY_GOOD),
    (20, 6, 65, 12, BelAqiIndex.GOOD),
    (30, 8, 75, 18, BelAqiIndex.FAIRLY_GOOD),
    (40, 12, 90, 22, BelAqiIndex.MODERATE),
    (50, 20, 110, 28, BelAqiIndex.POOR),
    (65, 30, 140, 33, BelAqiIndex.VERY_POOR),
    (75, 38, 180, 38, BelAqiIndex.BAD),
    (90, 45, 200, 45, BelAqiIndex.VERY_BAD),
    (110, 55, 230, 55, BelAqiIndex.HORRIBLE),
    (3, 30, 20, 8, BelAqiIndex.VERY_POOR),
    (110, 6, 65, 12, BelAqiIndex.HORRIBLE),
    (3, 6, 230, 12, BelAqiIndex.HORRIBLE),
    (3, 6, 65, 55, BelAqiIndex.HORRIBLE),
    (50, 5, 65, 12, BelAqiIndex.POOR),
    (10, 20, 65, 12, BelAqiIndex.POOR),
    (10, 5, 110, 12, BelAqiIndex.POOR),
    (10, 5, 65, 28, BelAqiIndex.POOR),
    (75, 5, 30, 8, BelAqiIndex.BAD),
    (10, 38, 30, 8, BelAqiIndex.BAD),
    (10, 5, 180, 8, BelAqiIndex.BAD),
    (10, 5, 30, 38, BelAqiIndex.BAD),
    (65, 3, 20, 22, BelAqiIndex.VERY_POOR),
    (3, 30, 20, 22, BelAqiIndex.VERY_POOR),
    (3, 3, 140, 22, BelAqiIndex.VERY_POOR),
    (3, 3, 20, 33, BelAqiIndex.VERY_POOR),
    (90, 6, 20, 22, BelAqiIndex.VERY_BAD),
    (10, 45, 20, 22, BelAqiIndex.VERY_BAD),
    (10, 6, 200, 22, BelAqiIndex.VERY_BAD),
    (10, 6, 20, 45, BelAqiIndex.VERY_BAD),
    (3, 30, 20, 4, BelAqiIndex.VERY_POOR),
    (110, 1, 20, 4, BelAqiIndex.HORRIBLE),
    (3, 1, 230, 4, BelAqiIndex.HORRIBLE),
    (3, 1, 20, 55, BelAqiIndex.HORRIBLE),
    (50, 3, 20, 4, BelAqiIndex.POOR),
    (3, 20, 20, 4, BelAqiIndex.POOR),
    (3, 1, 110, 4, BelAqiIndex.POOR),
    (3, 1, 20, 28, BelAqiIndex.POOR),
])
def test_belaqi_index_daily(pm10, pm25, o3, no2, expected_index):
    assert belaqi_index_daily(pm10, pm25, o3, no2) == expected_index


def test_belaqi_hourly_value_error():
    with pytest.raises(ValueError):
        belaqi_index_hourly(-1, 0, 12, 8)

    with pytest.raises(ValueError):
        belaqi_index_hourly(1, -20, 12, 8)

    with pytest.raises(ValueError):
        belaqi_index_hourly(1, 0, -12, 8)

    with pytest.raises(ValueError):
        belaqi_index_hourly(1, 0, 12, -8888)


def test_belaqi_daily_value_error():
    with pytest.raises(ValueError):
        belaqi_index_daily(-1, 0, 12, 8)

    with pytest.raises(ValueError):
        belaqi_index_daily(1, -20, 12, 8)

    with pytest.raises(ValueError):
        belaqi_index_daily(1, 0, -12, 8)

    with pytest.raises(ValueError):
        belaqi_index_daily(1, 0, 12, -8888)


def test_belaqi_hourly_value_error_none():
    with pytest.raises(ValueError):
        belaqi_index_hourly(None, 0, 12, 8)

    with pytest.raises(ValueError):
        belaqi_index_hourly(1, None, 12, 8)

    with pytest.raises(ValueError):
        belaqi_index_hourly(1, 0, None, 8)

    with pytest.raises(ValueError):
        belaqi_index_hourly(1, 0, 12, None)


def test_belaqi_daily_value_error_none():
    with pytest.raises(ValueError):
        belaqi_index_daily(None, 0, 12, 8)

    with pytest.raises(ValueError):
        belaqi_index_daily(1, None, 12, 8)

    with pytest.raises(ValueError):
        belaqi_index_daily(1, 0, None, 8)

    with pytest.raises(ValueError):
        belaqi_index_daily(1, 0, 12, None)


@freeze_time(datetime.fromisoformat("2024-06-19T19:30:09.581Z"))
async def test_belaqi_index_forecast():
    session = get_mock_session_many_csv()
    client = IrcelineForecastClient(session)
    pos = (50.55, 4.85)

    result = await belaqi_index_forecast_daily(client, pos)

    expected_days = {date(2024, 6, 19) + timedelta(days=i) for i in range(5)}

    assert set(result.keys()) == expected_days
    for v in result.values():
        assert v.get('value') == BelAqiIndex.MODERATE


async def test_belaqi_index_forecast_missing_day():
    session = get_mock_session_many_csv()
    client = IrcelineForecastClient(session)
    pos = (50.55, 4.85)

    result = await belaqi_index_forecast_daily(client, pos, date(2024, 6, 21))

    expected_days = {date(2024, 6, 21) + timedelta(days=i) for i in range(5)}
    assert set(result.keys()) == expected_days
    for v in result.values():
        assert v.get('value') is None


@freeze_time(datetime.fromisoformat("2024-06-23T12:30:09.581Z"))
async def test_belaqi_index_actual():
    session = get_mock_session(json_file='rio_wfs_for_belaqi.json')
    client = IrcelineRioClient(session)
    pos = (50.55, 4.85)

    result = await belaqi_index_rio_hourly(client, pos)
    assert result.get('value') == BelAqiIndex.GOOD


@freeze_time(datetime.fromisoformat("2024-06-23T12:30:09.581Z"))
async def test_belaqi_index_actual_missing_value():
    session = get_mock_session(json_file='rio_wfs.json')
    client = IrcelineRioClient(session)
    pos = (50.55, 4.85)

    with pytest.raises(ValueError):
        _ = await belaqi_index_rio_hourly(client, pos)
