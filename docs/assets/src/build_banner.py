"""
Generate the project banner: SVG sources plus rasterised JPGs.

Run from the repository root:

    python docs/assets/src/build_banner.py

The banner is thematic rather than informational: an isometric grid fabric with
energised traces linking smart-grid elements - a neural network, a smart meter, a
transmission tower, a wind turbine, a solar array and an AI processor - behind the
project title.

Glow is drawn as three stacked strokes of decreasing width rather than an SVG
filter, because filters are dropped by several renderers and by most slide
software; stacked strokes render everywhere.

Rasterising to JPG needs svglib, reportlab and Pillow. They are development-only
tools: if they are missing the script still writes the SVGs and says so.
"""

from __future__ import annotations

import math
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

OUT_DIR = Path(__file__).resolve().parent.parent
SRC_DIR = Path(__file__).resolve().parent

WIDTH, HEIGHT = 1280, 360
FONT = "Segoe UI, Helvetica, Arial, sans-serif"

DARK: Dict[str, str] = {
    "bg_top": "#0b2130",
    "bg_bottom": "#061219",
    "bg_mid": "#081a24",
    "lattice": "#14374a",
    "cyan": "#22d3ee",
    "green": "#4ade80",
    "orange": "#fb923c",
    "icon": "#7dd3fc",
    "icon_soft": "#38bdf8",
    "title": "#ffffff",
    "subtitle": "#9fc6d8",
    "scrim": "#061219",
    "chip_text": "#22d3ee",
}

LIGHT: Dict[str, str] = {
    "bg_top": "#eaf2f6",
    "bg_bottom": "#dbe8ef",
    "bg_mid": "#e3edf2",
    "lattice": "#bed4e0",
    "cyan": "#0891b2",
    "green": "#15803d",
    "orange": "#ea580c",
    "icon": "#155e75",
    "icon_soft": "#0e7490",
    "title": "#08202b",
    "subtitle": "#37606f",
    "scrim": "#eaf2f6",
    "chip_text": "#0891b2",
}

THEMES = {"dark": DARK, "light": LIGHT}

ISO = math.tan(math.radians(30))  # isometric slope


# --------------------------------------------------------------------------
# primitives
# --------------------------------------------------------------------------
def _hex_to_rgb(value: str) -> Tuple[int, int, int]:
    value = value.lstrip("#")
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))  # type: ignore[return-value]


def blend(foreground: str, background: str, alpha: float) -> str:
    """
    Mix two colours and return an opaque result.

    Glow and hairlines are drawn in pre-blended opaque colours rather than with
    stroke-opacity. Browsers honour transparency, but several rasterisers ignore
    both `opacity` and `stroke-opacity`, which collapses stacked glow layers into
    one solid bar. Blending here keeps the SVG and the exported JPG identical.
    """
    fr, fg, fb = _hex_to_rgb(foreground)
    br, bg, bb = _hex_to_rgb(background)
    return "#%02x%02x%02x" % (
        round(fr * alpha + br * (1 - alpha)),
        round(fg * alpha + bg * (1 - alpha)),
        round(fb * alpha + bb * (1 - alpha)),
    )


def vertical_gradient(top: str, bottom: str, bands: int = 60) -> List[str]:
    """
    A vertical gradient built from interpolated bands.

    PT-BR / note: an SVG <linearGradient> would be tidier, but several
    rasterisers mishandle gradient fills. Bands render identically everywhere,
    and at this count the seams are invisible.
    """
    r1, g1, b1 = _hex_to_rgb(top)
    r2, g2, b2 = _hex_to_rgb(bottom)
    height = HEIGHT / bands
    out: List[str] = []
    for i in range(bands):
        f = i / (bands - 1)
        colour = "#%02x%02x%02x" % (
            round(r1 + (r2 - r1) * f),
            round(g1 + (g2 - g1) * f),
            round(b1 + (b2 - b1) * f),
        )
        out.append(
            f'<rect x="0" y="{i * height:.2f}" width="{WIDTH}" '
            f'height="{height + 1:.2f}" fill="{colour}"/>'
        )
    return out


def lattice(t: Dict[str, str], spacing: int = 46) -> List[str]:
    """The isometric diamond grid running behind everything."""
    out: List[str] = []
    reach = int(WIDTH * ISO) + HEIGHT + spacing * 2
    for offset in range(-reach, reach, spacing):
        out.append(
            f'<line x1="0" y1="{offset}" x2="{WIDTH}" y2="{offset + WIDTH * ISO:.0f}" '
            f'stroke="{t["lattice"]}" stroke-width="1" stroke-opacity="0.5"/>'
        )
        out.append(
            f'<line x1="0" y1="{offset}" x2="{WIDTH}" y2="{offset - WIDTH * ISO:.0f}" '
            f'stroke="{t["lattice"]}" stroke-width="1" stroke-opacity="0.5"/>'
        )
    return out


