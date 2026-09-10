"""
Render the simulated 30-node scenario, in light and dark variants.

This pictures the TOPOLOGY MODEL that A* consumes. It is not simulation output:
no discrete-event run produced it, and the figure says so, because the ns-3
scenario for this band is not built.
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

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
KIND = {
    "control_centre": ("#1b3a6b", "s", 190), "lte_core": ("#3f7cac", "s", 150),
    "lte_enb": ("#3f7cac", "^", 150), "access_point": ("#c1666b", "^", 170),
    "remote_master": ("#6b8f71", "o", 90), "saf_relay": ("#d4a373", "D", 110),
    "field_device": ("#b23a48", "*", 260),
}


def draw(theme_name: str, palette: dict) -> None:
    topology = load_topology("simulated")
    problem = RoutingProblem(topology, "NOC", "FD_C")
    best = astar(problem, problem.heuristic())

    fig, ax = plt.subplots(figsize=(12, 7.2), facecolor=palette["bg"])
    ax.set_facecolor(palette["bg"])

    for link in topology.active_links():
        a, b = topology.node(link.a), topology.node(link.b)
        dashed = link.type.startswith("radio")
        ax.plot([a.x, b.x], [a.y, b.y], "--" if dashed else "-",
                color=palette["edge"], lw=1.4, zorder=1, alpha=0.9)

    xs = [topology.node(n).x for n in best.path]
    ys = [topology.node(n).y for n in best.path]
    ax.plot(xs, ys, "-", color=palette["path"], lw=4.5, zorder=2, alpha=0.9,
            solid_capstyle="round",
            label=f"A*: {' -> '.join(best.path)}  =  {best.cost:.1f} ms")

    for node in topology.nodes.values():
        colour, marker, size = KIND[node.kind]
        ax.scatter(node.x, node.y, s=size, c=colour, marker=marker, zorder=3,
                   edgecolors=palette["bg"], linewidths=1.2)
        ax.annotate(node.id, (node.x, node.y), textcoords="offset points",
                    xytext=(0, 9), ha="center", fontsize=7,
                    color=palette["muted"], zorder=4)

    ax.set_title("Cenario simulado — 30 nos, tres setores  /  Simulated scenario",
                 fontsize=14, color=palette["ink"], pad=14)
    ax.set_xlabel("metros / metres", color=palette["muted"], fontsize=9)
    ax.set_ylabel("metros / metres", color=palette["muted"], fontsize=9)
    ax.tick_params(colors=palette["muted"], labelsize=8)
    for spine in ax.spines.values():
        spine.set_color(palette["edge"])
    ax.grid(color=palette["grid"], lw=0.6)
    ax.set_aspect("equal", adjustable="datalim")
    legend = ax.legend(loc="upper left", fontsize=9, facecolor=palette["bg"],
                       edgecolor=palette["edge"])
    for text in legend.get_texts():
        text.set_color(palette["ink"])

    fig.text(0.5, 0.015,
             "MODELO de topologia, nao saida de simulacao: nenhuma execucao "
             "produziu estes numeros.  /  Topology MODEL, not simulation output.",
             ha="center", fontsize=8.5, color=palette["muted"])
    fig.tight_layout(rect=(0, 0.03, 1, 1))

    for suffix in ("svg", "png"):
        path = OUT / f"05-simulated-30-{theme_name}.{suffix}"
        fig.savefig(path, facecolor=palette["bg"], dpi=200)
        print(f"wrote {path.name}")
    plt.close(fig)


if __name__ == "__main__":
    for name, palette in THEMES.items():
        draw(name, palette)
