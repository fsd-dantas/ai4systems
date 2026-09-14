"""
State-space search: A*, uniform cost, greedy best-first, breadth-first, depth-first.

PT-BR: A busca e definida sobre um *problema* abstrato (estado inicial, teste de
       objetivo, funcao sucessora). Assim o mesmo A* atende tanto ao roteamento no
       grafo de comunicacao quanto a busca no espaco de estados do planejador.

EN:    Search is defined over an abstract *problem* (initial state, goal test,
       successor function). The same A* therefore serves both routing over the
       communication graph and the planner's state-space search.

Every algorithm returns a :class:`SearchResult` carrying the exact path, its cost,
and the instrumentation needed to compare strategies in class: expansion order,
number of nodes expanded and generated, and the peak frontier size.
"""

from __future__ import annotations

import heapq
import itertools
from collections import deque
from dataclasses import dataclass, field
from typing import (
    Callable,
    Dict,
    Generic,
    Hashable,
    Iterable,
    List,
    Optional,
    Protocol,
    Sequence,
    Tuple,
    TypeVar,
)

S = TypeVar("S", bound=Hashable)
A = TypeVar("A")


class SearchProblem(Protocol[S, A]):
    """The interface every searchable problem must provide."""

    def initial_state(self) -> S:
        ...

    def is_goal(self, state: S) -> bool:
        ...

    def successors(self, state: S) -> Iterable[Tuple[A, S, float]]:
        """Yield ``(action, next_state, step_cost)`` triples."""
        ...


@dataclass
class SearchResult(Generic[S, A]):
    """Outcome of a search, including instrumentation for comparison."""

    algorithm: str
    found: bool
    path: List[S] = field(default_factory=list)
    actions: List[A] = field(default_factory=list)
    cost: float = 0.0
    expanded: int = 0
    generated: int = 0
    peak_frontier: int = 0
    expansion_order: List[S] = field(default_factory=list)
    #: g-value at the moment each state was expanded (A*, UCS)
    g_at_expansion: Dict[S, float] = field(default_factory=dict)

    def __bool__(self) -> bool:  # allows `if result:`
        return self.found

    @property
    def length(self) -> int:
        """Number of actions in the solution."""
        return len(self.actions)

    def describe(self, lang: str = "pt", arrow: str = " -> ") -> str:
        if not self.found:
            return (
                "Nenhuma solucao encontrada."
                if lang == "pt"
                else "No solution found."
            )
        if lang == "pt":
            return (
                f"{self.algorithm}: caminho com {self.length} passo(s), "
                f"custo {self.cost:.2f} | expandidos {self.expanded}, "
                f"gerados {self.generated}, pico da fronteira {self.peak_frontier}\n"
                f"  {arrow.join(str(s) for s in self.path)}"
            )
        return (
            f"{self.algorithm}: path with {self.length} step(s), "
            f"cost {self.cost:.2f} | expanded {self.expanded}, "
            f"generated {self.generated}, peak frontier {self.peak_frontier}\n"
            f"  {arrow.join(str(s) for s in self.path)}"
        )


def _reconstruct(
    came_from: Dict[S, Tuple[Optional[S], Optional[A]]], state: S
) -> Tuple[List[S], List[A]]:
    path: List[S] = [state]
    actions: List[A] = []
    parent, action = came_from[state]
    while parent is not None:
        path.append(parent)
        actions.append(action)  # type: ignore[arg-type]
        parent, action = came_from[parent]
    path.reverse()
    actions.reverse()
    return path, actions


