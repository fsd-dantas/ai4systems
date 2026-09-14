"""
Multi-expert system on a blackboard / Sistema multiespecialista com quadro-negro.

PT-BR: Especialistas independentes cooperam por um quadro-negro compartilhado, sob
       um controlador central. Mapeamento para o exemplo da disciplina:
       ``QuadroNegro`` -> :class:`Blackboard`, ``AbstractEspecialista`` ->
       :class:`KnowledgeSource`, ``eh_ativado`` -> ``is_activated``, ``contribui``
       -> ``contribute``, ``Controlador`` -> :class:`Controller`,
       ``GeradorDeTarefa`` -> :class:`TaskGenerator`.

EN:    Independent experts cooperate through a shared blackboard, under a central
       controller. Mapping to the course example: ``QuadroNegro`` ->
       :class:`Blackboard`, ``AbstractEspecialista`` -> :class:`KnowledgeSource`,
       ``eh_ativado`` -> ``is_activated``, ``contribui`` -> ``contribute``,
       ``Controlador`` -> :class:`Controller`, ``GeradorDeTarefa`` ->
       :class:`TaskGenerator`.
"""

from typing import List

from aisg.blackboard.board import (
    TASK_GENERATOR,
    Blackboard,
    Entry,
    Level,
    level_label,
)
from aisg.blackboard.controller import Controller, CycleRecord, Run
from aisg.blackboard.network_sources import (
    CORRELATOR_PARAMETERS,
    AccessRouter,
    IncidentCorrelator,
    MultiRatArbiter,
    RestorationPlanner,
    medium_label,
)
from aisg.blackboard.scenarios import (
    SCENARIOS,
    Scenario,
    TaskGenerator,
    build_scenario,
    unreachable_without,
)
from aisg.blackboard.sources import (
    EXPERT_SPECS,
    KnowledgeSource,
    RuleExpert,
    build_rule_experts,
)
from aisg.domain.topology import Topology


def build_experts(topology: Topology) -> List[KnowledgeSource]:
    """Every expert of the restoration blackboard, in declaration order."""
    return [
        *build_rule_experts(),
        IncidentCorrelator(topology),
        AccessRouter(topology),
        MultiRatArbiter(),
        RestorationPlanner(topology),
    ]


def solve(scenario: Scenario, topology: Topology, *, limit: int = 100) -> Run:
    """Post a scenario's evidence and run the controller to quiescence."""
    board = Blackboard()
    TaskGenerator(board).post(scenario.observations)
    return Controller(board, build_experts(topology), limit=limit).loop()


__all__ = [
    "CORRELATOR_PARAMETERS",
    "EXPERT_SPECS",
    "SCENARIOS",
    "TASK_GENERATOR",
    "AccessRouter",
    "Blackboard",
    "Controller",
    "CycleRecord",
    "Entry",
    "IncidentCorrelator",
    "KnowledgeSource",
    "Level",
    "MultiRatArbiter",
    "RestorationPlanner",
    "RuleExpert",
    "Run",
    "Scenario",
    "TaskGenerator",
    "build_experts",
    "build_rule_experts",
    "build_scenario",
    "level_label",
    "medium_label",
    "solve",
    "unreachable_without",
]
