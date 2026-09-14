"""Tests for the STRIPS representation, the GPS solver, and the A* planner."""

from __future__ import annotations

import pytest

from aisg.domain import load_default_topology
from aisg.planning import (
    DIAGNOSIS_TO_FAULT,
    Operator,
    Predicate,
    Problem,
    build_restoration_problem,
    make_state,
    plan_with_astar,
    plan_with_gps,
    problem_from_diagnosis,
)

#: The node the tests restore: a store-and-forward relay of the 60-node scenario.
#: It carries other sites' traffic, so a congestion there has somewhere to go.
NODE = "SAF_01"


@pytest.fixture
def topology():
    return load_default_topology()


# --- STRIPS representation -------------------------------------------------
def test_predicate_parsing_round_trips():
    predicate = Predicate.parse("authorized(N1)")
    assert predicate.name == "authorized"
    assert predicate.args == ("N1",)
    assert str(predicate) == "authorized(N1)"


def test_predicate_parsing_rejects_malformed_text():
    with pytest.raises(ValueError, match="malformed predicate"):
        Predicate.parse("authorized(N1")


def test_variables_are_detected_by_the_question_mark():
    assert Predicate.parse("at(?crew, ?site)").variables == ("?crew", "?site")
    assert Predicate.parse("at(CREW, SITE)").is_ground


def test_operator_rejects_a_variable_not_declared_as_a_parameter():
    with pytest.raises(ValueError, match="not declared as parameters"):
        Operator.build("bad", parameters=("?a",), preconditions=("p(?b)",), add=("q(?a)",))


def test_operator_rejects_a_literal_in_both_add_and_delete_lists():
    with pytest.raises(ValueError, match="both the add and the delete list"):
        Operator.build("bad", parameters=("?a",), preconditions=("p(?a)",),
                       add=("q(?a)",), delete=("q(?a)",))


def test_state_must_be_ground():
    with pytest.raises(ValueError, match="only contain ground atoms"):
        make_state(["at(?x)"])


def test_applying_an_action_adds_and_deletes_correctly():
    problem = build_restoration_problem("N1", ["interference"])
    action = next(a for a in problem.ground_actions() if a.name == "request_authorization(N1)")
    result = action.apply(problem.initial)
    assert Predicate.parse("authorized(N1)") in result
    assert Predicate.parse("diagnosed(N1)") in result  # not in the delete list


def test_inapplicable_action_raises_with_the_missing_precondition():
    problem = build_restoration_problem("N1", ["interference"])
    action = next(a for a in problem.ground_actions() if a.name == "change_channel(N1)")
    with pytest.raises(ValueError, match="authorized"):
        action.apply(problem.initial)  # authorisation not yet requested


def test_a_binding_filter_removes_unwanted_groundings():
    problem = Problem(
        name="move",
        operators=[Operator.build("move", parameters=("?a", "?b"), preconditions=("at(?a)",),
                                  add=("at(?b)",), delete=("at(?a)",))],
        initial=make_state(["at(X)"]),
        goal=make_state(["at(Y)"]),
        objects={"place": ["X", "Y"]},
        parameter_types={"?a": "place", "?b": "place"},
        binding_filter=lambda _name, binding: binding["?a"] != binding["?b"],
    )
    names = {a.name for a in problem.ground_actions()}
    assert "move(X, X)" not in names
    assert "move(X, Y)" in names


# --- both planners ---------------------------------------------------------
@pytest.mark.parametrize("diagnosis", sorted(DIAGNOSIS_TO_FAULT))
def test_both_planners_solve_every_diagnosis(diagnosis, topology):
    problem = problem_from_diagnosis(diagnosis, NODE, topology=topology)

    gps_plan, _trace = plan_with_gps(problem, lang="en")
    astar_plan, _result = plan_with_astar(problem)

    assert gps_plan is not None, f"GPS failed on {diagnosis}"
    assert astar_plan is not None, f"A* failed on {diagnosis}"
    assert gps_plan.validate()[0], f"GPS plan invalid on {diagnosis}"
    assert astar_plan.validate()[0], f"A* plan invalid on {diagnosis}"