def astar(
    problem: SearchProblem[S, A],
    heuristic: Optional[Callable[[S], float]] = None,
    *,
    name: str = "A*",
) -> SearchResult[S, A]:
    """
    A* search with a priority queue ordered by f(n) = g(n) + h(n).

    PT-BR: Com heuristica admissivel, o caminho retornado e otimo. Com heuristica
           consistente, um estado nunca precisa ser reaberto — mesmo assim tratamos
           o caso geral, permitindo reabertura quando um caminho melhor aparece.
    EN:    With an admissible heuristic the returned path is optimal. With a
           consistent heuristic a state never needs re-opening — we still handle the
           general case and re-open a state when a cheaper path to it is found.

    Ties on f are broken by preferring the larger g (deeper node), then by insertion
    order, which keeps runs reproducible.
    """
    h = heuristic or (lambda _state: 0.0)
    start = problem.initial_state()

    counter = itertools.count()
    g_score: Dict[S, float] = {start: 0.0}
    came_from: Dict[S, Tuple[Optional[S], Optional[A]]] = {start: (None, None)}
    closed: set = set()

    frontier: List[Tuple[float, float, int, S]] = []
    heapq.heappush(frontier, (h(start), 0.0, next(counter), start))

    result: SearchResult[S, A] = SearchResult(algorithm=name, found=False)
    result.generated = 1
    result.peak_frontier = 1

    while frontier:
        _f, neg_g, _seq, state = heapq.heappop(frontier)
        if state in closed:
            continue
        g = -neg_g
        if g > g_score.get(state, float("inf")):
            continue  # a stale queue entry

        closed.add(state)
        result.expanded += 1
        result.expansion_order.append(state)
        result.g_at_expansion[state] = g

        if problem.is_goal(state):
            path, actions = _reconstruct(came_from, state)
            result.found = True
            result.path = path
            result.actions = actions
            result.cost = g
            return result

        for action, nxt, step_cost in problem.successors(state):
            if step_cost < 0:
                raise ValueError(
                    f"negative step cost {step_cost} on {state} -> {nxt}; "
                    "A* requires non-negative costs"
                )
            tentative = g + step_cost
            result.generated += 1
            if tentative < g_score.get(nxt, float("inf")):
                g_score[nxt] = tentative
                came_from[nxt] = (state, action)
                closed.discard(nxt)  # re-open if we found a cheaper route
                heapq.heappush(
                    frontier, (tentative + h(nxt), -tentative, next(counter), nxt)
                )
        result.peak_frontier = max(result.peak_frontier, len(frontier))

    return result


def uniform_cost(problem: SearchProblem[S, A]) -> SearchResult[S, A]:
    """Dijkstra / uniform-cost search: A* with h(n) = 0."""
    return astar(problem, None, name="Uniform cost (Dijkstra)")


def greedy_best_first(
    problem: SearchProblem[S, A], heuristic: Callable[[S], float]
) -> SearchResult[S, A]:
    """
    Greedy best-first: orders the frontier by h(n) alone.

    PT-BR: Rapido, porem NAO otimo — util para mostrar em aula por que o termo g(n)
           do A* importa.
    EN:    Fast but NOT optimal — useful in class to show why A*'s g(n) term matters.
    """
    start = problem.initial_state()
    counter = itertools.count()
    frontier: List[Tuple[float, int, S]] = [(heuristic(start), next(counter), start)]
    came_from: Dict[S, Tuple[Optional[S], Optional[A]]] = {start: (None, None)}
    cost_to: Dict[S, float] = {start: 0.0}
    visited: set = set()

    result: SearchResult[S, A] = SearchResult(algorithm="Greedy best-first", found=False)
    result.generated = 1
    result.peak_frontier = 1

    while frontier:
        _h, _seq, state = heapq.heappop(frontier)
        if state in visited:
            continue
        visited.add(state)
        result.expanded += 1
        result.expansion_order.append(state)

        if problem.is_goal(state):
            path, actions = _reconstruct(came_from, state)
            result.found = True
            result.path = path
            result.actions = actions
            result.cost = cost_to[state]
            return result

        for action, nxt, step_cost in problem.successors(state):
            result.generated += 1
            if nxt in visited or nxt in cost_to:
                continue
            cost_to[nxt] = cost_to[state] + step_cost
            came_from[nxt] = (state, action)
            heapq.heappush(frontier, (heuristic(nxt), next(counter), nxt))
        result.peak_frontier = max(result.peak_frontier, len(frontier))

    return result


