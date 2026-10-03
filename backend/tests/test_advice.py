from app.advice import accessories, alternatives, footwear, skin_advice, verdict_for


def test_verdict_levels():
    assert verdict_for(0.85) == "good"
    assert verdict_for(0.55) == "ok"
    assert verdict_for(0.45) == "change"


def test_alternatives_never_suggest_current_colors():
    out = alternatives("red", "green", "change")
    assert len(out) == 2
    assert "green" not in out[0].split("bottoms:")[1]


def test_alternatives_for_good_pair_is_single_line():
    assert len(alternatives("navy", "beige", "good")) == 1


def test_skin_advice_good_and_careful_colors():
    assert "great colour" in skin_advice("mustard", "wheatish")[0]
    assert "flat" in skin_advice("beige", "fair")[0]
    assert "works fine" in skin_advice("grey", "fair")[0]


def test_accessories_follow_occasion():
    office = " ".join(accessories("navy", "grey", "office"))
    assert "belt" in office and "silver-tone" in office
    warm = " ".join(accessories("mustard", "brown", "casual"))
    assert "gold-tone" in warm


def test_footwear_follows_occasion_and_bottom():
    assert any("black shoes" in s for s in footwear("navy", "office"))
    assert any("brown shoes" in s for s in footwear("olive", "office"))
    assert any("kolhapuri" in s for s in footwear("blue", "festival"))