def glow_path(points: Sequence[Tuple[float, float]], colour: str, t: Dict[str, str],
              width: float = 2.6, nodes: bool = True) -> List[str]:
    """A trace: a bright core over two pre-blended halo layers."""
    pts = " ".join(f"{x},{y}" for x, y in points)
    bg = t["bg_mid"]
    out = [
        f'<polyline points="{pts}" fill="none" stroke="{blend(colour, bg, 0.14)}" '
        f'stroke-width="{width * 3.6:.1f}" stroke-linejoin="round" stroke-linecap="round"/>',
        f'<polyline points="{pts}" fill="none" stroke="{blend(colour, bg, 0.34)}" '
        f'stroke-width="{width * 2.0:.1f}" stroke-linejoin="round" stroke-linecap="round"/>',
        f'<polyline points="{pts}" fill="none" stroke="{colour}" '
        f'stroke-width="{width}" stroke-linejoin="round" stroke-linecap="round"/>',
    ]
    if nodes:
        for x, y in points:
            out.append(f'<circle cx="{x}" cy="{y}" r="{width * 1.9:.1f}" '
                       f'fill="{blend(colour, bg, 0.26)}"/>')
            out.append(f'<circle cx="{x}" cy="{y}" r="{width * 0.85:.1f}" fill="{colour}"/>')
    return out


def stroke(d: str, colour: str, w: float = 2.0, cap: str = "round") -> str:
    return (f'<path d="{d}" fill="none" stroke="{colour}" stroke-width="{w}" '
            f'stroke-linecap="{cap}" stroke-linejoin="round"/>')


def ring(cx: float, cy: float, r: float, colour: str, bg: str, w: float = 2.0) -> List[str]:
    return [
        f'<circle cx="{cx}" cy="{cy}" r="{r + 5}" fill="none" '
        f'stroke="{blend(colour, bg, 0.11)}" stroke-width="{w * 3.4:.1f}"/>',
        f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{colour}" '
        f'stroke-width="{w}"/>',
    ]


# --------------------------------------------------------------------------
# icons
# --------------------------------------------------------------------------
def neural_network(cx: float, cy: float, t: Dict[str, str], s: float = 1.0) -> List[str]:
    """A 3-4-3 network: the AI half of the subject."""
    c = t["icon"]
    layers = [
        [(cx - 42 * s, cy - 26 * s), (cx - 42 * s, cy), (cx - 42 * s, cy + 26 * s)],
        [(cx, cy - 39 * s), (cx, cy - 13 * s), (cx, cy + 13 * s), (cx, cy + 39 * s)],
        [(cx + 42 * s, cy - 26 * s), (cx + 42 * s, cy), (cx + 42 * s, cy + 26 * s)],
    ]
    out: List[str] = []
    for left, right in ((layers[0], layers[1]), (layers[1], layers[2])):
        for x1, y1 in left:
            for x2, y2 in right:
                out.append(f'<line x1="{x1:.0f}" y1="{y1:.0f}" x2="{x2:.0f}" y2="{y2:.0f}" '
                           f'stroke="{blend(c, t["bg_mid"], 0.42)}" stroke-width="1"/>')
    for layer in layers:
        for x, y in layer:
            out.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{5 * s:.1f}" '
                       f'fill="{t["bg_bottom"]}" stroke="{c}" stroke-width="1.8"/>')
    return out


def smart_meter(cx: float, cy: float, t: Dict[str, str], r: float = 34) -> List[str]:
    """A metering point, drawn inside a ring as in the reference style."""
    c = t["icon"]
    out = ring(cx, cy, r, c, t["bg_mid"])
    out.append(f'<rect x="{cx - 15}" y="{cy - 17}" width="30" height="34" rx="5" '
               f'fill="none" stroke="{c}" stroke-width="1.8"/>')
    out.append(f'<rect x="{cx - 10}" y="{cy - 12}" width="20" height="11" rx="2" '
               f'fill="none" stroke="{c}" stroke-width="1.4"/>')
    for i in range(3):
        out.append(f'<line x1="{cx - 8}" y1="{cy + 4 + i * 5}" x2="{cx + 8}" '
                   f'y2="{cy + 4 + i * 5}" stroke="{blend(c, t["bg_mid"], 0.78)}" '
                   f'stroke-width="1.2"/>')
    return out


