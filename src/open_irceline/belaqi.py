"""
Compute the BelAQI index from concentrations of PM10, PM2.5, O3 and NO2, based on
https://www.irceline.be/en/air-quality/measurements/air-quality-index-november-2022/info_nov2022
"""
from datetime import datetime, date
from typing import Tuple, Dict, Final

from .api import IrcelineRioClient, IrcelineForecastClient
from .data import BelAqiIndex, RioFeature, ForecastFeature

# Ratio values from Figure 2 at
# https://www.irceline.be/en/air-quality/measurements/air-quality-index-november-2022/info_nov2022
NO2_MAX_HMEAN_TO_DMEAN: Final = 1.51
O3_MAX_HMEAN_TO_MAX8HMEAN: Final = 1.10


def belaqi_index_daily(pm10: float, pm25: float, o3: float, no2: float) -> BelAqiIndex:
    """
    Computes the daily BelAQI index based on the components
    Raise ValueError if a component is < 0

    Values taken from Table 1 of
    https://www.irceline.be/en/air-quality/measurements/air-quality-index-november-2022/info_nov2022

    :param pm10: PM10 daily mean (µg/m³)
    :param pm25: PM2.5 daily mean (µg/m³)
    :param o3: O3 maximum running 8-hour mean (µg/m³)
    :param no2: NO2 daily mean (µg/m³)
    :return: BelAQI index from 1 to 10 (Value of BelAqiIndex enum)
    """
    if pm10 is None or pm25 is None or o3 is None or no2 is None:
        raise ValueError("All the components should be valued (at lest one is None here)")

    if pm10 < 0 or pm25 < 0 or o3 < 0 or no2 < 0:
        raise ValueError("All the components should have a positive value")

    elif pm10 > 100 or pm25 > 50 or o3 > 220 or no2 > 50:
        return BelAqiIndex.HORRIBLE

    elif pm10 > 80 or pm25 > 40 or o3 > 190 or no2 > 40:
        return BelAqiIndex.VERY_BAD

    elif pm10 > 70 or pm25 > 35 or o3 > 160 or no2 > 35:
        return BelAqiIndex.BAD

    elif pm10 > 60 or pm25 > 25 or o3 > 130 or no2 > 30:
        return BelAqiIndex.VERY_POOR

    elif pm10 > 45 or pm25 > 15 or o3 > 100 or no2 > 25:
        return BelAqiIndex.POOR

    elif pm10 > 35 or pm25 > 10 or o3 > 80 or no2 > 20:
        return BelAqiIndex.MODERATE

    elif pm10 > 25 or pm25 > 7.5 or o3 > 70 or no2 > 15:
        return BelAqiIndex.FAIRLY_GOOD

    elif pm10 > 15 or pm25 > 5 or o3 > 60 or no2 > 10:
        return BelAqiIndex.GOOD

    elif pm10 > 5 or pm25 > 2.5 or o3 > 30 or no2 > 5:
        return BelAqiIndex.VERY_GOOD

    elif pm10 >= 0 or pm25 >= 0 or o3 >= 0 or no2 >= 0:
        return BelAqiIndex.EXCELLENT


