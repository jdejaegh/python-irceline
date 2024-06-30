from src.open_irceline.utils import epsg_transform


def test_epsg_transform():
    x, y = epsg_transform((50.4657, 4.8647))
    assert x == 185211
    assert y == 128437
