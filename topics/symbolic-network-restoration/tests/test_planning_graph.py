"""
Tests for the planning-graph analysis of the restoration domain.

These tests do two different jobs, and it is worth keeping them apart when
reading:

* Some check that the graph is BUILT correctly -- levels, no-ops, the three
  action mutex conditions, the fixpoint.
* The rest use the graph to assert PROPERTIES OF THE DOMAIN we wrote by hand.
  Those are the ones that earn the module its place: they turn statements that
  were previously prose in the documentation into assertions that fail when the
  domain drifts.
"""

from __future__ import annotations

import itertools

import pytest

from aisg.planning import (
    Operator,
    Predicate,
    Problem,
    build_operators,
    build_restoration_problem,
    make_state,
    plan_with_astar,
    plan_with_gps,
    problem_from_diagnosis,
)
from aisg.planning.planning_graph import (
    analyse,
    build_planning_graph,
    is_noop,
)

FIELD_FAULTS = ("interference", "misaligned", "power-failed", "relay-down",
                "vlan-wrong", "transient")
SIMULATED_FAULTS = ("excess-path-loss", "mac-contention", "node-stopped",
                    "route-missing")
SIMULATED_DIAGNOSES = ("excess_path_loss", "mac_contention", "node_failure",
                       "routing_misconfiguration")


def _restoration(faults, simulated=True, node="N"):
    return build_restoration_problem(node=node, faults=faults, simulated=simulated,
                                     alternate_route=True)


# --- graph construction ----------------------------------------------------
def test_level_zero_is_the_initial_state():
    problem = problem_from_diagnosis("excess_path_loss", "AP_C")
    graph = build_planning_graph(problem)
    assert graph.propositions[0] == frozenset(problem.initial)
    assert graph.proposition_mutex[0] == frozenset()


def test_the_graph_levels_off():
    """The fixpoint must be reached well inside the safety valve."""
    problem = _restoration(("excess-path-loss", "mac-contention"))
    graph = build_planning_graph(problem)
    assert 0 < graph.levelled_off_at < 32
    # once levelled off, the last two proposition levels agree
    assert graph.propositions[-1] == graph.propositions[-2]


def test_propositions_never_disappear_from_the_graph():
    """
    No-op maintenance actions make proposition levels monotonically increasing.

    This is the relaxation that makes a planning graph a lower bound rather than
    an exact answer, so it is worth pinning down.
    """
    problem = _restoration(("excess-path-loss", "mac-contention"))
    graph = build_planning_graph(problem)
    for earlier, later in zip(graph.propositions, graph.propositions[1:]):
        assert earlier <= later


def test_noops_are_generated_and_recognised():
    problem = problem_from_diagnosis("routing_misconfiguration", "AP_C")
    graph = build_planning_graph(problem)
    noops = [a for a in graph.actions[0] if is_noop(a)]
    assert {next(iter(a.add_list)) for a in noops} == frozenset(problem.initial)


def test_inconsistent_effects_produce_an_action_mutex():
    """stop_run deletes run-active; start_run adds it. They must be mutex."""
    problem = _restoration(("excess-path-loss",))
    graph = build_planning_graph(problem)
    for level in graph.actions:
        names = {a.operator.name: a for a in level}
        if "stop_run" in names and "start_run" in names:
            pair = frozenset({names["stop_run"], names["start_run"]})
            index = graph.actions.index(level)
            assert pair in graph.action_mutex[index]
            return
    pytest.skip("stop_run and start_run never share a level in this problem")


# --- the lower bound -------------------------------------------------------
@pytest.mark.parametrize("diagnosis", SIMULATED_DIAGNOSES)
def test_graph_level_is_a_lower_bound_on_the_plan_a_star_finds(diagnosis):
    """
    The level at which the goal first appears non-mutex can never exceed the
    length of a real plan. This is an optimality check that shares no code with
    either planner, in the same way Floyd-Warshall checks A* on the topology.
    """
    problem = problem_from_diagnosis(diagnosis, "AP_C")
    graph = build_planning_graph(problem)
    bound = graph.first_level_satisfying(problem.goal)
    plan, _ = plan_with_astar(problem)
    assert bound is not None
    assert bound <= len(plan.actions)


def test_an_unreachable_goal_has_no_level():
    problem = Problem(
        name="unreachable",
        operators=[Operator.build("noop_op", parameters=("?n",),
                                  preconditions=("a(?n)",), add=("b(?n)",))],
        initial=make_state(["a(N)"]),
        goal=make_state(["z(N)"]),
        objects={"node": ["N"]},
        parameter_types={"?n": "node"},
    )
    graph = build_planning_graph(problem)
    assert graph.first_level_satisfying(problem.goal) is None
    assert analyse(problem).goal_reachable is False


