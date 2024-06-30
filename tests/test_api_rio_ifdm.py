from datetime import datetime
from unittest.mock import call

from freezegun import freeze_time

from src.open_irceline.api import _rio_ifdm_wms_base_url, _user_agent
from src.open_irceline.data import RioIfdmFeature, FeatureValue
from src.open_irceline.rio import IrcelineRioIfdmClient
from tests.conftest import get_api_data, get_mock_session


def test_parse_capabilities():
    data = get_api_data('rio_ifdm_capabilities.xml', plain=True)
    result = IrcelineRioIfdmClient._parse_capabilities(data)

    expected = {'no2_dm3', 'belaqi_dm2', 'pm10_hmean', 'belaqi_dm1', 'pm25_dm3', 'pm25_dm2', 'pm10_dm1', 'o3_dm3',
                'no2_dm1', 'pm10_dm3', 'pm25_dm1', 'belaqi', 'belaqi_dm3', 'pm10_dm2', 'o3_dm2', 'pm25_hmean', 'o3_dm1',
                'o3_hmean', 'no2_dm2', 'no2_hmean'}

    assert result == expected

    for f in RioIfdmFeature:
        assert f"{f.split(':')[1]}" in result


async def test_aget_capabilities():
    session = get_mock_session(text_file='rio_ifdm_capabilities.xml')

    client = IrcelineRioIfdmClient(session)
    _ = await client.get_capabilities()

    session.request.assert_called_once_with(
        method='GET',
        url=_rio_ifdm_wms_base_url,
        params={"service": "WMS",
                "version": "1.1.1",
                "request": "GetCapabilities"},
        headers={'User-Agent': _user_agent}
    )


@freeze_time(datetime.fromisoformat("2024-06-30T13:00:21.520Z"))
async def test_api_forecast_error():
    pos = (50.4657, 4.8647)
    session = get_mock_session('forecast_wms_feature_info_invalid.json')

    client = IrcelineRioIfdmClient(session)

    features = [RioIfdmFeature.NO2_HMEAN, RioIfdmFeature.O3_HMEAN]
    result = await client.get_data(features, pos)

    for k, v in result.items():
        assert v == FeatureValue(timestamp=datetime.fromisoformat("2024-06-30T13:00:21.520Z"), value=None)


async def test_api_forecast():
    pos = (50.4657, 4.8647)
    lat, lon = pos
    session = get_mock_session('forecast_wms_feature_info.json')

    client = IrcelineRioIfdmClient(session)

    features = [RioIfdmFeature.NO2_HMEAN, RioIfdmFeature.O3_HMEAN]
    result = await client.get_data(features, pos)

    base = {"service": "WMS",
            "version": "1.1.1",
            "request": "GetFeatureInfo",
            "info_format": "application/json",
            "width": "1",
            "height": "1",
            "srs": "EPSG:4326",
            "bbox": f"{lon},{lat},{lon + 0.00001},{lat + 0.00001}",
            "X": "1",
            "Y": "1"}

    calls = [call(
        method='GET',
        url=_rio_ifdm_wms_base_url,
        params=base | {"layers": f"{feature}",
                       "query_layers": f"{feature}"},
        headers={'User-Agent': _user_agent},
    )
        for feature in features]

    session.request.assert_has_calls(calls, any_order=True)

    for k, v in result.items():
        assert v['value'] == 10.853286743164062


async def test_api_forecast_no_field():
    pos = (50.4657, 4.8647)
    session = get_mock_session('forecast_wms_feature_info_no_field.json')

    client = IrcelineRioIfdmClient(session)

    features = [RioIfdmFeature.NO2_HMEAN, RioIfdmFeature.O3_HMEAN]
    result = await client.get_data(features, pos)

    for k, v in result.items():
        assert v == FeatureValue(timestamp=None, value=None)
