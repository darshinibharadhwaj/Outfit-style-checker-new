"""
Rule-based outfit advice.

Everything here is a plain lookup or rule, so every suggestion can be traced
back to a line of code. The skin tone, occasion and style goal are always
chosen by the user from a menu -- nothing is inferred from a photo of the
person.
"""

from .color_utils import ColorResult, color_name

WARM = {"red", "orange", "mustard", "yellow", "maroon", "brown", "olive", "beige", "pink"}
DARK = {"black", "navy", "charcoal", "dark green", "maroon", "brown", "purple"}

# "goes well with" table, used for both tops and bottoms
GOES_WITH: dict[str, list[str]] = {
    "black":      ["white", "grey", "red", "beige", "blue jeans"],
    "white":      ["navy", "black", "blue jeans", "olive", "grey"],
    "grey":       ["black", "navy", "white", "maroon", "blue jeans"],
    "light grey": ["navy", "black", "blue jeans", "maroon", "white"],
    "charcoal":   ["white", "light grey", "beige", "sky blue", "blue jeans"],
    "navy":       ["white", "beige", "light grey", "sky blue", "mustard"],
    "beige":      ["navy", "brown", "olive", "white", "blue jeans"],
    "brown":      ["beige", "white", "olive", "navy", "blue jeans"],
    "red":        ["black", "navy", "white", "beige", "blue jeans"],
    "maroon":     ["beige", "grey", "navy", "white", "blue jeans"],
    "orange":     ["navy", "white", "beige", "blue jeans", "black"],
    "mustard":    ["navy", "black", "white", "blue jeans", "olive"],
    "yellow":     ["navy", "white", "blue jeans", "grey", "black"],
    "olive":      ["beige", "white", "black", "navy", "blue jeans"],
    "green":      ["white", "beige", "navy", "black", "blue jeans"],
    "dark green": ["beige", "white", "grey", "black", "blue jeans"],
    "teal":       ["white", "beige", "grey", "navy", "black"],
    "aqua":       ["white", "navy", "grey", "beige", "blue jeans"],
    "blue":       ["white", "beige", "grey", "black", "brown"],
    "sky blue":   ["navy", "beige", "white", "grey", "brown"],
    "purple":     ["white", "grey", "black", "beige", "blue jeans"],
    "pink":       ["navy", "grey", "white", "blue jeans", "beige"],
    "magenta":    ["black", "grey", "white", "navy", "blue jeans"],
}

# Colors that usually look good / can blend in near the face, per skin tone
# (the user picks the skin tone). These are general style guides only.
SKIN_GOOD: dict[str, set[str]] = {
    "fair":     {"navy", "maroon", "teal", "dark green", "purple", "blue", "red", "magenta"},
    "wheatish": {"mustard", "olive", "maroon", "teal", "dark green", "white", "blue", "orange", "red"},
    "medium":   {"white", "olive", "teal", "red", "blue", "mustard", "green", "pink", "purple"},
    "dusky":    {"white", "sky blue", "blue", "red", "yellow", "mustard", "teal", "pink", "magenta", "orange"},
    "deep":     {"white", "yellow", "blue", "sky blue", "red", "orange", "magenta", "pink", "green", "teal", "mustard"},
}
SKIN_CAREFUL: dict[str, set[str]] = {
    "fair":     {"beige", "light grey", "yellow"},
    "wheatish": {"beige", "brown", "light grey"},
    "medium":   {"beige", "grey", "brown"},
    "dusky":    {"brown", "charcoal", "grey"},
    "deep":     {"black", "charcoal", "brown", "navy"},
}
SKIN_LABEL = {
    "fair": "fair", "wheatish": "wheatish", "medium": "medium brown",
    "dusky": "dusky", "deep": "deep",
}

SHOES_BY_OCCASION = {
    "casual": "White sneakers go with almost everything.",
    "office": "Plain formal shoes (black or brown) look neat.",
    "formal": "Polished leather shoes look best.",
    "evening": "Clean loafers or simple sneakers look smart.",
    "festival": "Traditional footwear like kolhapuri chappals or juttis suits a festival look.",
}


def verdict_for(score: float) -> str:
    if score >= 0.70:
        return "good"
    if score >= 0.50:
        return "ok"
    return "change"


def _list_text(items: list[str]) -> str:
    if len(items) <= 1:
        return "".join(items)
    return ", ".join(items[:-1]) + " or " + items[-1]


