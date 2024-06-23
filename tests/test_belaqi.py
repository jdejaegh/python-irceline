from datetime import date, timedelta, datetime
from random import randint, seed

import pytest
from freezegun import freeze_time

from src.open_irceline.api import IrcelineForecastClient, IrcelineRioClient
from src.open_irceline.belaqi import belaqi_index, belaqi_index_forecast, belaqi_index_actual
from src.open_irceline.data import BelAqiIndex
from tests.conftest import get_mock_session_many_csv, get_mock_session


def test_belaqi_index():
    # Excellent
    assert belaqi_index(5, 2, 10, 10) == BelAqiIndex.EXCELLENT
    assert belaqi_index(0, 0, 0, 0) == BelAqiIndex.EXCELLENT
    assert belaqi_index(10, 5, 25, 20) == BelAqiIndex.EXCELLENT

    # Very good
    assert belaqi_index(15, 8, 40, 35) == BelAqiIndex.VERY_GOOD
    assert belaqi_index(11, 6, 26, 21) == BelAqiIndex.VERY_GOOD
    assert belaqi_index(20, 10, 50, 50) == BelAqiIndex.VERY_GOOD

    # Good
    assert belaqi_index(25, 12, 60, 60) == BelAqiIndex.GOOD
    assert belaqi_index(21, 11, 51, 51) == BelAqiIndex.GOOD
    assert belaqi_index(30, 15, 70, 70) == BelAqiIndex.GOOD

    # Fairly good
    assert belaqi_index(35, 20, 100, 90) == BelAqiIndex.FAIRLY_GOOD
    assert belaqi_index(31, 16, 71, 71) == BelAqiIndex.FAIRLY_GOOD
    assert belaqi_index(40, 25, 120, 120) == BelAqiIndex.FAIRLY_GOOD

    # Moderate
    assert belaqi_index(45, 30, 140, 130) == BelAqiIndex.MODERATE
    assert belaqi_index(41, 26, 121, 121) == BelAqiIndex.MODERATE
    assert belaqi_index(50, 35, 160, 150) == BelAqiIndex.MODERATE

    # Poor
    assert belaqi_index(55, 38, 170, 160) == BelAqiIndex.POOR
    assert belaqi_index(51, 36, 161, 151) == BelAqiIndex.POOR
    assert belaqi_index(60, 40, 180, 180) == BelAqiIndex.POOR

    # Very poor
    assert belaqi_index(65, 45, 200, 190) == BelAqiIndex.VERY_POOR
    assert belaqi_index(61, 41, 181, 181) == BelAqiIndex.VERY_POOR
    assert belaqi_index(70, 50, 240, 200) == BelAqiIndex.VERY_POOR

    # Bad
    assert belaqi_index(75, 55, 260, 220) == BelAqiIndex.BAD
    assert belaqi_index(71, 51, 241, 201) == BelAqiIndex.BAD
    assert belaqi_index(80, 60, 280, 250) == BelAqiIndex.BAD

    # Very bad
    assert belaqi_index(85, 65, 300, 270) == BelAqiIndex.VERY_BAD
    assert belaqi_index(81, 61, 281, 251) == BelAqiIndex.VERY_BAD
    assert belaqi_index(100, 70, 320, 300) == BelAqiIndex.VERY_BAD

    # Horrible
    assert belaqi_index(110, 75, 330, 310) == BelAqiIndex.HORRIBLE
    assert belaqi_index(101, 71, 321, 301) == BelAqiIndex.HORRIBLE
    assert belaqi_index(150, 100, 400, 400) == BelAqiIndex.HORRIBLE


def test_belaqi_single_component():
    # Tests with only PM10 varying
    assert belaqi_index(5, 0, 0, 0) == BelAqiIndex.EXCELLENT
    assert belaqi_index(15, 0, 0, 0) == BelAqiIndex.VERY_GOOD
    assert belaqi_index(25, 0, 0, 0) == BelAqiIndex.GOOD
    assert belaqi_index(35, 0, 0, 0) == BelAqiIndex.FAIRLY_GOOD
    assert belaqi_index(45, 0, 0, 0) == BelAqiIndex.MODERATE
    assert belaqi_index(55, 0, 0, 0) == BelAqiIndex.POOR
    assert belaqi_index(65, 0, 0, 0) == BelAqiIndex.VERY_POOR
    assert belaqi_index(75, 0, 0, 0) == BelAqiIndex.BAD
    assert belaqi_index(85, 0, 0, 0) == BelAqiIndex.VERY_BAD
    assert belaqi_index(110, 0, 0, 0) == BelAqiIndex.HORRIBLE

    # Tests with only PM2.5 varying
    assert belaqi_index(0, 2, 0, 0) == BelAqiIndex.EXCELLENT
    assert belaqi_index(0, 8, 0, 0) == BelAqiIndex.VERY_GOOD
    assert belaqi_index(0, 12, 0, 0) == BelAqiIndex.GOOD
    assert belaqi_index(0, 20, 0, 0) == BelAqiIndex.FAIRLY_GOOD
    assert belaqi_index(0, 30, 0, 0) == BelAqiIndex.MODERATE
    assert belaqi_index(0, 38, 0, 0) == BelAqiIndex.POOR
    assert belaqi_index(0, 45, 0, 0) == BelAqiIndex.VERY_POOR
    assert belaqi_index(0, 55, 0, 0) == BelAqiIndex.BAD
    assert belaqi_index(0, 65, 0, 0) == BelAqiIndex.VERY_BAD
    assert belaqi_index(0, 75, 0, 0) == BelAqiIndex.HORRIBLE

    # Tests with only O3 varying
    assert belaqi_index(0, 0, 10, 0) == BelAqiIndex.EXCELLENT
    assert belaqi_index(0, 0, 40, 0) == BelAqiIndex.VERY_GOOD
    assert belaqi_index(0, 0, 60, 0) == BelAqiIndex.GOOD
    assert belaqi_index(0, 0, 100, 0) == BelAqiIndex.FAIRLY_GOOD
    assert belaqi_index(0, 0, 140, 0) == BelAqiIndex.MODERATE
    assert belaqi_index(0, 0, 170, 0) == BelAqiIndex.POOR
    assert belaqi_index(0, 0, 200, 0) == BelAqiIndex.VERY_POOR
    assert belaqi_index(0, 0, 260, 0) == BelAqiIndex.BAD
    assert belaqi_index(0, 0, 300, 0) == BelAqiIndex.VERY_BAD
    assert belaqi_index(0, 0, 330, 0) == BelAqiIndex.HORRIBLE

    # Tests with only NO2 varying
    assert belaqi_index(0, 0, 0, 10) == BelAqiIndex.EXCELLENT
    assert belaqi_index(0, 0, 0, 35) == BelAqiIndex.VERY_GOOD
    assert belaqi_index(0, 0, 0, 60) == BelAqiIndex.GOOD
    assert belaqi_index(0, 0, 0, 90) == BelAqiIndex.FAIRLY_GOOD
    assert belaqi_index(0, 0, 0, 130) == BelAqiIndex.MODERATE
    assert belaqi_index(0, 0, 0, 160) == BelAqiIndex.POOR
    assert belaqi_index(0, 0, 0, 190) == BelAqiIndex.VERY_POOR
    assert belaqi_index(0, 0, 0, 220) == BelAqiIndex.BAD
    assert belaqi_index(0, 0, 0, 270) == BelAqiIndex.VERY_BAD
    assert belaqi_index(0, 0, 0, 310) == BelAqiIndex.HORRIBLE


