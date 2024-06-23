from collections import OrderedDict
from typing import Tuple

from pyproj import Transformer

_project_transform = Transformer.from_crs('EPSG:4326', 'EPSG:31370', always_xy=False)


class SizedDict(OrderedDict):
    """Dictionary with a maximum size.  When more items are added, the least recently accessed element is evicted"""

    def __init__(self, size: int):
        super().__init__()
        self._size = size

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        self.move_to_end(key)
        if len(self) > self._size:
            self.popitem(False)

    def __getitem__(self, key):
        self.move_to_end(key)
        return super().__getitem__(key)

    def get(self, __key, __default=None):
        self.move_to_end(__key)
        return super().get(__key, __default)

    def update(self, __m, **kwargs):
        raise NotImplementedError()


def epsg_transform(position: Tuple[float, float]) -> Tuple[int, int]:
    """
    Convert 'EPSG:4326' coordinates to 'EPSG:31370' coordinates
    :param position: (x, y) coordinates
    :return: tuple of int in the EPSG:31370 system
    """
    result = _project_transform.transform(position[0], position[1])
    return round(result[0]), round(result[1])


def round_coordinates(x: float, y: float, step=.05) -> Tuple[float, float]:
    """
    Round the coordinate to the precision given by step
    :param x: latitude
    :param y: longitude
    :param step: precision of the rounding
    :return: x and y round to the closest step increment
    """
    n = 1 / step
    return round(x * n) / n, round(y * n) / n
