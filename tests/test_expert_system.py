"""Tests for the inference engine and the backhaul knowledge base."""

from __future__ import annotations

import pytest

from aisg.expert_system import (
    CASES,
    Conclusion,
    Condition,
    ConflictResolution,
    InferenceEngine,
    KnowledgeBase,
    Operator,
    Rule,
    Variable,
    VariableKind,
    build_knowledge_base,
    combine_cf,
)


# --- certainty factor algebra ---------------------------------------------
def test_combine_cf_reinforcing_evidence_never_reaches_one():
    combined = combine_cf(0.8, 0.8)
    assert 0.8 < combined < 1.0
    assert combined == pytest.approx(0.96)


def test_combine_cf_is_commutative():
    assert combine_cf(0.6, 0.3) == pytest.approx(combine_cf(0.3, 0.6))


def test_combine_cf_contradictory_evidence_cancels():
    assert combine_cf(0.8, -0.8) == pytest.approx(0.0)


def test_combine_cf_negative_evidence_accumulates():
    assert combine_cf(-0.5, -0.5) == pytest.approx(-0.75)


# --- knowledge base integrity ---------------------------------------------
def test_shipped_knowledge_base_is_internally_consistent():
    assert build_knowledge_base().validate() == []


def test_every_goal_variable_is_concluded_by_some_rule():
    kb = build_knowledge_base()
    for goal in kb.goal_variables:
        assert kb.rules_concluding(goal), f"{goal} has no rule concluding it"


def test_duplicate_rule_ids_are_rejected():
    kb = build_knowledge_base()
    existing = kb.rules[0]
    with pytest.raises(ValueError, match="duplicate rule id"):
        kb.add_rule(existing)


def test_validation_detects_an_undeclared_variable():
    kb = KnowledgeBase("t", "t", goal_variables=("y",))
    kb.add_variable(Variable("y", VariableKind.CATEGORICAL, "y", "y", labels=("a",), askable=False))
    kb.add_rule(
        Rule("X1", (Condition("ghost", Operator.EQ, "a"),), Conclusion("y", "a"), 1.0)
    )
    problems = kb.validate()
    assert any("ghost" in p for p in problems)


def test_rule_rejects_out_of_range_certainty():
    with pytest.raises(ValueError, match=r"cf must be in \[-1, 1\]"):
        Rule("X", (Condition("a", Operator.EQ, "b"),), Conclusion("c", "d"), 1.5)


# --- forward chaining ------------------------------------------------------
@pytest.mark.parametrize(
    "case_name,expected",
    [
        ("interference", "rf_interference"),
        ("obstruction", "path_obstruction"),
        ("rain_fade", "rain_fade"),
        ("power_failure", "node_power_failure"),
        ("relay_failure", "upstream_relay_failure"),
        ("vlan", "vlan_misconfiguration"),
        ("congestion", "congestion"),
        ("healthy", "healthy"),
    ],
)
def test_forward_chaining_reaches_the_expected_diagnosis(case_name, expected):
    engine = InferenceEngine(build_knowledge_base())
    for variable, value in CASES[case_name].items():
        engine.given(variable, value)
    consultation = engine.forward_chain()

    best = consultation.memory.best("diagnosis")
    assert best is not None
    assert best.value == expected
    assert best.cf > 0.4


def test_every_case_also_yields_an_action_and_an_authorisation_decision():
    for case_name in CASES:
        engine = InferenceEngine(build_knowledge_base())
        for variable, value in CASES[case_name].items():
            engine.given(variable, value)
        conclusions = engine.forward_chain().conclusions()
        assert "recommended_action" in conclusions, case_name
        assert "authorization_required" in conclusions, case_name


def test_actions_touching_the_plant_always_require_authorisation():
    """Governance invariant: only monitoring and no-action may skip authorisation."""
    exempt = {"wait_and_monitor", "no_action"}
    for case_name in CASES:
        engine = InferenceEngine(build_knowledge_base())
        for variable, value in CASES[case_name].items():
            engine.given(variable, value)
        conclusions = engine.forward_chain().conclusions()
        action = conclusions["recommended_action"][0].value
        authorisation = conclusions["authorization_required"][0].value
        if action not in exempt:
            assert authorisation == "yes", f"{case_name}: {action} escaped authorisation"


def test_counter_evidence_suppresses_a_competing_hypothesis():
    """Clear weather is evidence AGAINST rain fade (rule R25, negative CF)."""
    engine = InferenceEngine(build_knowledge_base())
    for variable, value in CASES["interference"].items():
        engine.given(variable, value)
    engine.forward_chain()

    rain = engine.memory.get("diagnosis", "rain_fade")
    assert rain is not None and rain.cf < 0


def test_forward_chaining_terminates_and_fires_each_rule_at_most_once():
    engine = InferenceEngine(build_knowledge_base())
    for variable, value in CASES["congestion"].items():
        engine.given(variable, value)
    consultation = engine.forward_chain()
    assert len(consultation.fired_rules) == len(set(consultation.fired_rules))
    assert consultation.cycles < engine.max_cycles


# --- backward chaining -----------------------------------------------------
def test_backward_chaining_asks_only_what_the_goal_requires():
    """The goal-driven mode must not ask for every variable in the base."""
    asked = []
    case = CASES["power_failure"]

    def ask(variable, _why):
        asked.append(variable.name)
        value = case.get(variable.name)
        return (value, 1.0) if value is not None else None

    kb = build_knowledge_base()
    engine = InferenceEngine(kb, ask=ask)
    consultation = engine.backward_chain("diagnosis")

    assert consultation.memory.best("diagnosis") is not None
    askable = [v for v in kb.variables.values() if v.askable]
    assert len(set(asked)) < len(askable)


