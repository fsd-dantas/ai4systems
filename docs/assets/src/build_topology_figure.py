"""
Render the scenario maps, in light and dark variants.

These picture the TOPOLOGY MODEL that A* consumes. They are not the output of
any simulation or measurement: no run produced these numbers, and the figures
say so.

Two conventions, both deliberate:

* The figure is ENGLISH ONLY, like every other generated diagram. Unaccented
  Portuguese reads as misspelling, and the source files carry no accents.
* The map keeps an EQUAL aspect ratio. The admissibility argument for the
  heuristic is geometric - h(n) is a straight-line distance - so stretching one
  axis to fill a widescreen frame would make the picture disagree with the
  proof. The remaining width carries the legend, and nothing else: the route is
  a legend entry rather than a side panel.
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "src"))
from aisg.domain import load_topology  # noqa: E402
from aisg.search import RoutingProblem, astar  # noqa: E402

OUT = Path(__file__).resolve().parent.parent

THEMES = {
    "light": dict(bg="#fbfaf7", ink="#1f2933", muted="#52606d", edge="#c9c2b8",
                  path="#D55E00", grid="#e8e4dd"),
    "dark": dict(bg="#0d1117", ink="#e6edf3", muted="#9daab7", edge="#30363d",
                 path="#f2794a", grid="#1c2430"),
}

#: kind -> (colour, marker, size, legend label). Covers both scenarios; kinds
#: absent from a given topology simply do not appear in its legend.
KIND = {
    "control_centre": ("#1b3a6b", "s", 190, "control centre"),
    "lte_core": ("#3f7cac", "s", 150, "LTE core"),
    "lte_enb": ("#2f6690", "^", 200, "private LTE eNodeB"),
    "lte_relay": ("#6fa8cf", "^", 110, "LTE relay"),
    "cpe": ("#3f7cac", "o", 60, "CPE"),
    "access_point": ("#c1666b", "^", 170, "access point"),
    "remote_master": ("#6b8f71", "o", 60, "remote master"),
    "saf_relay": ("#d4a373", "D", 110, "store-and-forward relay"),
    "field_device": ("#b23a48", "*", 260, "field device"),
    "edge_router": ("#b23a48", "*", 230, "edge router (grid site)"),
}

#: link type -> (colour, line style, width). Colouring by MEDIUM is what makes
#: the two access networks legible as networks rather than as loose edges.
MEDIUM = {
    "fiber": ("#48525c", "-", 2.4),
    "ethernet": ("#9aa3ac", "-", 1.2),
    "lte": ("#3f7cac", "--", 1.4),
    "radio_900mhz": ("#c98b3a", ":", 1.7),
    "radio_900mhz_saf": ("#c98b3a", "-", 2.2),
}

#: Scenarios dense enough that labelling every node is unreadable: label the
#: infrastructure in full and the grid sites by number only.
def _sparse_label(node) -> str:
    if node.kind in ("cpe", "remote_master"):
        return ""
    if node.kind == "edge_router":
        return node.id.split("_")[-1]
    return node.id


#: Nodes whose default label position collides with a neighbour's.
#: node id -> (dx, dy, horizontal alignment)
LABEL_OFFSETS = {
    "NOC": (-10, 8, "right"),
    "LTE_CORE": (-8, -14, "right"),
    "LTE_ENB": (11, -4, "left"),
    "RM_A2": (10, 0, "left"),
    "SAF_A1": (-10, 2, "right"),
    "AP_A": (-10, -4, "right"),
    "RM_A1": (10, -2, "left"),
    "AP_B": (-9, -6, "right"),
    "RM_B1": (9, -2, "left"),
    "RM_B4": (-9, -2, "right"),
    "SAF_B1": (7, -13, "left"),
    "RM_C1": (10, -2, "left"),
    "AP_C": (-10, -4, "right"),
    "SAF_C1": (0, 9, "center"),
    "SAF_C2": (0, -16, "center"),
    "FD_C": (10, -4, "left"),
}


def draw(theme_name: str, palette: dict, *, scenario: str = "simulated",
         pair: tuple = ("NOC", "FD_C"), stem: str = "05-simulated-30",
         title: str = "Simulated scenario - 30 nodes, three sectors",
         sparse: bool = False) -> None:
    topology = load_topology(scenario)
    problem = RoutingProblem(topology, *pair)
    best = astar(problem, problem.heuristic())

    fig = plt.figure(figsize=(12.4, 7.4), facecolor=palette["bg"])
    grid = fig.add_gridspec(1, 2, width_ratios=(1.0, 3.1),
                            left=0.015, right=0.985, top=0.905, bottom=0.105,
                            wspace=0.03)
    ax = fig.add_subplot(grid[0, 1])
    ax.set_facecolor(palette["bg"])

    for link in topology.active_links():
        a, b = topology.node(link.a), topology.node(link.b)
        colour, style, width = MEDIUM.get(
            link.type, (palette["edge"], "--", 1.4))
        if colour in palette:
            colour = palette[colour]
        ax.plot([a.x, b.x], [a.y, b.y], style, color=colour, lw=width,
                zorder=1, alpha=0.8)

    xs = [topology.node(n).x for n in best.path]
    ys = [topology.node(n).y for n in best.path]
    ax.plot(xs, ys, "-", color=palette["path"], lw=4.5, zorder=2, alpha=0.9,
            solid_capstyle="round")

    for node in topology.nodes.values():
        colour, marker, size, _ = KIND[node.kind]
        ax.scatter(node.x, node.y, s=size, c=colour, marker=marker, zorder=3,
                   edgecolors=palette["bg"], linewidths=1.2)
        text = _sparse_label(node) if sparse else node.id
        if not text:
            continue
        dx, dy, ha = LABEL_OFFSETS.get(node.id, (0, 9, "center"))
        if sparse and node.kind == "edge_router":
            dx, dy, ha = 12, -4, "left"
        ax.annotate(text, (node.x, node.y), textcoords="offset points",
                    xytext=(dx, dy), ha=ha,
                    fontsize=8.5 if sparse and node.kind == "edge_router" else 7,
                    weight="bold" if sparse and node.kind == "edge_router" else None,
                    color=palette["muted"], zorder=4)

    ax.set_xlabel("metres", color=palette["muted"], fontsize=9)
    ax.set_ylabel("metres", color=palette["muted"], fontsize=9)
    ax.tick_params(colors=palette["muted"], labelsize=8)
    for spine in ax.spines.values():
        spine.set_color(palette["edge"])
    ax.grid(color=palette["grid"], lw=0.6)
    ax.set_aspect("equal", adjustable="box")

    # ------------------------------------------------------------- legend
    key = fig.add_subplot(grid[0, 0])
    key.set_facecolor(palette["bg"])
    key.axis("off")

    counts: dict[str, int] = {}
    for node in topology.nodes.values():
        counts[node.kind] = counts.get(node.kind, 0) + 1

    handles = [Line2D([], [], color=colour, marker=marker, linestyle="none",
                      markersize=(size / 22) ** 0.5 * 4,
                      label=f"{counts[kind]}x  {label}")
               for kind, (colour, marker, size, label) in KIND.items()
               if counts.get(kind)]
    used = {lk.type for lk in topology.active_links()}
    handles += [Line2D([], [], color=palette["bg"], label="")]
    handles += [Line2D([], [], color=c, lw=w, ls=st, label=lab)
                for kind, (c, st, w), lab in (
                    ("fiber", MEDIUM["fiber"], "fibre backbone"),
                    ("ethernet", MEDIUM["ethernet"], "cable to edge router"),
                    ("lte", MEDIUM["lte"], "pLTE air"),
                    ("radio_900mhz_saf", MEDIUM["radio_900mhz_saf"],
                     "900 MHz store-and-forward"),
                    ("radio_900mhz", MEDIUM["radio_900mhz"], "900 MHz access"),
                ) if kind in used]
    handles += [Line2D([], [], color=palette["path"], lw=4,
                       label=f"A* route, {best.cost:.1f} ms")]
    legend = key.legend(handles=handles, loc="center left",
                        bbox_to_anchor=(-0.06, 0.52), fontsize=8,
                        frameon=False, handletextpad=0.8, labelspacing=1.25)
    for text in legend.get_texts():
        text.set_color(palette["muted"])

    fig.suptitle(title, fontsize=15, color=palette["ink"], y=0.962)
    fig.text(0.5, 0.022,
             "Topology MODEL, not simulation output: no discrete-event run "
             "produced these numbers.",
             ha="center", fontsize=8.5, color=palette["muted"])

    for suffix in ("svg", "png"):
        path = OUT / f"{stem}-{theme_name}.{suffix}"
        fig.savefig(path, facecolor=palette["bg"], dpi=200)
        print(f"wrote {path.name}")
    plt.close(fig)


SCENARIOS = (
    dict(scenario="simulated", pair=("NOC", "FD_C"), stem="05-simulated-30",
         title="Simulated scenario - 30 nodes, three sectors"),
    dict(scenario="dual", pair=("NOC", "ER_03"), stem="06-dual-60",
         title="Dual-homed scenario - 60 nodes, 15 sites, two access networks",
         sparse=True),
)


if __name__ == "__main__":
    for spec in SCENARIOS:
        for name, palette in THEMES.items():
            draw(name, palette, **spec)
