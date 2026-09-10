"""
Render the simulated 30-node scenario, in light and dark variants.

This pictures the TOPOLOGY MODEL that A* consumes. It is not simulation output:
no discrete-event run produced it, and the figure says so, because the ns-3
scenario for this band is not built.

Layout note: the map keeps an EQUAL aspect ratio on purpose. The admissibility
argument for the heuristic is geometric - h(n) is a straight-line distance - so
stretching one axis to fill a widescreen frame would make the picture disagree
with the proof. The three sectors sit radially around the control centre, which
makes the data almost square; the width is therefore used for two side panels
that carry the node key and the A* path, rather than for whitespace.
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
                  path="#D55E00", grid="#e8e4dd", panel="#f2eee7"),
    "dark": dict(bg="#0d1117", ink="#e6edf3", muted="#9daab7", edge="#30363d",
                 path="#f2794a", grid="#1c2430", panel="#151b23"),
}

#: kind -> (colour, marker, size, human label)
KIND = {
    "control_centre": ("#1b3a6b", "s", 190, "centro de controle / control centre"),
    "lte_core": ("#3f7cac", "s", 150, "nucleo LTE / LTE core"),
    "lte_enb": ("#3f7cac", "^", 150, "eNB LTE privado / private LTE eNB"),
    "access_point": ("#c1666b", "^", 170, "ponto de acesso / access point"),
    "remote_master": ("#6b8f71", "o", 90, "unidade remota / remote master"),
    "saf_relay": ("#d4a373", "D", 110, "repetidor store-and-forward"),
    "field_device": ("#b23a48", "*", 260, "dispositivo de campo / field device"),
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
    "SAF_B1": (-8, -4, "right"),
    "RM_C1": (10, -2, "left"),
    "AP_C": (-10, -4, "right"),
    "SAF_C1": (0, 9, "center"),
    "SAF_C2": (0, -16, "center"),
    "FD_C": (10, -4, "left"),
}

#: Sector callouts, placed BESIDE each cluster in genuinely empty map space so
#: they never land on a node label.
SECTORS = [("SETOR A", -1400, 6800), ("SETOR B", -7500, 2400),
           ("SETOR C", -1200, -6200)]


def draw(theme_name: str, palette: dict) -> None:
    topology = load_topology("simulated")
    problem = RoutingProblem(topology, "NOC", "FD_C")
    best = astar(problem, problem.heuristic())

    fig = plt.figure(figsize=(14, 7.6), facecolor=palette["bg"])
    # narrow key | square map | path panel
    grid = fig.add_gridspec(1, 3, width_ratios=(1.05, 2.5, 1.25),
                            left=0.015, right=0.985, top=0.90, bottom=0.115,
                            wspace=0.04)
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

    for name, sx, sy in SECTORS:
        ax.annotate(name, (sx, sy), ha="center", fontsize=11, zorder=2,
                    color=palette["muted"], alpha=0.55, weight="bold")

    ax.set_xlabel("metros / metres", color=palette["muted"], fontsize=9)
    ax.set_ylabel("metros / metres", color=palette["muted"], fontsize=9)
    ax.tick_params(colors=palette["muted"], labelsize=8)
    for spine in ax.spines.values():
        spine.set_color(palette["edge"])
    ax.grid(color=palette["grid"], lw=0.6)
    ax.set_aspect("equal", adjustable="box")

    # ---------------------------------------------------------------- key
    key = fig.add_subplot(grid[0, 0])
    key.set_facecolor(palette["bg"])
    key.axis("off")
    counts: dict[str, int] = {}
    for node in topology.nodes.values():
        counts[node.kind] = counts.get(node.kind, 0) + 1
    key.text(0.0, 0.97, "TIPOS DE NO / NODE KINDS", fontsize=10,
             color=palette["ink"], weight="bold", va="top")
    handles = [Line2D([], [], color=colour, marker=marker, linestyle="none",
                      markersize=(size / 22) ** 0.5 * 4,
                      label=f"{counts.get(kind, 0)}x  {label}")
               for kind, (colour, marker, size, label) in KIND.items()]
    legend = key.legend(handles=handles, loc="upper left",
                        bbox_to_anchor=(-0.04, 0.93), fontsize=7.6,
                        frameon=False, handletextpad=0.7, labelspacing=1.05)
    for text in legend.get_texts():
        text.set_color(palette["muted"])

    key.text(0.0, 0.40, "ENLACES / LINKS", fontsize=10, color=palette["ink"],
             weight="bold", va="top")
    link_handles = [
        Line2D([], [], color=palette["edge"], lw=1.4, label="cabeado / wired"),
        Line2D([], [], color=palette["edge"], lw=1.4, ls="--",
               label="radio / wireless"),
        Line2D([], [], color=palette["path"], lw=4, label="rota A* / A* route"),
    ]
    link_legend = key.legend(handles=link_handles, loc="upper left",
                             bbox_to_anchor=(-0.04, 0.36), fontsize=7.6,
                             frameon=False, handletextpad=0.7, labelspacing=1.05)
    key.add_artist(legend)
    for text in link_legend.get_texts():
        text.set_color(palette["muted"])

    # ------------------------------------------------------------ A* panel
    panel = fig.add_subplot(grid[0, 2])
    panel.set_facecolor(palette["bg"])
    panel.axis("off")
    panel.text(0.0, 0.97, "ROTA OTIMA / OPTIMAL ROUTE", fontsize=10,
               color=palette["ink"], weight="bold", va="top")
    panel.text(0.0, 0.92, f"{best.path[0]}  ->  {best.path[-1]}", fontsize=9,
               color=palette["path"], weight="bold", va="top")

    y = 0.85
    total = 0.0
    for u, v in zip(best.path, best.path[1:]):
        link = min((lk for nb, lk in topology.neighbours(u) if nb == v),
                   key=topology.link_cost)
        cost = topology.link_cost(link)
        total += cost
        panel.text(0.0, y, f"{u} -> {v}", fontsize=7.8, color=palette["ink"],
                   va="top", family="monospace")
        panel.text(0.0, y - 0.035, f"   {link.type:<14} {cost:7.2f} ms",
                   fontsize=7.4, color=palette["muted"], va="top",
                   family="monospace")
        y -= 0.085

    panel.text(0.0, y - 0.01, f"total{total:>26.2f} ms", fontsize=8.6,
               color=palette["path"], weight="bold", va="top", family="monospace")

    panel.text(0.0, y - 0.10,
               "Menos saltos nao e mais barato:\no caminho mais curto em numero\n"
               "de saltos custa mais tempo.\n\nFewer hops is not cheaper: the\n"
               "shortest hop count costs more\ntime on this graph.",
               fontsize=7.6, color=palette["muted"], va="top", linespacing=1.5)

    fig.suptitle("Cenario simulado - 30 nos, tres setores  /  Simulated scenario "
                 "- 30 nodes, three sectors",
                 fontsize=14, color=palette["ink"], y=0.965)
    fig.text(0.5, 0.018,
             "MODELO de topologia, nao saida de simulacao: nenhuma execucao "
             "produziu estes numeros.  /  Topology MODEL, not simulation output.",
             ha="center", fontsize=8.5, color=palette["muted"])

    for suffix in ("svg", "png"):
        path = OUT / f"05-simulated-30-{theme_name}.{suffix}"
        fig.savefig(path, facecolor=palette["bg"], dpi=200)
        print(f"wrote {path.name}")
    plt.close(fig)


if __name__ == "__main__":
    for name, palette in THEMES.items():
        draw(name, palette)
