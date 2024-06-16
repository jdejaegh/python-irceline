from src.open_irceline.api import IrcelineForecastClient
from tests.conftest import get_api_data


def test_extract_from_csv():
    data = get_api_data('forecast.csv', plain=True)
    x, y = 50.45, 4.85

    result = IrcelineForecastClient.extract_result_from_csv(x, y, data)
    assert result == 13.0844

    result = IrcelineForecastClient.extract_result_from_csv(23, 4, data)
    assert result is None
