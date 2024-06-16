from collections import OrderedDict


class SizedDict(OrderedDict):
    """Dictionary with a maximum size.  When more items are added, the least recently accessed element is evicted"""

    def __init__(self, size: int):
        super().__init__()
        self._size = size

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        self.move_to_end(key)
        if len(self) > self._size:
            print('drop', self.popitem(False)[0])

    def __getitem__(self, key):
        self.move_to_end(key)
        return super().__getitem__(key)

    def get(self, __key, __default=None):
        self.move_to_end(__key)
        return super().get(__key, __default)

    def update(self, __m, **kwargs):
        raise NotImplementedError()