@pytest.mark.parametrize("diagnosis", sorted(DIAGNOSIS_TO_FAULT))
def test_astar_plan_is_never_more_expensive_than_the_gps_plan(diagnosis, topology):
    """A* is cost-optimal; GPS offers no such guarantee."""
    problem = problem_from_diagnosis(diagnosis, NODE, topology=topology)
    gps_plan, _ = plan_with_gps(problem, lang="en")
    astar_plan, _ = plan_with_astar(problem)
    assert astar_plan.cost <= gps_plan.cost + 1e-9


def test_plan_validation_catches_a_corrupted_plan(topology):
    problem = problem_from_diagnosis("mac_contention", NODE, topology=topology)
    plan, _ = plan_with_astar(problem)
    plan.actions.pop(0)  # remove request_authorization
    ok, reason = plan.validate()
    assert not ok
    assert "not applicable" in reason


def test_plan_validation_catches_a_plan_that_stops_short(topology):
    problem = problem_from_diagnosis("rf_interference", NODE, topology=topology)
    plan, _ = plan_with_astar(problem)
    plan.actions.pop()  # remove close_work_order
    ok, reason = plan.validate()
    assert not ok
    assert "does not satisfy the goal" in reason


# --- governance invariants encoded as preconditions ------------------------
@pytest.mark.parametrize("diagnosis", sorted(DIAGNOSIS_TO_FAULT))
def test_no_scenario_changing_action_precedes_authorisation(diagnosis, topology):
    """
    PT-BR: Invariante de governanca: nenhuma acao que altera o cenario pode aparecer
           antes da autorizacao. Nao e recomendacao, e precondicao.
    """
    exempt = {"request_authorization", "verify_link", "record_logbook", "close_work_order"}
    problem = problem_from_diagnosis(diagnosis, NODE, topology=topology)
    plan, _ = plan_with_astar(problem)

    authorised = False
    for action in plan.actions:
        if action.operator.name == "request_authorization":
            authorised = True
            continue
        if action.operator.name not in exempt:
            assert authorised, f"{action.name} ran before authorisation"


def test_every_plan_records_the_logbook_before_closing(topology):
    for diagnosis in DIAGNOSIS_TO_FAULT:
        problem = problem_from_diagnosis(diagnosis, NODE, topology=topology)
        plan, _ = plan_with_astar(problem)
        names = [a.operator.name for a in plan.actions]
        assert names.index("record_logbook") < names.index("close_work_order"), diagnosis


# --- multiple faults on one node ------------------------------------------
def _remaining_faults(problem, plan):
    """Fault literals still true after executing the plan."""
    from aisg.planning.domain_restoration import KNOWN_FAULTS

    state = problem.initial
    for action in plan.actions:
        state = action.apply(state)
    return sorted(str(p) for p in state if p.name in KNOWN_FAULTS)


@pytest.mark.parametrize(
    "faults",
    [
        ["interference", "node-stopped"],
        ["mac-contention", "route-missing"],
        ["mac-contention", "excess-path-loss", "relay-down"],
        ["congested", "interference"],
    ],
)
def test_a_plan_never_closes_the_work_order_with_a_fault_still_present(faults):
    """
    PT-BR: Regressao. Com um sinalizador unico 'fault-cleared', reparar UMA falha
           entre varias liberava a verificacao e o plano fechava a ordem de servico
           com o defeito ainda presente — e a validacao passava, porque o objetivo
           realmente estava satisfeito.
    EN:    Regression. With a single shared 'fault-cleared' flag, repairing ONE
           fault among several unlocked verification and the plan closed the work
           order with the defect still in place — and validation passed, because
           the goal genuinely was satisfied.
    """
    problem = build_restoration_problem("N1", faults, alternate_route=True)
    plan, _ = plan_with_astar(problem)

    assert plan is not None
    assert plan.validate()[0]
    assert _remaining_faults(problem, plan) == []