# --- properties of the domain we wrote -------------------------------------
def test_the_restoration_domain_has_no_choice_points():
    """
    No literal in the domain has more than one achieving operator.

    PT-BR: E a explicacao ESTRUTURAL de por que o GPS nunca perde para o A*
           neste dominio: a analise meios-fins nao tem escolha para errar.
    EN:    This is the STRUCTURAL reason GPS never loses to A* in this domain:
           means-ends analysis has no choice to get wrong.

    If this test ever fails, that is not a regression -- it means the domain
    finally became rich enough for the GPS/A* comparison to be interesting, and
    the claim in the planning slides needs revisiting.
    """
    for faults, simulated in ((FIELD_FAULTS, False), (SIMULATED_FAULTS, True)):
        problem = _restoration(faults, simulated=simulated)
        assert analyse(problem).choice_points == {}


def test_gps_matches_a_star_on_every_solvable_fault_combination():
    """The empirical companion to the structural result above."""
    compared = 0
    for pool, simulated in ((FIELD_FAULTS, False), (SIMULATED_FAULTS, True)):
        for size in (1, 2, 3):
            for combo in itertools.combinations(pool, size):
                problem = _restoration(combo, simulated=simulated)
                astar_plan, _ = plan_with_astar(problem)
                gps_plan, _ = plan_with_gps(problem)
                if astar_plan is None or gps_plan is None:
                    continue
                compared += 1
                assert gps_plan.cost == astar_plan.cost
    assert compared == 55


def test_crew_operators_are_dead_in_the_simulated_scenario():
    """
    A simulated run has no field crew, so nothing ever establishes crew-at.

    The operators remain on offer, which is harmless for correctness -- they
    simply never fire -- but the graph is what tells us so without having to
    read the operator list by hand.
    """
    problem = _restoration(SIMULATED_FAULTS, simulated=True)
    dead = set(analyse(problem).dead_operators)
    assert {"dispatch_crew", "realign_antenna"} <= dead


# --- the success invariant -------------------------------------------------
@pytest.mark.parametrize("faults", [
    ("excess-path-loss",),
    ("mac-contention",),
    ("excess-path-loss", "mac-contention"),
    ("excess-path-loss", "mac-contention", "node-stopped"),
])
def test_success_is_mutex_with_every_live_fault(faults):
    """
    The domain must not permit declaring service restored over a live fault.

    PT-BR: Este e o invariante que a correcao dos literais cleared-<falha> por
           falha estabeleceu. Antes dela, um plano podia relatar servico
           restaurado com uma falha ainda ativa.
    EN:    This is the invariant established by the per-fault cleared-<fault>
           literals. Before that fix, a plan could report service restored with
           a fault still live.
    """
    problem = _restoration(faults)
    result = analyse(
        problem,
        success=Predicate("service-restored", ("N",)),
        fault_literals=[Predicate(f, ("N",)) for f in faults],
    )
    assert result.success_invariant_violations == ()


def _two_fault_domain(*, shared_cleared: bool) -> Problem:
    """
    A minimal reconstruction of the domain shape before and after the fix.

    ``shared_cleared=True`` is the pre-fix shape: a single fault-cleared literal
    that ANY repair satisfies, so verifying needs only one of two repairs.
    """
    def cleared(fault: str) -> str:
        return "fault-cleared(?n)" if shared_cleared else f"cleared-{fault}(?n)"

    operators = [
        Operator.build("fix_a", parameters=("?n",), preconditions=("fault-a(?n)",),
                       add=(cleared("fault-a"),), delete=("fault-a(?n)",)),
        Operator.build("fix_b", parameters=("?n",), preconditions=("fault-b(?n)",),
                       add=(cleared("fault-b"),), delete=("fault-b(?n)",)),
        Operator.build("verify", parameters=("?n",),
                       preconditions=tuple({cleared("fault-a"), cleared("fault-b")}),
                       add=("service-restored(?n)",)),
    ]
    return Problem(
        name=f"two-fault(shared={shared_cleared})",
        operators=operators,
        initial=make_state(["fault-a(N)", "fault-b(N)"]),
        goal=make_state(["service-restored(N)"]),
        objects={"node": ["N"]},
        parameter_types={"?n": "node"},
    )


def test_the_analysis_detects_the_multi_fault_defect():
    """
    Regression guard, stated as a property rather than as a single bad plan.

    The reported bug was a plan that announced service restored while a power
    failure remained. In planning-graph terms the defect is a MISSING MUTEX:
    service-restored is compatible with a live fault. Reconstructing the pre-fix
    domain shape must reproduce that, and the fixed shape must not.
    """
    faults = [Predicate("fault-a", ("N",)), Predicate("fault-b", ("N",))]
    success = Predicate("service-restored", ("N",))

    broken = analyse(_two_fault_domain(shared_cleared=True),
                     success=success, fault_literals=faults)
    assert len(broken.success_invariant_violations) == 2
    # and the graph also names the cause: one literal, two achievers
    assert broken.choice_points == {"fault-cleared(N)": ("fix_a", "fix_b")}

    fixed = analyse(_two_fault_domain(shared_cleared=False),
                    success=success, fault_literals=faults)
    assert fixed.success_invariant_violations == ()
    assert fixed.choice_points == {}


def test_analysis_renders_in_both_languages():
    problem = _restoration(("mac-contention",))
    result = analyse(problem)
    assert "Analise do grafo" in result.render("pt")
    assert "Planning-graph analysis" in result.render("en")
