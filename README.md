# Simple asynchronous Python client for IRCEL - CELINE open data

**Work in progress**

Python module to get data from the [IRCEL - CELINE open data](https://irceline.be/en/documentation/open-data)

Target features:

- [X] Get data for real time measurements interpolated
- [X] Get forecast data for PM10, PM2.5 and O3
- [X] Compute or fetch BelAQI index (observation and forecast)
- [ ] Maybe: also provide data from the stations and not only interpolation

## Install

The library is published on PyPI.  Install it using `pip`

```shell
pip install open-irceline
```

## Example of use

```python
import aiohttp
import asyncio
from datetime import datetime, date

from open_irceline import IrcelineRioClient, RioFeature, IrcelineForecastClient, ForecastFeature, belaqi_index_rio_hourly


async def get_rio_interpolated_data():
    """Get current level of PM2.5 and PM10 at Brussels from the RIO interpolated data"""
    async with aiohttp.ClientSession() as session:
        client = IrcelineRioClient(session)
        result = await client.get_data(
            timestamp=datetime.utcnow(),  # must be timezone aware
            features=[RioFeature.PM25_HMEAN, RioFeature.PM10_HMEAN],
            position=(50.85, 4.35)  # (lat, lon) for Brussels
        )

    print(f"PM2.5  {result[RioFeature.PM25_HMEAN]['value']} µg/m³")
    print(f"PM10   {result[RioFeature.PM10_HMEAN]['value']} µg/m³")


async def get_forecast():
    """Get forecast for O3 concentration for Brussels for the next days"""
    async with aiohttp.ClientSession() as session:
        client = IrcelineForecastClient(session)
        result = await client.get_data(
            timestamp=date.today(),
            features=[ForecastFeature.O3_MAXHMEAN],
            position=(50.85, 4.35)  # (lat, lon) for Brussels
        )

    for (feature, day), v in result.items():
        print(f"{feature} {day} {v['value']} µg/m³")


async def get_current_belaqi():
    """Get current BelAQI index from RIO interpolated values"""
    async with aiohttp.ClientSession() as session:
        client = IrcelineRioClient(session)
        result = await belaqi_index_rio_hourly(
            rio_client=client,
            timestamp=datetime.utcnow(),  # must be timezone aware
            position=(50.85, 4.35)        # (lat, lon) for Brussels
        )

    print(f"Current BelAQI index for Brussels: {result}")


if __name__ == '__main__':
    print("RIO interpolated data")
    asyncio.run(get_rio_interpolated_data())

    print("\nO3 forecast for Brussels")
    asyncio.run(get_forecast())

    print("\nCurrent BelAQI index")
    asyncio.run(get_current_belaqi())
```

## Attribution

The data provided by this module is provided by the [Belgian Interregional Environment Agency (IRCEL - CELINE)](https://www.irceline.be/en). 
No change to the provided data is made. 
Their data is made available under the [Creative Commons Attribution 4.0 license](https://creativecommons.org/licenses/by/4.0/). 

This work is not endorsed by the Belgian Interregional Environment Agency (IRCEL - CELINE).


