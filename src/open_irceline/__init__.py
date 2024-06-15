from pyproj import Transformer

project_transform = Transformer.from_crs('EPSG:4326', 'EPSG:31370', always_xy=True)
rio_wfs_base_url = 'https://geo.irceline.be/rio/wfs'
