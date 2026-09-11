"""
Tests for the indoor conducted-simulated scenario knowledge base.

PT-BR: A propriedade central desta base nao e "diagnostica corretamente" — e que
       toda condicao que ela reconhece pode ser INDUZIDA na bancada. Uma regra
       sobre um fenomeno que o laboratorio nao consegue produzir e regra morta.
EN:    This base's central property is not "diagnoses correctly" but that every
       condition it recognises can be INDUCED on the simulated scenario. A rule about a
       phenomenon the laboratory cannot produce is a dead rule.
"""

from __future__ import annotations

import pytest

from aisg.expert_system import (
    SIM_CASES,
    SIM_THRESHOLDS,
    INDUCIBLE_BY,
    KNOWLEDGE_BASES,
    InferenceEngine,
    build_simulated_knowledge_base,
)


def test_simulated_knowledge_base_is_internally_consistent():
    assert build_simulated_knowledge_base().validate() == []


def test_the_simulated_base_has_no_weather_and_no_rain_fade():
    """
    An indoor conducted path has no weather to observe and no rain fade to induce.
    Keeping either would be a rule that can never fire.
    """
    kb = build_simulated_knowledge_base()
    for absent in ("weather", "residual_leakage_dbm"):
        assert absent not in kb.variables, f"{absent} cannot exist in a simulation"
    for absent in ("rain_fade", "path_obstruction", "containment_breach"):
        assert absent not in kb.variables["diagnosis"].labels


def test_commanded_attenuation_replaces_weather_as_evidence():
    kb = build_simulated_knowledge_base()
    attenuation = kb.variables["excess_path_loss_db"]
    assert attenuation.askable
    assert attenuation.unit == "dB"
    assert kb.rules_concluding("diagnosis"), "attenuation must feed a diagnosis"


def test_every_diagnosis_is_inducible_on_the_simulated():
    """
    The property that makes this base labellable: no diagnosis exists that the
    simulated scenario cannot deliberately produce.
    """
    kb = build_simulated_knowledge_base()
    for label in kb.variables["diagnosis"].labels:
        assert label in INDUCIBLE_BY, f"{label} has no documented way to induce it"
        assert INDUCIBLE_BY[label].strip(), f"{label} has an empty induction recipe"


@pytest.mark.parametrize("case", sorted(SIM_CASES))
def test_each_induced_condition_is_diagnosed_as_itself(case):
    """
    Each case is named after the condition the simulated scenario would command, so the case
    name IS the ground-truth label. That is the whole point of this base.
    """
    engine = InferenceEngine(build_simulated_knowledge_base())
    for variable, value in SIM_CASES[case].items():
        engine.given(variable, value)
    best = engine.forward_chain().memory.best("diagnosis")

    assert best is not None
    assert best.value == case
    assert best.cf > 0.4


def test_nominal_path_loss_is_counter_evidence_for_excess_loss():
    """Replaces the clear-weather rule, and is stronger: the value is commanded."""
    engine = InferenceEngine(build_simulated_knowledge_base())
    for variable, value in SIM_CASES["rf_interference"].items():
        engine.given(variable, value)
    engine.forward_chain()

    attenuation = engine.memory.get("diagnosis", "excess_path_loss")
    assert attenuation is not None and attenuation.cf < 0


def test_commanded_loss_outranks_contention():
    """
    With the attenuator commanded high, path loss explains the poor signal; the
    physical-path hypothesis should not win.
    """
    engine = InferenceEngine(build_simulated_knowledge_base())
    for variable, value in SIM_CASES["excess_path_loss"].items():
        engine.given(variable, value)
    engine.forward_chain()

    excess = engine.memory.get("diagnosis", "excess_path_loss")
    cabling = engine.memory.get("diagnosis", "mac_contention")
    assert excess is not None
    assert cabling is None or excess.cf > cabling.cf


def test_actions_touching_the_rig_require_an_authorised_window():
    """
    Changing the scenario mid-campaign invalidates the run, so every action but
    `no_action` waits for an authorised window.
    """
    exempt = {"no_action"}
    for case in SIM_CASES:
        engine = InferenceEngine(build_simulated_knowledge_base())
        for variable, value in SIM_CASES[case].items():
            engine.given(variable, value)
        conclusions = engine.forward_chain().conclusions()
        action = conclusions["recommended_action"][0].value
        required = conclusions["authorization_required"][0].value
        if action not in exempt:
            assert required == "yes", f"{case}: {action} escaped the window gate"


def test_thresholds_are_declared_in_one_block():
    kb = build_simulated_knowledge_base()
    assert kb.thresholds == SIM_THRESHOLDS
    assert "path_loss_high_db" in kb.thresholds


def test_both_knowledge_bases_run_on_the_same_engine():
    """
    The engine is domain-independent: swapping the knowledge swaps the domain,
    with no change to the inference machinery.
    """
    for name, (build, cases) in KNOWLEDGE_BASES.items():
        kb = build()
        assert kb.validate() == [], name
        engine = InferenceEngine(kb)
        first = next(iter(cases))
        for variable, value in cases[first].items():
            engine.given(variable, value)
        assert engine.forward_chain().conclusions(), name


