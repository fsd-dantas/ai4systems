"""
Tests for observation records and the Prometheus reader.

PT-BR: A propriedade que importa aqui e o que o sistema faz com o que NAO tem.
       Uma variavel ausente deve permanecer desconhecida e reduzir a certeza —
       nunca receber um valor plausivel.
EN:    The property that matters here is what the system does with what it does
       NOT have. A missing variable must stay unknown and lower the certainty -
       never receive a plausible value.
"""

from __future__ import annotations

import json

import pytest

from aisg.expert_system import SIM_CASES, InferenceEngine, build_simulated_knowledge_base
from aisg.observation import SCHEMA, Observation, ObservationError
from aisg.prometheus import (
    MetricSpec,
    PrometheusClient,
    PrometheusError,
    fetch_observation,
    seconds_to_ms,
    success_ratio_to_loss_pct,
)


def _prometheus_reply(value):
    return {
        "status": "success",
        "data": {
            "resultType": "vector",
            "result": [{"metric": {}, "value": [1757520000.0, str(value)]}],
        },
    }


# --- the record format -----------------------------------------------------
def test_a_bare_value_is_accepted_and_taken_as_certain():
    record = Observation.from_dict({
        "subject": {"id": "L1"},
        "observations": {"rssi_dbm": -90.0},
    })
    assert record.values["rssi_dbm"] == (-90.0, 1.0)


def test_a_certainty_below_one_is_preserved():
    record = Observation.from_dict({
        "subject": {"id": "L1"},
        "observations": {"co_channel_emitter": {"value": "yes", "cf": 0.6}},
    })
    assert record.values["co_channel_emitter"] == ("yes", 0.6)


def test_records_round_trip_through_json(tmp_path):
    original = Observation(
        subject_id="L1",
        values={"rssi_dbm": (-97.2, 1.0), "node_responding": ("yes", 1.0)},
        unavailable={"retry_rate_pct": "no exporter"},
    )
    path = tmp_path / "obs.json"
    original.save(path)
    reloaded = Observation.load(path)

    assert reloaded.values == original.values
    assert reloaded.unavailable == original.unavailable
    assert json.loads(path.read_text(encoding="utf-8"))["schema"] == SCHEMA


def test_an_unknown_schema_is_refused():
    with pytest.raises(ObservationError, match="unsupported schema"):
        Observation.from_dict({"schema": "something-else/9", "subject": {"id": "L1"}})


def test_a_record_without_a_subject_is_refused():
    with pytest.raises(ObservationError, match="subject.id is required"):
        Observation.from_dict({"observations": {}})


def test_an_out_of_range_certainty_is_refused():
    with pytest.raises(ObservationError, match=r"cf must be in \[-1, 1\]"):
        Observation.from_dict({
            "subject": {"id": "L1"},
            "observations": {"rssi_dbm": {"value": -90.0, "cf": 4.0}},
        })


# --- agreement with the knowledge base ------------------------------------
def test_values_outside_the_declared_domain_are_caught_before_inference():
    kb = build_simulated_knowledge_base()
    record = Observation.from_dict({
        "subject": {"id": "L1"},
        "observations": {"snr_db": 999.0, "node_responding": "sideways"},
    })
    problems = record.validate_against(kb)
    assert len(problems) == 2
    assert any("outside the declared range" in p for p in problems)
    assert any("is not one of" in p for p in problems)


def test_a_variable_the_base_concludes_cannot_be_observed():
    kb = build_simulated_knowledge_base()
    record = Observation.from_dict({
        "subject": {"id": "L1"},
        "observations": {"diagnosis": "rf_interference"},
    })
    assert any("concluded by rules" in p for p in record.validate_against(kb))


def test_applying_a_mismatched_record_raises_rather_than_half_loading():
    engine = InferenceEngine(build_simulated_knowledge_base())
    record = Observation.from_dict({
        "subject": {"id": "L1"},
        "observations": {"snr_db": 999.0},
    })
    with pytest.raises(ObservationError):
        record.apply_to(engine)


def test_the_bundled_example_record_agrees_with_the_knowledge_base():
    from pathlib import Path

    example = Path(__file__).resolve().parents[1] / "examples" / "observation-partial.json"
    record = Observation.load(example)
    assert record.validate_against(build_simulated_knowledge_base()) == []


# --- partial evidence, which is the normal case ---------------------------
def test_coverage_reports_what_is_missing():
    kb = build_simulated_knowledge_base()
    record = Observation.from_dict({
        "subject": {"id": "L1"},
        "observations": {"rssi_dbm": -97.0, "snr_db": 6.0},
    })
    supplied, askable, missing = record.coverage(kb)

    assert supplied == 2
    assert askable == 13
    assert "retry_rate_pct" in missing and "node_responding" in missing


