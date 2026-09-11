"""
Planning-graph analysis of a STRIPS domain (Graphplan, Blum & Furst 1997).

PT-BR: Este modulo NAO e um quarto planejador. Ele constroi o grafo de
       planejamento -- niveis alternados de proposicoes e acoes, carregando
       relacoes de exclusao mutua -- e usa esse grafo para INTERROGAR o dominio
       que escrevemos a mao. O grafo se constroi em tempo polinomial e nao
       precisa da busca regressiva do Graphplan para ser util.

       As quatro perguntas que respondemos com ele estao em ``analyse``:
       operadores mortos, pontos de escolha, invariante de sucesso, e um limite
       inferior para o tamanho do plano.

EN:    This module is NOT a fourth planner. It builds the planning graph --
       alternating proposition and action levels carrying mutual-exclusion
       relations -- and uses that graph to INTERROGATE the domain we wrote by
       hand. The graph is polynomial to build and is useful without running
       Graphplan's backward search.

       The four questions we ask of it live in ``analyse``: dead operators,
       choice points, the success invariant, and a lower bound on plan length.

A caveat that belongs next to every result this module produces: the planning
graph is a RELAXATION. It ignores delete lists when propagating reachability,
so "reachable in the graph" is a necessary condition for reachability, never a
sufficient one. A level is therefore a lower bound on plan length, and a
proposition absent from the graph is genuinely unreachable, but a proposition
present in it may still be unreachable in the real state space.

Graphplan also minimises LEVELS, not cost. It cannot rank the plans that
``plan_with_astar`` ranks, and no function here tries to.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, FrozenSet, Iterable, List, Optional, Sequence, Set, Tuple

from aisg.planning.strips import Action, Operator, Predicate, Problem, State

#: A mutex pair. Always a two-element frozenset.
MutexPair = FrozenSet[object]

#: Safety valve: the graph levels off long before this in any domain we ship.
MAX_LEVELS = 64


def _noop(proposition: Predicate) -> Action:
    """
    A maintenance action carrying one proposition to the next level.

    PT-BR: O no-op precisa de nome unico: a igualdade de ``Action`` usa o nome do
           operador e a ligacao, e todos os no-ops teriam a ligacao vazia.
    EN:    The no-op needs a unique name: ``Action`` equality uses the operator
           name and the binding, and every no-op would share an empty binding.
    """
    operator = Operator(
        name=f"noop[{proposition}]",
        parameters=(),
        preconditions=frozenset({proposition}),
        add_list=frozenset({proposition}),
        delete_list=frozenset(),
        cost=0.0,
        description_pt=f"Manter {proposition} verdadeiro.",
        description_en=f"Keep {proposition} true.",
    )
    return Action(
        operator=operator,
        binding={},
        preconditions=frozenset({proposition}),
        add_list=frozenset({proposition}),
        delete_list=frozenset(),
    )


def is_noop(action: Action) -> bool:
    return action.operator.name.startswith("noop[")


@dataclass(frozen=True)
class PlanningGraph:
    """
    The levelled graph itself.

    ``propositions[i]`` is the proposition level *i*; ``actions[i]`` is the
    action level between proposition levels *i* and *i+1*. Both mutex lists are
    indexed to match.
    """

    problem: Problem
    propositions: Tuple[FrozenSet[Predicate], ...]
    proposition_mutex: Tuple[FrozenSet[MutexPair], ...]
    actions: Tuple[FrozenSet[Action], ...]
    action_mutex: Tuple[FrozenSet[MutexPair], ...]
    #: the level at which the graph stopped changing
    levelled_off_at: int

    # -- queries ---------------------------------------------------------
    @property
    def depth(self) -> int:
        """Number of proposition levels."""
        return len(self.propositions)

    def mutex(self, level: int, one: Predicate, other: Predicate) -> bool:
        """Are two propositions mutually exclusive at ``level``?"""
        if one == other:
            return False
        return frozenset({one, other}) in self.proposition_mutex[level]

    def first_level_satisfying(self, goal: Iterable[Predicate]) -> Optional[int]:
        """
        The first level where every goal atom is present and no two are mutex.

        PT-BR: E um LIMITE INFERIOR para o numero de passos paralelos, nao uma
               promessa de que exista plano desse tamanho.
        EN:    This is a LOWER BOUND on the number of parallel steps, not a
               promise that a plan of that length exists.
        """
        goal = frozenset(goal)
        for level in range(self.depth):
            if not goal <= self.propositions[level]:
                continue
            atoms = sorted(goal, key=str)
            if any(
                self.mutex(level, atoms[i], atoms[j])
                for i in range(len(atoms))
                for j in range(i + 1, len(atoms))
            ):
                continue
            return level
        return None

    def operator_names_used(self) -> Set[str]:
        """Operators that appear, ground, in at least one action level."""
        return {
            action.operator.name
            for level in self.actions
            for action in level
            if not is_noop(action)
        }

    def achievers(self, level: int, proposition: Predicate) -> FrozenSet[Action]:
        """Non-no-op actions at ``level`` whose add list contains ``proposition``."""
        return frozenset(
            action
            for action in self.actions[level]
            if proposition in action.add_list and not is_noop(action)
        )


def build_planning_graph(problem: Problem, *, max_levels: int = MAX_LEVELS) -> PlanningGraph:
    """
    Expand the planning graph until it levels off, or until ``max_levels``.

    PT-BR: Para no ponto fixo: quando o conjunto de proposicoes E o conjunto de
           mutexes deixam de mudar, nenhum nivel adicional acrescenta informacao.
    EN:    Stops at the fixpoint: once the proposition set AND the mutex set stop
           changing, no further level adds information.
    """
    ground = problem.ground_actions()

    prop_levels: List[FrozenSet[Predicate]] = [frozenset(problem.initial)]
    prop_mutex: List[FrozenSet[MutexPair]] = [frozenset()]
    action_levels: List[FrozenSet[Action]] = []
    action_mutex: List[FrozenSet[MutexPair]] = []

    levelled_off_at = 0
    for level in range(max_levels):
        available = prop_levels[level]
        mutex_here = prop_mutex[level]

        applicable = [a for a in ground if a.preconditions <= available]
        applicable += [_noop(p) for p in available]
        applicable_set = frozenset(applicable)

        pair_mutex = _action_mutex(applicable, mutex_here)
        action_levels.append(applicable_set)
        action_mutex.append(pair_mutex)

        next_props = frozenset(p for a in applicable for p in a.add_list)
        next_mutex = _proposition_mutex(next_props, applicable, pair_mutex)

        prop_levels.append(next_props)
        prop_mutex.append(next_mutex)

        if next_props == available and next_mutex == mutex_here:
            levelled_off_at = level
            break
        levelled_off_at = level + 1

    return PlanningGraph(
        problem=problem,
        propositions=tuple(prop_levels),
        proposition_mutex=tuple(prop_mutex),
        actions=tuple(action_levels),
        action_mutex=tuple(action_mutex),
        levelled_off_at=levelled_off_at,
    )


def _action_mutex(
    actions: Sequence[Action], proposition_mutex: FrozenSet[MutexPair]
) -> FrozenSet[MutexPair]:
    """
    The three classical action mutex conditions.

    PT-BR: efeitos inconsistentes, interferencia, e necessidades concorrentes.
    EN:    inconsistent effects, interference, and competing needs.
    """
    pairs: Set[MutexPair] = set()
    for i, one in enumerate(actions):
        for other in actions[i + 1 :]:
            # inconsistent effects: one deletes what the other adds
            if one.delete_list & other.add_list or other.delete_list & one.add_list:
                pairs.add(frozenset({one, other}))
                continue
            # interference: one deletes a precondition of the other
            if one.delete_list & other.preconditions or other.delete_list & one.preconditions:
                pairs.add(frozenset({one, other}))
                continue
            # competing needs: their preconditions are mutex at this level
            if any(
                frozenset({p, q}) in proposition_mutex
                for p in one.preconditions
                for q in other.preconditions
                if p != q
            ):
                pairs.add(frozenset({one, other}))
    return frozenset(pairs)


def _proposition_mutex(
    propositions: FrozenSet[Predicate],
    actions: Sequence[Action],
    action_mutex: FrozenSet[MutexPair],
) -> FrozenSet[MutexPair]:
    """
    Two propositions are mutex when EVERY way of achieving them together clashes.

    PT-BR: Se existe uma unica acao que produz as duas, ou um par de acoes nao
           mutuamente exclusivas, entao as proposicoes sao compativeis.
    EN:    If a single action produces both, or any pair of non-mutex actions
           does, the propositions are compatible.
    """
    by_proposition: Dict[Predicate, List[Action]] = {p: [] for p in propositions}
    for action in actions:
        for produced in action.add_list:
            if produced in by_proposition:
                by_proposition[produced].append(action)

    ordered = sorted(propositions, key=str)
    pairs: Set[MutexPair] = set()
    for i, one in enumerate(ordered):
        for other in ordered[i + 1 :]:
            producers_one = by_proposition[one]
            producers_other = by_proposition[other]
            compatible = any(
                a is b or frozenset({a, b}) not in action_mutex
                for a in producers_one
                for b in producers_other
            )
            if not compatible:
                pairs.add(frozenset({one, other}))
    return frozenset(pairs)


# --------------------------------------------------------------------------
# The four domain questions
# --------------------------------------------------------------------------
@dataclass
class DomainAnalysis:
    """What the planning graph says about a hand-written domain."""

    problem_name: str
    #: operators offered by the problem that can never fire
    dead_operators: Tuple[str, ...] = ()
    #: proposition -> the operators that can produce it, where there is more than one
    choice_points: Dict[str, Tuple[str, ...]] = field(default_factory=dict)
    #: fault literals the success literal is NOT mutex with, i.e. states the
    #: domain permits in which we declare success with the fault still live
    success_invariant_violations: Tuple[str, ...] = ()
    #: lower bound on the number of parallel steps, or None if unreachable
    goal_lower_bound: Optional[int] = None
    #: level at which the graph stopped changing
    levelled_off_at: int = 0

    @property
    def goal_reachable(self) -> bool:
        return self.goal_lower_bound is not None

    def render(self, lang: str = "pt") -> str:
        pt = lang == "pt"
        lines: List[str] = []
        head = "Analise do grafo de planejamento" if pt else "Planning-graph analysis"
        lines.append(f"{head}: {self.problem_name}")
        lines.append("-" * (len(head) + len(self.problem_name) + 2))

        label = "ponto fixo no nivel" if pt else "levelled off at level"
        lines.append(f"{label}: {self.levelled_off_at}")

        label = "limite inferior do plano" if pt else "plan lower bound"
        value = self.goal_lower_bound
        lines.append(
            f"{label}: {'inalcancavel' if value is None and pt else 'unreachable' if value is None else value}"
        )

        label = "operadores mortos" if pt else "dead operators"
        lines.append(f"{label}: {', '.join(self.dead_operators) or ('nenhum' if pt else 'none')}")

        label = "pontos de escolha" if pt else "choice points"
        if self.choice_points:
            lines.append(f"{label}:")
            for proposition, producers in sorted(self.choice_points.items()):
                lines.append(f"  {proposition} <- {', '.join(producers)}")
        else:
            lines.append(f"{label}: {'nenhum' if pt else 'none'}")

        label = (
            "violacoes do invariante de sucesso" if pt else "success invariant violations"
        )
        if self.success_invariant_violations:
            lines.append(f"{label}:")
            for violation in self.success_invariant_violations:
                lines.append(f"  {violation}")
        else:
            lines.append(f"{label}: {'nenhuma' if pt else 'none'}")
        return "\n".join(lines)


def analyse(
    problem: Problem,
    *,
    success: Optional[Predicate] = None,
    fault_literals: Iterable[Predicate] = (),
    max_levels: int = MAX_LEVELS,
) -> DomainAnalysis:
    """
    Interrogate a STRIPS domain through its planning graph.

    ``success`` and ``fault_literals`` drive the third check: at the fixpoint,
    the literal that declares the job done must be mutually exclusive with every
    fault literal that is still live. If it is not, the domain permits a plan
    that reports success over an unrepaired fault -- which is precisely the
    defect that per-fault ``cleared-<fault>`` literals were introduced to fix.
    """
    graph = build_planning_graph(problem, max_levels=max_levels)

    offered = {op.name for op in problem.operators}
    dead = tuple(sorted(offered - graph.operator_names_used()))

    fixpoint = min(graph.levelled_off_at, len(graph.actions) - 1)
    producers: Dict[Predicate, Set[str]] = {}
    for level in graph.actions:
        for action in level:
            if is_noop(action):
                continue
            for produced in action.add_list:
                producers.setdefault(produced, set()).add(action.operator.name)
    choice_points = {
        str(proposition): tuple(sorted(names))
        for proposition, names in producers.items()
        if len(names) > 1
    }

    violations: List[str] = []
    if success is not None:
        prop_fixpoint = min(graph.levelled_off_at, graph.depth - 1)
        for fault in fault_literals:
            present = (
                success in graph.propositions[prop_fixpoint]
                and fault in graph.propositions[prop_fixpoint]
            )
            if present and not graph.mutex(prop_fixpoint, success, fault):
                violations.append(f"{success} is not mutex with {fault}")

    return DomainAnalysis(
        problem_name=problem.name,
        dead_operators=dead,
        choice_points=choice_points,
        success_invariant_violations=tuple(violations),
        goal_lower_bound=graph.first_level_satisfying(problem.goal),
        levelled_off_at=fixpoint,
    )
