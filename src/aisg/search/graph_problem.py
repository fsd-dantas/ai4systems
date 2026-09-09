"""
Routing problem over the communication backhaul.

PT-BR: Adapta a topologia para a interface de problema de busca. O estado e o
       identificador do no; a acao e o enlace percorrido; o custo do passo e o
       custo de transporte do enlace, em milissegundos.

EN:    Adapts the topology to the search-problem interface. A state is a node id, an
       action is the traversed link, and the step cost is the link's transport cost
       in milliseconds.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable, List, Optional, Tuple

from aisg.domain.topology import Topology


@dataclass
class RoutingProblem:
    """Find the cheapest route between two nodes of the backhaul."""

    topology: Topology
    start: str
    goal: str
    #: node ids that must not be traversed (e.g. a node under maintenance)
    avoid: Tuple[str, ...] = ()

    def __post_init__(self) -> None:
        self.topology.node(self.start)
        self.topology.node(self.goal)
        for node_id in self.avoid:
            self.topology.node(node_id)
        if self.start in self.avoid:
            raise ValueError(f"start node {self.start} is also in the avoid set")
        if self.goal in self.avoid:
            raise ValueError(f"goal node {self.goal} is also in the avoid set")

    # -- SearchProblem interface ----------------------------------------
    def initial_state(self) -> str:
        return self.start

    def is_goal(self, state: str) -> bool:
        return state == self.goal

    def successors(self, state: str) -> Iterable[Tuple[str, str, float]]:
        for neighbour, cost in self.topology.successors(state):
            if neighbour in self.avoid:
                continue
            yield (f"{state}->{neighbour}", neighbour, cost)

    # -- helpers ---------------------------------------------------------
    def heuristic(self) -> Callable[[str], float]:
        """Admissible, consistent straight-line heuristic towards the goal."""
        return self.topology.heuristic(self.goal)

    def explain_path(self, path: List[str], lang: str = "pt") -> str:
        """Render a path hop by hop, with medium, quality, and per-hop cost."""
        if len(path) < 2:
            return " ".join(path)
        header = (
            f"{'salto':<22} {'meio':<32} {'qual.':>6} {'custo(ms)':>10} {'acum.(ms)':>10}"
            if lang == "pt"
            else f"{'hop':<22} {'medium':<32} {'qual.':>6} {'cost(ms)':>10} {'cum.(ms)':>10}"
        )
        lines = [header, "-" * len(header)]
        total = 0.0
        for u, v in zip(path, path[1:]):
            link = min(
                (lk for nb, lk in self.topology.neighbours(u) if nb == v),
                key=self.topology.link_cost,
            )
            cost = self.topology.link_cost(link)
            total += cost
            lines.append(
                f"{u + ' -> ' + v:<22} {link.link_type.label(lang):<32} "
                f"{link.quality:>6.2f} {cost:>10.2f} {total:>10.2f}"
            )
        return "\n".join(lines)


def shortest_route(
    topology: Topology,
    start: str,
    goal: str,
    *,
    avoid: Iterable[str] = (),
) -> Optional[List[str]]:
    """
    Convenience wrapper: cheapest route as a list of node ids, or ``None``.

    PT-BR: Usado pelo planejador quando a acao 'desviar trafego' precisa saber se
           existe rota alternativa.
    EN:    Used by the planner when the 'reroute traffic' action needs to know
           whether an alternative route exists.
    """
    from aisg.search.algorithms import astar  # local import avoids a cycle

    problem = RoutingProblem(topology, start, goal, tuple(avoid))
    result = astar(problem, problem.heuristic())
    return result.path if result.found else None
