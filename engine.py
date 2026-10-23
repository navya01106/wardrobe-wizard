"""Outfit matching logic for Wardrobe Wizard.

Everything here is plain Python with no Streamlit dependency, so it can be
tested on its own (see test_engine.py).
"""
import colorsys
import itertools
import json
import random
import uuid
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"
PHOTO_DIR = DATA_DIR / "photos"

CATEGORIES = ["top", "bottom", "dress", "outerwear", "shoes"]
OCCASIONS = ["casual", "work", "formal", "party", "sports"]

# Display colours (hex) for each colour name the app understands.
COLORS = {
    "black": "#1a1a1a", "white": "#f5f5f5", "grey": "#9e9e9e",
    "beige": "#d9c7a3", "navy": "#1f2a52", "denim": "#4a6fa5",
    "brown": "#6b4a2f", "red": "#c62828", "orange": "#ef6c00",
    "yellow": "#f9c80e", "green": "#2e7d32", "olive": "#6b7a2f",
    "blue": "#1e5bd8", "purple": "#6a1b9a", "pink": "#e86a9a",
}
# Neutrals pair with almost anything. Everything else counts as a "bold" colour.
NEUTRALS = {"black", "white", "grey", "beige", "navy", "denim", "brown"}


# ---------- storage ----------

def load(name):
    path = DATA_DIR / f"{name}.json"
    if not path.exists():
        return []
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError:
        return []


def save(name, data):
    DATA_DIR.mkdir(exist_ok=True)
    (DATA_DIR / f"{name}.json").write_text(json.dumps(data, indent=2))


def add_item(name, category, color, occasions, photo_bytes=None, photo_ext=None):
    item = {
        "id": uuid.uuid4().hex[:8],
        "name": name.strip(),
        "category": category,
        "color": color,
        "occasions": list(occasions),
        "photo": None,
    }
    if photo_bytes:
        PHOTO_DIR.mkdir(parents=True, exist_ok=True)
        item["photo"] = f"{item['id']}.{photo_ext or 'png'}"
        (PHOTO_DIR / item["photo"]).write_bytes(photo_bytes)
    save("wardrobe", load("wardrobe") + [item])
    return item


def remove_item(item_id):
    kept = []
    for item in load("wardrobe"):
        if item["id"] == item_id:
            if item.get("photo"):
                (PHOTO_DIR / item["photo"]).unlink(missing_ok=True)
        else:
            kept.append(item)
    save("wardrobe", kept)


def sample_wardrobe():
    rows = [
        ("White cotton tee", "top", "white", ["casual", "sports"]),
        ("Navy shirt", "top", "navy", ["work", "formal", "casual"]),
        ("Red crop top", "top", "red", ["party", "casual"]),
        ("Blue jeans", "bottom", "denim", ["casual", "party"]),
        ("Black trousers", "bottom", "black", ["work", "formal", "party"]),
        ("Beige chinos", "bottom", "beige", ["casual", "work"]),
        ("Olive joggers", "bottom", "olive", ["sports", "casual"]),
        ("Black dress", "dress", "black", ["party", "formal"]),
        ("Yellow sundress", "dress", "yellow", ["casual", "party"]),
        ("White sneakers", "shoes", "white", ["casual", "sports"]),
        ("Black loafers", "shoes", "black", ["work", "formal", "party"]),
        ("Brown boots", "shoes", "brown", ["casual", "party"]),
        ("Denim jacket", "outerwear", "denim", ["casual", "party"]),
        ("Grey blazer", "outerwear", "grey", ["work", "formal"]),
        ("Green hoodie", "outerwear", "green", ["sports", "casual"]),
    ]
    return [
        {"id": uuid.uuid4().hex[:8], "name": n, "category": c, "color": col,
         "occasions": o, "photo": None}
        for n, c, col, o in rows
    ]


# ---------- colour matching ----------

def hue(color):
    hex_code = COLORS[color].lstrip("#")
    r, g, b = (int(hex_code[i:i + 2], 16) / 255 for i in (0, 2, 4))
    return colorsys.rgb_to_hsv(r, g, b)[0] * 360


def pair_score(a, b):
    """Score how well two colours go together, from 0 to 10, with a short note."""
    if a in NEUTRALS and b in NEUTRALS:
        return 9, None
    if a in NEUTRALS or b in NEUTRALS:
        bold = b if a in NEUTRALS else a
        base = a if a in NEUTRALS else b
        return 9, f"{bold} stands out against the {base}"
    if a == b:
        return 7, f"tone-on-tone {a}"
    gap = abs(hue(a) - hue(b))
    gap = min(gap, 360 - gap)  # 0 to 180 degrees around the colour wheel
    if gap <= 40:
        return 7, f"{a} and {b} are close neighbours on the colour wheel"
    if gap >= 150:
        return 8, f"{a} and {b} are near opposites, so they contrast well"
    if gap >= 100:
        return 5, None
    return 3, f"{a} and {b} may clash"


def outfit_score(pieces):
    """Return (score out of 100, list of short notes) for a set of pieces."""
    colors = [p["color"] for p in pieces]
    scores, notes = [], []
    for a, b in itertools.combinations(colors, 2):
        s, note = pair_score(a, b)
        scores.append(s)
        if note and note not in notes:
            notes.append(note)
    avg = sum(scores) / len(scores) if scores else 9
    bold_count = len({c for c in colors if c not in NEUTRALS})
    penalty = max(0, bold_count - 2) * 15
    if penalty:
        notes.append("three or more bold colours makes the look busy")
    return max(0, min(100, round(avg * 10 - penalty))), notes


# ---------- outfit generation ----------

def generate(wardrobe, occasion, cold=False, limit=4):
    """Build outfits for an occasion. Returns the best ones, best first."""
    pool = [i for i in wardrobe if occasion in i["occasions"]]

    def of(cat):
        return [i for i in pool if i["category"] == cat]

    bases = [[d] for d in of("dress")]
    bases += [[t, b] for t, b in itertools.product(of("top"), of("bottom"))]
    shoe_opts = [[s] for s in of("shoes")] or [[]]
    coat_opts = [[o] for o in of("outerwear")] if cold and of("outerwear") else [[]]

    outfits = []
    for base, shoes, coat in itertools.product(bases, shoe_opts, coat_opts):
        pieces = base + shoes + coat
        score, notes = outfit_score(pieces)
        outfits.append({"pieces": pieces, "score": score, "notes": notes})

    random.shuffle(outfits)  # ties come out in a different order each time
    outfits.sort(key=lambda o: o["score"], reverse=True)
    return outfits[:limit]