def pylon(cx: float, cy: float, t: Dict[str, str], s: float = 1.0) -> List[str]:
    """A transmission tower: the grid half of the subject."""
    c = t["icon"]
    h, half = 74 * s, 26 * s
    top, base = cy - h / 2, cy + h / 2
    out = [
        stroke(f"M {cx - half} {base} L {cx - 8 * s} {top} L {cx + 8 * s} {top} "
               f"L {cx + half} {base}", c, 2.0),
        stroke(f"M {cx - half * 0.72} {base - h * 0.28} L {cx + half * 0.72} "
               f"{base - h * 0.28}", c, 1.4),
        stroke(f"M {cx - half * 0.46} {base - h * 0.56} L {cx + half * 0.46} "
               f"{base - h * 0.56}", c, 1.4),
    ]
    # lattice bracing
    out.append(stroke(f"M {cx - half} {base} L {cx + half * 0.46} {base - h * 0.56}", c, 1.0))
    out.append(stroke(f"M {cx + half} {base} L {cx - half * 0.46} {base - h * 0.56}", c, 1.0))
    # cross-arms
    for y, arm in ((top + 10 * s, 30 * s), (top + 26 * s, 22 * s)):
        out.append(stroke(f"M {cx - arm} {y} L {cx + arm} {y}", c, 1.8))
        for side in (-1, 1):
            out.append(f'<circle cx="{cx + side * arm:.0f}" cy="{y:.0f}" r="{3 * s:.1f}" '
                       f'fill="{c}"/>')
    return out


def turbine(cx: float, cy: float, t: Dict[str, str], s: float = 1.0) -> List[str]:
    """A wind turbine: generation at the edge of the network."""
    c = t["icon"]
    hub_y = cy - 22 * s
    out = [
        stroke(f"M {cx} {cy + 40 * s} L {cx} {hub_y}", c, 2.2),
        stroke(f"M {cx - 12 * s} {cy + 40 * s} L {cx + 12 * s} {cy + 40 * s}", c, 2.0),
    ]
    for angle in (270, 30, 150):
        rad = math.radians(angle)
        tip = (cx + 36 * s * math.cos(rad), hub_y + 36 * s * math.sin(rad))
        # Control point offset perpendicular to the blade gives it a taper
        # instead of the kink a naive rotation produces.
        mid = (cx + 20 * s * math.cos(rad), hub_y + 20 * s * math.sin(rad))
        perp = rad + math.pi / 2
        ctrl = (mid[0] + 7 * s * math.cos(perp), mid[1] + 7 * s * math.sin(perp))
        out.append(stroke(f"M {cx} {hub_y} Q {ctrl[0]:.0f} {ctrl[1]:.0f} "
                          f"{tip[0]:.0f} {tip[1]:.0f}", c, 2.2))
    out.append(f'<circle cx="{cx}" cy="{hub_y}" r="{4 * s:.1f}" fill="{c}"/>')
    return out


def solar_array(cx: float, cy: float, t: Dict[str, str], s: float = 1.0) -> List[str]:
    """An isometric photovoltaic array."""
    c = t["icon"]
    w, d = 46 * s, 22 * s
    top = (cx, cy - d)
    right = (cx + w, cy - d + w * ISO)
    bottom = (cx, cy + d + 2 * w * ISO - w * ISO)
    left = (cx - w, cy - d + w * ISO)
    out = [stroke(f"M {top[0]:.0f} {top[1]:.0f} L {right[0]:.0f} {right[1]:.0f} "
                  f"L {bottom[0]:.0f} {bottom[1]:.0f} L {left[0]:.0f} {left[1]:.0f} Z", c, 2.0)]
    for i in (1, 2):
        f = i / 3
        out.append(stroke(
            f"M {top[0] + (left[0] - top[0]) * f:.0f} {top[1] + (left[1] - top[1]) * f:.0f} "
            f"L {right[0] + (bottom[0] - right[0]) * f:.0f} "
            f"{right[1] + (bottom[1] - right[1]) * f:.0f}", c, 1.1))
        out.append(stroke(
            f"M {top[0] + (right[0] - top[0]) * f:.0f} {top[1] + (right[1] - top[1]) * f:.0f} "
            f"L {left[0] + (bottom[0] - left[0]) * f:.0f} "
            f"{left[1] + (bottom[1] - left[1]) * f:.0f}", c, 1.1))
    out.append(stroke(f"M {bottom[0]:.0f} {bottom[1]:.0f} L {bottom[0]:.0f} "
                      f"{bottom[1] + 14 * s:.0f}", c, 1.8))
    return out


