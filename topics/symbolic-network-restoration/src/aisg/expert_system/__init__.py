"""
Rule-based expert system / Sistema especialista baseado em regras.

PT-BR: Motor de inferencia generico + base de conhecimento de diagnostico de enlace
       no cenario simulado.
EN:    Generic inference engine + link-diagnosis knowledge base for the simulated
       scenario.
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
from aisg.expert_system.kb_simulated import (
    INDUCIBLE_BY,
    SIM_CASES,
    SIM_THRESHOLDS,
    build_simulated_knowledge_base,
)

__all__ = [
    "INDUCIBLE_BY",
    "SIM_CASES",
    "SIM_THRESHOLDS",
    "build_simulated_knowledge_base",
    "FIRING_THRESHOLD",
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
    "combine_cf",
]