def test_belaqi_random():
    seed(42)
    # Generate random test values and their expected indices
    test_cases = [
        (randint(0, 10), randint(0, 5), randint(0, 25), randint(0, 20), BelAqiIndex.EXCELLENT),
        (randint(11, 20), randint(6, 10), randint(26, 50), randint(21, 50), BelAqiIndex.VERY_GOOD),
        (randint(21, 30), randint(11, 15), randint(51, 70), randint(51, 70), BelAqiIndex.GOOD),
        (randint(31, 40), randint(16, 25), randint(71, 120), randint(71, 120), BelAqiIndex.FAIRLY_GOOD),
        (randint(41, 50), randint(26, 35), randint(121, 160), randint(121, 150), BelAqiIndex.MODERATE),
        (randint(51, 60), randint(36, 40), randint(161, 180), randint(151, 180), BelAqiIndex.POOR),
        (randint(61, 70), randint(41, 50), randint(181, 240), randint(181, 200), BelAqiIndex.VERY_POOR),
        (randint(71, 80), randint(51, 60), randint(241, 280), randint(201, 250), BelAqiIndex.BAD),
        (randint(81, 100), randint(61, 70), randint(281, 320), randint(251, 300), BelAqiIndex.VERY_BAD),
        (randint(101, 150), randint(71, 100), randint(321, 400), randint(301, 400), BelAqiIndex.HORRIBLE)
    ]

    # Test each case
    for pm10, pm25, o3, no2, expected in test_cases:
        assert belaqi_index(pm10, pm25, o3, no2) == expected


def test_belaqi_value_error():
    with pytest.raises(ValueError):
        belaqi_index(-1, 0, 12, 8)

    with pytest.raises(ValueError):
        belaqi_index(1, -20, 12, 8)

    with pytest.raises(ValueError):
        belaqi_index(1, 0, -12, 8)

    with pytest.raises(ValueError):
        belaqi_index(1, 0, 12, -8888)


@freeze_time(datetime.fromisoformat("2024-06-19T19:30:09.581Z"))
async def test_belaqi_index_forecast():
    session = get_mock_session_many_csv()
    client = IrcelineForecastClient(session)
    pos = (50.55, 4.85)

    result = await belaqi_index_forecast(client, pos)

    expected_days = {date(2024, 6, 19) + timedelta(days=i) for i in range(5)}

    assert set(result.keys()) == expected_days
    for v in result.values():
        assert v == BelAqiIndex.GOOD


async def test_belaqi_index_forecast_missing_day():
    session = get_mock_session_many_csv()
    client = IrcelineForecastClient(session)
    pos = (50.55, 4.85)

    result = await belaqi_index_forecast(client, pos, date(2024, 6, 21))

    expected_days = {date(2024, 6, 21) + timedelta(days=i) for i in range(5)}
    assert set(result.keys()) == expected_days
    for v in result.values():
        assert v is None


@freeze_time(datetime.fromisoformat("2024-06-23T12:30:09.581Z"))
async def test_belaqi_index_actual():
    session = get_mock_session(json_file='rio_wfs_for_belaqi.json')
    client = IrcelineRioClient(session)
    pos = (50.55, 4.85)

    result = await belaqi_index_actual(client, pos)
    print(result)
    assert result == BelAqiIndex.FAIRLY_GOOD


@freeze_time(datetime.fromisoformat("2024-06-23T12:30:09.581Z"))
async def test_belaqi_index_actual_missing_value():
    session = get_mock_session(json_file='rio_wfs.json')
    client = IrcelineRioClient(session)
    pos = (50.55, 4.85)

    with pytest.raises(ValueError):
        _ = await belaqi_index_actual(client, pos)
