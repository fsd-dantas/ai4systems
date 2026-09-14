"""
Observation records: evidence gathered from a real system, fed to the engine.

PT-BR: Um registro de observacao e o que separa "o sistema funciona com casos
       inventados" de "o sistema funciona com o que o laboratorio consegue medir
       hoje". Ele e deliberadamente tolerante a lacunas: uma variavel ausente fica
       DESCONHECIDA, e nunca recebe um valor plausivel por conveniencia. Inventar
       um valor omitido e como se produzem diagnosticos confiantes e errados.

EN:    An observation record is what separates "the system works on invented
       cases" from "the system works on what the laboratory can measure today".
       It is deliberately tolerant of gaps: a missing variable stays UNKNOWN and
       is never given a plausible value for convenience. Inventing an omitted
       value is how confident, wrong diagnoses are produced.

Formato / Format
----------------
```json
{
  "schema": "aisg-observation/1",
  "captured_at": "2026-09-10T14:32:00Z",
  "source": "prometheus",
  "window": "5m",
  "subject": { "kind": "link", "id": "RELAY_5-CPE_03" },
  "observations": {
    "rssi_dbm":           { "value": -97.2, "cf": 1.0, "query": "min_over_time(...)" },
    "co_channel_emitter": { "value": "yes", "cf": 0.6, "source": "operator-read sweep" }
  },
  "unavailable": { "retry_rate_pct": "no exporter for the MAC counters yet" }
}
```

``cf`` carries how much the reading should be believed. A locally measured RSSI
earns 1.0; an operator reading a spectrum sweep by eye is evidence, not
measurement, and should say so with something lower. ``unavailable`` records why
a variable is missing, so a gap is documented rather than merely absent.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Tuple

SCHEMA = "aisg-observation/1"


class ObservationError(ValueError):
    """Raised when a record is malformed or disagrees with the knowledge base."""


@dataclass
class Observation:
    """Evidence about one subject at one moment."""

    subject_id: str
    subject_kind: str = "link"
    captured_at: str = ""
    source: str = "manual"
    window: str = ""
    #: variable -> (value, certainty)
    values: Dict[str, Tuple[Any, float]] = field(default_factory=dict)
    #: variable -> why it could not be obtained
    unavailable: Dict[str, str] = field(default_factory=dict)
    #: variable -> free-form provenance (the query, the exporter, the operator)
    provenance: Dict[str, str] = field(default_factory=dict)

    # -- construction ----------------------------------------------------
    @classmethod
    def from_dict(cls, raw: Mapping[str, Any]) -> "Observation":
        schema = raw.get("schema", SCHEMA)
        if schema != SCHEMA:
            raise ObservationError(
                f"unsupported schema {schema!r}; this build reads {SCHEMA!r}"
            )
        subject = raw.get("subject") or {}
        if not subject.get("id"):
            raise ObservationError("subject.id is required")

        record = cls(
            subject_id=str(subject["id"]),
            subject_kind=str(subject.get("kind", "link")),
            captured_at=str(raw.get("captured_at", "")),
            source=str(raw.get("source", "manual")),
            window=str(raw.get("window", "")),
            unavailable=dict(raw.get("unavailable", {}) or {}),
        )

        for name, entry in (raw.get("observations") or {}).items():
            if isinstance(entry, Mapping):
                if "value" not in entry:
                    raise ObservationError(f"{name}: entry has no 'value'")
                value = entry["value"]
                cf = float(entry.get("cf", 1.0))
                origin = entry.get("query") or entry.get("source")
                if origin:
                    record.provenance[name] = str(origin)
            else:
                # A bare value is accepted, and taken as fully certain.
                value, cf = entry, 1.0
            if not -1.0 <= cf <= 1.0:
                raise ObservationError(f"{name}: cf must be in [-1, 1], got {cf}")
            record.values[name] = (value, cf)
        return record

    @classmethod
    def load(cls, path: Path | str) -> "Observation":
        with Path(path).open(encoding="utf-8") as handle:
            return cls.from_dict(json.load(handle))

    def to_dict(self) -> Dict[str, Any]:
        observations: Dict[str, Any] = {}
        for name, (value, cf) in sorted(self.values.items()):
            entry: Dict[str, Any] = {"value": value, "cf": cf}
            if name in self.provenance:
                entry["query"] = self.provenance[name]
            observations[name] = entry
        payload: Dict[str, Any] = {
            "schema": SCHEMA,
            "captured_at": self.captured_at or _now(),
            "source": self.source,
            "subject": {"kind": self.subject_kind, "id": self.subject_id},
            "observations": observations,
        }
        if self.window:
            payload["window"] = self.window
        if self.unavailable:
            payload["unavailable"] = dict(sorted(self.unavailable.items()))
        return payload

    def save(self, path: Path | str) -> None:
        Path(path).write_text(
            json.dumps(self.to_dict(), indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

    # -- use --------------------------------------------------------------
    def validate_against(self, kb) -> List[str]:
        """
        Check the record against a knowledge base without applying it.

        Returns the problems found. An empty list means every value is a variable
        the base declares, of the right type, and inside its declared domain.
        """
        problems: List[str] = []
        for name, (value, _cf) in self.values.items():
            variable = kb.variables.get(name)
            if variable is None:
                problems.append(f"{name}: not a variable of this knowledge base")
                continue
            if not variable.askable:
                problems.append(f"{name}: is concluded by rules, not observed")
                continue
            try:
                variable.validate_value(value)
            except ValueError as exc:
                problems.append(f"{name}: {exc}")
        return problems

    def apply_to(self, engine) -> int:
        """Load every observed value into the engine. Returns how many were applied."""
        problems = self.validate_against(engine.kb)
        if problems:
            raise ObservationError(
                "record does not fit the knowledge base:\n  - "
                + "\n  - ".join(problems)
            )
        for name, (value, cf) in self.values.items():
            engine.given(name, value, cf)
        return len(self.values)

    def coverage(self, kb) -> Tuple[int, int, List[str]]:
        """
        How much of the askable evidence this record supplies.

        Returns ``(supplied, askable, missing)``. Partial coverage is normal while
        instrumentation is being built: the engine simply concludes less, and
        backward chaining will ask for what matters.
        """
        askable = [v.name for v in kb.variables.values() if v.askable]
        missing = sorted(set(askable) - set(self.values))
        return len(self.values), len(askable), missing

    def report(self, kb, lang: str = "pt") -> str:
        supplied, askable, missing = self.coverage(kb)
        lines = []
        if lang == "pt":
            lines.append(f"Observacao de {self.subject_id} ({self.subject_kind})")
            if self.captured_at:
                lines.append(f"  capturada em {self.captured_at}  fonte: {self.source}"
                             + (f"  janela: {self.window}" if self.window else ""))
            lines.append(f"  cobertura: {supplied} de {askable} variaveis perguntaveis")
            if missing:
                lines.append(f"  ausentes: {', '.join(missing)}")
            for name, reason in sorted(self.unavailable.items()):
                lines.append(f"    {name}: {reason}")
            if missing:
                lines.append("  variaveis ausentes permanecem DESCONHECIDAS — nada e presumido")
        else:
            lines.append(f"Observation of {self.subject_id} ({self.subject_kind})")
            if self.captured_at:
                lines.append(f"  captured {self.captured_at}  source: {self.source}"
                             + (f"  window: {self.window}" if self.window else ""))
            lines.append(f"  coverage: {supplied} of {askable} askable variables")
            if missing:
                lines.append(f"  missing: {', '.join(missing)}")
            for name, reason in sorted(self.unavailable.items()):
                lines.append(f"    {name}: {reason}")
            if missing:
                lines.append("  missing variables stay UNKNOWN - nothing is assumed")
        return "\n".join(lines)


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace(
        "+00:00", "Z"
    )
