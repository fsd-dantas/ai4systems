"""
Eco-resolution / Eco-resolucao.

PT-BR: Resolucao de problemas por interacao de agentes reativos (Ferber). Cada
       agente busca satisfazer o proprio objetivo; quem impede a satisfacao e
       agredido e foge; quem nao consegue fugir agride quem bloqueia a fuga. A
       solucao emerge das interacoes locais, sem planejador central.
EN:    Problem solving by the interaction of reactive agents (Ferber). Each agent
       seeks to satisfy its own goal; whoever prevents satisfaction is attacked
       and flees; an agent that cannot flee attacks whoever blocks its flight. The
       solution emerges from local interactions, with no central planner.
"""

from aisg.eco.blocks_world import (
    COURSE_EXAMPLE,
    BlockAgent,
    BlocksWorld,
    blocks_ecosystem,
    enumerate_configurations,
)
from aisg.eco.engine import (
    AgentState,
    EcoAgent,
    EcoWorld,
    Ecosystem,
    Move,
    Resolution,
    TraceEntry,
)
from aisg.eco.network import (
    ECO_NETWORK_PARAMETERS,
    FLOW_CLASSES,
    PARKED,
    FlowAgent,
    NetworkEcoWorld,
    NetworkProblem,
    network_ecosystem,
)

__all__ = [
    "COURSE_EXAMPLE",
    "ECO_NETWORK_PARAMETERS",
    "FLOW_CLASSES",
    "PARKED",
    "FlowAgent",
    "NetworkEcoWorld",
    "NetworkProblem",
    "network_ecosystem",
    "AgentState",
    "BlockAgent",
    "BlocksWorld",
    "EcoAgent",
    "EcoWorld",
    "Ecosystem",
    "Move",
    "Resolution",
    "TraceEntry",
    "blocks_ecosystem",
    "enumerate_configurations",
]
