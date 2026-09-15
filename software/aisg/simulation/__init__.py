"""
Network simulation support / Suporte a simulacao de rede.

PT-BR: Exporta a topologia declarada para os programas ns-3 em
       ``software/ns-3-modules/``. O nucleo continua sem dependencias: o ns-3 e
       usado fora do Python, lendo o arquivo de cenario gerado aqui.
EN:    Exports the declared topology to the ns-3 programs under
       ``software/ns-3-modules/``. The core stays dependency-free: ns-3 runs
       outside Python, reading the scenario file generated here.
"""

from aisg.simulation.ns3_scenario import (
    FORMAT_HEADER,
    NS3_PARAMETERS,
    LinkBudget,
    Ns3Scenario,
    P2PLink,
    ScenarioError,
    Site,
    build_ns3_scenario,
    radio_link_budget,
)

__all__ = [
    "FORMAT_HEADER",
    "NS3_PARAMETERS",
    "LinkBudget",
    "Ns3Scenario",
    "P2PLink",
    "ScenarioError",
    "Site",
    "build_ns3_scenario",
    "radio_link_budget",
]
