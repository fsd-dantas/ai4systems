"""
Tests for the indoor conducted-bench knowledge base.

PT-BR: A propriedade central desta base nao e "diagnostica corretamente" — e que
       toda condicao que ela reconhece pode ser INDUZIDA na bancada. Uma regra
       sobre um fenomeno que o laboratorio nao consegue produzir e regra morta.
EN:    This base's central property is not "diagnoses correctly" but that every
       condition it recognises can be INDUCED on the bench. A rule about a
       phenomenon the laboratory cannot produce is a dead rule.
"""

from __future__ import annotations

import pytest

from aisg.expert_system import (
    BENCH_CASES,
    BENCH_THRESHOLDS,
    INDUCIBLE_BY,
    KNOWLEDGE_BASES,
    InferenceEngine,
    build_bench_knowledge_base,
)


def test_bench_knowledge_base_is_internally_consistent():
    assert build_bench_knowledge_base().validate() == []


def test_the_bench_base_has_no_weather_and_no_rain_fade():
    """
    An indoor conducted path has no weather to observe and no rain fade to induce.
    Keeping either would be a rule that can never fire.
    """
    kb = build_bench_knowledge_base()
    assert "weather" not in kb.variables
    assert "rain_fade" not in kb.variables["diagnosis"].labels


def test_commanded_attenuation_replaces_weather_as_evidence():
    kb = build_bench_knowledge_base()
    attenuation = kb.variables["attenuation_db"]
    assert attenuation.askable
    assert attenuation.unit == "dB"
    assert kb.rules_concluding("diagnosis"), "attenuation must feed a diagnosis"


def test_every_diagnosis_is_inducible_on_the_bench():
    """
    The property that makes this base labellable: no diagnosis exists that the
    bench cannot deliberately produce.
    """
    kb = build_bench_knowledge_base()
    for label in kb.variables["diagnosis"].labels:
        assert label in INDUCIBLE_BY, f"{label} has no documented way to induce it"
        assert INDUCIBLE_BY[label].strip(), f"{label} has an empty induction recipe"


@pytest.mark.parametrize("case", sorted(BENCH_CASES))
def test_each_induced_condition_is_diagnosed_as_itself(case):
    """
    Each case is named after the condition the bench would command, so the case
    name IS the ground-truth label. That is the whole point of this base.
    """
    engine = InferenceEngine(build_bench_knowledge_base())
    for variable, value in BENCH_CASES[case].items():
        engine.given(variable, value)
    best = engine.forward_chain().memory.best("diagnosis")

    assert best is not None
    assert best.value == case
    assert best.cf > 0.4


def test_attenuator_at_the_floor_is_counter_evidence_for_path_loss():
    """Replaces the clear-weather rule, and is stronger: the value is commanded."""
    engine = InferenceEngine(build_bench_knowledge_base())
    for variable, value in BENCH_CASES["rf_interference"].items():
        engine.given(variable, value)
    engine.forward_chain()

    attenuation = engine.memory.get("diagnosis", "excess_attenuation")
    assert attenuation is not None and attenuation.cf < 0


def test_high_attenuation_outranks_a_cabling_fault():
    """
    With the attenuator commanded high, path loss explains the poor signal; the
    physical-path hypothesis should not win.
    """
    engine = InferenceEngine(build_bench_knowledge_base())
    for variable, value in BENCH_CASES["excess_attenuation"].items():
        engine.given(variable, value)
    engine.forward_chain()

    excess = engine.memory.get("diagnosis", "excess_attenuation")
    cabling = engine.memory.get("diagnosis", "cabling_fault")
    assert excess is not None
    assert cabling is None or excess.cf > cabling.cf


