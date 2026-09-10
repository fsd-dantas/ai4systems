"""
Render the simulated 30-node scenario, in light and dark variants.

This pictures the TOPOLOGY MODEL that A* consumes. It is not simulation output:
no discrete-event run produced it, and the figure says so, because the ns-3
scenario for this band is not built.

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

#: kind -> (colour, marker, size, legend label)
KIND = {
    "control_centre": ("#1b3a6b", "s", 190, "control centre"),
    "lte_core": ("#3f7cac", "s", 150, "LTE core"),
    "lte_enb": ("#3f7cac", "^", 150, "private LTE eNB"),
    "access_point": ("#c1666b", "^", 170, "access point"),
    "remote_master": ("#6b8f71", "o", 90, "remote master"),
    "saf_relay": ("#d4a373", "D", 110, "store-and-forward relay"),
    "field_device": ("#b23a48", "*", 260, "field device"),
}

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


def draw(theme_name: str, palette: dict) -> None:
    topology = load_topology("simulated")
    problem = RoutingProblem(topology, "NOC", "FD_C")
    best = astar(problem, problem.heuristic())

    fig = plt.figure(figsize=(12.4, 7.4), facecolor=palette["bg"])
    grid = fig.add_gridspec(1, 2, width_ratios=(1.0, 3.1),
                            left=0.015, right=0.985, top=0.905, bottom=0.105,
                            wspace=0.03)
    ax = fig.add_subplot(grid[0, 1])
    ax.set_facecolor(palette["bg"])

    for link in topology.active_links():
        a, b = topology.node(link.a), topology.node(link.b)
        dashed = link.type.startswith("radio")
        ax.plot([a.x, b.x], [a.y, b.y], "--" if dashed else "-",
                color=palette["edge"], lw=1.4, zorder=1, alpha=0.9)

    xs = [topology.node(n).x for n in best.path]
    ys = [topology.node(n).y for n in best.path]
    ax.plot(xs, ys, "-", color=palette["path"], lw=4.5, zorder=2, alpha=0.9,
            solid_capstyle="round")

    for node in topology.nodes.values():
        colour, marker, size, _ = KIND[node.kind]
        ax.scatter(node.x, node.y, s=size, c=colour, marker=marker, zorder=3,
                   edgecolors=palette["bg"], linewidths=1.2)
        dx, dy, ha = LABEL_OFFSETS.get(node.id, (0, 9, "center"))
        ax.annotate(node.id, (node.x, node.y), textcoords="offset points",
                    xytext=(dx, dy), ha=ha, fontsize=7,
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
                      label=f"{counts.get(kind, 0)}x  {label}")
               for kind, (colour, marker, size, label) in KIND.items()]
    handles += [
        Line2D([], [], color=palette["bg"], label=""),
        Line2D([], [], color=palette["edge"], lw=1.4, label="wired link"),
        Line2D([], [], color=palette["edge"], lw=1.4, ls="--", label="wireless link"),
        Line2D([], [], color=palette["path"], lw=4,
               label=f"A* route, {best.cost:.1f} ms"),
    ]
    legend = key.legend(handles=handles, loc="center left",
                        bbox_to_anchor=(-0.06, 0.52), fontsize=8,
                        frameon=False, handletextpad=0.8, labelspacing=1.25)
    for text in legend.get_texts():
        text.set_color(palette["muted"])

    fig.suptitle("Simulated scenario - 30 nodes, three sectors",
                 fontsize=15, color=palette["ink"], y=0.962)
    fig.text(0.5, 0.022,
             "Topology MODEL, not simulation output: no discrete-event run "
             "produced these numbers.",
             ha="center", fontsize=8.5, color=palette["muted"])

    for suffix in ("svg", "png"):
        path = OUT / f"05-simulated-30-{theme_name}.{suffix}"
        fig.savefig(path, facecolor=palette["bg"], dpi=200)
        print(f"wrote {path.name}")
    plt.close(fig)


if __name__ == "__main__":
    for name, palette in THEMES.items():
        draw(name, palette)
