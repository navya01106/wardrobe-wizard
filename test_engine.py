import engine


def item(name, category, color, occasions):
    return {"id": name, "name": name, "category": category,
            "color": color, "occasions": occasions, "photo": None}


def test_neutral_goes_with_anything():
    assert engine.pair_score("black", "red")[0] == 9


def test_near_opposites_contrast():
    assert engine.pair_score("blue", "orange")[0] == 8


def test_clashing_colours_score_low():
    assert engine.pair_score("red", "green")[0] <= 5


def test_busy_outfit_is_penalised():
    calm = [item("a", "top", "red", []), item("b", "bottom", "black", [])]
    busy = [item("a", "top", "red", []), item("b", "bottom", "green", []),
            item("c", "shoes", "purple", [])]
    assert engine.outfit_score(busy)[0] < engine.outfit_score(calm)[0]


def test_generate_respects_occasion():
    wardrobe = [
        item("tee", "top", "white", ["casual"]),
        item("suit trousers", "bottom", "black", ["formal"]),
        item("jeans", "bottom", "denim", ["casual"]),
    ]
    for outfit in engine.generate(wardrobe, "casual", limit=10):
        assert all("casual" in p["occasions"] for p in outfit["pieces"])


def test_no_outfit_without_a_bottom():
    wardrobe = [item("tee", "top", "white", ["casual"])]
    assert engine.generate(wardrobe, "casual") == []


def test_outerwear_only_when_cold():
    wardrobe = engine.sample_wardrobe()
    warm = engine.generate(wardrobe, "casual", cold=False, limit=50)
    assert all(p["category"] != "outerwear" for o in warm for p in o["pieces"])
    cold = engine.generate(wardrobe, "casual", cold=True, limit=5)
    assert all(any(p["category"] == "outerwear" for p in o["pieces"]) for o in cold)