def ai_chip(cx: float, cy: float, t: Dict[str, str], s: float = 1.0) -> List[str]:
    """The processor at the centre of the reference image."""
    c = t["icon"]
    half = 30 * s
    out = [
        f'<rect x="{cx - half - 6}" y="{cy - half - 6}" width="{2 * half + 12}" '
        f'height="{2 * half + 12}" rx="12" fill="none" '
        f'stroke="{blend(c, t["bg_mid"], 0.11)}" stroke-width="6"/>',
        f'<rect x="{cx - half}" y="{cy - half}" width="{2 * half}" height="{2 * half}" '
        f'rx="9" fill="{t["bg_bottom"]}" stroke="{c}" stroke-width="2.2"/>',
    ]
    for i in (-1, 0, 1):
        off = i * 15 * s
        out.append(stroke(f"M {cx + off} {cy - half} L {cx + off} {cy - half - 13 * s}", c, 1.8))
        out.append(stroke(f"M {cx + off} {cy + half} L {cx + off} {cy + half + 13 * s}", c, 1.8))
        out.append(stroke(f"M {cx - half} {cy + off} L {cx - half - 13 * s} {cy + off}", c, 1.8))
        out.append(stroke(f"M {cx + half} {cy + off} L {cx + half + 13 * s} {cy + off}", c, 1.8))
    out.append(f'<text x="{cx}" y="{cy + 7 * s:.0f}" font-size="{21 * s:.0f}" '
               f'font-weight="700" fill="{t["chip_text"]}" text-anchor="middle" '
               f'font-family="{FONT}">AI</text>')
    return out


# --------------------------------------------------------------------------
def build(t: Dict[str, str]) -> str:
    body: List[str] = []

    body += vertical_gradient(t["bg_top"], t["bg_bottom"])
    body += lattice(t)

    # Energised traces. They run behind the icons, on isometric bearings, and
    # are kept clear of the title scrim.
    body += glow_path([(26, 172), (146, 102), (296, 102), (386, 50)], t["cyan"], t)
    body += glow_path([(54, 306), (172, 238), (330, 238), (448, 306)], t["green"], t)
    body += glow_path([(190, 338), (306, 270), (462, 270)], t["orange"], t, 2.2)
    body += glow_path([(852, 52), (966, 52), (1086, 122), (1256, 122)], t["cyan"], t)
    body += glow_path([(806, 336), (924, 268), (1064, 268), (1182, 336)], t["green"], t)
    body += glow_path([(1090, 226), (1090, 268)], t["orange"], t, 2.2)

    # icons
    body += neural_network(128, 152, t)
    body += solar_array(148, 292, t)
    body += pylon(316, 116, t)
    body += smart_meter(330, 288, t)
    body += smart_meter(944, 74, t, 28)
    body += ai_chip(1090, 158, t)
    body += turbine(1204, 268, t)

    # Title. No scrim panel: the traces are routed clear of this band, so the
    # text sits directly on the lattice as in a poster.
    body.append(f'<text x="640" y="172" font-size="43" font-weight="700" '
                f'fill="{t["title"]}" text-anchor="middle" font-family="{FONT}">'
                f'Artificial Intelligence</text>')
    body.append(f'<text x="640" y="218" font-size="43" font-weight="700" '
                f'fill="{t["title"]}" text-anchor="middle" font-family="{FONT}">'
                f'for Smartgrid Networks</text>')

    return "\n".join([
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {HEIGHT}" '
        f'width="{WIDTH}" height="{HEIGHT}" font-family="{FONT}">',
        "  <title>ai-for-smartgrids</title>",
        "  <desc>Artificial Intelligence for Smartgrid Networks. An isometric grid "
        "fabric with energised traces linking a neural network, a solar array, a "
        "transmission tower, smart meters, a wind turbine and an AI processor.</desc>",
        *[f"  {line}" for line in body],
        "</svg>",
        "",
    ])


def rasterise(svg_path: Path, jpg_path: Path, scale: float = 2.0) -> bool:
    """Render an SVG to JPG. Returns False when the tools are unavailable."""
    try:
        from svglib.svglib import svg2rlg
        from reportlab.graphics import renderPM
        from PIL import Image
    except ImportError:
        return False

    drawing = svg2rlg(str(svg_path))
    png_path = jpg_path.with_suffix(".png")
    renderPM.drawToFile(drawing, str(png_path), fmt="PNG", dpi=int(72 * scale))
    with Image.open(png_path) as image:
        image.convert("RGB").save(jpg_path, "JPEG", quality=92, optimize=True,
                                  progressive=True)
    png_path.unlink()
    return True


def main() -> None:
    rastered = True
    for theme_name, palette in THEMES.items():
        svg_path = OUT_DIR / f"banner-{theme_name}.svg"
        svg_path.write_text(build(palette), encoding="utf-8")
        print(f"wrote {svg_path.relative_to(OUT_DIR.parent.parent)}")

        jpg_path = OUT_DIR / f"banner-{theme_name}.jpg"
        if rasterise(svg_path, jpg_path):
            print(f"wrote {jpg_path.relative_to(OUT_DIR.parent.parent)}")
        else:
            rastered = False

    if not rastered:
        print("\nJPG export skipped: install svglib, reportlab and Pillow to enable it.")


if __name__ == "__main__":
    main()
