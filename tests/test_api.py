from src.open_irceline.api import IrcelineClient
from src.open_irceline.data import RioFeature, FeatureValue
from tests.conftest import get_api_data
from datetime import datetime
from freezegun import freeze_time


@freeze_time(datetime.fromisoformat("2024-06-15T16:55:03.419Z"))
async def test_format_result():
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
