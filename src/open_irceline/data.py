from enum import StrEnum
from typing import TypedDict
from datetime import datetime, date


class RioFeature(StrEnum):
    BC_24HMEAN = 'rio:bc_24hmean'
    BC_DMEAN = 'rio:bc_dmean'
    BC_HMEAN = 'rio:bc_hmean'
    NO2_ANMEAN = 'rio:no2_anmean'
    NO2_DMEAN = 'rio:no2_dmean'
    NO2_HMEAN = 'rio:no2_hmean'
    O3_8HMEAN = 'rio:o3_8hmean'
    O3_ANMEAN = 'rio:o3_anmean'
    O3_HMEAN = 'rio:o3_hmean'
    O3_MAX8HMEAN = 'rio:o3_max8hmean'
    O3_MAXHMEAN = 'rio:o3_maxhmean'
    PM10_24HMEAN = 'rio:pm10_24hmean'
    PM10_ANMEAN = 'rio:pm10_anmean'
    PM10_DMEAN = 'rio:pm10_dmean'
    PM10_HMEAN = 'rio:pm10_hmean'
    PM25_24HMEAN = 'rio:pm25_24hmean'
    PM25_ANMEAN = 'rio:pm25_anmean'
    PM25_DMEAN = 'rio:pm25_dmean'
    PM25_HMEAN = 'rio:pm25_hmean'
    SO2_HMEAN = 'rio:so2_hmean'


class FeatureValue(TypedDict):
    timestamp: datetime | date
    value: int | float | None
