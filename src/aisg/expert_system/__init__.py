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

__all__ = [
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
