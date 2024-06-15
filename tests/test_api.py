from datetime import datetime, date

from aiohttp import ClientSession
from freezegun import freeze_time

from src.open_irceline.api import IrcelineClient
from src.open_irceline.data import RioFeature, FeatureValue
from tests.conftest import get_api_data


@freeze_time(datetime.fromisoformat("2024-06-15T16:55:03.419Z"))
async def test_format_result_hmean():
    data = get_api_data('rio_wfs.json')
    result = IrcelineClient.format_result('rio', data, [RioFeature.NO2_HMEAN, RioFeature.O3_HMEAN])

    expected = {
        str(RioFeature.O3_HMEAN): FeatureValue(
            timestamp=datetime.fromisoformat("2024-06-15T16:00:00Z"),
            value=71
        ),
        str(RioFeature.NO2_HMEAN): FeatureValue(
            timestamp=datetime.fromisoformat("2024-06-15T16:00:00Z"),
            value=4
        )
    }

    assert result == expected


@freeze_time(datetime.fromisoformat("2024-06-15T19:30:09.581Z"))

async def test_format_result_dmean():
    data = get_api_data('rio_wfs_dmean.json')
    result = IrcelineClient.format_result('rio', data,
                                          [RioFeature.BC_DMEAN, RioFeature.PM10_DMEAN, RioFeature.PM25_DMEAN])

    expected = {
        str(RioFeature.BC_DMEAN): FeatureValue(timestamp=date(2024, 6, 15), value=0.1),
        str(RioFeature.PM10_DMEAN): FeatureValue(timestamp=date(2024, 6, 15), value=5.9),
        str(RioFeature.PM25_DMEAN): FeatureValue(timestamp=date(2024, 6, 15), value=1.1),
    }

    assert result == expected

async def test_run():
    async with ClientSession() as session:
        api = IrcelineClient(session)
        r = await api.get_rio_value(
            date.today(),
            [RioFeature.BC_DMEAN, RioFeature.PM10_DMEAN, RioFeature.PM25_DMEAN],
            (4.8637, 50.4656))
        print(r)
