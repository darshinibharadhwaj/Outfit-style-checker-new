"""
Rule-based color-coordination engine.

This deliberately does NOT attempt garment detection, body analysis, or any
deep-learning classification of the person in the photo. It extracts the
dominant colors from two user-cropped regions (top garment / bottom garment)
and applies well-established color-theory rules to judge coordination.
"""

import base64
import io
import colorsys
from dataclasses import dataclass

import numpy as np
from PIL import Image


@dataclass
class ColorResult:
    hex: str
    rgb: tuple[int, int, int]
    hsv: tuple[float, float, float]


def decode_base64_image(data_url: str) -> Image.Image:
    if "," in data_url:
        data_url = data_url.split(",", 1)[1]
    raw = base64.b64decode(data_url)
    return Image.open(io.BytesIO(raw)).convert("RGB")


def _dominant_color(image: Image.Image, num_colors: int = 5) -> tuple[int, int, int]:
    """Quantize the region to a small palette and return the most common color,
    ignoring near-white/near-black pixels that are usually background or shadow."""
    small = image.resize((60, 60))
    quantized = small.quantize(colors=num_colors, method=Image.MEDIANCUT)
    palette = quantized.getpalette()
    color_counts = quantized.getcolors()  # list of (count, palette_index)

    color_counts = sorted(color_counts, key=lambda c: c[0], reverse=True)

    for count, idx in color_counts:
        r, g, b = palette[idx * 3: idx * 3 + 3]
        brightness = (r + g + b) / 3
        # skip near-white / near-black -- usually background, not clothing
        if 25 < brightness < 235:
            return (r, g, b)

    # fall back to the single most common color if everything was filtered
    count, idx = color_counts[0]
    return tuple(palette[idx * 3: idx * 3 + 3])


def analyze_region(image: Image.Image, box: tuple[float, float, float, float]) -> ColorResult:
    """box is (left, top, right, bottom) as fractions of image width/height, 0-1."""
    w, h = image.size
    left, top, right, bottom = box
    crop = image.crop((int(left * w), int(top * h), int(right * w), int(bottom * h)))
    if crop.size[0] < 2 or crop.size[1] < 2:
        raise ValueError("The selected region is too small")
    r, g, b = _dominant_color(crop)
    hsv = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
    return ColorResult(hex=f"#{r:02x}{g:02x}{b:02x}", rgb=(r, g, b), hsv=hsv)


NEUTRALS_SATURATION_THRESHOLD = 0.15
NEUTRAL_NAMES = {"black", "white", "grey", "light grey", "charcoal", "navy", "beige"}


def color_name(hsv: tuple[float, float, float]) -> str:
    """Turn an HSV color into a simple everyday name (red, navy, beige ...).

    hsv = (hue 0-1, saturation 0-1, value 0-1), as returned by colorsys.
    """
    h, s, v = hsv
    h = h * 360

    if v < 0.18:
        return "black"
    if s < 0.12:  # no real color -> a shade of white/grey
        if v > 0.88:
            return "white"
        if v > 0.62:
            return "light grey"
        if v > 0.38:
            return "grey"
        return "charcoal"
    if 200 <= h < 260 and v < 0.42:
        return "navy"
    if 15 <= h < 55 and s < 0.32 and v > 0.62:
        return "beige"
    if 10 <= h < 50 and v < 0.58:
        return "brown"
    if h < 15 or h >= 345:
        if v < 0.50:
            return "maroon"
        if s < 0.45 and v > 0.78:
            return "pink"
        return "red"
    if h < 40:
        return "orange"
    if h < 70:
        if v < 0.60:
            return "olive"
        return "mustard" if (h < 55 and s > 0.55) else "yellow"
    if h < 165:
        if h < 100 and v < 0.62:
            return "olive"
        return "dark green" if v < 0.40 else "green"
    if h < 200:
        return "teal" if v < 0.65 else "aqua"
    if h < 260:
        if s < 0.5 and v > 0.75:
            return "sky blue"
        return "blue"
    if h < 290:
        return "purple"
    if s < 0.55 and v > 0.75:
        return "pink"
    return "magenta"


def _is_neutral(hsv: tuple[float, float, float]) -> bool:
    _, s, v = hsv
    if s < NEUTRALS_SATURATION_THRESHOLD or v < 0.12 or v > 0.95:
        return True
    return color_name(hsv) in NEUTRAL_NAMES


def score_harmony(top: ColorResult, bottom: ColorResult) -> dict:
    """
    Returns a harmony verdict using standard color-wheel relationships:
    - either color being a neutral (black/white/grey/navy/beige) -> always safe
    - hue difference small (<40deg)  -> analogous / tonal, harmonious
    - hue difference ~150-210deg     -> complementary, bold contrast (works well)
    - hue difference ~60-140deg or 220-330deg -> can clash, flagged for a second look
    """
    if _is_neutral(top.hsv) or _is_neutral(bottom.hsv):
        return {
            "label": "Safe neutral pairing",
            "score": 0.85,
            "detail": "One of these tones is a neutral, so it pairs easily with almost anything.",
        }

    hue_top = top.hsv[0] * 360
    hue_bottom = bottom.hsv[0] * 360
    diff = abs(hue_top - hue_bottom)
    diff = min(diff, 360 - diff)

    if diff < 40:
        return {
            "label": "Harmonious (tonal)",
            "score": 0.8,
            "detail": "These colors sit close together on the color wheel, giving a calm, coordinated look.",
        }
    if 150 <= diff <= 210:
        return {
            "label": "Bold complementary contrast",
            "score": 0.75,
            "detail": "These are near-opposite hues -- a classic, energetic contrast that reads as intentional.",
        }
    if diff < 90:
        return {
            "label": "Slightly clashing",
            "score": 0.45,
            "detail": "These hues are close enough to compete rather than complement. Consider adjusting one shade lighter/darker or adding a neutral layer.",
        }
    return {
        "label": "High contrast - can go either way",
        "score": 0.55,
        "detail": "This is a less common pairing. It can look striking or busy depending on fit and accessories -- a neutral shoe or bag can help ground it.",
    }