def test_missing_evidence_lowers_certainty_rather_than_being_invented():
    """
    PT-BR: O mesmo diagnostico, com menos evidencia, deve vir com MENOS certeza.
    EN:    The same diagnosis, on less evidence, must come with LESS certainty.
    """
    full = dict(SIM_CASES["rf_interference"])
    partial = {k: full[k] for k in ("rssi_dbm", "snr_db", "co_channel_emitter")}

    results = {}
    for name, evidence in (("full", full), ("partial", partial)):
        engine = InferenceEngine(build_simulated_knowledge_base())
        Observation.from_dict(
            {"subject": {"id": "L1"}, "observations": evidence}
        ).apply_to(engine)
        results[name] = engine.forward_chain().memory.best("diagnosis")

    assert results["full"].value == results["partial"].value == "rf_interference"
    assert results["partial"].cf < results["full"].cf


# --- the Prometheus reader -------------------------------------------------
def test_unit_converters():
    assert seconds_to_ms(0.18) == pytest.approx(180.0)
    assert success_ratio_to_loss_pct(0.876) == pytest.approx(12.4)
    assert success_ratio_to_loss_pct(1.0) == 0.0


def test_string_values_and_float_timestamps_are_normalised():
    client = PrometheusClient("http://x", _fetch=lambda q: _prometheus_reply("-97.2"))
    assert client.scalar("anything") == pytest.approx(-97.2)


def test_an_empty_result_is_an_error_not_a_zero():
    empty = {"status": "success", "data": {"resultType": "vector", "result": []}}
    client = PrometheusClient("http://x", _fetch=lambda q: empty)
    with pytest.raises(PrometheusError, match="no series"):
        client.scalar("up")


def test_an_ambiguous_result_is_refused():
    two = {
        "status": "success",
        "data": {"result": [
            {"metric": {}, "value": [0, "1"]},
            {"metric": {}, "value": [0, "2"]},
        ]},
    }
    client = PrometheusClient("http://x", _fetch=lambda q: two)
    with pytest.raises(PrometheusError, match="returned 2 series"):
        client.scalar("up")


def test_a_failing_metric_becomes_a_documented_gap_not_a_guess():
    """The whole point of the reader: a partly instrumented setup still works."""
    def fetch(query):
        if "rssi" in query:
            return _prometheus_reply("-97.2")
        return {"status": "success", "data": {"result": []}}

    client = PrometheusClient("http://x", _fetch=fetch)
    specs = [
        MetricSpec("rssi_dbm", 'radio_rssi_dbm{{link="{subject}"}}'),
        MetricSpec("snr_db", 'radio_snr_db{{link="{subject}"}}'),
    ]
    record = fetch_observation(client, "RELAY_5-CPE_03", specs)

    assert record.values["rssi_dbm"][0] == pytest.approx(-97.2)
    assert "snr_db" not in record.values
    assert "no series" in record.unavailable["snr_db"]


def test_categorical_mapping_turns_a_number_into_a_declared_label():
    client = PrometheusClient("http://x", _fetch=lambda q: _prometheus_reply("1"))
    spec = MetricSpec("node_responding", "s", mapping={"1": "yes", "0": "no"})
    record = fetch_observation(client, "L1", [spec])
    assert record.values["node_responding"][0] == "yes"


def test_an_unmapped_numeric_result_is_refused_rather_than_passed_through():
    client = PrometheusClient("http://x", _fetch=lambda q: _prometheus_reply("7"))
    spec = MetricSpec("node_responding", "s", mapping={"1": "yes", "0": "no"})
    record = fetch_observation(client, "L1", [spec])
    assert "node_responding" not in record.values
    assert "not in the declared mapping" in record.unavailable["node_responding"]


def test_a_fetched_record_carries_the_query_as_provenance():
    client = PrometheusClient("http://x", _fetch=lambda q: _prometheus_reply("-90"))
    spec = MetricSpec("rssi_dbm", 'radio_rssi_dbm{{link="{subject}"}}')
    record = fetch_observation(client, "L1", [spec])
    assert 'link="L1"' in record.provenance["rssi_dbm"]


def test_a_fetched_record_is_accepted_by_the_knowledge_base():
    client = PrometheusClient("http://x", _fetch=lambda q: _prometheus_reply("-97.2"))
    record = fetch_observation(
        client, "L1", [MetricSpec("rssi_dbm", 'radio_rssi_dbm{{link="{subject}"}}')]
    )
    assert record.validate_against(build_simulated_knowledge_base()) == []


def test_every_default_metric_names_a_variable_the_base_can_be_asked():
    from aisg.prometheus import DEFAULT_SPECS

    kb = build_simulated_knowledge_base()
    for spec in DEFAULT_SPECS:
        assert spec.variable in kb.variables, spec.variable
        assert kb.variables[spec.variable].askable, spec.variable
