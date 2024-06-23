from pyproj import Transformer as _Transformer

from .data import RioFeature, ForecastFeature, FeatureValue, BelAqiIndex
from .api import IrcelineRioClient, IrcelineForecastClient
from .belaqi import belaqi_index, belaqi_index_actual, belaqi_index_forecast

__version__ = '0.0.3'

_project_transform = _Transformer.from_crs('EPSG:4326', 'EPSG:31370', always_xy=False)
_rio_wfs_base_url = 'https://geo.irceline.be/wfs'
# noinspection HttpUrlsUsage
# There is not HTTPS version of this endpoint
_forecast_base_url = 'http://ftp.irceline.be/forecast'
_user_agent = 'github.com/jdejaegh/python-irceline'
