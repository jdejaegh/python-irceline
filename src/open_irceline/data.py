from datetime import datetime, date
from enum import StrEnum, Enum
from typing import TypedDict


class IrcelineFeature(StrEnum):
    pass


class RioFeature(IrcelineFeature):
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


class ForecastFeature(IrcelineFeature):
    NO2_MAXHMEAN = 'chimere_no2_maxhmean'
    O3_MAXHMEAN = 'chimere_o3_maxhmean'
    PM10_DMEAN = 'chimere_pm10_dmean'
    PM25_DMEAN = 'chimere_pm25_dmean'


class FeatureValue(TypedDict):
    # Timestamp at which the value was computed
    timestamp: datetime | date
    value: int | float | None


class BelAqiIndex(Enum):
    EXCELLENT = 1
    VERY_GOOD = 2
    GOOD = 3
    FAIRLY_GOOD = 4
    MODERATE = 5
    POOR = 6
    VERY_POOR = 7
    BAD = 8
    VERY_BAD = 9
    HORRIBLE = 10