def summary_sentence(top: str, bottom: str, verdict: str) -> str:
    if verdict == "good":
        return f"Your {top} top and {bottom} bottom look good together."
    if verdict == "ok":
        return f"Your {top} top and {bottom} bottom are okay together. Small changes can make it better."
    return f"Your {top} top and {bottom} bottom may not match well. See the ideas below."


def alternatives(top: str, bottom: str, verdict: str) -> list[str]:
    bottoms = [c for c in GOES_WITH.get(top, []) if c != bottom and c != top][:4]
    tops = [c for c in GOES_WITH.get(bottom, []) if c != top and c != bottom][:4]
    if verdict == "good":
        return [f"Your {top} top also goes well with: {_list_text(bottoms)}."] if bottoms else []
    out = []
    if bottoms:
        out.append(f"To keep your {top} top, try these bottoms: {_list_text(bottoms)}.")
    if tops:
        out.append(f"To keep your {bottom} bottom, try these tops: {_list_text(tops)}.")
    return out


def skin_advice(top: str, skin_tone: str) -> list[str]:
    label = SKIN_LABEL.get(skin_tone, "medium brown")
    good = SKIN_GOOD.get(skin_tone, set())
    careful = SKIN_CAREFUL.get(skin_tone, set())
    if top in good:
        line = f"{top.capitalize()} is a great colour near the face for {label} skin. It makes your face stand out."
    elif top in careful:
        line = (
            f"{top.capitalize()} can look flat near the face on {label} skin. "
            "A brighter scarf, collar, glasses or earrings will lift it."
        )
    else:
        line = f"{top.capitalize()} works fine for {label} skin."
    return [line, "These are general style guides. If you like how a colour looks on you, wear it."]


def accessories(top: str, bottom: str, occasion: str) -> list[str]:
    warm_count = sum(1 for c in (top, bottom) if c in WARM)
    if warm_count == 2:
        metal, strap = "gold-tone", "a brown leather strap"
    elif warm_count == 0:
        metal, strap = "silver-tone", "a black or dark strap"
    else:
        metal, strap = "either gold-tone or silver-tone", "a brown or black strap"

    items = [f"Choose {metal} jewellery, chain or watch so everything matches."]
    if occasion in ("office", "formal"):
        items += [
            f"Wear a simple watch with {strap}.",
            "Keep your belt the same colour as your shoes.",
            "Carry a plain bag. Fewer accessories look more professional.",
        ]
    elif occasion == "evening":
        items += [
            "Pick one statement piece (a watch, a chain or a stole) and keep the rest simple.",
            "Keep your belt the same colour as your shoes.",
        ]
    elif occasion == "festival":
        items += [
            "Add one festive piece such as a stole or traditional jewellery.",
            "Keep the rest simple so the festive piece stands out.",
        ]
    else:
        items += [
            f"A simple watch with {strap} suits a casual look.",
            "A small sling bag or backpack in a plain colour is enough.",
        ]
    return items


def footwear(bottom: str, occasion: str) -> list[str]:
    out = [SHOES_BY_OCCASION.get(occasion, SHOES_BY_OCCASION["casual"])]
    if occasion in ("office", "formal"):
        if bottom in ("black", "charcoal", "grey", "navy", "light grey"):
            out.append("With your bottom colour, black shoes are the safest choice.")
        else:
            out.append("With your bottom colour, brown shoes look good. Black also works.")
    elif occasion != "festival":
        if bottom in DARK:
            out.append("Your bottom is dark, so white or light sneakers will stand out nicely.")
        elif bottom in ("white", "beige", "light grey"):
            out.append("Your bottom is light, so brown, tan or white shoes look good.")
        else:
            out.append("White sneakers or brown shoes both go with your bottom.")
    out.append("Keep shoes clean. Clean shoes improve any outfit.")
    return out


def build_advice(
    top: ColorResult,
    bottom: ColorResult,
    harmony: dict,
    skin_tone: str,
    occasion: str,
) -> dict:
    top_name = color_name(top.hsv)
    bottom_name = color_name(bottom.hsv)
    verdict = verdict_for(harmony["score"])
    return {
        "top_name": top_name,
        "bottom_name": bottom_name,
        "verdict": verdict,
        "summary": summary_sentence(top_name, bottom_name, verdict),
        "skin_advice": skin_advice(top_name, skin_tone),
        "alternatives": alternatives(top_name, bottom_name, verdict),
        "accessories": accessories(top_name, bottom_name, occasion),
        "footwear": footwear(bottom_name, occasion),
    }
