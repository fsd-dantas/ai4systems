"""
Planning domain: restoring service on a degraded backhaul node.

PT-BR: Este dominio e o ponto de encontro dos tres trabalhos. O DIAGNOSTICO vem do
       sistema especialista e vira o estado inicial; o PLANO e gerado por GPS ou por
       A* progressivo; e a acao 'desviar trafego' so e aplicavel quando a BUSCA A*
       sobre a topologia confirma que existe rota alternativa.

EN:    This domain is where the three assignments meet. The DIAGNOSIS comes from the
       expert system and becomes the initial state; the PLAN is produced by GPS or by
       A* progression; and the 'reroute traffic' action is applicable only when A*
       SEARCH over the topology confirms an alternative route exists.

Governance encoded as preconditions / Governanca como precondicao
-----------------------------------------------------------------
Every operator that reaches the plant requires ``authorized(?n)``. That is not
decoration: it makes "we acted without authorisation" *unreachable* rather than
merely discouraged. Only ``monitor_and_wait`` skips it, because observing changes
nothing.
"""

from __future__ import annotations

from typing import Dict, Iterable, List, Optional, Sequence

from aisg.domain.topology import Topology
from aisg.planning.strips import Operator, Predicate, Problem, make_state

#: Base of operations the field crew starts from.
CREW_BASE = "BASE"

#: Expert-system diagnosis -> the fault literal it puts in the initial state.
DIAGNOSIS_TO_FAULT: Dict[str, Optional[str]] = {
    "rf_interference": "interference",
    "path_obstruction": "misaligned",
    "rain_fade": "transient",
    "node_power_failure": "power-failed",
    "upstream_relay_failure": "relay-down",
    "vlan_misconfiguration": "vlan-wrong",
    "congestion": "congested",
    "healthy": None,  # nothing to repair; the link is already clear
}


def build_operators() -> List[Operator]:
    """The twelve restoration operators, in STRIPS form."""
    build = Operator.build
    return [
        build(
            "request_authorization",
            parameters=("?n",),
            preconditions=("diagnosed(?n)",),
            add=("authorized(?n)",),
            cost=1.0,
            description_pt="Solicitar autorizacao e janela de manutencao para ?n.",
            description_en="Request authorisation and a maintenance window for ?n.",
        ),
        build(
            "dispatch_crew",
            parameters=("?from", "?to"),
            preconditions=("authorized(?to)", "crew-at(?from)"),
            add=("crew-at(?to)",),
            delete=("crew-at(?from)",),
            cost=4.0,
            description_pt="Deslocar a equipe de ?from ate ?to.",
            description_en="Move the field crew from ?from to ?to.",
        ),
        build(
            "change_channel",
            parameters=("?n",),
            preconditions=("authorized(?n)", "interference(?n)"),
            add=("fault-cleared(?n)",),
            delete=("interference(?n)",),
            cost=2.0,
            description_pt="Mudar o canal de ?n para sair da emissao interferente.",
            description_en="Change the channel of ?n to move away from the interferer.",
        ),
        build(
            "realign_antenna",
            parameters=("?n",),
            preconditions=("authorized(?n)", "crew-at(?n)", "misaligned(?n)"),
            add=("fault-cleared(?n)",),
            delete=("misaligned(?n)",),
            cost=3.0,
            description_pt="Realinhar a antena de ?n (exige equipe no local).",
            description_en="Realign the antenna at ?n (requires the crew on site).",
        ),
        build(
            "replace_power_unit",
            parameters=("?n",),
            preconditions=("authorized(?n)", "crew-at(?n)", "power-failed(?n)"),
            add=("fault-cleared(?n)",),
            delete=("power-failed(?n)",),
            cost=5.0,
            description_pt="Substituir a fonte de alimentacao de ?n (exige equipe no local).",
            description_en="Replace the power unit at ?n (requires the crew on site).",
        ),
        build(
            "restore_relay",
            parameters=("?n",),
            preconditions=("authorized(?n)", "relay-down(?n)"),
            add=("fault-cleared(?n)",),
            delete=("relay-down(?n)",),
            cost=2.0,
            description_pt="Recuperar o repetidor a montante de ?n.",
            description_en="Recover the relay upstream of ?n.",
        ),
        build(
            "fix_vlan",
            parameters=("?n",),
            preconditions=("authorized(?n)", "vlan-wrong(?n)"),
            add=("fault-cleared(?n)",),
            delete=("vlan-wrong(?n)",),
            cost=1.0,
            description_pt="Corrigir a lista de VLANs permitidas no tronco de ?n.",
            description_en="Correct the allowed-VLAN list on the trunk of ?n.",
        ),
        build(
            "reroute_traffic",
            parameters=("?n",),
            preconditions=("authorized(?n)", "congested(?n)", "alternate-route(?n)"),
            add=("fault-cleared(?n)", "traffic-rerouted(?n)"),
            delete=("congested(?n)",),
            cost=2.0,
            description_pt="Desviar o trafego de ?n pela rota alternativa calculada por A*.",
            description_en="Reroute the traffic of ?n over the alternative route computed by A*.",
        ),
        build(
            "monitor_and_wait",
            parameters=("?n",),
            preconditions=("diagnosed(?n)", "transient(?n)"),
            add=("fault-cleared(?n)",),
            delete=("transient(?n)",),
            cost=1.0,
            description_pt="Acompanhar ?n: causa transitoria, nenhuma intervencao na planta.",
            description_en="Monitor ?n: transient cause, no intervention on the plant.",
        ),
        build(
            "verify_link",
            parameters=("?n",),
            preconditions=("fault-cleared(?n)",),
            add=("link-up(?n)",),
            cost=1.0,
            description_pt="Verificar o enlace de ?n apos a correcao.",
            description_en="Verify the link at ?n after the correction.",
        ),
        build(
            "record_logbook",
            parameters=("?n",),
            preconditions=("link-up(?n)",),
            add=("logged(?n)",),
            cost=1.0,
            description_pt="Registrar a intervencao em ?n no livro de registro.",
            description_en="Record the intervention on ?n in the logbook.",
        ),
        build(
            "close_work_order",
            parameters=("?n",),
            preconditions=("link-up(?n)", "logged(?n)"),
            add=("service-restored(?n)",),
            cost=1.0,
            description_pt="Encerrar a ordem de servico de ?n.",
            description_en="Close the work order for ?n.",
        ),
    ]


