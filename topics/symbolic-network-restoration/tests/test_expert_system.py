"""Tests for the inference engine, run over the simulated knowledge base."""

from __future__ import annotations

import pytest

from aisg.expert_system import (
    SIM_CASES,
    Conclusion,
    Condition,
    ConflictResolution,
    InferenceEngine,
    KnowledgeBase,
    Operator,
    Rule,
    Variable,
    VariableKind,
    build_simulated_knowledge_base,
    combine_cf,
)


def _engine(case_name, **options):
    """An engine loaded with one of the preset cases."""
    engine = InferenceEngine(build_simulated_knowledge_base(), **options)
    for variable, value in SIM_CASES[case_name].items():
        engine.given(variable, value)
    return engine


def _asker(case_name, asked=None):
    """A backward-chaining question callback that answers from a preset case."""
    case = SIM_CASES[case_name]

    def ask(variable, _why):
        if asked is not None:
            asked.append(variable.name)
        value = case.get(variable.name)
        return (value, 1.0) if value is not None else None

    return ask


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
    assert build_simulated_knowledge_base().validate() == []


def test_every_goal_variable_is_concluded_by_some_rule():
    kb = build_simulated_knowledge_base()
    for goal in kb.goal_variables:
        assert kb.rules_concluding(goal), f"{goal} has no rule concluding it"


def test_duplicate_rule_ids_are_rejected():
    kb = build_simulated_knowledge_base()
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
def test_every_case_also_yields_an_action_and_an_authorisation_decision():
    for case_name in SIM_CASES:
        conclusions = _engine(case_name).forward_chain().conclusions()
        assert "recommended_action" in conclusions, case_name
        assert "authorization_required" in conclusions, case_name


def test_counter_evidence_suppresses_a_competing_hypothesis():
    """Low retransmission is evidence AGAINST MAC contention (rule S25, negative CF)."""
    engine = _engine("congestion")
    engine.forward_chain()

    contention = engine.memory.get("diagnosis", "mac_contention")
    assert contention is not None and contention.cf < 0


def test_forward_chaining_terminates_and_fires_each_rule_at_most_once():
    engine = _engine("congestion")
    consultation = engine.forward_chain()
    assert len(consultation.fired_rules) == len(set(consultation.fired_rules))
    assert consultation.cycles < engine.max_cycles


# --- backward chaining -----------------------------------------------------
def test_backward_chaining_asks_only_what_the_goal_requires():
    """
    The goal-driven mode must not ask for every variable in the base.

    The MAC-contention case concludes after 6 of the 13 askable variables - the
    figure the expert-system diagram and the slides quote.
    """
    asked = []
    kb = build_simulated_knowledge_base()
    engine = InferenceEngine(kb, ask=_asker("mac_contention", asked))
    consultation = engine.backward_chain("diagnosis")

    assert consultation.memory.best("diagnosis").value == "mac_contention"
    askable = [v for v in kb.variables.values() if v.askable]
    assert len(askable) == 13
    assert len(set(asked)) == 6


@pytest.mark.parametrize("case_name", sorted(SIM_CASES))
def test_backward_chaining_matches_forward_chaining_on_the_same_evidence(case_name):
    forward_best = _engine(case_name).forward_chain().memory.best("diagnosis")

    backward = InferenceEngine(build_simulated_knowledge_base(), ask=_asker(case_name))
    backward_best = backward.backward_chain("diagnosis").memory.best("diagnosis")

    assert forward_best.value == backward_best.value


def test_why_explains_the_rule_chain_behind_a_question():
    seen = {}
    case = SIM_CASES["rf_interference"]

    def ask(variable, why_stack):
        seen.setdefault(variable.name, len(why_stack))
        value = case.get(variable.name)
        return (value, 1.0) if value is not None else None

    engine = InferenceEngine(build_simulated_knowledge_base(), ask=ask)
    engine.backward_chain("diagnosis")
    assert any(depth > 0 for depth in seen.values())


# --- explanation -----------------------------------------------------------
def test_how_traces_a_conclusion_back_to_user_supplied_facts():
    consultation = _engine("node_failure").forward_chain()

    explanation = consultation.how("diagnosis", "node_failure", "en")
    assert "S16" in explanation
    assert "initial fact" in explanation


# --- conflict resolution ---------------------------------------------------
@pytest.mark.parametrize("strategy", list(ConflictResolution))
def test_all_conflict_resolution_policies_reach_the_same_diagnosis(strategy):
    """
    The policy changes the ORDER of reasoning, not the fixed point.

    PT-BR: Com regras monotonicas, a ordem de disparo altera o trace, nao a conclusao.
    """
    consultation = _engine("excess_path_loss", strategy=strategy).forward_chain()
    assert consultation.memory.best("diagnosis").value == "excess_path_loss"


def test_conflict_resolution_policies_produce_different_firing_orders():
    orders = {
        strategy: tuple(_engine("rf_interference", strategy=strategy).forward_chain().fired_rules)
        for strategy in ConflictResolution
    }
    assert len(set(orders.values())) > 1, "policies should differ in firing order"


# --- input validation ------------------------------------------------------
def test_out_of_range_measurement_is_rejected():
    engine = InferenceEngine(build_simulated_knowledge_base())
    with pytest.raises(ValueError, match="outside the declared range"):
        engine.given("snr_db", 999.0)


def test_undeclared_label_is_rejected():
    engine = InferenceEngine(build_simulated_knowledge_base())
    with pytest.raises(ValueError, match="is not one of"):
        engine.given("node_responding", "sideways")


def test_uncertain_evidence_lowers_the_conclusion_certainty():
    """The same case asserted with hedged evidence must conclude less strongly."""
    certain = InferenceEngine(build_simulated_knowledge_base())
    hedged = InferenceEngine(build_simulated_knowledge_base())
    for variable, value in SIM_CASES["rf_interference"].items():
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
    for case in SIM_CASES:
        certainties = set()
        for strategy in ConflictResolution:
            conclusions = _engine(case, strategy=strategy).forward_chain().conclusions()
            certainties.add((
                conclusions["diagnosis"][0].value,
                round(conclusions["diagnosis"][0].cf, 6),
                conclusions["recommended_action"][0].value,
                round(conclusions["recommended_action"][0].cf, 6),
            ))
        assert len(certainties) == 1, f"{case}: policy changed the outcome: {certainties}"


def test_a_rule_refiring_does_not_count_its_own_evidence_twice():
    """A rule that fires again must replace its contribution, not compound it."""
    engine = _engine("rf_interference")
    engine.forward_chain()

    best = engine.memory.best("diagnosis")
    assert best.cf <= 1.0
    # The supporting rules are named once each, never repeated.
    sources = best.source.split("+")
    assert len(sources) == len(set(sources))
