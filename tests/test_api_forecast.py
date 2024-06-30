from datetime import datetime
from itertools import product
from unittest.mock import call

from freezegun import freeze_time

from src.open_irceline import IrcelineForecastClient, ForecastFeature, FeatureValue
from src.open_irceline.api import _user_agent, _forecast_wms_base_url
from tests.conftest import get_api_data, get_mock_session


def test_parse_capabilities():
    data = get_api_data('forecast_wms_capabilities.xml', plain=True)
    result = IrcelineForecastClient._parse_capabilities(data)

    expected = {'o3_maxhmean_wl_d3', 'pm25_dmean_wl_d0', 'o3_max8hmean_chimv2022_d2', 'no2_maxhmean_tf_d2',
                'belaqi_forecast_chimv2022_d2', 'pm25_dmean_chimv2022_d3', 'pm10_dmean_chimv2022_d0',
                'no2_maxhmean_wl_d0', 'no2_maxhmean_d2', 'no2_dmean_chimv2022_d2', 'o3_maxhmean_chimv2022_d3',
                'pm25_dmean_wl_d3', 'o3_maxhmean_chimv2022_d0', 'pm25_dmean', 'pm25_dmean_tf_d0', 'no2_dmean_wl_d2',
                'o3_max8hmean_chimv2022_d3', 'pm25_dmean_d2', 'o3_max8hmean_chimv2022_d0', 'o3_maxhmean_wl_d2',
                'no2_maxhmean_wl_d1', 'pm10_dmean_tf_d2', 'pm25_dmean_d1', 'o3_maxhmean_chimv2022_d2',
                'pm10_dmean_chimv2022_d2', 'o3_maxhmean_vl', 'belaqi_wl_d2', 'pm10_dmean_wl', 'pm10_dmean_d2',
                'no2_dmean_wl_d0', 'no2_dmean_d1', 'o3_maxhmean_d2', 'o3_maxhmean_wl', 'pm25_dmean_wl_d2',
                'o3_maxhmean_d3', 'o3_max8hmean_wl_d3', 'belaqi_d0', 'no2_maxhmean_wl_d2', 'no2_maxhmean_wl',
                'pm10_dmean_wl_d1', 'no2_dmean_chimv2022_d3', 'o3_maxhmean_tf_d1', 'pm25_dmean_vl', 'pm10_dmean_d0',
                'o3_max8hmean_d0', 'o3_max8hmean_d2', 'no2_maxhmean_vl', 'o3_max8hmean_chimv2022_d1', 'pm10_dmean',
                'pm10_dmean_wl_d2', 'euaqi_d3', 'belaqi_d1', 'o3_max8hmean_d1', 'o3_maxhmean_chimv2022_d1', 'belaqi_vl',
                'belaqi_wl_d0', 'no2_dmean_chimv2022_d0', 'pm25_dmean_wl_d1', 'pm25_dmean_tf_d2', 'no2_dmean_d2',
                'o3_maxhmean', 'belaqi_wl', 'no2_maxhmean_d0', 'no2_maxhmean_d3', 'o3_max8hmean_d3', 'euaqi_forecast',
                'o3_max8hmean_wl_d1', 'pm10_dmean_chimv2022_d3', 'no2_maxhmean_wl_d3', 'o3_maxhmean_d1',
                'no2_dmean_wl_d1', 'o3_maxhmean_wl_d1', 'no2_dmean_d3', 'belaqi_d3', 'belaqi', 'pm25_dmean_d3',
                'belaqi_forecast', 'no2_dmean_d0', 'pm25_dmean_chimv2022_d1', 'belaqi_wl_d1', 'pm10_dmean_d3',
                'no2_dmean_wl_d3', 'pm25_dmean_tf_d1', 'euaqi_d0', 'o3_maxhmean_wl_d0', 'belaqi_forecast_chimv2022_d3',
                'no2_dmean_chimv2022_d1', 'o3_max8hmean_wl_d0', 'o3_max8hmean_wl_d2', 'pm10_dmean_chimv2022_d1',
                'pm10_dmean_wl_d3', 'pm25_dmean_wl', 'belaqi_forecast_chimv2022_d1', 'euaqi_d2', 'pm10_dmean_d1',
                'belaqi_wl_d3', 'belaqi_forecast_chimv2022_d0', 'o3_maxhmean_tf_d0', 'euaqi_d1', 'no2_maxhmean',
                'pm25_dmean_chimv2022_d2', 'belaqi_d2', 'pm25_dmean_d0', 'no2_maxhmean_tf_d0', 'pm10_dmean_tf_d0',
                'pm25_dmean_chimv2022_d0', 'o3_maxhmean_d0', 'pm10_dmean_tf_d1', 'pm10_dmean_vl', 'no2_maxhmean_tf_d1',
                'o3_maxhmean_tf_d2', 'pm10_dmean_wl_d0', 'no2_maxhmean_d1'}

    assert result == expected

    for f, d in product(ForecastFeature, range(4)):
        assert f"{f.split(':')[1]}_d{d}" in result


async def test_aget_capabilities():
    session = get_mock_session(text_file='forecast_wms_capabilities.xml')

    client = IrcelineForecastClient(session)
    _ = await client.get_capabilities()

    session.request.assert_called_once_with(
        method='GET',
        url=_forecast_wms_base_url,
        params={"service": "WMS",
                "version": "1.1.1",
                "request": "GetCapabilities"},
        headers={'User-Agent': _user_agent}
    )


@freeze_time(datetime.fromisoformat("2024-06-30T13:00:21.520Z"))
async def test_api_forecast_error():
    pos = (50.4657, 4.8647)
    session = get_mock_session('forecast_wms_feature_info_invalid.json')

    client = IrcelineForecastClient(session)

    features = [ForecastFeature.NO2_DMEAN, ForecastFeature.O3_MAXHMEAN]
    result = await client.get_data(features, pos)

    for k, v in result.items():
        assert v == FeatureValue(timestamp=datetime.fromisoformat("2024-06-30T13:00:21.520Z"), value=None)


async def test_api_forecast_no_field():
    pos = (50.4657, 4.8647)
    session = get_mock_session('forecast_wms_feature_info_no_field.json')

    client = IrcelineForecastClient(session)

    features = [ForecastFeature.NO2_DMEAN, ForecastFeature.O3_MAXHMEAN]
    result = await client.get_data(features, pos)

    for k, v in result.items():
        assert v == FeatureValue(timestamp=None, value=None)


async def test_api_forecast():
    pos = (50.4657, 4.8647)
    lat, lon = pos
    session = get_mock_session('forecast_wms_feature_info.json')

    client = IrcelineForecastClient(session)

    features = [ForecastFeature.NO2_DMEAN, ForecastFeature.O3_MAXHMEAN]
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
        url=_forecast_wms_base_url,
        params=base | {"layers": f"{feature}_d{d}",
                       "query_layers": f"{feature}_d{d}"},
        headers={'User-Agent': _user_agent},
    )
        for feature, d in product(features, range(4))]

    session.request.assert_has_calls(calls, any_order=True)

    for k, v in result.items():
        assert v['value'] == 10.853286743164062


def test_parse_capabilities_with_error():
    result = IrcelineForecastClient._parse_capabilities("wow there no valid XML")
    assert result == set()
