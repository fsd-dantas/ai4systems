"""
Forward state-space planning driven by the SAME A* used for network routing.

PT-BR: O planejador progressivo trata o planejamento como busca: o estado e o
       conjunto de literais verdadeiros, a acao sucessora e qualquer acao aplicavel e
       o teste de objetivo e a inclusao do objetivo no estado. Isso permite reutilizar
       literalmente o mesmo A* do terceiro trabalho — a mesma funcao, sem copia.

EN:    The progression planner treats planning as search: a state is the set of true
       literals, a successor is any applicable action, and the goal test is goal
       inclusion. This lets us reuse literally the same A* as the third assignment —
       the same function, not a copy.

Heuristics / Heuristicas
------------------------
``goal_count``  h(s) = number of unsatisfied goal literals.
    Admissible **only if** no single action can satisfy more than one goal literal
    and every action costs at least 1. In the restoration domain that holds: the two
    goal literals, ``service-restored`` and ``logged``, are added by different
    operators, each of unit cost. We state the condition rather than assume it — an
    inadmissible heuristic would silently cost us optimality.

``zero``        h(s) = 0, turning A* into uniform-cost search. Useful as the control
    condition when measuring how much the heuristic actually saves.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable, List, Optional, Tuple

from aisg.planning.strips import Action, Plan, Problem, State
from aisg.search.algorithms import SearchResult, astar


@dataclass
class PlanningProblem:
    """Adapts a STRIPS problem to the generic search-problem interface."""

    problem: Problem

    def __post_init__(self) -> None:
        self._actions: List[Action] = self.problem.ground_actions()

    @property
    def actions(self) -> List[Action]:
        return self._actions

    # -- SearchProblem interface -----------------------------------------
    def initial_state(self) -> State:
        return self.problem.initial

    def is_goal(self, state: State) -> bool:
        return self.problem.is_goal(state)

    def successors(self, state: State) -> Iterable[Tuple[Action, State, float]]:
        for action in self._actions:
            if action.applicable(state):
                yield (action, action.apply(state), action.cost)


def goal_count_heuristic(problem: Problem) -> Callable[[State], float]:
    """h(s) = number of goal literals not yet true. See the module docstring."""

    def h(state: State) -> float:
        return float(len(problem.goal - state))

    return h


def zero_heuristic(_problem: Problem) -> Callable[[State], float]:
    """h(s) = 0 — makes A* behave as uniform-cost search."""
    return lambda _state: 0.0


def plan_with_astar(
    problem: Problem, *, heuristic: str = "goal_count"
) -> Tuple[Optional[Plan], SearchResult]:
    """
    Find a cost-optimal plan by A* progression search.

    PT-BR: Retorna o plano e o resultado bruto da busca, para que a apresentacao possa
           mostrar nos expandidos e gerados lado a lado com o A* de roteamento.
    EN:    Returns the plan and the raw search result, so the presentation can show
           expanded and generated nodes side by side with the routing A*.
    """
    builders = {"goal_count": goal_count_heuristic, "zero": zero_heuristic}
    if heuristic not in builders:
        raise ValueError(
            f"unknown heuristic {heuristic!r}; choose from {', '.join(builders)}"
        )

    search_problem = PlanningProblem(problem)
    h = builders[heuristic](problem)
    result = astar(search_problem, h, name=f"A* progression ({heuristic})")

    if not result.found:
        return None, result

    plan = Plan(
        problem=problem,
        actions=list(result.actions),
        trajectory=list(result.path[1:]),
        strategy=result.algorithm,
        stats={
            "expanded": float(result.expanded),
            "generated": float(result.generated),
            "peak_frontier": float(result.peak_frontier),
        },
    )
    return plan, result