def test_verification_is_blocked_until_every_fault_is_cleared():
    """verify_link must not be applicable while any diagnosed fault remains."""
    problem = build_restoration_problem("N1", ["interference", "node-stopped"])
    verify = next(a for a in problem.ground_actions() if a.name == "verify_link(N1)")

    # Clear only the interference, exactly as the shared-flag version did.
    state = problem.initial
    for name in ("request_authorization(N1)", "change_channel(N1)"):
        action = next(a for a in problem.ground_actions() if a.name == name)
        state = action.apply(state)

    assert Predicate.parse("node-stopped(N1)") in state
    assert not verify.applicable(state), "verification unlocked with a fault outstanding"


def test_gps_and_astar_agree_on_multiple_faults():
    problem = build_restoration_problem("N1", ["interference", "node-stopped"])
    gps_plan, _ = plan_with_gps(problem, lang="en")
    astar_plan, _ = plan_with_astar(problem)

    assert gps_plan is not None and astar_plan is not None
    assert _remaining_faults(problem, gps_plan) == []
    assert _remaining_faults(problem, astar_plan) == []


def test_no_restoration_is_claimed_when_one_fault_cannot_be_resolved():
    """
    PT-BR: Com duas falhas em que uma nao tem reparo disponivel — congestionamento
           sem rota alternativa — o planejador deve FALHAR, e nao reparar a outra
           e declarar servico restaurado. E a garantia que a correcao do
           sinalizador unico existe para dar.
    EN:    With two faults where one has no available repair - congestion with no
           alternative route - the planner must FAIL rather than repair the other
           and declare service restored. This is the guarantee the shared-flag fix
           exists to provide.
    """
    problem = build_restoration_problem(
        "N1", ["interference", "congested"], alternate_route=False
    )
    astar_plan, _ = plan_with_astar(problem)
    gps_plan, _ = plan_with_gps(problem, lang="en")

    assert astar_plan is None, "A* restored service with an unresolvable fault"
    assert gps_plan is None, "GPS restored service with an unresolvable fault"


def test_unknown_fault_is_rejected_rather_than_silently_unplannable():
    with pytest.raises(ValueError, match="unknown fault"):
        build_restoration_problem("N1", ["gremlins"])


# --- integration with A* routing ------------------------------------------
def test_rerouting_is_only_planned_when_a_real_alternative_route_exists(topology):
    """The planner's option depends on an actual A* result over the topology."""
    with_alternative = problem_from_diagnosis("congestion", NODE, topology=topology)
    assert Predicate.parse(f"alternate-route({NODE})") in with_alternative.initial

    plan, _ = plan_with_astar(with_alternative)
    assert "reroute_traffic" in [a.operator.name for a in plan.actions]


def test_without_an_alternative_route_the_reroute_action_is_unavailable():
    """No alternate-route literal means the congestion cannot be planned away."""
    problem = build_restoration_problem("N1", ["congested"], alternate_route=False)
    gps_plan, _ = plan_with_gps(problem, lang="en")
    astar_plan, _ = plan_with_astar(problem)
    assert gps_plan is None
    assert astar_plan is None


# --- heuristic behaviour in the planner ------------------------------------
def test_goal_count_heuristic_does_not_change_the_optimal_plan_cost(topology):
    problem = problem_from_diagnosis("mac_contention", NODE, topology=topology)
    informed, _ = plan_with_astar(problem, heuristic="goal_count")
    blind, _ = plan_with_astar(problem, heuristic="zero")
    assert informed.cost == pytest.approx(blind.cost)


def test_unknown_heuristic_is_rejected(topology):
    problem = problem_from_diagnosis("congestion", NODE, topology=topology)
    with pytest.raises(ValueError, match="unknown heuristic"):
        plan_with_astar(problem, heuristic="magic")


def test_unknown_diagnosis_is_rejected(topology):
    with pytest.raises(ValueError, match="unknown diagnosis"):
        problem_from_diagnosis("gremlins", NODE, topology=topology)