def test_backward_chaining_matches_forward_chaining_on_the_same_evidence():
    case = CASES["vlan"]

    forward = InferenceEngine(build_knowledge_base())
    for variable, value in case.items():
        forward.given(variable, value)
    forward_best = forward.forward_chain().memory.best("diagnosis")

    backward = InferenceEngine(
        build_knowledge_base(),
        ask=lambda v, _w: (case[v.name], 1.0) if v.name in case else None,
    )
    backward_best = backward.backward_chain("diagnosis").memory.best("diagnosis")

    assert forward_best.value == backward_best.value


def test_why_explains_the_rule_chain_behind_a_question():
    seen = {}

    def ask(variable, why_stack):
        seen.setdefault(variable.name, len(why_stack))
        value = CASES["interference"].get(variable.name)
        return (value, 1.0) if value is not None else None

    engine = InferenceEngine(build_knowledge_base(), ask=ask)
    engine.backward_chain("diagnosis")
    assert any(depth > 0 for depth in seen.values())


# --- explanation -----------------------------------------------------------
def test_how_traces_a_conclusion_back_to_user_supplied_facts():
    engine = InferenceEngine(build_knowledge_base())
    for variable, value in CASES["power_failure"].items():
        engine.given(variable, value)
    consultation = engine.forward_chain()

    explanation = consultation.how("diagnosis", "node_power_failure", "en")
    assert "R16" in explanation
    assert "initial fact" in explanation


# --- conflict resolution ---------------------------------------------------
@pytest.mark.parametrize("strategy", list(ConflictResolution))
def test_all_conflict_resolution_policies_reach_the_same_diagnosis(strategy):
    """
    The policy changes the ORDER of reasoning, not the fixed point.

    PT-BR: Com regras monotonicas, a ordem de disparo altera o trace, nao a conclusao.
    """
    engine = InferenceEngine(build_knowledge_base(), strategy=strategy)
    for variable, value in CASES["obstruction"].items():
        engine.given(variable, value)
    consultation = engine.forward_chain()
    assert consultation.memory.best("diagnosis").value == "path_obstruction"


def test_conflict_resolution_policies_produce_different_firing_orders():
    orders = {}
    for strategy in ConflictResolution:
        engine = InferenceEngine(build_knowledge_base(), strategy=strategy)
        for variable, value in CASES["interference"].items():
            engine.given(variable, value)
        orders[strategy] = tuple(engine.forward_chain().fired_rules)
    assert len(set(orders.values())) > 1, "policies should differ in firing order"


# --- input validation ------------------------------------------------------
def test_out_of_range_measurement_is_rejected():
    engine = InferenceEngine(build_knowledge_base())
    with pytest.raises(ValueError, match="outside the declared range"):
        engine.given("snr_db", 999.0)


def test_undeclared_label_is_rejected():
    engine = InferenceEngine(build_knowledge_base())
    with pytest.raises(ValueError, match="is not one of"):
        engine.given("link_state", "sideways")


def test_uncertain_evidence_lowers_the_conclusion_certainty():
    """The same case asserted with hedged evidence must conclude less strongly."""
    certain = InferenceEngine(build_knowledge_base())
    hedged = InferenceEngine(build_knowledge_base())
    for variable, value in CASES["interference"].items():
        certain.given(variable, value)
        hedged.given(variable, value, cf=0.6)

    certain_cf = certain.forward_chain().memory.best("diagnosis").cf
    hedged_cf = hedged.forward_chain().memory.best("diagnosis").cf
    assert hedged_cf < certain_cf


def test_downstream_certainty_does_not_depend_on_the_conflict_policy():
    """
    PT-BR: A afirmacao apresentada e que a politica muda a ORDEM do raciocinio,
           nao o resultado. Verificar apenas o diagnostico vencedor nao sustenta
           isso: uma regra de acao que dispara cedo, sobre um diagnostico ainda
           parcial, congelava um CF derivado mais baixo.
    EN:    The claim presented is that the policy changes the ORDER of reasoning,
           not the outcome. Checking only the winning diagnosis does not support
           it: an action rule firing early, on a still-partial diagnosis, froze a
           lower derived CF.
    """
    for case in CASES:
        certainties = set()
        for strategy in ConflictResolution:
            engine = InferenceEngine(build_knowledge_base(), strategy=strategy)
            for variable, value in CASES[case].items():
                engine.given(variable, value)
            conclusions = engine.forward_chain().conclusions()
            certainties.add((
                conclusions["diagnosis"][0].value,
                round(conclusions["diagnosis"][0].cf, 6),
                conclusions["recommended_action"][0].value,
                round(conclusions["recommended_action"][0].cf, 6),
            ))
        assert len(certainties) == 1, f"{case}: policy changed the outcome: {certainties}"


def test_a_rule_refiring_does_not_count_its_own_evidence_twice():
    """A rule that fires again must replace its contribution, not compound it."""
    engine = InferenceEngine(build_knowledge_base())
    for variable, value in CASES["interference"].items():
        engine.given(variable, value)
    engine.forward_chain()

    best = engine.memory.best("diagnosis")
    assert best.cf <= 1.0
    # The supporting rules are named once each, never repeated.
    sources = best.source.split("+")
    assert len(sources) == len(set(sources))