def test_actions_touching_the_rig_require_an_authorised_window():
    """
    Two exemptions, for opposite reasons: `no_action` changes nothing, and
    `halt_transmission` is the safe act - gating a stop behind a window is the
    dangerous design this base exists to avoid.
    """
    exempt = {"no_action", "halt_transmission"}
    for case in BENCH_CASES:
        engine = InferenceEngine(build_bench_knowledge_base())
        for variable, value in BENCH_CASES[case].items():
            engine.given(variable, value)
        conclusions = engine.forward_chain().conclusions()
        action = conclusions["recommended_action"][0].value
        required = conclusions["authorization_required"][0].value
        if action not in exempt:
            assert required == "yes", f"{case}: {action} escaped the window gate"
        elif action == "halt_transmission":
            assert required == "no", "halting must not wait for a window"


def test_thresholds_are_declared_in_one_block():
    kb = build_bench_knowledge_base()
    assert kb.thresholds == BENCH_THRESHOLDS
    assert "attenuation_high_db" in kb.thresholds


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


# --- containment: a stop condition, not a restoration one ------------------
def test_leakage_above_the_criterion_is_diagnosed_as_a_breach():
    engine = InferenceEngine(build_bench_knowledge_base())
    for variable, value in BENCH_CASES["containment_breach"].items():
        engine.given(variable, value)
    conclusions = engine.forward_chain().conclusions()

    assert conclusions["diagnosis"][0].value == "containment_breach"
    assert conclusions["recommended_action"][0].value == "halt_transmission"


def test_a_breach_outranks_a_service_fault():
    """
    PT-BR: Com interferencia E contencao violada, o sistema deve mandar PARAR —
           nao mudar de canal. Recomendar uma acao de radio num equipamento que
           irradia acima do criterio e a recomendacao perigosa que esta base
           existe para evitar.
    EN:    With interference AND a breach, the system must say STOP - not change
           channel. Recommending a radio action on a rig radiating above the
           criterion is the dangerous recommendation this base exists to avoid.
    """
    engine = InferenceEngine(build_bench_knowledge_base())
    for variable, value in BENCH_CASES["rf_interference"].items():
        engine.given(variable, value)
    engine.given("residual_leakage_dbm", -40.0)  # above the declared limit
    conclusions = engine.forward_chain().conclusions()

    assert conclusions["diagnosis"][0].value == "containment_breach"
    assert conclusions["recommended_action"][0].value == "halt_transmission"


def test_halting_does_not_wait_for_an_authorised_window():
    """The inversion: authorisation gates changes to the plant, never stopping."""
    engine = InferenceEngine(build_bench_knowledge_base())
    for variable, value in BENCH_CASES["containment_breach"].items():
        engine.given(variable, value)
    conclusions = engine.forward_chain().conclusions()

    assert conclusions["authorization_required"][0].value == "no"


def test_measured_containment_within_the_criterion_argues_against_a_breach():
    engine = InferenceEngine(build_bench_knowledge_base())
    for variable, value in BENCH_CASES["healthy"].items():
        engine.given(variable, value)
    engine.forward_chain()

    breach = engine.memory.get("diagnosis", "containment_breach")
    assert breach is not None and breach.cf < 0


def test_unmeasured_leakage_does_not_certify_containment():
    """
    PT-BR: A nota de conceitos do laboratorio e explicita: a contencao deve ser
           MEDIDA, nunca presumida pela presenca do cabo. Sem a medicao, o motor
           nao deve concluir que a contencao esta boa.
    EN:    The lab's concepts note is explicit that containment must be MEASURED,
           never presumed from the presence of a cable. Without the measurement,
           the engine must not conclude containment is fine.
    """
    evidence = dict(BENCH_CASES["healthy"])
    evidence.pop("residual_leakage_dbm")

    engine = InferenceEngine(build_bench_knowledge_base())
    for variable, value in evidence.items():
        engine.given(variable, value)
    engine.forward_chain()

    # Neither confirmed nor refuted: absence of measurement is not evidence.
    assert engine.memory.get("diagnosis", "containment_breach") is None
