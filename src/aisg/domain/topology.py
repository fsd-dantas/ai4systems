"""
Shared domain model: the communication backhaul of a smart electric grid.

PT-BR: Este modulo define o grafo usado pelos tres sistemas da disciplina. O
       modelo e SINTETICO e didatico: nao contem inventario real, enderecamento,
       identificacao de equipamento nem topologia de campo de qualquer laboratorio
       ou concessionaria.

EN:    This module defines the graph used by the three course systems. The model is
       SYNTHETIC and didactic: it contains no real inventory, addressing, equipment
       identification, or field topology of any laboratory or utility.

Cost model / Modelo de custo
----------------------------
The cost of traversing a link is a *transport cost* in milliseconds:

    cost(u, v) = overhead(type) + distance(u, v) / (speed(type) * quality)

``speed`` is an *effective transport speed* in metres per millisecond. It is a
modelling abstraction, not a physical propagation speed: it folds serialization,
queueing, and the fact that longer radio hops run at lower modulation rates into a
single distance-proportional term. ``quality`` in (0, 1] degrades that speed, and
``overhead`` charges a fixed per-hop price (a store-and-forward relay terminates and
re-transmits the frame, so it is charged much more than a switched hop).

This shape is chosen deliberately so that the straight-line heuristic used by A* is
provably admissible and consistent — see :func:`Topology.heuristic` and
``docs/03-astar.md``.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, Iterator, List, Optional, Tuple

DATA_DIR = Path(__file__).resolve().parent / "data"
DEFAULT_TOPOLOGY_FILE = DATA_DIR / "backhaul-topology.json"

#: Bundled scenarios, by short name.
#:
#: PT-BR: ``base`` e o cenario de trabalho (17 nos). ``scale`` e o cenario de escala
#:        (30 nos, tres setores), usado para mostrar como as estrategias de busca se
#:        comportam quando o grafo cresce.
#: EN:    ``base`` is the working scenario (17 nodes). ``scale`` is the scale
#:        scenario (30 nodes, three sectors), used to show how the search strategies
#:        behave as the graph grows.
BUNDLED_TOPOLOGIES: Dict[str, Path] = {
    "base": DEFAULT_TOPOLOGY_FILE,
    "simulated": DATA_DIR / "backhaul-topology-30.json",
    # Kept as an alias: the 30-node scenario was introduced as the "scale" case
    # before it was framed as the simulated bench extension.
    "scale": DATA_DIR / "backhaul-topology-30.json",
}


@dataclass(frozen=True)
class LinkType:
    """A class of transmission medium and its cost parameters."""

    name: str
    label_pt: str
    label_en: str
    #: effective transport speed, metres per millisecond (modelling abstraction)
    speed_m_per_ms: float
    #: fixed cost charged once per hop, in milliseconds
    overhead_ms: float

    def label(self, lang: str = "pt") -> str:
        return self.label_pt if lang == "pt" else self.label_en


#: Registry of link types. ``speed_m_per_ms`` orders the media by capability.
LINK_TYPES: Dict[str, LinkType] = {
    lt.name: lt
    for lt in (
        LinkType("fiber", "fibra optica", "optical fibre", 150.0, 0.5),
        LinkType("ethernet", "ethernet local", "local ethernet", 120.0, 0.4),
        LinkType("lte", "LTE privativo", "private LTE", 60.0, 8.0),
        LinkType("radio_900mhz", "radio 900 MHz", "900 MHz radio", 25.0, 12.0),
        LinkType(
            "radio_900mhz_saf",
            "radio 900 MHz armazena-e-encaminha",
            "900 MHz store-and-forward radio",
            25.0,
            25.0,
        ),
    )
}

#: The fastest effective speed in the registry. The A* heuristic divides by this
#: value, which is what makes it a lower bound on any real path cost.
MAX_SPEED_M_PER_MS: float = max(lt.speed_m_per_ms for lt in LINK_TYPES.values())


@dataclass(frozen=True)
class Node:
    id: str
    label_pt: str
    label_en: str
    kind: str
    sector: str
    x: float
    y: float

    def label(self, lang: str = "pt") -> str:
        return self.label_pt if lang == "pt" else self.label_en

    @property
    def position(self) -> Tuple[float, float]:
        return (self.x, self.y)


@dataclass(frozen=True)
class Link:
    a: str
    b: str
    type: str
    quality: float

    @property
    def link_type(self) -> LinkType:
        return LINK_TYPES[self.type]

    def other(self, node_id: str) -> str:
        if node_id == self.a:
            return self.b
        if node_id == self.b:
            return self.a
        raise KeyError(f"{node_id} is not an endpoint of {self.a}-{self.b}")


class TopologyError(ValueError):
    """Raised when a topology file is structurally inconsistent."""


@dataclass
class Topology:
    """An undirected, weighted graph of communication nodes."""

    id: str
    title_pt: str
    title_en: str
    provenance: str
    nodes: Dict[str, Node] = field(default_factory=dict)
    links: List[Link] = field(default_factory=list)
    #: node id -> list of (neighbour id, link)
    _adjacency: Dict[str, List[Tuple[str, Link]]] = field(
        default_factory=dict, repr=False
    )
    #: links disabled at runtime, e.g. to simulate a failure
    _disabled: set = field(default_factory=set, repr=False)

    # -- construction ----------------------------------------------------
    @classmethod
    def from_dict(cls, raw: dict) -> "Topology":
        topo = cls(
            id=raw["id"],
            title_pt=raw["title_pt"],
            title_en=raw["title_en"],
            provenance=raw["provenance"],
        )
        for n in raw["nodes"]:
            node = Node(
                id=n["id"],
                label_pt=n["label_pt"],
                label_en=n["label_en"],
                kind=n["kind"],
                sector=n["sector"],
                x=float(n["x"]),
                y=float(n["y"]),
            )
            if node.id in topo.nodes:
                raise TopologyError(f"duplicate node id: {node.id}")
            topo.nodes[node.id] = node

        for raw_link in raw["links"]:
            link = Link(
                a=raw_link["a"],
                b=raw_link["b"],
                type=raw_link["type"],
                quality=float(raw_link["quality"]),
            )
            for endpoint in (link.a, link.b):
                if endpoint not in topo.nodes:
                    raise TopologyError(f"link endpoint not declared as a node: {endpoint}")
            if link.type not in LINK_TYPES:
                raise TopologyError(f"unknown link type: {link.type}")
            if not 0.0 < link.quality <= 1.0:
                raise TopologyError(
                    f"link {link.a}-{link.b}: quality must be in (0, 1], got {link.quality}"
                )
            topo.links.append(link)

        topo._rebuild_adjacency()
        return topo

    @classmethod
    def load(cls, path: Optional[Path] = None) -> "Topology":
        path = Path(path) if path else DEFAULT_TOPOLOGY_FILE
        with path.open(encoding="utf-8") as handle:
            return cls.from_dict(json.load(handle))

    def _rebuild_adjacency(self) -> None:
        self._adjacency = {node_id: [] for node_id in self.nodes}
        for link in self.links:
            if self._link_key(link) in self._disabled:
                continue
            self._adjacency[link.a].append((link.b, link))
            self._adjacency[link.b].append((link.a, link))
        for neighbours in self._adjacency.values():
            neighbours.sort(key=lambda pair: pair[0])

    @staticmethod
    def _link_key(link: Link) -> Tuple[str, str]:
        return tuple(sorted((link.a, link.b)))  # type: ignore[return-value]

    # -- queries ---------------------------------------------------------
    def title(self, lang: str = "pt") -> str:
        return self.title_pt if lang == "pt" else self.title_en

    def node(self, node_id: str) -> Node:
        try:
            return self.nodes[node_id]
        except KeyError as exc:
            raise KeyError(f"unknown node: {node_id}") from exc

    def neighbours(self, node_id: str) -> List[Tuple[str, Link]]:
        """Return ``(neighbour_id, link)`` pairs, excluding disabled links."""
        if node_id not in self._adjacency:
            raise KeyError(f"unknown node: {node_id}")
        return list(self._adjacency[node_id])

    def active_links(self) -> Iterator[Link]:
        for link in self.links:
            if self._link_key(link) not in self._disabled:
                yield link

    def distance(self, a: str, b: str) -> float:
        """Straight-line distance in metres between two nodes."""
        na, nb = self.node(a), self.node(b)
        return math.hypot(na.x - nb.x, na.y - nb.y)

    def link_cost(self, link: Link) -> float:
        """Transport cost of one hop, in milliseconds."""
        lt = link.link_type
        span = self.distance(link.a, link.b)
        return lt.overhead_ms + span / (lt.speed_m_per_ms * link.quality)

    def edge_cost(self, a: str, b: str) -> float:
        """Cheapest cost among the active links joining ``a`` and ``b``."""
        costs = [self.link_cost(link) for nb, link in self.neighbours(a) if nb == b]
        if not costs:
            raise KeyError(f"no active link between {a} and {b}")
        return min(costs)

    def path_cost(self, path: Iterable[str]) -> float:
        path = list(path)
        return sum(self.edge_cost(u, v) for u, v in zip(path, path[1:]))

    # -- failure injection ----------------------------------------------
    def disable_link(self, a: str, b: str) -> None:
        """Take a link out of service (used to demonstrate re-routing)."""
        key = tuple(sorted((a, b)))
        if not any(self._link_key(link) == key for link in self.links):
            raise KeyError(f"no link between {a} and {b}")
        self._disabled.add(key)
        self._rebuild_adjacency()

    def enable_link(self, a: str, b: str) -> None:
        self._disabled.discard(tuple(sorted((a, b))))
        self._rebuild_adjacency()

    def restore_all_links(self) -> None:
        self._disabled.clear()
        self._rebuild_adjacency()

    @property
    def disabled_links(self) -> List[Tuple[str, str]]:
        return sorted(self._disabled)

    # -- search support --------------------------------------------------
    def successors(self, node_id: str) -> List[Tuple[str, float]]:
        """Successor function for the search algorithms: ``(node, step cost)``."""
        best: Dict[str, float] = {}
        for neighbour, link in self.neighbours(node_id):
            cost = self.link_cost(link)
            if neighbour not in best or cost < best[neighbour]:
                best[neighbour] = cost
        return sorted(best.items())

    def heuristic(self, goal: str):
        """
        Build the straight-line heuristic h(n) = distance(n, goal) / MAX_SPEED.

        PT-BR: Admissivel e consistente por construcao — ver docs/03-astar.md.
        EN:    Admissible and consistent by construction — see docs/03-astar.md.

        Admissibility: every hop on any path from ``n`` to ``goal`` costs at least
        ``distance(hop) / MAX_SPEED_M_PER_MS`` (because overhead >= 0 and
        speed * quality <= MAX_SPEED). Summing hops, the true cheapest cost is at
        least the *total* travelled distance / MAX_SPEED, which by the triangle
        inequality is at least the straight-line distance / MAX_SPEED = h(n).

        Consistency: h(u) - h(v) <= distance(u, v) / MAX_SPEED <= cost(u, v),
        again by the triangle inequality.
        """
        self.node(goal)  # fail fast on an unknown goal

        def h(node_id: str) -> float:
            return self.distance(node_id, goal) / MAX_SPEED_M_PER_MS

        h.__doc__ = f"Straight-line admissible heuristic towards {goal}."
        return h

    # -- reporting -------------------------------------------------------
    def summary(self, lang: str = "pt") -> str:
        lines = [
            self.title(lang),
            f"  {len(self.nodes)} " + ("nos" if lang == "pt" else "nodes")
            + f", {sum(1 for _ in self.active_links())} "
            + ("enlaces ativos" if lang == "pt" else "active links"),
        ]
        if self._disabled:
            label = "enlaces fora de servico" if lang == "pt" else "links out of service"
            joined = ", ".join(f"{a}-{b}" for a, b in self.disabled_links)
            lines.append(f"  {label}: {joined}")
        return "\n".join(lines)


def load_default_topology() -> Topology:
    """Convenience loader used across the three systems."""
    return Topology.load()


def load_topology(name: str = "base") -> Topology:
    """
    Load a bundled scenario by short name.

    PT-BR: ``base`` (17 nos) ou ``scale`` (30 nos). Tambem aceita um caminho de
           arquivo, para cenarios proprios fora do repositorio.
    EN:    ``base`` (17 nodes) or ``scale`` (30 nodes). Also accepts a file path, for
           private scenarios kept outside the repository.
    """
    path = BUNDLED_TOPOLOGIES.get(name)
    if path is None:
        candidate = Path(name)
        if candidate.is_file():
            return Topology.load(candidate)
        raise KeyError(
            f"unknown topology {name!r}; bundled scenarios: "
            f"{', '.join(sorted(BUNDLED_TOPOLOGIES))}"
        )
    return Topology.load(path)
