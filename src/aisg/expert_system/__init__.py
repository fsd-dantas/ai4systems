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
from aisg.expert_system.kb_simulated import (
    INDUCIBLE_BY,
    SIM_CASES,
    SIM_THRESHOLDS,
    build_simulated_knowledge_base,
)

#: The knowledge bases this engine ships with. `backhaul` models an outdoor field
#: network, where weather attenuates the link. `simulated` models the ns-3
#: scenario, where there is no weather, no antenna and no cable - only wireless
#: nodes on a shared medium and the quantities a simulator produces. Same engine,
#: different knowledge.
KNOWLEDGE_BASES = {
    "backhaul": (build_knowledge_base, CASES),
    "simulated": (build_simulated_knowledge_base, SIM_CASES),
}

__all__ = [
    "INDUCIBLE_BY",
    "SIM_CASES",
    "SIM_THRESHOLDS",
    "KNOWLEDGE_BASES",
    "build_simulated_knowledge_base",
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
