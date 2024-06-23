"""
Compute the BelAQI index from concentrations of PM10, PM2.5, O3 and NO2, based on
https://www.irceline.be/en/air-quality/measurements/belaqi-air-quality-index/information

> to calculate the actual (hour per hour varying) sub-indexes and the global index, the concentration scales of Table 4
> are applied to the latest hourly mean O3 and NO2 concentrations and the running 24-hourly mean PM2.5 and PM10
> concentrations.
"""
from datetime import datetime, date
from typing import Tuple, Dict

from src.open_irceline.api import IrcelineRioClient, IrcelineForecastClient
from src.open_irceline.data import BelAqiIndex, RioFeature, ForecastFeature


def belaqi_index(pm10: float, pm25: float, o3: float, no2: float) -> BelAqiIndex:
    """
    Computes the BelAQI index based on the components
    Raise ValueError if a component is < 0
    :param pm10: PM10 daily mean (or running 24-hourly mean for real-time) (µg/m³)
    :param pm25: PM2.5 daily mean (or running 24-hourly mean for real-time) (µg/m³)
    :param o3: O3 max 1-hourly mean per day (or latest hourly mean for real-time) (µg/m³)
    :param no2: NO2 max 1-hourly mean per day (or latest hourly mean for real-time) (µg/m³)
    :return: BelAQI index from 1 to 10 (Value of BelAqiIndex enum)
    """
    if pm10 is None or pm25 is None or o3 is None or no2 is None:
        raise ValueError("All the components should be valued (at lest one is None here)")

    if pm10 < 0 or pm25 < 0 or o3 < 0 or no2 < 0:
        raise ValueError("All the components should have a positive value")

    elif pm10 > 100 or pm25 > 70 or o3 > 320 or no2 > 300:
        return BelAqiIndex.HORRIBLE

    elif pm10 > 80 or pm25 > 60 or o3 > 280 or no2 > 250:
        return BelAqiIndex.VERY_BAD

    elif pm10 > 70 or pm25 > 50 or o3 > 240 or no2 > 200:
        return BelAqiIndex.BAD

    elif pm10 > 60 or pm25 > 40 or o3 > 180 or no2 > 180:
        return BelAqiIndex.VERY_POOR

    elif pm10 > 50 or pm25 > 35 or o3 > 160 or no2 > 150:
        return BelAqiIndex.POOR

    elif pm10 > 40 or pm25 > 25 or o3 > 120 or no2 > 120:
        return BelAqiIndex.MODERATE

    elif pm10 > 30 or pm25 > 15 or o3 > 70 or no2 > 70:
        return BelAqiIndex.FAIRLY_GOOD

    elif pm10 > 20 or pm25 > 10 or o3 > 50 or no2 > 50:
        return BelAqiIndex.GOOD

    elif pm10 > 10 or pm25 > 5 or o3 > 25 or no2 > 20:
        return BelAqiIndex.VERY_GOOD

    elif pm10 >= 0 or pm25 >= 0 or o3 >= 0 or no2 >= 0:
        return BelAqiIndex.EXCELLENT


async def belaqi_index_actual(rio_client: IrcelineRioClient, position: Tuple[float, float],
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
        features=[RioFeature.PM10_24HMEAN,
                  RioFeature.PM25_24HMEAN,
                  RioFeature.O3_HMEAN,
                  RioFeature.NO2_HMEAN],
        position=position
    )

    return belaqi_index(
        components.get(RioFeature.PM10_24HMEAN, {}).get('value', -1),
        components.get(RioFeature.PM25_24HMEAN, {}).get('value', -1),
        components.get(RioFeature.O3_HMEAN, {}).get('value', -1),
        components.get(RioFeature.NO2_HMEAN, {}).get('value', -1)
    )


async def belaqi_index_forecast(forecast_client: IrcelineForecastClient, position: Tuple[float, float],
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
            result[day] = belaqi_index(
                components.get((ForecastFeature.PM10_DMEAN, day), {}).get('value', -1),
                components.get((ForecastFeature.PM25_DMEAN, day), {}).get('value', -1),
                components.get((ForecastFeature.O3_MAXHMEAN, day), {}).get('value', -1),
                components.get((ForecastFeature.NO2_MAXHMEAN, day), {}).get('value', -1)
            )
        except ValueError:
            result[day] = None

    return result
