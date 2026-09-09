"""
GPS — General Problem Solver: planning by means-ends analysis.

PT-BR: Reimplementacao didatica do GPS de Newell e Simon (1959). A ideia central e
       a ANALISE MEIOS-FINS: olhar a DIFERENCA entre o estado atual e o objetivo,
       escolher um operador que reduza essa diferenca e, recursivamente, resolver as
       precondicoes desse operador. O 'porque' de cada acao e, portanto, explicito:
       toda acao existe para eliminar uma diferenca concreta.

EN:    Didactic reimplementation of Newell and Simon's GPS (1959). Its central idea
       is MEANS-ENDS ANALYSIS: look at the DIFFERENCE between the current state and
       the goal, choose an operator that reduces that difference, and recursively
       solve that operator's preconditions. The 'why' of each action is therefore
       explicit: every action exists to remove a concrete difference.

Known limitations, stated honestly / Limitacoes conhecidas
---------------------------------------------------------
GPS is not complete and not optimal. It commits to the first operator that reduces
the difference and never revises that commitment except by backtracking on failure.
It is also subject to the *Sussman anomaly*: with interacting subgoals, achieving
them one at a time can undo earlier work. This is exactly why the A* forward planner
in :mod:`aisg.planning.forward` exists next to it — see ``docs/02-planning.md``.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Set, Tuple

from aisg.planning.strips import Action, Plan, Predicate, Problem, State


@dataclass
class GPSTrace:
    """Human-readable record of the means-ends reasoning."""

    lines: List[str] = field(default_factory=list)

    def log(self, depth: int, text: str) -> None:
        self.lines.append(f"{'  ' * depth}{text}")

    def render(self) -> str:
        return "\n".join(self.lines)


class GPSPlanner:
    """
    Means-ends analysis planner.

    PT-BR: ``max_depth`` limita a recursao e evita regressao infinita em dominios com
           precondicoes circulares.
    EN:    ``max_depth`` bounds the recursion and prevents infinite regression in
           domains with circular preconditions.
    """

    def __init__(self, problem: Problem, *, max_depth: int = 30, lang: str = "pt") -> None:
        self.problem = problem
        self.max_depth = max_depth
        self.lang = lang
        self.actions: List[Action] = problem.ground_actions()
        self.trace = GPSTrace()
        self._applied: List[Action] = []
        self._trajectory: List[State] = []
        self._considered = 0

    # -- public API -------------------------------------------------------
    def solve(self) -> Optional[Plan]:
        """Return a plan, or ``None`` when means-ends analysis fails."""
        self.trace = GPSTrace()
        self._applied = []
        self._trajectory = []
        self._considered = 0

        goals = sorted(self.problem.goal, key=str)
        self.trace.log(0, self._say(
            f"OBJETIVO: {', '.join(str(g) for g in goals)}",
            f"GOAL: {', '.join(str(g) for g in goals)}",
        ))
        final = self._achieve_all(self.problem.initial, goals, (), depth=0)
        if final is None:
            self.trace.log(0, self._say("FALHA: nenhum plano encontrado.", "FAILURE: no plan found."))
            return None

        plan = Plan(
            problem=self.problem,
            actions=list(self._applied),
            trajectory=list(self._trajectory),
            strategy="GPS (means-ends analysis)",
            stats={"actions_considered": float(self._considered)},
        )
        return plan

    # -- means-ends core --------------------------------------------------
    def _achieve_all(
        self, state: State, goals: Sequence[Predicate], stack: Tuple[Predicate, ...], depth: int
    ) -> Optional[State]:
        """
        Achieve every goal in turn, then re-check that none was undone.

        PT-BR: A reverificacao final e a defesa minima do GPS contra a anomalia de
               Sussman: se atingir o segundo objetivo desfez o primeiro, falhamos
               explicitamente em vez de devolver um plano invalido.
        EN:    The final re-check is GPS's minimal defence against the Sussman
               anomaly: if achieving the second goal undid the first, we fail
               explicitly instead of returning an invalid plan.
        """
        current = state
        for goal in goals:
            result = self._achieve(current, goal, stack, depth)
            if result is None:
                return None
            current = result

        unmet = [g for g in goals if g not in current]
        if unmet:
            self.trace.log(depth, self._say(
                f"CONFLITO: {', '.join(str(g) for g in unmet)} foi desfeito por um subobjetivo posterior.",
                f"CLOBBERED: {', '.join(str(g) for g in unmet)} was undone by a later subgoal.",
            ))
            return None
        return current

    def _achieve(
        self, state: State, goal: Predicate, stack: Tuple[Predicate, ...], depth: int
    ) -> Optional[State]:
        if depth > self.max_depth:
            self.trace.log(depth, self._say(
                f"limite de profundidade atingido em {goal}",
                f"depth limit reached at {goal}",
            ))
            return None

        if goal in state:
            self.trace.log(depth, self._say(
                f"ja satisfeito: {goal}", f"already satisfied: {goal}"
            ))
            return state

        if goal in stack:
            self.trace.log(depth, self._say(
                f"recursao em {goal} — abandonando este ramo",
                f"recursion on {goal} — abandoning this branch",
            ))
            return None

        self.trace.log(depth, self._say(
            f"DIFERENCA a reduzir: {goal}", f"DIFFERENCE to reduce: {goal}"
        ))

        for action in self._relevant_actions(goal):
            self._considered += 1
            self.trace.log(depth + 1, self._say(
                f"operador candidato: {action.name}", f"candidate operator: {action.name}"
            ))
            result = self._apply(state, action, goal, stack, depth + 1)
            if result is not None:
                return result

        self.trace.log(depth, self._say(
            f"nenhum operador reduz {goal}", f"no operator reduces {goal}"
        ))
        return None

    def _apply(
        self,
        state: State,
        action: Action,
        goal: Predicate,
        stack: Tuple[Predicate, ...],
        depth: int,
    ) -> Optional[State]:
        """Achieve the action's preconditions, then apply it."""
        preconditions = sorted(action.preconditions, key=str)
        if preconditions:
            self.trace.log(depth, self._say(
                f"precondicoes de {action.name}: {', '.join(str(p) for p in preconditions)}",
                f"preconditions of {action.name}: {', '.join(str(p) for p in preconditions)}",
            ))

        checkpoint_actions = len(self._applied)
        checkpoint_traj = len(self._trajectory)

        ready = self._achieve_all(state, preconditions, (goal,) + stack, depth + 1)
        if ready is None:
            # Undo any actions recorded while exploring this failed branch.
            del self._applied[checkpoint_actions:]
            del self._trajectory[checkpoint_traj:]
            return None

        if not action.applicable(ready):
            del self._applied[checkpoint_actions:]
            del self._trajectory[checkpoint_traj:]
            return None

        nxt = action.apply(ready)
        self._applied.append(action)
        self._trajectory.append(nxt)
        self.trace.log(depth, self._say(
            f"APLICA {action.name}  =>  {goal}", f"APPLY {action.name}  =>  {goal}"
        ))
        return nxt

    def _relevant_actions(self, goal: Predicate) -> List[Action]:
        """
        Actions whose add list contains the goal — the 'means' for this 'end'.

        Cheaper actions are tried first, so the first plan found is usually a
        reasonable one even though GPS gives no optimality guarantee.
        """
        relevant = [a for a in self.actions if goal in a.add_list]
        return sorted(relevant, key=lambda a: (a.cost, a.name))

    def _say(self, pt: str, en: str) -> str:
        return pt if self.lang == "pt" else en


def plan_with_gps(
    problem: Problem, *, max_depth: int = 30, lang: str = "pt"
) -> Tuple[Optional[Plan], GPSTrace]:
    """Convenience wrapper returning both the plan and the reasoning trace."""
    planner = GPSPlanner(problem, max_depth=max_depth, lang=lang)
    plan = planner.solve()
    return plan, planner.trace