def belaqi_index_hourly(pm10: float, pm25: float, o3: float, no2: float) -> BelAqiIndex:
    """
    Computes the hourly BelAQI index based on the components
    Raise ValueError if a component is < 0

    Values taken from Table 2 of
    https://www.irceline.be/en/air-quality/measurements/air-quality-index-november-2022/info_nov2022

    :param pm10: PM10 hourly mean (µg/m³)
    :param pm25: PM2.5 hourly mean (µg/m³)
    :param o3: O3 hourly mean (µg/m³)
    :param no2: NO2 hourly mean (µg/m³)
    :return: BelAQI index from 1 to 10 (Value of BelAqiIndex enum)
    """
    if pm10 is None or pm25 is None or o3 is None or no2 is None:
        raise ValueError("All the components should be valued (at lest one is None here)")

    if pm10 < 0 or pm25 < 0 or o3 < 0 or no2 < 0:
        raise ValueError("All the components should have a positive value")

    elif pm10 > 140 or pm25 > 75 or o3 > 240 or no2 > 75:
        return BelAqiIndex.HORRIBLE

    elif pm10 > 110 or pm25 > 60 or o3 > 210 or no2 > 60:
        return BelAqiIndex.VERY_BAD

    elif pm10 > 95 or pm25 > 50 or o3 > 180 or no2 > 50:
        return BelAqiIndex.BAD

    elif pm10 > 80 or pm25 > 35 or o3 > 150 or no2 > 45:
        return BelAqiIndex.VERY_POOR

    elif pm10 > 60 or pm25 > 20 or o3 > 110 or no2 > 40:
        return BelAqiIndex.POOR

    elif pm10 > 45 or pm25 > 15 or o3 > 90 or no2 > 30:
        return BelAqiIndex.MODERATE

    elif pm10 > 35 or pm25 > 10 or o3 > 75 or no2 > 20:
        return BelAqiIndex.FAIRLY_GOOD

    elif pm10 > 20 or pm25 > 7.5 or o3 > 65 or no2 > 15:
        return BelAqiIndex.GOOD

    elif pm10 > 10 or pm25 > 3.5 or o3 > 30 or no2 > 10:
        return BelAqiIndex.VERY_GOOD

    elif pm10 >= 0 or pm25 >= 0 or o3 >= 0 or no2 >= 0:
        return BelAqiIndex.EXCELLENT


async def belaqi_index_rio_hourly(rio_client: IrcelineRioClient, position: Tuple[float, float],
                                  timestamp: datetime | None = None) -> BelAqiIndex:
    """
    Get current BelAQI index value for the given position using the rio_client
    Raise ValueError if one or more components are not available
    :param rio_client: client for the RIO WFS service
    :param position: position for which to get the data
    :param timestamp: desired time for the data (now if None)
    :return: BelAQI index value for the position at the time
    """
    if timestamp is None:
        timestamp = datetime.utcnow()
    components = await rio_client.get_data(
        timestamp=timestamp,
        features=[RioFeature.PM10_HMEAN,
                  RioFeature.PM25_HMEAN,
                  RioFeature.O3_HMEAN,
                  RioFeature.NO2_HMEAN],
        position=position
    )

    return belaqi_index_hourly(
        pm10=components.get(RioFeature.PM10_HMEAN, {}).get('value', -1),
        pm25=components.get(RioFeature.PM25_HMEAN, {}).get('value', -1),
        o3=components.get(RioFeature.O3_HMEAN, {}).get('value', -1),
        no2=components.get(RioFeature.NO2_HMEAN, {}).get('value', -1)
    )


async def belaqi_index_forecast_daily(forecast_client: IrcelineForecastClient, position: Tuple[float, float],
                                      timestamp: date | None = None) -> Dict[date, BelAqiIndex | None]:
    """
    Get forecasted BelAQI index value for the given position using the forecast_client.
    Data is downloaded for the given day and the four next days
    Value is None for the date if one or more components cannot be downloaded
    :param forecast_client: client for the forecast data
    :param position: position for which to get the data
    :param timestamp: day at which the forecast are issued
    :return: dict mapping a day to the forecasted BelAQI index
    """
    if timestamp is None:
        timestamp = date.today()
    components = await forecast_client.get_data(
        timestamp=timestamp,
        features=[ForecastFeature.PM10_DMEAN,
                  ForecastFeature.PM25_DMEAN,
                  ForecastFeature.O3_MAXHMEAN,
                  ForecastFeature.NO2_MAXHMEAN],
        position=position
    )

    result = dict()

    for _, day in components.keys():
        try:
            result[day] = belaqi_index_daily(
                pm10=components.get((ForecastFeature.PM10_DMEAN, day), {}).get('value', -1),
                pm25=components.get((ForecastFeature.PM25_DMEAN, day), {}).get('value', -1),
                o3=components.get((ForecastFeature.O3_MAXHMEAN, day), {}).get('value', -1) * O3_MAX_HMEAN_TO_MAX8HMEAN,
                no2=components.get((ForecastFeature.NO2_MAXHMEAN, day), {}).get('value', -1) * NO2_MAX_HMEAN_TO_DMEAN
            )
        except (ValueError, TypeError):
            result[day] = None

    return result
