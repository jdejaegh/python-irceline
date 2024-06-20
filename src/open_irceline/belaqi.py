"""
Compute the BelAQI index from concentrations of PM10, PM2.5, O3 and NO2, based on
https://www.irceline.be/en/air-quality/measurements/belaqi-air-quality-index/information

> to calculate the actual (hour per hour varying) sub-indexes and the global index, the concentration scales of Table 4
> are applied to the latest hourly mean O3 and NO2 concentrations and the running 24-hourly mean PM2.5 and PM10
> concentrations.
"""
from src.open_irceline.data import BelAqiIndex


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
