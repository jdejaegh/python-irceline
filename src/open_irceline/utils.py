from typing import Tuple

from pyproj import Transformer

_project_transform = Transformer.from_crs('EPSG:4326', 'EPSG:31370', always_xy=False)


def epsg_transform(position: Tuple[float, float]) -> Tuple[int, int]:
    """
    Convert 'EPSG:4326' coordinates to 'EPSG:31370' coordinates
    :param position: (x, y) coordinates
    :return: tuple of int in the EPSG:31370 system
    """
    result = _project_transform.transform(position[0], position[1])
    return round(result[0]), round(result[1])
