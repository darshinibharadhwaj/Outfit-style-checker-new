import colorsys

from app.color_utils import ColorResult, color_name, score_harmony


def hsv_of(r, g, b):
    return colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)


def color(r, g, b) -> ColorResult:
    return ColorResult(hex="#%02x%02x%02x" % (r, g, b), rgb=(r, g, b), hsv=hsv_of(r, g, b))


def test_color_names():
    assert color_name(hsv_of(0, 0, 0)) == "black"
    assert color_name(hsv_of(255, 255, 255)) == "white"
    assert color_name(hsv_of(128, 128, 128)) == "grey"
    assert color_name(hsv_of(20, 30, 90)) == "navy"
    assert color_name(hsv_of(220, 40, 40)) == "red"
    assert color_name(hsv_of(120, 20, 40)) == "maroon"
    assert color_name(hsv_of(225, 205, 170)) == "beige"
    assert color_name(hsv_of(30, 90, 220)) == "blue"
    assert color_name(hsv_of(230, 190, 40)) == "mustard"


def test_neutral_pairs_are_safe():
    result = score_harmony(color(200, 30, 30), color(20, 30, 90))  # red + navy
    assert result["label"] == "Safe neutral pairing"
    assert result["score"] >= 0.7


def test_close_hues_are_tonal():
    result = score_harmony(color(200, 40, 40), color(220, 100, 30))  # red + orange
    assert result["label"] == "Harmonious (tonal)"


def test_complementary_hues():
    result = score_harmony(color(220, 40, 40), color(40, 200, 200))  # red + cyan
    assert result["label"] == "Bold complementary contrast"


def test_clashing_hues_score_low():
    result = score_harmony(color(220, 40, 40), color(60, 200, 60))  # red + green (~120 degrees apart)
    assert result["score"] < 0.6