def _no_self_move(operator_name: str, binding: Dict[str, str]) -> bool:
    """Reject dispatching the crew from a place to that same place."""
    if operator_name == "dispatch_crew":
        return binding.get("?from") != binding.get("?to")
    return True


def build_restoration_problem(
    node: str,
    faults: Sequence[str],
    *,
    alternate_route: bool = False,
    crew_base: str = CREW_BASE,
    extra_initial: Iterable[str] = (),
) -> Problem:
    """
    Build the STRIPS problem for restoring ``node``.

    :param faults: fault predicate names, e.g. ``["interference"]``.
    :param alternate_route: whether A* confirmed an alternative route exists.
    """
    initial: List[str] = [f"diagnosed({node})", f"crew-at({crew_base})"]
    initial += [f"{fault}({node})" for fault in faults]
    if alternate_route:
        initial.append(f"alternate-route({node})")
    if not faults:
        # Nothing to repair: the link is already clear, only closure remains.
        initial.append(f"fault-cleared({node})")
    initial += list(extra_initial)

    return Problem(
        name=f"restore-service-{node}",
        operators=build_operators(),
        initial=make_state(initial),
        goal=make_state([f"service-restored({node})", f"logged({node})"]),
        objects={"node": [node], "location": [crew_base, node]},
        parameter_types={"?n": "node", "?from": "location", "?to": "location"},
        binding_filter=_no_self_move,
    )


def problem_from_diagnosis(
    diagnosis: str,
    node: str,
    *,
    topology: Optional[Topology] = None,
    reroute_target: Optional[str] = None,
    crew_base: str = CREW_BASE,
) -> Problem:
    """
    Turn an expert-system diagnosis into a planning problem.

    PT-BR: Quando o diagnostico e congestionamento, consultamos o A* sobre a topologia
           para saber se existe de fato rota alternativa evitando o no afetado. Se nao
           existir, a acao 'desviar trafego' fica inaplicavel e o planejador precisa
           encontrar outro caminho — ou falhar honestamente.
    EN:    When the diagnosis is congestion we consult A* over the topology to learn
           whether an alternative route avoiding the affected node really exists. If
           it does not, 'reroute traffic' is inapplicable and the planner must find
           another way — or fail honestly.
    """
    if diagnosis not in DIAGNOSIS_TO_FAULT:
        raise ValueError(
            f"unknown diagnosis {diagnosis!r}; expected one of "
            f"{', '.join(sorted(DIAGNOSIS_TO_FAULT))}"
        )

    fault = DIAGNOSIS_TO_FAULT[diagnosis]
    faults = [fault] if fault else []

    alternate = False
    if fault == "congested" and topology is not None:
        from aisg.search.graph_problem import shortest_route

        source = reroute_target or _default_source(topology)
        target = _default_target(topology, node)
        if target is not None:
            alternate = shortest_route(topology, source, target, avoid=(node,)) is not None

    return build_restoration_problem(
        node, faults, alternate_route=alternate, crew_base=crew_base
    )


def _default_source(topology: Topology) -> str:
    """The operations centre, if the topology declares one."""
    for node in topology.nodes.values():
        if node.kind == "control_centre":
            return node.id
    return next(iter(topology.nodes))


def _default_target(topology: Topology, node: str) -> Optional[str]:
    """
    A node whose traffic the congested node carries.

    PT-BR: Usamos um dispositivo de campo a jusante como destino do desvio.
    EN:    We use a downstream field device as the reroute destination.
    """
    for candidate in topology.nodes.values():
        if candidate.kind == "field_device" and candidate.id != node:
            return candidate.id
    return None


def fault_literals(problem: Problem) -> List[Predicate]:
    """The fault literals present in a problem's initial state, for reporting."""
    fault_names = {name for name in DIAGNOSIS_TO_FAULT.values() if name}
    return sorted(
        (p for p in problem.initial if p.name in fault_names), key=str
    )