# --- GPS's documented weakness --------------------------------------------
def test_gps_can_be_suboptimal_when_a_cheap_action_has_expensive_preconditions():
    """
    PT-BR: GPS escolhe o operador mais barato que reduz a diferenca, sem olhar o
           custo das PRECONDICOES desse operador. Aqui o operador barato exige
           deslocamento caro, e o A* encontra o plano melhor.
    EN:    GPS picks the cheapest operator that reduces the difference, without
           looking at the cost of that operator's PRECONDITIONS. Here the cheap
           operator needs an expensive trip, and A* finds the better plan.
    """
    operators = [
        Operator.build("cheap_but_needs_trip", parameters=("?n",),
                       preconditions=("on-site(?n)",), add=("fixed(?n)",), cost=1.0),
        Operator.build("travel", parameters=("?n",),
                       preconditions=(), add=("on-site(?n)",), cost=10.0),
        Operator.build("remote_fix", parameters=("?n",),
                       preconditions=(), add=("fixed(?n)",), cost=3.0),
    ]
    problem = Problem(
        name="gps-trap",
        operators=operators,
        initial=make_state(["broken(N1)"]),
        goal=make_state(["fixed(N1)"]),
        objects={"node": ["N1"]},
        parameter_types={"?n": "node"},
    )

    gps_plan, _ = plan_with_gps(problem, lang="en")
    astar_plan, _ = plan_with_astar(problem)

    assert gps_plan.cost == 11.0  # travel (10) + cheap fix (1)
    assert astar_plan.cost == 3.0  # remote fix
    assert astar_plan.cost < gps_plan.cost


# --- the run: stopping it is the cost that matters -------------------------
@pytest.mark.parametrize(
    "fault,repair",
    [("excess-path-loss", "restore_path_budget"), ("mac-contention", "separate_channels")],
)
def test_parameter_faults_have_planning_semantics(fault, repair):
    """Both scenario-parameter faults must produce an executable plan."""
    problem = build_restoration_problem("N1", [fault])
    plan, _ = plan_with_astar(problem)

    assert plan is not None
    assert repair in [a.operator.name for a in plan.actions]
    assert plan.validate()[0]
    assert _remaining_faults(problem, plan) == []


def test_a_parameter_change_requires_the_run_to_be_stopped():
    """Changing a scenario parameter mid-run would invalidate the measurement."""
    problem = build_restoration_problem("N1", ["mac-contention"])
    change = next(
        a for a in problem.ground_actions() if a.name == "separate_channels(N1)"
    )
    assert not change.applicable(problem.initial), "parameter changed during a live run"

    plan, _ = plan_with_astar(problem)
    names = [a.operator.name for a in plan.actions]
    assert names.index("stop_run") < names.index("separate_channels")


def test_verification_requires_the_run_active_again():
    """Stopping is a cost, not a free precaution: the link must be re-verified."""
    problem = build_restoration_problem("N1", ["mac-contention"])
    plan, _ = plan_with_astar(problem)
    names = [a.operator.name for a in plan.actions]
    assert names.index("start_run") < names.index("verify_link")


def test_parameter_changes_share_one_run_restart():
    """
    PT-BR: Parar a execucao tem custo. Duas correcoes de parametro devem caber numa
           unica parada — e o compromisso que torna o planejamento necessario.
    EN:    Stopping the run has a cost. Two parameter repairs must fit inside one
           stop - the trade-off that makes planning necessary.
    """
    problem = build_restoration_problem("N1", ["mac-contention", "excess-path-loss"])
    plan, _ = plan_with_astar(problem)
    names = [a.operator.name for a in plan.actions]

    assert names.count("stop_run") == 1
    assert names.count("start_run") == 1
    assert _remaining_faults(problem, plan) == []


def test_a_runtime_repair_needs_no_run_restart():
    """A runtime repair must not stop the run: only parameter changes do."""
    problem = build_restoration_problem("N1", ["node-stopped"])
    plan, _ = plan_with_astar(problem)
    names = [a.operator.name for a in plan.actions]
    assert "stop_run" not in names
