"""
Pull evidence from Prometheus into an observation record.

PT-BR: Escrito para um laboratorio que ainda NAO esta pronto. Cada metrica e
       buscada de forma independente: uma consulta que falha, ou que nao retorna
       serie alguma, vira uma entrada em `unavailable` com o motivo — nunca um
       valor plausivel. Assim, instrumentar a bancada aos poucos aumenta a
       cobertura de forma monotonica, sem que a saida minta enquanto isso.

EN:    Written for a laboratory that is NOT yet ready. Each metric is fetched
       independently: a query that fails, or returns no series, becomes an entry
       in `unavailable` with the reason - never a plausible value. Instrumenting
       the bench gradually therefore raises coverage monotonically, without the
       output lying in the meantime.

Usa apenas a biblioteca padrao / Standard library only: the package core takes no
third-party dependencies, and that includes this.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Mapping, Optional, Sequence

from aisg.observation import Observation, _now


class PrometheusError(RuntimeError):
    """Raised when Prometheus is unreachable or answers with an error."""


# --------------------------------------------------------------------------
# converters: Prometheus units -> the units the knowledge base declares
# --------------------------------------------------------------------------
def identity(value: float) -> float:
    return value


def seconds_to_ms(value: float) -> float:
    return value * 1000.0


def success_ratio_to_loss_pct(value: float) -> float:
    """`probe_success` is 1 when the probe worked; the base wants loss percent."""
    return max(0.0, min(100.0, (1.0 - value) * 100.0))


def fraction_to_pct(value: float) -> float:
    return value * 100.0


CONVERTERS: Dict[str, Callable[[float], float]] = {
    "identity": identity,
    "seconds_to_ms": seconds_to_ms,
    "success_ratio_to_loss_pct": success_ratio_to_loss_pct,
    "fraction_to_pct": fraction_to_pct,
}


@dataclass
class MetricSpec:
    """
    How one knowledge-base variable is obtained from Prometheus.

    ``query`` may contain ``{subject}``, replaced with the link or node id. For a
    categorical variable, ``mapping`` turns the numeric result into a declared
    label; without it the converted number is used as-is.
    """

    variable: str
    query: str
    convert: str = "identity"
    mapping: Optional[Dict[str, str]] = None
    cf: float = 1.0
    note: str = ""

    def render(self, subject: str) -> str:
        return self.query.replace("{subject}", subject)

    def interpret(self, raw: float) -> Any:
        value = CONVERTERS[self.convert](raw)
        if self.mapping is None:
            return value
        key = str(int(value)) if float(value).is_integer() else str(value)
        if key not in self.mapping:
            raise PrometheusError(
                f"{self.variable}: result {value!r} is not in the declared mapping "
                f"({', '.join(sorted(self.mapping))})"
            )
        return self.mapping[key]


#: A starting set for the field knowledge base. Queries are deliberately generic:
#: metric names differ per exporter, so treat these as templates to edit, not as
#: names that will exist in any particular installation.
DEFAULT_SPECS: List[MetricSpec] = [
    MetricSpec("rssi_dbm", 'min_over_time(radio_rssi_dbm{{link="{subject}"}}[5m])'),
    MetricSpec("snr_db", 'min_over_time(radio_snr_db{{link="{subject}"}}[5m])'),
    MetricSpec(
        "packet_loss_pct",
        'avg_over_time(probe_success{{link="{subject}"}}[5m])',
        convert="success_ratio_to_loss_pct",
    ),
    MetricSpec(
        "rtt_ms",
        'avg_over_time(probe_duration_seconds{{link="{subject}"}}[5m])',
        convert="seconds_to_ms",
    ),
    MetricSpec(
        "traffic_load_pct",
        '100 * rate(link_in_octets{{link="{subject}"}}[5m]) * 8'
        ' / link_capacity_bps{{link="{subject}"}}',
    ),
    MetricSpec(
        "link_state",
        'link_oper_status{{link="{subject}"}}',
        mapping={"1": "up", "0": "down"},
        note="flapping is not a level; derive it from changes() over a window",
    ),
    MetricSpec(
        "upstream_relay_reachable",
        'probe_success{{link="{subject}",role="upstream"}}',
        mapping={"1": "yes", "0": "no"},
    ),
]


@dataclass
class PrometheusClient:
    """Minimal read-only client for the instant-query API."""

    base_url: str
    timeout: float = 10.0
    #: injected in tests; production leaves it as the real fetcher
    _fetch: Optional[Callable[[str], Mapping[str, Any]]] = field(
        default=None, repr=False
    )

    def instant(self, query: str) -> Mapping[str, Any]:
        if self._fetch is not None:
            return self._fetch(query)
        url = (
            self.base_url.rstrip("/")
            + "/api/v1/query?"
            + urllib.parse.urlencode({"query": query})
        )
        try:
            with urllib.request.urlopen(url, timeout=self.timeout) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.URLError as exc:
            raise PrometheusError(f"cannot reach Prometheus at {self.base_url}: {exc}")
        except json.JSONDecodeError as exc:
            raise PrometheusError(f"Prometheus returned malformed JSON: {exc}")

    def scalar(self, query: str) -> float:
        """
        One number for one query.

        Prometheus returns values as STRINGS and timestamps as float seconds; both
        are normalised here so callers never see that detail.
        """
        payload = self.instant(query)
        if payload.get("status") != "success":
            raise PrometheusError(
                f"query failed: {payload.get('error', 'no reason given')}"
            )
        result = (payload.get("data") or {}).get("result") or []
        if not result:
            raise PrometheusError("query returned no series")
        if len(result) > 1:
            raise PrometheusError(
                f"query returned {len(result)} series; add a label so it selects one"
            )
        try:
            return float(result[0]["value"][1])
        except (KeyError, IndexError, TypeError, ValueError) as exc:
            raise PrometheusError(f"unexpected result shape: {exc}")


def fetch_observation(
    client: PrometheusClient,
    subject: str,
    specs: Sequence[MetricSpec] = (),
    *,
    subject_kind: str = "link",
    window: str = "5m",
) -> Observation:
    """
    Build an observation from whatever Prometheus can currently answer.

    Every metric is attempted independently. A failure is recorded as a reason in
    ``unavailable`` and the variable stays unknown, so a partly instrumented bench
    yields a partly populated record rather than an error or a guess.
    """
    specs = list(specs) if specs else list(DEFAULT_SPECS)
    record = Observation(
        subject_id=subject,
        subject_kind=subject_kind,
        captured_at=_now(),
        source=f"prometheus:{client.base_url}",
        window=window,
    )

    for spec in specs:
        query = spec.render(subject)
        try:
            raw = client.scalar(query)
            value = spec.interpret(raw)
        except PrometheusError as exc:
            reason = str(exc)
            if spec.note:
                reason = f"{reason} ({spec.note})"
            record.unavailable[spec.variable] = reason
            continue
        record.values[spec.variable] = (value, spec.cf)
        record.provenance[spec.variable] = query

    return record


def load_specs(path: str) -> List[MetricSpec]:
    """
    Read metric specs from JSON, so queries can be edited without touching code.

    Each entry: ``{"variable", "query", "convert"?, "mapping"?, "cf"?, "note"?}``.
    """
    with open(path, encoding="utf-8") as handle:
        entries = json.load(handle)
    specs: List[MetricSpec] = []
    for entry in entries:
        convert = entry.get("convert", "identity")
        if convert not in CONVERTERS:
            raise PrometheusError(
                f"unknown converter {convert!r}; available: {', '.join(sorted(CONVERTERS))}"
            )
        specs.append(
            MetricSpec(
                variable=entry["variable"],
                query=entry["query"],
                convert=convert,
                mapping=entry.get("mapping"),
                cf=float(entry.get("cf", 1.0)),
                note=entry.get("note", ""),
            )
        )
    return specs
