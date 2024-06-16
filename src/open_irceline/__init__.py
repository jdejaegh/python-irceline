from pyproj import Transformer

project_transform = Transformer.from_crs('EPSG:4326', 'EPSG:31370', always_xy=False)
rio_wfs_base_url = 'https://geo.irceline.be/rio/wfs'
# noinspection HttpUrlsUsage
# There is not HTTPS version of this endpoint
forecast_base_url = 'http://ftp.irceline.be/forecast'
user_agent = 'github.com/jdejaegh/python-irceline'
