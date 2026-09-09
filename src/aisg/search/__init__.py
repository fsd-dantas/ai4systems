"""
Search strategies / Estrategias de busca.

PT-BR: Busca em largura, em profundidade, custo uniforme, gulosa e A*.
EN:    Breadth-first, depth-first, uniform cost, greedy, and A* search.
"""

from aisg.search.algorithms import (
    SearchProblem,
    SearchResult,
    astar,
    breadth_first,
    compare,
    depth_first,
    greedy_best_first,
    iterative_deepening,
    uniform_cost,
)
from aisg.search.graph_problem import RoutingProblem, shortest_route

__all__ = [
    "RoutingProblem",
    "SearchProblem",
    "SearchResult",
    "astar",
    "breadth_first",
    "compare",
    "depth_first",
    "greedy_best_first",
    "iterative_deepening",
    "shortest_route",
    "uniform_cost",
]