def breadth_first(problem: SearchProblem[S, A]) -> SearchResult[S, A]:
    """
    Breadth-first search: fewest actions, ignoring cost.

    PT-BR: Otimo em numero de passos, nao em custo — a diferenca aparece
           claramente no backhaul, onde um salto de fibra e um salto de radio
           armazena-e-encaminha contam o mesmo aqui.
    EN:    Optimal in number of steps, not in cost — the difference is visible on the
           backhaul, where a fibre hop and a store-and-forward radio hop count alike.
    """
    start = problem.initial_state()
    result: SearchResult[S, A] = SearchResult(algorithm="Breadth-first", found=False)
    came_from: Dict[S, Tuple[Optional[S], Optional[A]]] = {start: (None, None)}
    cost_to: Dict[S, float] = {start: 0.0}

    if problem.is_goal(start):
        result.found, result.path = True, [start]
        return result

    frontier: deque = deque([start])
    discovered = {start}
    result.generated = 1
    result.peak_frontier = 1

    while frontier:
        state = frontier.popleft()
        result.expanded += 1
        result.expansion_order.append(state)

        for action, nxt, step_cost in problem.successors(state):
            result.generated += 1
            if nxt in discovered:
                continue
            discovered.add(nxt)
            came_from[nxt] = (state, action)
            cost_to[nxt] = cost_to[state] + step_cost
            if problem.is_goal(nxt):
                path, actions = _reconstruct(came_from, nxt)
                result.found = True
                result.path = path
                result.actions = actions
                result.cost = cost_to[nxt]
                return result
            frontier.append(nxt)
        result.peak_frontier = max(result.peak_frontier, len(frontier))

    return result


def depth_first(
    problem: SearchProblem[S, A], *, depth_limit: Optional[int] = None
) -> SearchResult[S, A]:
    """
    Depth-first search with cycle checking along the current branch.

    PT-BR: Nao e otimo nem completo em grafos infinitos; o limite de profundidade
           opcional torna a busca em profundidade limitada.
    EN:    Neither optimal nor complete on infinite graphs; the optional depth limit
           turns it into depth-limited search.
    """
    start = problem.initial_state()
    name = "Depth-first" if depth_limit is None else f"Depth-limited ({depth_limit})"
    result: SearchResult[S, A] = SearchResult(algorithm=name, found=False)

    # (state, path, actions, cost)
    stack: List[Tuple[S, List[S], List[A], float]] = [(start, [start], [], 0.0)]
    result.generated = 1
    result.peak_frontier = 1

    while stack:
        state, path, actions, cost = stack.pop()
        result.expanded += 1
        result.expansion_order.append(state)

        if problem.is_goal(state):
            result.found = True
            result.path = path
            result.actions = actions
            result.cost = cost
            return result

        if depth_limit is not None and len(actions) >= depth_limit:
            continue

        # reversed() so the first successor is explored first
        for action, nxt, step_cost in reversed(list(problem.successors(state))):
            result.generated += 1
            if nxt in path:
                continue  # cycle on this branch
            stack.append((nxt, path + [nxt], actions + [action], cost + step_cost))
        result.peak_frontier = max(result.peak_frontier, len(stack))

    return result


def iterative_deepening(
    problem: SearchProblem[S, A], *, max_depth: int = 50
) -> SearchResult[S, A]:
    """Iterative deepening: depth-first memory with breadth-first completeness."""
    total_expanded = total_generated = peak = 0
    for limit in range(max_depth + 1):
        attempt = depth_first(problem, depth_limit=limit)
        total_expanded += attempt.expanded
        total_generated += attempt.generated
        peak = max(peak, attempt.peak_frontier)
        if attempt.found:
            attempt.algorithm = f"Iterative deepening (depth {limit})"
            attempt.expanded = total_expanded
            attempt.generated = total_generated
            attempt.peak_frontier = peak
            return attempt
    failed: SearchResult[S, A] = SearchResult(
        algorithm="Iterative deepening", found=False
    )
    failed.expanded, failed.generated, failed.peak_frontier = (
        total_expanded,
        total_generated,
        peak,
    )
    return failed


def compare(
    problem: SearchProblem[S, A],
    heuristic: Optional[Callable[[S], float]] = None,
    *,
    algorithms: Optional[Sequence[str]] = None,
) -> List[SearchResult[S, A]]:
    """Run several strategies on the same problem for side-by-side comparison."""
    available: Dict[str, Callable[[], SearchResult[S, A]]] = {
        "bfs": lambda: breadth_first(problem),
        "dfs": lambda: depth_first(problem),
        "ids": lambda: iterative_deepening(problem),
        "ucs": lambda: uniform_cost(problem),
        "greedy": lambda: greedy_best_first(problem, heuristic or (lambda _s: 0.0)),
        "astar": lambda: astar(problem, heuristic),
    }
    chosen = algorithms or ("bfs", "dfs", "ucs", "greedy", "astar")
    unknown = [a for a in chosen if a not in available]
    if unknown:
        raise ValueError(f"unknown algorithm(s): {', '.join(unknown)}")
    return [available[a]() for a in chosen]
