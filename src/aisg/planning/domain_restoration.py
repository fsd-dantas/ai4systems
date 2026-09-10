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
    # From the bench knowledge base. Not a service fault: a stop condition.
    "containment_breach": "containment-breached",
}

#: Every fault the domain can repair. A fault outside this set would have no
#: operator able to clear it, and the planner would fail with no explanation.
KNOWN_FAULTS = frozenset(f for f in DIAGNOSIS_TO_FAULT.values() if f)


def cleared(fault: str) -> str:
    """
    The literal asserting that one specific fault has been repaired.

    PT-BR: Um literal POR FALHA, e nao um sinalizador unico. Com um sinalizador
           compartilhado, reparar uma falha entre varias marcaria o no como
           verificavel enquanto as outras permanecem — e o plano fecharia a ordem
           de servico com o defeito ainda presente.
    EN:    One literal PER FAULT, not a single shared flag. With a shared flag,
           repairing one fault among several would mark the node verifiable while
           the others remain, and the plan would close the work order with the
           defect still in place.
    """
    return f"cleared-{fault}(?n)"


def build_operators(faults: Sequence[str] = ()) -> List[Operator]:
    """
    The twelve restoration operators, in STRIPS form.

    ``faults`` are the fault names present in the problem being built. They
    determine what ``verify_link`` demands: the link counts as verified only once
    *every* fault diagnosed on it has its own ``cleared-…`` literal. STRIPS has no
    negative preconditions, so "no fault remains" is expressed as the conjunction
    of the specific repairs the instance requires.
    """
    build = Operator.build
    verify_preconditions = ("diagnosed(?n)",) + tuple(cleared(f) for f in faults)

    # Safety gate. While containment is breached the rig is radiating above the
    # test's acceptance criterion, so nothing may touch the plant and no crew may
    # be sent until transmission has stopped. STRIPS cannot say "while not
    # breached", so the requirement is expressed positively: when a breach is in
    # the instance, every plant-touching operator additionally demands that the
    # breach has been cleared. Halting is what clears it, so halting must come
    # first - it is a precondition, not an instruction to be followed.
    breached = "containment-breached" in faults

    def gate_on(parameter: str) -> tuple:
        """The gate literal, bound to whichever parameter names the node."""
        if not breached:
            return ()
        return (cleared("containment-breached").replace("?n", parameter),)

    gate = gate_on("?n")
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
            preconditions=("authorized(?to)", "crew-at(?from)") + gate_on("?to"),
            add=("crew-at(?to)",),
            delete=("crew-at(?from)",),
            cost=4.0,
            description_pt="Deslocar a equipe de ?from ate ?to.",
            description_en="Move the field crew from ?from to ?to.",
        ),
        build(
            "change_channel",
            parameters=("?n",),
            preconditions=("authorized(?n)", "interference(?n)") + gate,
            add=("cleared-interference(?n)",),
            delete=("interference(?n)",),
            cost=2.0,
            description_pt="Mudar o canal de ?n para sair da emissao interferente.",
            description_en="Change the channel of ?n to move away from the interferer.",
        ),
        build(
            "realign_antenna",
            parameters=("?n",),
            preconditions=("authorized(?n)", "crew-at(?n)", "misaligned(?n)") + gate,
            add=("cleared-misaligned(?n)",),
            delete=("misaligned(?n)",),
            cost=3.0,
            description_pt="Realinhar a antena de ?n (exige equipe no local).",
            description_en="Realign the antenna at ?n (requires the crew on site).",
        ),
        build(
            "replace_power_unit",
            parameters=("?n",),
            preconditions=("authorized(?n)", "crew-at(?n)", "power-failed(?n)") + gate,
            add=("cleared-power-failed(?n)",),
            delete=("power-failed(?n)",),
            cost=5.0,
            description_pt="Substituir a fonte de alimentacao de ?n (exige equipe no local).",
            description_en="Replace the power unit at ?n (requires the crew on site).",
        ),
        build(
            "restore_relay",
            parameters=("?n",),
            preconditions=("authorized(?n)", "relay-down(?n)") + gate,
            add=("cleared-relay-down(?n)",),
            delete=("relay-down(?n)",),
            cost=2.0,
            description_pt="Recuperar o repetidor a montante de ?n.",
            description_en="Recover the relay upstream of ?n.",
        ),
        build(
            "fix_vlan",
            parameters=("?n",),
            preconditions=("authorized(?n)", "vlan-wrong(?n)") + gate,
            add=("cleared-vlan-wrong(?n)",),
            delete=("vlan-wrong(?n)",),
            cost=1.0,
            description_pt="Corrigir a lista de VLANs permitidas no tronco de ?n.",
            description_en="Correct the allowed-VLAN list on the trunk of ?n.",
        ),
        build(
            "reroute_traffic",
            parameters=("?n",),
            preconditions=("authorized(?n)", "congested(?n)", "alternate-route(?n)") + gate,
            add=("cleared-congested(?n)", "traffic-rerouted(?n)"),
            delete=("congested(?n)",),
            cost=2.0,
            description_pt="Desviar o trafego de ?n pela rota alternativa calculada por A*.",
            description_en="Reroute the traffic of ?n over the alternative route computed by A*.",
        ),
        build(
            "monitor_and_wait",
            parameters=("?n",),
            preconditions=("diagnosed(?n)", "transient(?n)"),
            add=("cleared-transient(?n)",),
            delete=("transient(?n)",),
            cost=1.0,
            description_pt="Acompanhar ?n: causa transitoria, nenhuma intervencao na planta.",
            description_en="Monitor ?n: transient cause, no intervention on the plant.",
        ),
        build(
            "halt_transmission",
            parameters=("?n",),
            # Deliberately NOT gated on authorised(?n). Authorisation exists to
            # gate changes to the plant; ceasing to transmit is the safe act, and
            # making it wait for a window would be the dangerous design.
            preconditions=("diagnosed(?n)", "containment-breached(?n)"),
            add=(cleared("containment-breached"),),
            delete=("containment-breached(?n)",),
            cost=1.0,
            description_pt="Interromper a transmissao: contencao violada.",
            description_en="Interrupt transmission: containment breached.",
        ),
        build(
            "verify_link",
            parameters=("?n",),
            preconditions=verify_preconditions,
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
    unknown = [f for f in faults if f not in KNOWN_FAULTS]
    if unknown:
        raise ValueError(
            f"unknown fault(s): {', '.join(unknown)}; expected one or more of "
            f"{', '.join(sorted(KNOWN_FAULTS))}"
        )

    initial: List[str] = [f"diagnosed({node})", f"crew-at({crew_base})"]
    initial += [f"{fault}({node})" for fault in faults]
    if alternate_route:
        initial.append(f"alternate-route({node})")
    initial += list(extra_initial)

    # With no faults the link needs only verification and closure: verify_link's
    # preconditions reduce to diagnosed(?n).
    return Problem(
        name=f"restore-service-{node}",
        operators=build_operators(faults),
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
