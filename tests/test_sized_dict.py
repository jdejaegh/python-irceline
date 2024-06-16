from src.open_irceline.utils import SizedDict


def test_size_dict():
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
    assert 'f' in s_dict
    assert len(s_dict) == 5

    s_dict['b'] = 42
    s_dict['g'] = 7
    assert 'f' in s_dict
    assert 'g' in s_dict
    assert 'b' in s_dict
    assert 'c' not in s_dict
    assert len(s_dict) == 5

    del s_dict['b']
    assert len(s_dict) == 4
    assert 'b' not in s_dict
