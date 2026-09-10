"""
Rule-based expert system / Sistema especialista baseado em regras.

PT-BR: Motor de inferencia generico + base de conhecimento de diagnostico de enlace.
EN:    Generic inference engine + link-diagnosis knowledge base.
"""

from aisg.expert_system.engine import (
    FIRING_THRESHOLD,
    Conclusion,
    Condition,
    ConflictResolution,
    Consultation,
    Fact,
    InferenceEngine,
    KnowledgeBase,
    Operator,
    Rule,
    Variable,
    VariableKind,
    WorkingMemory,
    combine_cf,
)
from aisg.expert_system.kb_backhaul import CASES, THRESHOLDS, build_knowledge_base
from aisg.expert_system.kb_bench import (
    BENCH_CASES,
    BENCH_THRESHOLDS,
    INDUCIBLE_BY,
    build_bench_knowledge_base,
)

#: The knowledge bases this engine ships with. `backhaul` models an outdoor field
#: network; `bench` models an indoor conducted rig, where weather is neither
#: observable nor inducible. Same engine, different knowledge.
KNOWLEDGE_BASES = {
    "backhaul": (build_knowledge_base, CASES),
    "bench": (build_bench_knowledge_base, BENCH_CASES),
}

__all__ = [
    "BENCH_CASES",
    "BENCH_THRESHOLDS",
    "INDUCIBLE_BY",
    "KNOWLEDGE_BASES",
    "build_bench_knowledge_base",
    "CASES",
    "FIRING_THRESHOLD",
    "THRESHOLDS",
    "Conclusion",
    "Condition",
    "ConflictResolution",
    "Consultation",
    "Fact",
    "InferenceEngine",
    "KnowledgeBase",
    "Operator",
    "Rule",
    "Variable",
    "VariableKind",
    "WorkingMemory",
    "build_knowledge_base",
    "combine_cf",
]
