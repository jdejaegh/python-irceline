from datetime import datetime, date

from freezegun import freeze_time

from src.open_irceline.api import IrcelineRioClient
from src.open_irceline.data import RioFeature, FeatureValue
from tests.conftest import get_api_data


@freeze_time(datetime.fromisoformat("2024-06-15T16:55:03.419Z"))
async def test_format_result_hmean():
    data = get_api_data('rio_wfs.json')
    result = IrcelineRioClient._format_result('rio', data, [RioFeature.NO2_HMEAN, RioFeature.O3_HMEAN])

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
    result = IrcelineRioClient._format_result('rio', data,
                                              [RioFeature.BC_DMEAN, RioFeature.PM10_DMEAN, RioFeature.PM25_DMEAN])

    expected = {
        str(RioFeature.BC_DMEAN): FeatureValue(timestamp=date(2024, 6, 15), value=0.1),
        str(RioFeature.PM10_DMEAN): FeatureValue(timestamp=date(2024, 6, 15), value=5.9),
        str(RioFeature.PM25_DMEAN): FeatureValue(timestamp=date(2024, 6, 15), value=1.1),
    }

    assert result == expected


def test_parse_capabilities():
    with open('tests/fixtures/capabilities.xml', 'r') as xml_file:
        result = IrcelineRioClient._parse_capabilities(xml_file.read())

    expected = {'rio:so2_anmean_be', 'rio:o3_hmean', 'rio:bc_anmean_vl', 'rio:o3_anmean_be', 'rio:pm10_hmean_vl',
                'rio:o3_aot40for_be', 'rio:no2_maxhmean', 'rio:pm10_24hmean_1x1', 'rio:o3_aot40veg_5y_be',
                'rio:pm10_24hmean_vl', 'rio:pm10_anmean', 'rio:pm25_anmean_be', 'rio:o3_net60_be', 'rio:pm25_hmean_vl',
                'rio:so2_25thmax_hmean_be', 'rio:so2_hmean_vl', 'rio:pm10_dmean', 'rio:bc_hmean_wl',
                'rio:o3_aot40veg_be', 'rio:o3_max8hmean', 'rio:pm25_24hmean', 'rio:no2_hmean',
                'rio:rio_grid_4x4_centroids', 'rio:no2_anmean', 'rio:so2_hmean', 'rio:o3_hmean_vl', 'rio:rio_grid_4x4',
                'rio:pm10_hmean_1x1', 'rio:pm25_anmean_vl', 'rio:pm25_dmean', 'rio:rio_grid_1x1', 'rio:o3_aot60_be',
                'rio:no2_anmean_be', 'rio:o3_net60_3y_be', 'rio:pm10_anmean_be', 'rio:o3_maxhmean',
                'rio:no2_19thmax_hmean_be', 'rio:bc_anmean_be', 'rio:bc_24hmean', 'rio:no2_anmean_vl',
                'rio:no2_hmean_wl', 'rio:pm10_24hmean', 'rio:bc_hmean_vl', 'rio:pm10_anmean_vl', 'rio:pm10_hmean_wl',
                'rio:pm25_anmean', 'rio:o3_aot40for_5y_be', 'rio:rio_grid_4x4_be', 'rio:o3_8hmean',
                'rio:pm25_hmean_1x1', 'rio:no2_hmean_vl', 'rio:o3_anmean', 'rio:pm10_excday_be', 'rio:o3_anmean_vl',
                'rio:pm10_hmean', 'rio:pm25_24hmean_vl', 'rio:pm25_hmean', 'rio:bc_hmean', 'rio:so2_anmean_vl',
                'rio:bc_dmean'}

    assert result == expected
