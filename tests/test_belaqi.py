from src.open_irceline.belaqi import belaqi_index
from src.open_irceline.data import BelAqiIndex


def test_belaqi_index():
    # Excellent
    assert belaqi_index(5, 2, 10, 10) == BelAqiIndex.EXCELLENT
    assert belaqi_index(0, 0, 0, 0) == BelAqiIndex.EXCELLENT
    assert belaqi_index(10, 5, 25, 20) == BelAqiIndex.EXCELLENT

    # Very good
    assert belaqi_index(15, 8, 40, 35) == BelAqiIndex.VERY_GOOD
    assert belaqi_index(11, 6, 26, 21) == BelAqiIndex.VERY_GOOD
    assert belaqi_index(20, 10, 50, 50) == BelAqiIndex.VERY_GOOD

    # Good
    assert belaqi_index(25, 12, 60, 60) == BelAqiIndex.GOOD
    assert belaqi_index(21, 11, 51, 51) == BelAqiIndex.GOOD
    assert belaqi_index(30, 15, 70, 70) == BelAqiIndex.GOOD

    # Fairly good
    assert belaqi_index(35, 20, 100, 90) == BelAqiIndex.FAIRLY_GOOD
    assert belaqi_index(31, 16, 71, 71) == BelAqiIndex.FAIRLY_GOOD
    assert belaqi_index(40, 25, 120, 120) == BelAqiIndex.FAIRLY_GOOD

    # Moderate
    assert belaqi_index(45, 30, 140, 130) == BelAqiIndex.MODERATE
    assert belaqi_index(41, 26, 121, 121) == BelAqiIndex.MODERATE
    assert belaqi_index(50, 35, 160, 150) == BelAqiIndex.MODERATE

    # Poor
    assert belaqi_index(55, 38, 170, 160) == BelAqiIndex.POOR
    assert belaqi_index(51, 36, 161, 151) == BelAqiIndex.POOR
    assert belaqi_index(60, 40, 180, 180) == BelAqiIndex.POOR

    # Very poor
    assert belaqi_index(65, 45, 200, 190) == BelAqiIndex.VERY_POOR
    assert belaqi_index(61, 41, 181, 181) == BelAqiIndex.VERY_POOR
    assert belaqi_index(70, 50, 240, 200) == BelAqiIndex.VERY_POOR

    # Bad
    assert belaqi_index(75, 55, 260, 220) == BelAqiIndex.BAD
    assert belaqi_index(71, 51, 241, 201) == BelAqiIndex.BAD
    assert belaqi_index(80, 60, 280, 250) == BelAqiIndex.BAD

    # Very bad
    assert belaqi_index(85, 65, 300, 270) == BelAqiIndex.VERY_BAD
    assert belaqi_index(81, 61, 281, 251) == BelAqiIndex.VERY_BAD
    assert belaqi_index(100, 70, 320, 300) == BelAqiIndex.VERY_BAD

    # Horrible
    assert belaqi_index(110, 75, 330, 310) == BelAqiIndex.HORRIBLE
    assert belaqi_index(101, 71, 321, 301) == BelAqiIndex.HORRIBLE
    assert belaqi_index(150, 100, 400, 400) == BelAqiIndex.HORRIBLE
