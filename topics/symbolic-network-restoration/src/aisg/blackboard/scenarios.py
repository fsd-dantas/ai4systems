"""
Task generator: the fault scenarios that put evidence on the board.

PT-BR: Corresponde ao ``GeradorDeTarefa`` do exemplo da disciplina. Cada cenario
       COMANDA falhas na topologia e produz a observacao de cada no a partir dos
       casos da base simulada. Quem esta a jusante de uma falha e decidido por
       ALCANCABILIDADE (busca em largura sem os nos falhos), e nao pelas rotas que o
       correlacionador usa - assim o cenario nao compartilha codigo com o que ele
       vai verificar.

       As falhas comandadas ficam em ``commanded`` e servem SO para avaliar o
       resultado. Nenhum especialista as le.

EN:    Corresponds to the course example's ``GeradorDeTarefa``. Each scenario
       COMMANDS faults on the topology and produces every node's observation from
       the simulated base's cases. What lies downstream of a fault is decided by
       REACHABILITY (breadth-first search without the failed nodes), not by the
       routes the correlator uses, so the scenario shares no code with what it will
       check.

       The commanded faults live in ``commanded`` and are used ONLY to score the
       result. No expert reads them.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from typing import Callable, Dict, Iterable, List, Set

from aisg.blackboard.board import TASK_GENERATOR, Blackboard, Entry, Level
from aisg.domain.topology import Topology
from aisg.expert_system import SIM_CASES
from aisg.observation import Observation

#: Node kinds that report telemetry in the scenarios.
OBSERVED_KINDS = ("saf_relay", "lte_relay", "remote_radio", "cpe")


@dataclass
class Scenario:
    name: str
    title_pt: str
    title_en: str
    observations: List[Observation] = field(default_factory=list)
    #: node -> diagnosis actually commanded. Ground truth, for scoring only.
    commanded: Dict[str, str] = field(default_factory=dict)

    def title(self, lang: str = "pt") -> str:
        return self.title_pt if lang == "pt" else self.title_en


def observation_for(node: str, case: str, scenario: str) -> Observation:
    return Observation(
        subject_id=node,
        subject_kind="node",
        source=f"scenario:{scenario}",
        values={variable: (value, 1.0) for variable, value in SIM_CASES[case].items()},
    )


def unreachable_without(topology: Topology, failed: Iterable[str]) -> Set[str]:
    """
    Observed nodes the control centre can no longer reach once ``failed`` stop.

    PT-BR: Busca em largura a partir do centro de operacao, sem atravessar nos
           falhos nem roteadores de borda (que nao fazem transito).
    EN:    Breadth-first search from the operations centre, crossing neither
           failed nodes nor edge routers (which do not carry transit).
    """
    down = set(failed)
    start = next(n.id for n in topology.nodes.values() if n.kind == "control_centre")
    seen = {start}
    queue = deque([start])
    while queue:
        node = queue.popleft()
        if node != start and topology.node(node).stub:
            continue
        for neighbour, _link in topology.neighbours(node):
            if neighbour not in seen and neighbour not in down:
                seen.add(neighbour)
                queue.append(neighbour)
    return {
        n.id for n in topology.nodes.values()
        if n.kind in OBSERVED_KINDS and n.id not in seen and n.id not in down
    }


def relay_outage(topology: Topology, name: str, failed: List[str],
                 title_pt: str, title_en: str) -> Scenario:
    """Stop ``failed``; everything they cut reports an upstream-relay failure."""
    cut = unreachable_without(topology, failed)
    scenario = Scenario(name, title_pt, title_en,
                        commanded={node: "node_failure" for node in failed})
    for node in sorted(n.id for n in topology.nodes.values() if n.kind in OBSERVED_KINDS):
        if node in failed:
            case = "node_failure"
        elif node in cut:
            case = "upstream_relay_failure"
        else:
            case = "healthy"
        scenario.observations.append(observation_for(node, case, name))
    return scenario


def independent_faults(topology: Topology) -> Scenario:
    """Two unrelated degradations: nothing should be merged into a common cause."""
    name = "independent-faults"
    faults = {"RM_07": "rf_interference", "RELAY_5": "congestion"}
    scenario = Scenario(
        name,
        "Duas degradacoes independentes: interferencia em RM_07 e congestionamento em RELAY_5",
        "Two independent degradations: interference at RM_07, congestion at RELAY_5",
        commanded=dict(faults),
    )
    for node in sorted(n.id for n in topology.nodes.values() if n.kind in OBSERVED_KINDS):
        scenario.observations.append(observation_for(node, faults.get(node, "healthy"), name))
    return scenario


SCENARIOS: Dict[str, Callable[[Topology], Scenario]] = {
    "saf-chain-outage": lambda topo: relay_outage(
        topo, "saf-chain-outage", ["SAF_02"],
        "Queda do repetidor SAF_02 na cadeia de 900 MHz",
        "Relay SAF_02 down in the 900 MHz chain",
    ),
    "dual-outage": lambda topo: relay_outage(
        topo, "dual-outage", ["SAF_02", "RELAY_5"],
        "Queda simultanea de SAF_02 (900 MHz) e RELAY_5 (LTE privativo)",
        "Simultaneous loss of SAF_02 (900 MHz) and RELAY_5 (private LTE)",
    ),
    "independent-faults": independent_faults,
}


def build_scenario(name: str, topology: Topology) -> Scenario:
    if name not in SCENARIOS:
        raise KeyError(f"unknown scenario {name!r}; available: {', '.join(sorted(SCENARIOS))}")
    return SCENARIOS[name](topology)


class TaskGenerator:
    """Posts a scenario's observations on the board, one subject at a time."""

    def __init__(self, board: Blackboard) -> None:
        self.board = board

    def post(self, observations: Iterable[Observation]) -> int:
        count = 0
        for observation in observations:
            entries = [
                Entry(
                    level=Level.OBSERVATION,
                    subject=observation.subject_id,
                    key=variable,
                    value=value,
                    cf=cf,
                    author=TASK_GENERATOR,
                    support=(observation.source,),
                )
                for variable, (value, cf) in sorted(observation.values.items())
            ]
            self.board.publish(
                TASK_GENERATOR, entries,
                levels=(Level.OBSERVATION,), subjects=(observation.subject_id,),
            )
            count += 1
        return count
