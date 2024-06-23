import pytest

from src.open_irceline.utils import SizedDict, round_coordinates, epsg_transform


def test_sized_dict():
    s_dict = SizedDict(5)
    assert len(s_dict) == 0

    s_dict['a'] = 1
    s_dict['b'] = 2
    s_dict['c'] = 3
    s_dict['d'] = 4
    s_dict['e'] = 5
    assert len(s_dict) == 5

    s_dict['f'] = 6
    assert 'a' not in s_dict
    assert s_dict['f'] == 6
    assert len(s_dict) == 5

    s_dict['b'] = 42
    s_dict['g'] = 7
    assert s_dict.get('f') == 6
    assert s_dict['g'] == 7
    assert s_dict['b'] == 42
    assert 'c' not in s_dict
    assert len(s_dict) == 5

    del s_dict['b']
    assert len(s_dict) == 4
    assert 'b' not in s_dict

    with pytest.raises(NotImplementedError):
        s_dict.update({'a': 1})


def test_round_coord():
    x, y = round_coordinates(50.4657, 4.8647)
    assert x == 50.45
    assert y == 4.85


def test_epsg_transform():
    x, y = epsg_transform((50.4657, 4.8647))
    assert x == 185211
    assert y == 128437
