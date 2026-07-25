"""
Run once to populate the style_tips collection:
    python -m app.seed_tips

All tips are framed around style choices (cuts, layering, proportion,
color), never around body weight or size. Users pick a 'goal' themselves;
nothing here is inferred from a photo.
"""

from .mongo import tips_collection

TIPS = [
    # -- structure: sharper, more tailored silhouette --
    {"goal": "structure", "title": "Structured shoulders",
     "body": "A blazer or jacket with a defined shoulder line adds crisp structure to any outfit, casual or formal."},
    {"goal": "structure", "title": "Tuck it in",
     "body": "A half-tuck or full tuck creates a clean waistline and makes the whole outfit read as more intentional."},
    {"goal": "structure", "title": "Crisp fabrics",
     "body": "Cotton poplin, denim, and structured knits hold their shape better than soft jersey -- great for a put-together look."},

    # -- balance: even proportions top to bottom --
    {"goal": "balance", "title": "Match your proportions",
     "body": "If your top is fitted, balance it with a relaxed bottom (or vice versa) -- fitted-fitted or loose-loose can read as one shapeless block."},
    {"goal": "balance", "title": "Belt at the waist",
     "body": "A belt (even a thin one) visually splits an outfit into top and bottom halves, which reads as balanced and deliberate."},
    {"goal": "balance", "title": "Consistent color temperature",
     "body": "Keeping warm tones with warm tones (or cool with cool) makes an outfit feel like it belongs together."},

    # -- elongate: lengthen the line of an outfit --
    {"goal": "elongate", "title": "Monochrome or tonal dressing",
     "body": "Wearing similar shades top to bottom removes visual breaks, which reads as one long, elongated line."},
    {"goal": "elongate", "title": "Vertical details",
     "body": "Vertical stripes, a long open cardigan, or a single column of buttons all draw the eye up and down rather than side to side."},
    {"goal": "elongate", "title": "Match shoes to trousers",
     "body": "Shoes close in color to your trousers extend the leg line visually instead of cutting it off at the ankle."},

    # -- relaxed: comfortable, easy, low-effort looks --
    {"goal": "relaxed", "title": "Soft, breathable fabrics",
     "body": "Jersey, linen, and brushed cotton move with you and look intentionally relaxed rather than sloppy."},
    {"goal": "relaxed", "title": "One statement piece",
     "body": "In an otherwise simple outfit, one interesting piece (a jacket, a bag, a print) keeps it from looking too plain."},
    {"goal": "relaxed", "title": "Layer, don't bulk",
     "body": "Two thin layers (t-shirt + open shirt, or tee + light cardigan) look more considered than one bulky piece."},
]


def seed():
    tips_collection.delete_many({})
    tips_collection.insert_many(TIPS)
    print(f"Seeded {len(TIPS)} style tips.")


if __name__ == "__main__":
    seed()
