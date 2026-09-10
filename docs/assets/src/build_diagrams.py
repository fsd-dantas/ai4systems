"""
Generate every figure in docs/assets/, in a light and a dark variant.

Run from the repository root:

    python docs/assets/src/build_diagrams.py

One themed source produces both variants of each figure, so a wording change is
made once rather than ten times, and the two variants can never drift apart.

Arrowheads are explicit polygons rather than SVG markers: several renderers and
most slide software silently drop marker elements, which would leave the figures
with headless lines.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List

OUT_DIR = Path(__file__).resolve().parent.parent

# --------------------------------------------------------------------------
# palettes
# --------------------------------------------------------------------------
LIGHT: Dict[str, str] = {
    "bg": "#fbfaf7",
    "panel": "#ffffff",
    "ink": "#1f2933",
    "muted": "#52606d",
    "faint": "#8a94a0",
    "border": "#c9c2b8",
    "rule": "#b6b0a6",
    "neutral_fill": "#eef1f4",
    "neutral_border": "#c3ccd5",
    "header_text": "#ffffff",
    "blue": "#0072B2", "blue_fill": "#e8f2f8", "blue_text": "#0b5c8a",
    "green": "#009E73", "green_fill": "#e6f5f0", "green_text": "#046c50",
    "amber": "#E69F00", "amber_fill": "#fdf1dc", "amber_text": "#8a6100",
    "red": "#D55E00", "red_fill": "#fdecea", "red_text": "#a8442a",
    "purple": "#8c6db5", "purple_fill": "#f3eefa", "purple_text": "#5b3f86",
    "pink": "#CC79A7", "pink_fill": "#faeef5", "pink_text": "#a44a7f",
    "n_core": "#1b3a6b", "n_lte": "#3f7cac", "n_ap": "#c1666b",
    "n_rm": "#6b8f71", "n_saf": "#d4a373", "n_field": "#b23a48",
    "edge_radio": "#9a8c78", "edge_saf": "#d4a373",
}

DARK: Dict[str, str] = {
    "bg": "#0d1117",
    "panel": "#161b22",
    "ink": "#e6edf3",
    "muted": "#9daab7",
    "faint": "#788593",
    "border": "#30363d",
    "rule": "#3d444d",
    "neutral_fill": "#1c2430",
    "neutral_border": "#3a4552",
    "header_text": "#0d1117",
    "blue": "#58a6ff", "blue_fill": "#122238", "blue_text": "#8cc8ff",
    "green": "#4ec9a0", "green_fill": "#0f2a22", "green_text": "#7fe0c0",
    "amber": "#e3b341", "amber_fill": "#2e2410", "amber_text": "#f0cc72",
    "red": "#f2794a", "red_fill": "#33190f", "red_text": "#ffa07a",
    "purple": "#b39ddb", "purple_fill": "#221b30", "purple_text": "#cbb8e8",
    "pink": "#e79ac4", "pink_fill": "#2e1d27", "pink_text": "#f0b8d8",
    "n_core": "#7aa2d6", "n_lte": "#58a6ff", "n_ap": "#e8908f",
    "n_rm": "#7fc99a", "n_saf": "#e0b070", "n_field": "#ff7b72",
    "edge_radio": "#6b7280", "edge_saf": "#a8814f",
}

THEMES = {"light": LIGHT, "dark": DARK}

FONT = "Segoe UI, Helvetica, Arial, sans-serif"
MONO = "Consolas, SFMono-Regular, Menlo, monospace"


# --------------------------------------------------------------------------
# tiny SVG helpers
# --------------------------------------------------------------------------
def esc(text: str) -> str:
    return (
        text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    )


def txt(x, y, s, size=13, fill="ink", weight=None, anchor=None, mono=False,
        italic=False, t=None) -> str:
    parts = [f'<text x="{x}" y="{y}" font-size="{size}" fill="{t[fill]}"']
    if weight:
        parts.append(f'font-weight="{weight}"')
    if anchor:
        parts.append(f'text-anchor="{anchor}"')
    if mono:
        parts.append(f'font-family="{MONO}"')
    if italic:
        parts.append('font-style="italic"')
    return " ".join(parts) + f">{esc(s)}</text>"


def box(x, y, w, h, t, fill="panel", stroke="border", width=1.0, rx=8) -> str:
    return (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" '
        f'fill="{t[fill]}" stroke="{t[stroke]}" stroke-width="{width}"/>'
    )


def header_band(x, y, w, t, colour, label, rx=10, band_h=36) -> List[str]:
    """A rounded card header: filled band with the card title."""
    return [
        f'<path d="M {x + rx} {y} H {x + w - rx} A {rx} {rx} 0 0 1 {x + w} {y + rx} '
        f'V {y + band_h} H {x} V {y + rx} A {rx} {rx} 0 0 1 {x + rx} {y} Z" '
        f'fill="{t[colour]}"/>',
        txt(x + 18, y + 25, label, 15, "header_text", "700", t=t),
    ]


def line(x1, y1, x2, y2, t, colour="muted", width=2.0, dash=None) -> str:
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (
        f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{t[colour]}" '
        f'stroke-width="{width}"{d}/>'
    )


def arrow(x1, y1, x2, y2, t, colour="muted", width=2.0) -> List[str]:
    """A straight arrow whose head is a polygon (portable across renderers)."""
    import math

    angle = math.atan2(y2 - y1, x2 - x1)
    head = 11.0
    bx, by = x2 - head * math.cos(angle), y2 - head * math.sin(angle)
    wing = 5.5
    p1 = (bx - wing * math.sin(angle), by + wing * math.cos(angle))
    p2 = (bx + wing * math.sin(angle), by - wing * math.cos(angle))
    return [
        f'<line x1="{x1}" y1="{y1}" x2="{bx:.1f}" y2="{by:.1f}" '
        f'stroke="{t[colour]}" stroke-width="{width}"/>',
        f'<polygon points="{x2},{y2} {p1[0]:.1f},{p1[1]:.1f} {p2[0]:.1f},{p2[1]:.1f}" '
        f'fill="{t[colour]}"/>',
    ]


def document(width, height, title, desc, body: List[str], t) -> str:
    return "\n".join(
        [
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
            f'width="{width}" height="{height}" font-family="{FONT}">',
            f"  <title>{esc(title)}</title>",
            f"  <desc>{esc(desc)}</desc>",
            f'  <rect width="{width}" height="{height}" fill="{t["bg"]}"/>',
            *[f"  {line}" for line in body],
            "</svg>",
            "",
        ]
    )


# --------------------------------------------------------------------------
# 01 — integration
# --------------------------------------------------------------------------
def build_integration(t) -> str:
    b: List[str] = []
    b.append(txt(40, 46, "How the three systems connect", 23, "ink", "600", t=t))
    b.append(txt(40, 72, "One incident crosses all three. The arrows show what each "
                         "system hands to the next.", 14, "muted", t=t))

    # input. Kept short: the figure must also read where Segoe UI is unavailable
    # and a wider fallback font is substituted.
    b.append(box(40, 108, 260, 62, t, "neutral_fill", "neutral_border"))
    b.append(txt(170, 134, "telemetry", 14, "ink", "600", "middle", t=t))
    b.append(txt(170, 154, "RSSI, SNR, loss, RTT", 12, "muted", "middle", t=t))
    b += arrow(170, 172, 170, 204, t)

    cards = [
        (40, 320, "blue", "1 - EXPERT SYSTEM", [
            ("41 production rules, 5 layers", "ink"),
            ("forward and backward chaining", "muted"),
            ("certainty factors (MYCIN)", "muted"),
            ("explanation: why / how", "muted"),
        ], "diagnosis + action + authorisation", "blue_fill", "blue_text"),
        (440, 320, "green", "2 - STRIPS / GPS PLANNER", [
            ("initial state = the diagnosis", "ink"),
            ("18 STRIPS operators", "muted"),
            ("GPS means-ends + A* progression", "muted"),
            ("plan validation", "muted"),
        ], "ordered, validated plan", "green_fill", "green_text"),
        (840, 300, "amber", "3 - A* SEARCH", [
            ("f(n) = g(n) + h(n)", "ink"),
            ("admissible, consistent heuristic", "muted"),
            ("breadth-first, depth-first, uniform cost", "muted"),
            ("greedy - for comparison", "muted"),
        ], "exact path + optimal cost", "amber_fill", "amber_text"),
    ]
    for x, w, colour, title, rows, out, out_fill, out_text in cards:
        b.append(box(x, 208, w, 180, t, "panel", colour, 2, 10))
        b += header_band(x, 208, w, t, colour, title)
        for i, (label, tone) in enumerate(rows):
            b.append(txt(x + 18, 270 + i * 20, label, 13, tone, t=t))
        b.append(box(x + 18, 344, w - 36, 32, t, out_fill, colour, 1.0, 6))
        b.append(txt(x + w / 2, 365, out, 12.5, out_text, "600", "middle", t=t))

    # diagnosis hand-off
    b += arrow(364, 298, 436, 298, t, width=2.4)
    # The hand-off is named once, on the arrow. What it becomes is stated inside
    # the planner card, where there is room to say it without crowding the box.
    b.append(txt(400, 284, "diagnosis", 12, "ink", "600", "middle", t=t))

    # query / answer
    b += arrow(764, 282, 836, 282, t, "red", 2.4)
    b.append(txt(800, 258, "alternative", 11.5, "red", "600", "middle", t=t))
    b.append(txt(800, 271, "route?", 11.5, "red", "600", "middle", t=t))
    b += arrow(836, 326, 764, 326, t, "red", 2.4)
    b.append(txt(800, 346, "yes / no", 11.5, "red", "600", "middle", t=t))

    # reuse note
    b.append(f'<path d="M 600 392 L 600 428 L 990 428 L 990 392" '
             f'stroke="{t["purple"]}" stroke-width="2" stroke-dasharray="6 4" fill="none"/>')
    b.append(box(636, 412, 318, 32, t, "purple_fill", "purple", 1.0, 6))
    b.append(txt(795, 433, "the SAME astar() function, not a copy", 12.5,
                 "purple_text", "600", "middle", t=t))

    # shared domain
    b.append(box(40, 474, 1100, 80, t, "panel", "rule", 1.6, 10))
    b.append(txt(60, 500, "SHARED DOMAIN - synthetic communication backhaul",
                 14, "ink", "700", t=t))
    b.append(txt(60, 522, "Synthetic 30-node scenario in three sectors - fibre core - "
                          "900 MHz radio - store-and-forward chains - private LTE overlay",
                 12.5, "muted", t=t))
    b.append(txt(60, 541, "link cost = overhead(type) + distance / (speed(type) x quality)"
                          "     -     distances derived from the coordinates", 12.5, "muted", t=t))
    for x, y in ((200, 390), (600, 446), (990, 446)):
        b.append(line(x, 470, x, y, t, "rule", 1.4, "4 4"))

    return document(1180, 584, "Integration of the three systems",
                    "The expert system produces a diagnosis that becomes the planner's initial "
                    "state; the planner asks A* whether an alternative route exists; and the "
                    "progression planner reuses the same A* function that solves routing.", b, t)


# --------------------------------------------------------------------------
# 02 — expert system
# --------------------------------------------------------------------------
def build_expert(t) -> str:
    b: List[str] = []
    b.append(txt(40, 46, "Expert system - 41 rules in five layers", 23, "ink", "600", t=t))
    b.append(txt(40, 72, "Diagnostic rules never read the raw measurement: they read the "
                         "previous layer's conclusion. Replacing the sensor changes ONE layer.",
                 14, "muted", t=t))

    layers = [
        (100, 66, "border", 1.0, "LAYER 1 - S01-S04", "ink",
         ["RSSI, SNR  ->  signal quality  (good / marginal / poor)",
          "S01: IF rssi < -95 AND snr < 8 THEN quality = poor   (CF +0.90)"]),
        (182, 66, "border", 1.0, "LAYER 2 - S05-S08", "ink",
         ["node responding, loss, delay  ->  link symptom",
          "none / degraded / outage"]),
        (264, 94, "blue", 2.0, "LAYER 3 - S10-S22  ->  DIAGNOSIS", "blue",
         ["rf_interference - excess_path_loss - mac_contention - congestion",
          "node_failure - upstream_relay_failure - routing_misconfiguration - healthy",
          "eight competing hypotheses, each with its own certainty factor"]),
    ]
    for y, h, stroke, sw, title, title_tone, rows in layers:
        b.append(box(230, y, 470, h, t, "panel", stroke, sw))
        b.append(txt(248, y + 24, title, 14, title_tone, "700", t=t))
        for i, row in enumerate(rows):
            tone = "muted" if i == 0 else "faint"
            size = 12.5 if i == 0 else 11.5
            b.append(txt(248, y + 45 + i * 19, row, size, tone, t=t))

    b.append(box(230, 374, 470, 60, t, "red_fill", "red", 1.6))
    b.append(txt(248, 396, "LAYER 3b - S23-S26 - COUNTER-EVIDENCE (negative CF)",
                 13.5, "red_text", "700", t=t))
    b.append(txt(248, 416, "S25: IF retry_rate_pct <= 30 THEN mac_contention  (CF -0.80)",
                 11.5, "red_text", t=t))

    b.append(box(230, 450, 470, 60, t, "panel", "border"))
    b.append(txt(248, 472, "LAYER 4 - S27-S34  ->  RECOMMENDED ACTION", 14, "ink", "700", t=t))
    b.append(txt(248, 494, "change_channel - separate_channels - restart_node - fix_routing - ...",
                 11.5, "faint", t=t))

    b.append(box(230, 526, 470, 60, t, "green_fill", "green", 1.6))
    b.append(txt(248, 548, "LAYER 5 - S35-S42  ->  AUTHORISATION REQUIRED?",
                 14, "green_text", "700", t=t))
    b.append(txt(248, 570, "every action that changes the scenario: yes. observing: no.",
                 11.5, "green_text", t=t))

    # rails
    # Rail captions are left-aligned rather than centred: text-anchor is honoured
    # unevenly outside browsers, and these boxes sit tight against the rails.
    b += arrow(200, 566, 200, 124, t, "blue", 2.6)
    b.append(box(60, 270, 128, 128, t, "blue_fill", "blue"))
    b.append(txt(74, 296, "FORWARD", 13, "blue", "700", t=t))
    b.append(txt(74, 318, "data-driven", 11, "muted", t=t))
    b.append(txt(74, 344, "telemetry arrives,", 10.5, "faint", t=t))
    b.append(txt(74, 358, "the system concludes", 10.5, "faint", t=t))
    b.append(txt(74, 380, "the monitoring", 10.5, "faint", t=t))
    b.append(txt(74, 393, "alarm mode", 10.5, "faint", t=t))

    b += arrow(732, 124, 732, 570, t, "pink", 2.6)
    b.append(box(756, 270, 160, 146, t, "pink_fill", "pink"))
    b.append(txt(770, 296, "BACKWARD", 13, "pink_text", "700", t=t))
    b.append(txt(770, 318, "goal-driven", 11, "muted", t=t))
    b.append(txt(770, 344, "asks only what the", 10.5, "faint", t=t))
    b.append(txt(770, 358, "goal requires", 10.5, "faint", t=t))
    b.append(txt(770, 382, "the engineer at", 10.5, "faint", t=t))
    b.append(txt(770, 395, "2 a.m. mode", 10.5, "faint", t=t))
    b.append(txt(770, 412, "6 of 13 questions", 11, "pink_text", "700", t=t))

    b.append(box(756, 432, 324, 78, t, "panel", "border"))
    b.append(txt(772, 453, "what keeps the consultation short", 12.5, "ink", "700", t=t))
    b.append(txt(772, 473, "1. short-circuit: a false condition abandons the rule -",
                 11.5, "muted", t=t))
    b.append(txt(772, 487, "    the remaining conditions are never asked", 11.5, "muted", t=t))
    b.append(txt(772, 503, "2. sufficiency cut-off: goal at CF >= 0.9 ends the search",
                 11.5, "muted", t=t))

    b.append(box(40, 430, 150, 156, t, "panel", "border"))
    b.append(txt(56, 452, "CERTAINTY", 12.5, "ink", "700", t=t))
    b.append(txt(56, 468, "FACTORS", 12.5, "ink", "700", t=t))
    b.append(txt(56, 490, "premise = minimum", 11, "muted", t=t))
    b.append(txt(56, 504, "(weakest link)", 11, "muted", t=t))
    b.append(txt(56, 524, "conclusion =", 11, "muted", t=t))
    b.append(txt(56, 538, "premise x rule", 11, "muted", t=t))
    b.append(txt(56, 558, "fires only above", 11, "muted", t=t))
    b.append(txt(56, 572, "0.2", 11, "muted", t=t))

    b.append(box(756, 100, 324, 150, t, "panel", "border"))
    b.append(txt(772, 122, "CONFLICT RESOLUTION", 12.5, "ink", "700", t=t))
    b.append(txt(772, 141, "several rules ready - which fires first?", 11.5, "muted", t=t))
    b.append(txt(772, 164, "- first-match: rule base order", 11.5, "ink", t=t))
    b.append(txt(772, 182, "- specificity: most conditions first (default)", 11.5, "ink", t=t))
    b.append(txt(772, 200, "- recency: newest facts first", 11.5, "ink", t=t))
    b.append(txt(772, 224, "changes the ORDER of reasoning,", 11.5, "faint", italic=True, t=t))
    b.append(txt(772, 239, "not the fixed point", 11.5, "faint", italic=True, t=t))

    b.append(box(40, 100, 150, 150, t, "neutral_fill", "neutral_border"))
    b.append(txt(56, 122, "EVIDENCE", 12.5, "ink", "700", t=t))
    b.append(txt(56, 142, "13 askable", 11, "muted", t=t))
    b.append(txt(56, 156, "variables", 11, "muted", t=t))
    for i, name in enumerate(["PHY: rssi_dbm, snr_db,", "excess_path_loss_db",
                              "MAC: retry_rate_pct", "flow: loss, delay,",
                              "offered load, route, ..."]):
        b.append(txt(56, 178 + i * 14, name, 10.5, "faint", t=t))
    b += arrow(194, 150, 228, 132, t, width=1.6)

    b.append(box(40, 608, 1040, 62, t, "panel", "border"))
    b.append(txt(60, 630, "EXPLANATION", 13, "ink", "700", t=t))
    b.append(txt(170, 630, "why  - during the consultation: the chain of rules that led to "
                           "this question", 12, "muted", t=t))
    b.append(txt(170, 650, "how  - after concluding: walks the supporting rules down to the "
                           "facts the user supplied", 12, "muted", t=t))

    return document(1120, 700, "Expert system: rule layers and both chaining directions",
                    "The 43 rules in five layers. Forward chaining rises from measurements to "
                    "authorisation; backward chaining descends from the goal to the questions "
                    "it actually needs.", b, t)


# --------------------------------------------------------------------------
# 03 — planning
# --------------------------------------------------------------------------
def build_planning(t) -> str:
    b: List[str] = []
    b.append(txt(40, 46, "Automated action planning - STRIPS and GPS", 23, "ink", "600", t=t))
    b.append(txt(40, 72, "STRIPS is the REPRESENTATION. GPS is the STRATEGY: every action "
                         "exists to remove a concrete difference.", 14, "muted", t=t))

    b.append(txt(40, 112, "1 - Anatomy of a STRIPS operator", 15, "ink", "700", t=t))
    b.append(box(40, 126, 420, 212, t, "panel", "green", 2, 10))
    b += header_band(40, 126, 420, t, "green", "", band_h=32)
    b.append(f'<text x="58" y="148" font-size="14" font-weight="700" '
             f'fill="{t["header_text"]}" font-family="{MONO}">separate_channels(?n)</text>')
    b.append(f'<text x="442" y="148" font-size="12.5" font-weight="600" '
             f'fill="{t["header_text"]}" text-anchor="end">cost 3</text>')

    b.append(txt(58, 182, "PRECONDITIONS - what must hold", 12.5, "amber_text", "700", t=t))
    for i, p in enumerate(["authorized(?n)", "mac-contention(?n)",
                           "run-stopped(?n)"]):
        b.append(txt(70, 202 + i * 17, p, 12, "ink", mono=True, t=t))
    b.append(txt(58, 264, "ADD LIST - what becomes true", 12.5, "green_text", "700", t=t))
    b.append(txt(70, 284, "+ cleared-mac-contention(?n)", 12, "ink", mono=True, t=t))
    b.append(txt(58, 310, "DELETE LIST - what stops being true", 12.5, "red_text", "700", t=t))
    b.append(txt(70, 330, "- mac-contention(?n)", 12, "ink", mono=True, t=t))

    b.append(box(40, 352, 420, 66, t, "green_fill", "green"))
    b.append(txt(58, 374, "A CONSTRAINT AS A PRECONDITION", 12.5, "green_text", "700", t=t))
    b.append(txt(58, 393, "Operators that change the scenario require authorized(?n).",
                 11.5, "green_text", t=t))
    b.append(txt(58, 409, "The constraint lives in the state space, not in a runtime check.",
                 11.5, "green_text", t=t))

    b.append(box(40, 432, 420, 86, t, "panel", "border"))
    b.append(txt(58, 453, "CLOSED-WORLD ASSUMPTION", 12.5, "ink", "700", t=t))
    b.append(txt(58, 472, "A state is the set of TRUE literals.", 11.5, "muted", t=t))
    b.append(txt(58, 488, "Anything absent from the set is taken to be false.", 11.5, "muted", t=t))
    b.append(txt(58, 508, "state = { diagnosed(N), run-active(N), mac-contention(N) }",
                 11.5, "faint", t=t))

    b.append(box(40, 532, 420, 152, t, "panel", "border"))
    b.append(txt(58, 554, "TWO SOLVERS OVER ONE REPRESENTATION", 13, "ink", "700", t=t))
    b.append(txt(58, 578, "GPS - means-ends analysis", 12, "blue", "700", t=t))
    b.append(txt(58, 596, "explainable - NOT complete - NOT optimal", 11.5, "muted", t=t))
    b.append(txt(58, 612, "subject to the Sussman anomaly", 11.5, "muted", t=t))
    b.append(txt(58, 638, "A* progression - planning as search", 12, "amber", "700", t=t))
    b.append(txt(58, 656, "cost-optimal - uses the SAME astar() function", 11.5, "muted", t=t))
    b.append(txt(58, 672, "heuristic: unsatisfied goal literals", 11.5, "muted", t=t))

    # recursion
    b.append(txt(500, 112, "2 - Means-ends analysis: the GPS recursion", 15, "ink", "700", t=t))
    steps = [
        (126, 42, "blue_fill", "blue", 1.8, [("DIFFERENCE to reduce", 12, "blue_text", "700", False),
                                             ("service-restored(N)", 12, "ink", None, True)]),
        (194, 34, "panel", "green", 1.6, [("close_work_order(N)", 12, "ink", None, True)]),
        (254, 42, "blue_fill", "blue", 1.4, [("link-up(N)", 12, "ink", None, True),
                                             ("logged(N)", 12, "ink", None, True)]),
        (322, 34, "panel", "green", 1.6, [("verify_link(N)", 12, "ink", None, True)]),
        (382, 34, "blue_fill", "blue", 1.4,
         [("cleared-mac-contention(N)", 12, "ink", None, True)]),
        (442, 34, "panel", "green", 1.6, [("separate_channels(N)", 12, "ink", None, True)]),
        (502, 42, "green_fill", "green", 1.4, [("run-active(N)  - already true", 12, "ink", None, True),
                                               ("recursion ends: the difference is gone", 11, "faint", None, False)]),
    ]
    for y, h, fill, stroke, sw, rows in steps:
        b.append(box(500, y, 300, h, t, fill, stroke, sw, 7))
        for i, (s, size, tone, weight, mono) in enumerate(rows):
            b.append(txt(514, y + 18 + i * 17, s, size, tone, weight, mono=mono, t=t))

    for y in (170, 230, 298, 358, 418, 478):
        b += arrow(650, y, 650, y + 20, t, width=1.8)
    b.append(txt(662, 186, "an operator that reduces it", 11, "faint", t=t))
    b.append(txt(662, 246, "preconditions become differences", 11, "faint", t=t))

    b.append(f'<path d="M 812 520 C 862 520 862 152 818 150" stroke="{t["green"]}" '
             f'stroke-width="2" fill="none" stroke-dasharray="6 4"/>')
    b.append(f'<polygon points="806,150 819,144 818,157" fill="{t["green"]}"/>')
    b.append(txt(874, 330, "the plan is the", 12, "green_text", "700", t=t))
    b.append(txt(874, 348, "stack unwound", 12, "green_text", "700", t=t))
    b.append(txt(874, 368, "in reverse order", 11, "muted", t=t))

    # The trap below is a MINIMAL constructed problem, not the restoration
    # domain: see tests/test_planning.py::test_gps_can_be_suboptimal_...
    # The restoration domain cannot show this, and the panel says so.
    b.append(box(500, 552, 580, 156, t, "red_fill", "red", 1.6))
    b.append(txt(518, 574, "THE WEAKNESS OF GPS", 13, "red_text", "700", t=t))
    b.append(txt(518, 595, "GPS orders operators by their OWN cost - and never sees the cost "
                           "of their PRECONDITIONS.", 11.5, "red_text", t=t))
    b.append(txt(518, 618, "GPS:  travel (10) + cheap_fix (1)  =  cost 11",
                 11.5, "ink", mono=True, t=t))
    b.append(txt(518, 636, "A* :  remote_fix (3)               =  cost  3",
                 11.5, "ink", mono=True, t=t))
    b.append(txt(518, 660, "Isolated in a constructed test problem where the goal has TWO",
                 11, "red_text", t=t))
    b.append(txt(518, 676, "achievers. In the restoration domain every literal has exactly ONE,",
                 11, "red_text", t=t))
    b.append(txt(518, 692, "so GPS matches A* on all 55 solvable fault combinations.",
                 11, "red_text", "600", t=t))

    b.append(box(820, 126, 260, 120, t, "panel", "border"))
    b.append(txt(836, 148, "WHY COST MATTERS", 12.5, "ink", "700", t=t))
    b.append(txt(836, 168, "If every action cost 1,", 11.5, "muted", t=t))
    b.append(txt(836, 183, "planning would be counting steps.", 11.5, "muted", t=t))
    for i, row in enumerate(["stop_run + start_run  4", "separate_channels ... 3",
                             "fix_routing ......... 1"]):
        b.append(txt(836, 205 + i * 16, row, 11.5, "ink", t=t))

    return document(1120, 720, "STRIPS and GPS: operator anatomy and means-ends analysis",
                    "On the left, the three sets that define a STRIPS action. On the right, the "
                    "GPS means-ends recursion for restoring service on a node.", b, t)


# --------------------------------------------------------------------------
# 04 — A*
# --------------------------------------------------------------------------
def build_astar(t) -> str:
    b: List[str] = []
    b.append(txt(40, 46, "A* search - f(n) = g(n) + h(n)", 23, "ink", "600", t=t))
    b.append(txt(40, 72, "g is the cost already paid; h estimates what remains. g alone is "
                         "uniform cost (optimal, blind). h alone is greedy (fast, no guarantee).",
                 14, "muted", t=t))

    b.append(txt(40, 112, "Optimal path in the simulated scenario: LTE_ENB to AP_B",
                 15, "ink", "700", t=t))
    b.append(box(40, 126, 530, 396, t, "panel", "border", 1.0, 10))

    # Two competing routes, both priced. The teaching point is that the CHEAPER
    # route has MORE hops, so hop counting and cost minimisation disagree here.
    #   breadth-first / greedy : LTE_ENB -> RM_B4 -> AP_B            2 hops, 381.46 ms
    #   uniform cost / A*      : LTE_ENB -> LTE_CORE -> NOC -> AP_B  3 hops,  70.51 ms
    b.append(line(120, 210, 300, 160, t, "edge_radio", 2.4, "4 4"))
    b.append(line(300, 160, 500, 210, t, "edge_radio", 2.4, "4 4"))

    b.append(f'<polyline points="120,210 220,320 380,360 500,210" fill="none" '
             f'stroke="{t["red"]}" stroke-width="5" stroke-linejoin="round" '
             f'stroke-linecap="round" opacity="0.9"/>')

    b.append(f'<polygon points="120,196 130,214 110,214" fill="{t["n_lte"]}"/>')
    b.append(txt(56, 190, "LTE_ENB", 11, "ink", "700", t=t))
    b.append(f'<circle cx="220" cy="320" r="10" fill="{t["n_lte"]}"/>')
    b.append(txt(150, 326, "LTE_CORE", 10.5, "ink", t=t))
    b.append(f'<rect x="368" y="348" width="24" height="24" rx="4" fill="{t["n_core"]}"/>')
    b.append(txt(400, 368, "NOC", 10.5, "ink", t=t))
    b.append(f'<polygon points="500,196 510,214 490,214" fill="{t["n_ap"]}"/>')
    b.append(txt(514, 206, "AP_B", 11, "ink", "700", t=t))
    b.append(f'<circle cx="300" cy="160" r="9" fill="{t["n_rm"]}"/>')
    b.append(txt(280, 142, "RM_B4", 10.5, "ink", t=t))

    # the cheap route, hop by hop
    for x, y, label in ((116, 274, "13.86"), (288, 386, "9.41"), (452, 292, "47.23")):
        b.append(txt(x, y, label, 10.5, "red_text", "600", t=t))
    # the expensive two-hop route
    for x, y, label in ((172, 176, "263.15"), (382, 176, "118.31")):
        b.append(txt(x, y, label, 10.5, "muted", "600", t=t))

    b.append(box(58, 400, 494, 108, t, "red_fill", "red", 1.0, 6))
    b.append(txt(72, 424, "A*:  LTE_ENB -> LTE_CORE -> NOC -> AP_B", 11.5,
                 "red_text", "700", t=t))
    b.append(txt(72, 446, "3 hops,  total cost = 70.51 ms", 13, "red_text", "700", t=t))
    b.append(txt(72, 474, "breadth-first (dashed):  LTE_ENB -> RM_B4 -> AP_B",
                 11, "muted", t=t))
    b.append(txt(72, 494, "2 hops, 381.46 ms - fewer hops, five times the cost",
                 11, "red_text", "600", t=t))

    # heuristic
    b.append(box(596, 126, 484, 150, t, "panel", "amber", 2, 10))
    b.append(txt(614, 150, "THE HEURISTIC", 14, "amber_text", "700", t=t))
    b.append(txt(614, 180, "h(n) =", 13, "ink", mono=True, t=t))
    b.append(txt(676, 174, "straight_line_distance(n, goal)", 12.5, "ink", mono=True, t=t))
    b.append(line(672, 182, 936, 182, t, "ink", 1.2))
    b.append(txt(742, 200, "MAX_SPEED", 12.5, "ink", mono=True, t=t))
    b.append(txt(614, 232, "MAX_SPEED = 150 m/ms - the fastest effective speed in the",
                 11.5, "muted", t=t))
    b.append(txt(614, 248, "system (fibre). Dividing by the MAXIMUM is what guarantees",
                 11.5, "muted", t=t))
    b.append(txt(614, 264, "the estimate can never exceed the real cost.", 11.5, "muted", t=t))

    b.append(box(596, 288, 484, 164, t, "blue_fill", "blue", 1.6, 10))
    b.append(txt(614, 312, "WHY IT IS ADMISSIBLE", 13.5, "blue_text", "700", t=t))
    b.append(txt(614, 334, "overhead >= 0,  quality <= 1,  speed(type) <= MAX_SPEED",
                 11.5, "ink", t=t))
    b.append(txt(614, 356, "=> cost(u,v) >= d(u,v) / MAX_SPEED", 12, "ink", mono=True, t=t))
    b.append(txt(614, 378, "Summing along the path and applying the triangle", 11.5, "muted", t=t))
    b.append(txt(614, 394, "inequality, distance travelled >= the straight line.",
                 11.5, "muted", t=t))
    b.append(txt(614, 416, "=> optimal_cost(n) >= h(n)    admissible", 12, "ink", mono=True, t=t))
    b.append(txt(614, 440, "h(u) <= cost(u,v) + h(v)      consistent", 12, "ink", mono=True, t=t))

    b.append(box(596, 464, 484, 58, t, "green_fill", "green"))
    b.append(txt(614, 486, "VERIFIED, NOT MERELY ARGUED", 12.5, "green_text", "700", t=t))
    b.append(txt(614, 506, "Checked over every ordered pair, in both scenarios, against "
                           "Floyd-Warshall.", 11.5, "green_text", t=t))

    # table
    b.append(txt(40, 558, "Five strategies on one problem - three lessons", 15, "ink", "700", t=t))
    b.append(box(40, 572, 1040, 128, t, "panel", "border"))
    b.append(line(40, 600, 1080, 600, t, "border", 1))
    for x, label in ((60, "strategy"), (300, "steps"), (400, "cost (ms)"),
                     (530, "nodes expanded"), (700, "optimal?"), (820, "lesson")):
        b.append(txt(x, 592, label, 12, "muted", "700", t=t))

    rows = [
        (620, "Breadth-first", "2", "381.46", "7", ("steps only", "red_text"),
         "fewest hops - and five times the cost"),
        (640, "Depth-first", "6", "694.78", "7", ("no", "red_text"),
         "no guarantee at all"),
        (660, "Uniform cost", "3", "70.51", "6", ("yes", "green_text"),
         "optimal, but blind"),
        (680, "Greedy", "2", "381.46", "3", ("no", "red_text"),
         "the fastest - and wrong"),
    ]
    for y, name, steps_, cost, exp, (opt, opt_tone), lesson in rows:
        b.append(txt(60, y, name, 12, "ink", t=t))
        b.append(txt(300, y, steps_, 12, "ink", t=t))
        b.append(txt(400, y, cost, 12, "ink", "700" if cost == "70.51" else None, t=t))
        b.append(txt(530, y, exp, 12, "ink", "700" if exp == "3" else None, t=t))
        b.append(txt(700, y, opt, 12, opt_tone, "700" if opt == "yes" else None, t=t))
        b.append(txt(820, y, lesson, 11, "red_text" if "wrong" in lesson else "muted", t=t))

    for x, val in ((60, "A*"), (300, "3"), (400, "70.51"), (530, "4")):
        b.append(txt(x, 716, val, 12.5, "amber_text", "700", t=t))
    b.append(txt(700, 716, "yes", 12.5, "green_text", "700", t=t))
    b.append(txt(820, 716, "same optimum, less work", 11.5, "amber_text", "700", t=t))

    b.append(box(40, 726, 1040, 28, t, "amber_fill", "amber", 1.0, 6))
    b.append(txt(60, 745, "Summed over every ORDERED node pair, A* expands 9.4% fewer nodes "
                          "than uniform cost at 17 nodes and 25.9% fewer at 30 - a larger "
                          "saving here, not a scaling law.", 11.5, "amber_text", t=t))

    return document(1120, 770, "A* search: f = g + h, admissibility, and strategy comparison",
                    "On the left, the cheapest route A* finds in the simulated scenario. On the right, "
                    "the heuristic, its admissibility and consistency proofs, and the comparison "
                    "table for five search strategies.", b, t)


# --------------------------------------------------------------------------
# banner
# --------------------------------------------------------------------------
# --------------------------------------------------------------------------
# The banner is not built here: it is thematic artwork rather than an
# information figure, and lives in build_banner.py.
BUILDERS = {
    "01-integration": build_integration,
    "02-expert-system": build_expert,
    "03-planning": build_planning,
    "04-astar": build_astar,
}


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, builder in BUILDERS.items():
        for theme_name, palette in THEMES.items():
            path = OUT_DIR / f"{name}-{theme_name}.svg"
            path.write_text(builder(palette), encoding="utf-8")
            print(f"wrote {path.relative_to(OUT_DIR.parent.parent)}")


if __name__ == "__main__":
    main()
