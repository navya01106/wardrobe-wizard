# Wardrobe Wizard

A Python app that suggests outfits from clothes you already own. You add your wardrobe (with optional photos), pick an occasion, and it returns outfits ranked by how well the colours work together.

I built it to combine my interest in fashion with my coding practice. Getting more outfits out of a wardrobe you already have also means buying less.

[Add a screenshot of the Outfit ideas tab here]

## Features

- Add clothes with a type, main colour, occasions and an optional photo
- Outfit suggestions for casual, work, formal, party and sports
- A "cold" option that adds outerwear
- A match score and a short reason for each suggestion
- Save outfits you like
- Data is stored locally in JSON files

## How the matching works

Colours are split into neutrals (black, white, grey, beige, navy, denim, brown) and bold colours. Each pair of colours in an outfit gets a score from 0 to 10:

- A neutral with anything: 9
- Two colours close on the colour wheel, or the same colour: 7
- Two near-opposite colours: 8
- Colours in between, or a bold pair that is far apart: 3 to 5, with a clash note when low

The scores are averaged and scaled to 100. Outfits with three or more bold colours lose 15 points per extra colour, because they tend to look busy. Colour positions come from converting each colour to hue with Python's `colorsys` module. Every piece must be tagged for the chosen occasion.

The matching code lives in `engine.py` and does not depend on Streamlit, so it is tested separately in `test_engine.py`.

## Run it

```
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

Run the tests with `pytest`.

## Limits

- Colour rules are simple. They don't know about patterns, fabric or personal style.
- Each item has one main colour.
- No automatic tagging from photos yet.

## Ideas for next steps

- Tag clothes from photos with an image-recognition model
- Add weather data instead of a cold checkbox
- Let users rate suggestions and learn their taste
