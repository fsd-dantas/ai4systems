"""
Knowledge base: diagnosis on an INDOOR conducted RF bench.

PT-BR: Segunda base de conhecimento sobre o MESMO motor de inferencia. A base de
       [`kb_backhaul`] modela uma rede de campo, onde a propagacao e exterior e a
       chuva atenua o enlace. Num laboratorio interno de percurso conduzido, isso
       nao se aplica: nao ha clima a observar e nao ha desvanecimento por chuva a
       induzir. Uma regra que nao pode disparar nao e conservadorismo — e regra
       morta, que da falsa impressao de cobertura.

EN:    A second knowledge base over the SAME inference engine. [`kb_backhaul`]
       models a field network, where propagation is outdoors and rain attenuates
       the link. On an indoor conducted bench neither applies: there is no weather
       to observe and no rain fade to induce. A rule that can never fire is not
       caution - it is a dead rule that gives a false impression of coverage.

O que muda / What changes
-------------------------
=========================  ==================================================
`weather` (clear/rain/storm)  ->  `attenuation_db`, a atenuacao COMANDADA
`rain_fade`                   ->  `excess_attenuation`
`path_obstruction`            ->  `cabling_fault`
=========================  ==================================================

`attenuation_db` e estritamente melhor que `weather` como evidencia: e observavel
E controlavel. O clima acontece; a atenuacao e comandada. Por isso cada condicao
desta base pode ser **induzida deliberadamente** — ver :data:`INDUCIBLE_BY`.

`attenuation_db` is strictly better evidence than `weather`: it is observable AND
controllable. Weather happens; attenuation is commanded. Every condition in this
base can therefore be **induced deliberately** - see :data:`INDUCIBLE_BY`.

Por que isso importa para os dados / Why this matters for data
--------------------------------------------------------------
A base de campo nao pode ser aprendida porque nao ha rotulos: ninguem sabe, na
hora da medicao, que a chuva causou aquela perda. Aqui o operador **comanda** a
condicao, portanto conhece o rotulo por construcao. Esta base define, assim, o
conjunto de classes para as quais dados rotulados sao *produziveis* — que e a
condicao que falta para qualquer metodo indutivo neste dominio.

The field base cannot be learned because it has no labels: nobody knows, at
measurement time, that rain caused that loss. Here the operator *commands* the
condition and therefore knows the label by construction. This base defines the
set of classes for which labelled data is *producible* - the missing precondition
for any inductive method in this domain.
"""

from __future__ import annotations

from typing import Dict, Union

from aisg.expert_system.engine import (
    Condition,
    Conclusion,
    KnowledgeBase,
    Operator,
    Rule,
    Variable,
    VariableKind,
)

Number = Union[int, float]

#: NOMINAL, UNCALIBRATED. Replace with measured distributions once a scrape of
#: the bench exists; the rules that use them do not change.
BENCH_THRESHOLDS: Dict[str, Number] = {
    "rssi_poor_dbm": -95.0,
    "rssi_marginal_dbm": -85.0,
    "snr_poor_db": 8.0,
    "snr_marginal_db": 15.0,
    "loss_high_pct": 5.0,
    "loss_low_pct": 1.0,
    "rtt_high_ms": 250.0,
    "load_high_pct": 80.0,
    # Bench-specific. The nominal figure is the fixed insertion loss of the
    # conducted path with the attenuator at its floor; "high" is where path loss
    # starts to dominate the link budget rather than the radio.
    "attenuation_nominal_db": 6.0,
    "attenuation_high_db": 30.0,
    # PLACEHOLDER. The containment acceptance criterion is per-experiment and
    # belongs to the authorised test plan; it is not a value to invent here.
    # Replace with the figure the plan declares before any transmitting run.
    "leakage_limit_dbm": -60.0,
}

#: How each diagnosis is DELIBERATELY INDUCED on the bench. This is the
#: experiment protocol for producing labelled data: command the condition, record
#: the telemetry, and the label is known because you set it.
INDUCIBLE_BY: Dict[str, str] = {
    "rf_interference": "inject a carrier or noise source into the conducted path",
    "excess_attenuation": "raise the programmable attenuator above the nominal floor",
    "cabling_fault": "loosen or substitute a connector, or swap in a known-bad cable",
    "node_power_failure": "remove bench power from the node, or run it down on battery",
    "upstream_relay_failure": "power down or isolate the store-and-forward relay",
    "vlan_misconfiguration": "remove the VLAN from the trunk allow-list on the switch",
    "congestion": "drive the link past capacity with a traffic generator",
    "healthy": "baseline run: attenuator at floor, no injection, nominal configuration",
    # Not a condition to induce. It is detected during any transmitting run and
    # stops it. Listed so the "every diagnosis is accounted for" test still holds.
    "containment_breach": "NOT induced deliberately: measured during a run and halts it",
}

VALIDITY_PT = (
    "LIMITE DE VALIDADE: base para BANCADA INTERNA de percurso conduzido. Os "
    "limiares sao NOMINAIS e NAO CALIBRADOS ate que exista medicao. Ao contrario "
    "da base de campo, toda condicao aqui e INDUZIVEL — logo, rotulavel: o "
    "operador comanda a condicao e conhece o rotulo por construcao. O sistema "
    "RECOMENDA, nao atua; toda acao exige janela de experimento autorizada."
)

VALIDITY_EN = (
    "VALIDITY LIMIT: base for an INDOOR conducted bench. Thresholds are NOMINAL "
    "and UNCALIBRATED until measurement exists. Unlike the field base, every "
    "condition here is INDUCIBLE and therefore labellable: the operator commands "
    "the condition and knows the label by construction. The system RECOMMENDS, it "
    "does not act; every action requires an authorised experiment window."
)


def _cond(variable: str, operator: str, value: object) -> Condition:
    return Condition(variable, Operator(operator), value)


def build_bench_knowledge_base() -> KnowledgeBase:
    """Assemble the bench variables and rules."""
    kb = KnowledgeBase(
        name_pt="Diagnostico em bancada interna de percurso conduzido",
        name_en="Indoor conducted-bench diagnosis",
        goal_variables=("diagnosis", "recommended_action", "authorization_required"),
        thresholds=dict(BENCH_THRESHOLDS),
        validity_note_pt=VALIDITY_PT,
        validity_note_en=VALIDITY_EN,
    )
    add = kb.add_variable

    # ---- observable evidence -------------------------------------------
    add(Variable(
        "rssi_dbm", VariableKind.NUMERIC,
        "potencia do sinal recebido", "received signal strength",
        bounds=(-120.0, -30.0), unit="dBm",
        prompt_pt="Qual a potencia recebida, em dBm [-120, -30]?",
        prompt_en="What is the received signal strength, in dBm [-120, -30]?",
    ))
    add(Variable(
        "snr_db", VariableKind.NUMERIC,
        "relacao sinal-ruido", "signal-to-noise ratio",
        bounds=(-5.0, 40.0), unit="dB",
        prompt_pt="Qual a relacao sinal-ruido, em dB [-5, 40]?",
        prompt_en="What is the signal-to-noise ratio, in dB [-5, 40]?",
    ))
    # The variable that replaces `weather`: commanded, not observed.
    add(Variable(
        "attenuation_db", VariableKind.NUMERIC,
        "atenuacao comandada no percurso", "commanded path attenuation",
        bounds=(0.0, 80.0), unit="dB",
        prompt_pt="Qual a atenuacao comandada no percurso, em dB [0, 80]?",
        prompt_en="What attenuation is commanded on the path, in dB [0, 80]?",
    ))
    # Containment is a SAFETY measurement, not a performance one. The lab's own
    # concepts note is explicit that a conducted path is not zero power, that
    # residual leakage always exists, and that containment must be measured or
    # technically justified - never presumed from the presence of a cable.
    add(Variable(
        "residual_leakage_dbm", VariableKind.NUMERIC,
        "vazamento residual medido", "measured residual leakage",
        bounds=(-140.0, 0.0), unit="dBm",
        prompt_pt="Qual o vazamento residual medido na fronteira de contencao, em dBm [-140, 0]?",
        prompt_en="What residual leakage is measured at the containment boundary, in dBm [-140, 0]?",
    ))
    add(Variable(
        "packet_loss_pct", VariableKind.NUMERIC,
        "perda de pacotes", "packet loss",
        bounds=(0.0, 100.0), unit="%",
        prompt_pt="Qual a perda de pacotes, em % [0, 100]?",
        prompt_en="What packet loss is observed, in % [0, 100]?",
    ))
    add(Variable(
        "rtt_ms", VariableKind.NUMERIC,
        "tempo de ida e volta", "round-trip time",
        bounds=(0.0, 5000.0), unit="ms",
        prompt_pt="Qual o tempo de ida e volta, em ms [0, 5000]?",
        prompt_en="What is the round-trip time, in ms [0, 5000]?",
    ))
    add(Variable(
        "traffic_load_pct", VariableKind.NUMERIC,
        "utilizacao do enlace", "link utilisation",
        bounds=(0.0, 100.0), unit="%",
        prompt_pt="Qual a utilizacao sustentada do enlace, em % [0, 100]?",
        prompt_en="What is the sustained link utilisation, in % [0, 100]?",
    ))
    add(Variable(
        "link_state", VariableKind.CATEGORICAL,
        "estado do enlace", "link state",
        labels=("up", "down", "flapping"),
        prompt_pt="Qual o estado do enlace [up, down, flapping]?",
        prompt_en="What is the link state [up, down, flapping]?",
    ))
    add(Variable(
        "node_power", VariableKind.CATEGORICAL,
        "alimentacao do no", "node power",
        labels=("ok", "on-battery", "failed"),
        prompt_pt="Qual a alimentacao do no [ok, on-battery, failed]?",
        prompt_en="What is the node's power state [ok, on-battery, failed]?",
    ))
    add(Variable(
        "spectrum_scan", VariableKind.CATEGORICAL,
        "varredura de espectro", "spectrum scan",
        labels=("clean", "occupied"),
        prompt_pt="O que mostra a varredura no canal [clean, occupied]?",
        prompt_en="What does the channel scan show [clean, occupied]?",
    ))
    add(Variable(
        "neighbours_affected", VariableKind.CATEGORICAL,
        "nos vizinhos afetados", "affected neighbours",
        labels=("none", "one", "many"),
        prompt_pt="Quantos nos vizinhos estao afetados [none, one, many]?",
        prompt_en="How many neighbouring nodes are affected [none, one, many]?",
    ))
    # 'antenna' is replaced by 'cabling': a conducted bench has no antenna to
    # disturb, but it does have connectors and cables.
    add(Variable(
        "recent_change", VariableKind.CATEGORICAL,
        "mudanca recente", "recent change",
        labels=("none", "config", "firmware", "cabling"),
        prompt_pt="Houve mudanca recente [none, config, firmware, cabling]?",
        prompt_en="Was there a recent change [none, config, firmware, cabling]?",
    ))
    add(Variable(
        "vlan_trunk_ok", VariableKind.BOOLEAN,
        "tronco de VLAN correto", "VLAN trunk correct",
        labels=("yes", "no"),
        prompt_pt="A lista de VLANs no tronco esta correta [yes, no]?",
        prompt_en="Is the trunk's VLAN allow-list correct [yes, no]?",
    ))
    add(Variable(
        "upstream_relay_reachable", VariableKind.BOOLEAN,
        "repetidor a montante alcancavel", "upstream relay reachable",
        labels=("yes", "no"),
        prompt_pt="O repetidor a montante responde [yes, no]?",
        prompt_en="Does the upstream relay respond [yes, no]?",
    ))

    # ---- intermediate ---------------------------------------------------
    add(Variable(
        "signal_quality", VariableKind.CATEGORICAL,
        "qualidade do sinal", "signal quality",
        labels=("good", "marginal", "poor"), askable=False,
    ))
    add(Variable(
        "link_symptom", VariableKind.CATEGORICAL,
        "sintoma do enlace", "link symptom",
        labels=("none", "degraded", "unstable", "outage"), askable=False,
    ))

    # ---- goals ----------------------------------------------------------
    add(Variable(
        "diagnosis", VariableKind.CATEGORICAL, "diagnostico", "diagnosis",
        labels=tuple(INDUCIBLE_BY), askable=False,
    ))
    add(Variable(
        "recommended_action", VariableKind.CATEGORICAL,
        "acao recomendada", "recommended action",
        labels=(
            "change_channel",
            "restore_path_budget",
            "inspect_connectors",
            "restore_bench_power",
            "restore_upstream_relay",
            "fix_vlan_allowlist",
            "reroute_traffic",
            "halt_transmission",
            "no_action",
        ),
        askable=False,
    ))
    add(Variable(
        "authorization_required", VariableKind.BOOLEAN,
        "exige janela autorizada", "authorised window required",
        labels=("yes", "no"), askable=False,
    ))

    t = BENCH_THRESHOLDS
    r = kb.add_rule

    # ---- layer 1: signal quality ----------------------------------------
    r(Rule("B01",
        (_cond("rssi_dbm", "<", t["rssi_poor_dbm"]), _cond("snr_db", "<", t["snr_poor_db"])),
        Conclusion("signal_quality", "poor"), 0.90,
        "Potencia e relacao sinal-ruido abaixo do limiar.",
        "Signal strength and SNR both below threshold."))
    r(Rule("B02",
        (_cond("rssi_dbm", ">=", t["rssi_poor_dbm"]), _cond("rssi_dbm", "<", t["rssi_marginal_dbm"])),
        Conclusion("signal_quality", "marginal"), 0.70,
        "Potencia recebida na faixa de margem estreita.",
        "Received power in the thin-margin band."))
    r(Rule("B03",
        (_cond("snr_db", ">=", t["snr_poor_db"]), _cond("snr_db", "<", t["snr_marginal_db"])),
        Conclusion("signal_quality", "marginal"), 0.60,
        "Relacao sinal-ruido insuficiente para taxa plena.",
        "SNR insufficient for full rate."))
    r(Rule("B04",
        (_cond("rssi_dbm", ">=", t["rssi_marginal_dbm"]), _cond("snr_db", ">=", t["snr_marginal_db"])),
        Conclusion("signal_quality", "good"), 0.90,
        "Potencia e relacao sinal-ruido dentro do esperado.",
        "Signal strength and SNR within expectation."))

    # ---- layer 2: symptom -----------------------------------------------
    r(Rule("B05", (_cond("link_state", "=", "down"),),
        Conclusion("link_symptom", "outage"), 1.00,
        "Enlace fora do ar e indisponibilidade por definicao.",
        "A link that is down is an outage by definition."))
    r(Rule("B06", (_cond("link_state", "=", "flapping"),),
        Conclusion("link_symptom", "unstable"), 0.90,
        "Oscilacao de estado indica instabilidade.",
        "State oscillation indicates instability."))
    r(Rule("B07",
        (_cond("link_state", "=", "up"), _cond("packet_loss_pct", ">", t["loss_high_pct"])),
        Conclusion("link_symptom", "degraded"), 0.80,
        "Enlace ativo com perda sustentada.",
        "Link up with sustained loss."))
    r(Rule("B08",
        (_cond("link_state", "=", "up"), _cond("rtt_ms", ">", t["rtt_high_ms"])),
        Conclusion("link_symptom", "degraded"), 0.70,
        "Latencia acima do limiar.",
        "Latency above threshold."))
    r(Rule("B09",
        (_cond("link_state", "=", "up"),
         _cond("packet_loss_pct", "<=", t["loss_low_pct"]),
         _cond("rtt_ms", "<=", t["rtt_high_ms"])),
        Conclusion("link_symptom", "none"), 0.90,
        "Enlace ativo, perda baixa e latencia esperada.",
        "Link up, low loss, latency as expected."))

    # ---- layer 3: diagnosis ---------------------------------------------
    r(Rule("B10",
        (_cond("signal_quality", "=", "poor"), _cond("spectrum_scan", "=", "occupied")),
        Conclusion("diagnosis", "rf_interference"), 0.85,
        "Sinal degradado com canal ocupado: emissao interferente injetada.",
        "Degraded signal with an occupied channel: an injected interferer."))
    r(Rule("B11",
        (_cond("spectrum_scan", "=", "occupied"), _cond("neighbours_affected", "=", "many")),
        Conclusion("diagnosis", "rf_interference"), 0.70,
        "Varios nos afetados ao mesmo tempo: causa no meio compartilhado.",
        "Several nodes affected at once: a cause in the shared medium."))

    # The two rules that replace rain fade. Note they key on a COMMANDED value.
    r(Rule("B12",
        (_cond("attenuation_db", ">", t["attenuation_high_db"]),
         _cond("signal_quality", "=", "poor")),
        Conclusion("diagnosis", "excess_attenuation"), 0.90,
        "Atenuacao comandada alta explica o sinal ruim: a perda e do percurso, nao do radio.",
        "High commanded attenuation explains the poor signal: the loss is the path, not the radio."))
    r(Rule("B13",
        (_cond("attenuation_db", ">", t["attenuation_high_db"]),
         _cond("link_symptom", "=", "degraded")),
        Conclusion("diagnosis", "excess_attenuation"), 0.75,
        "Degradacao sob atenuacao comandada alta.",
        "Degradation under high commanded attenuation."))

    r(Rule("B14",
        (_cond("signal_quality", "=", "poor"),
         _cond("spectrum_scan", "=", "clean"),
         _cond("attenuation_db", "<=", t["attenuation_high_db"])),
        Conclusion("diagnosis", "cabling_fault"), 0.65,
        "Sinal ruim sem interferencia e sem atenuacao comandada: suspeitar do percurso fisico.",
        "Poor signal with no interference and no commanded attenuation: suspect the physical path."))
    r(Rule("B15",
        (_cond("recent_change", "=", "cabling"), _cond("signal_quality", "!=", "good")),
        Conclusion("diagnosis", "cabling_fault"), 0.80,
        "Degradacao logo apos intervencao em cabeamento.",
        "Degradation right after cabling work."))

    r(Rule("B16", (_cond("node_power", "=", "failed"),),
        Conclusion("diagnosis", "node_power_failure"), 0.95,
        "Falha de alimentacao explica a perda do no.",
        "A power failure explains the loss of the node."))
    r(Rule("B17",
        (_cond("node_power", "=", "on-battery"), _cond("link_symptom", "=", "unstable")),
        Conclusion("diagnosis", "node_power_failure"), 0.50,
        "No em bateria com enlace oscilante.",
        "Node on battery with an oscillating link."))
    r(Rule("B18",
        (_cond("upstream_relay_reachable", "=", "no"), _cond("link_state", "=", "down")),
        Conclusion("diagnosis", "upstream_relay_failure"), 0.85,
        "A queda do repetidor derruba tudo a jusante.",
        "Losing the relay drops everything downstream."))
    r(Rule("B19",
        (_cond("upstream_relay_reachable", "=", "no"), _cond("neighbours_affected", "=", "many")),
        Conclusion("diagnosis", "upstream_relay_failure"), 0.70,
        "Perda simultanea a jusante do mesmo repetidor.",
        "Simultaneous loss downstream of the same relay."))
    r(Rule("B20",
        (_cond("vlan_trunk_ok", "=", "no"), _cond("recent_change", "=", "config")),
        Conclusion("diagnosis", "vlan_misconfiguration"), 0.90,
        "Lista de VLANs incorreta apos mudanca de configuracao.",
        "Incorrect VLAN list after a configuration change."))
    r(Rule("B21",
        (_cond("vlan_trunk_ok", "=", "no"), _cond("link_state", "=", "up")),
        Conclusion("diagnosis", "vlan_misconfiguration"), 0.60,
        "Radio em pe e payload que nao passa: camada 2, nao RF.",
        "Radio up while payload does not pass: layer 2, not RF."))
    r(Rule("B22",
        (_cond("traffic_load_pct", ">", t["load_high_pct"]),
         _cond("rtt_ms", ">", t["rtt_high_ms"]),
         _cond("signal_quality", "!=", "poor")),
        Conclusion("diagnosis", "congestion"), 0.80,
        "Latencia alta com RF saudavel: enfileiramento.",
        "High latency with healthy RF: queueing."))
    r(Rule("B23",
        (_cond("traffic_load_pct", ">", t["load_high_pct"]),
         _cond("packet_loss_pct", ">", t["loss_low_pct"]),
         _cond("spectrum_scan", "=", "clean")),
        Conclusion("diagnosis", "congestion"), 0.60,
        "Perda por descarte de fila, sem interferencia.",
        "Loss from queue drops, with no interference."))
    r(Rule("B24",
        (_cond("link_symptom", "=", "none"), _cond("signal_quality", "=", "good")),
        Conclusion("diagnosis", "healthy"), 0.90,
        "Sem sintoma e com sinal bom: linha de base.",
        "No symptom and good signal: the baseline."))

    # ---- counter-evidence -----------------------------------------------
    # Replaces the clear-weather rule, and is stronger: the attenuator setting is
    # commanded, so this counter-evidence is a fact rather than an observation.
    r(Rule("B25", (_cond("attenuation_db", "<=", t["attenuation_nominal_db"]),),
        Conclusion("diagnosis", "excess_attenuation"), -0.85,
        "Atenuador no piso: evidencia CONTRA perda de percurso.",
        "Attenuator at its floor: evidence AGAINST path loss."))
    r(Rule("B26", (_cond("node_power", "=", "ok"),),
        Conclusion("diagnosis", "node_power_failure"), -0.90,
        "Alimentacao normal e evidencia CONTRA falha de energia.",
        "Normal power is evidence AGAINST a power failure."))
    r(Rule("B27", (_cond("spectrum_scan", "=", "clean"),),
        Conclusion("diagnosis", "rf_interference"), -0.70,
        "Espectro limpo e evidencia CONTRA interferencia.",
        "A clean spectrum is evidence AGAINST interference."))

    # ---- layer 4: recommended action -------------------------------------
    for rule_id, diagnosis, action, cf, pt, en in (
        ("B28", "rf_interference", "change_channel", 0.90,
         "Mudar de canal afasta a emissao interferente.",
         "Changing channel moves away from the interferer."),
        ("B29", "excess_attenuation", "restore_path_budget", 0.85,
         "Rever a atenuacao comandada e o orcamento de enlace.",
         "Review the commanded attenuation and the link budget."),
        ("B30", "cabling_fault", "inspect_connectors", 0.80,
         "Inspecionar conectores e cabos do percurso conduzido.",
         "Inspect the conducted path's connectors and cables."),
        ("B31", "node_power_failure", "restore_bench_power", 0.95,
         "Restabelecer alimentacao precede qualquer acao de radio.",
         "Restoring power precedes any radio action."),
        ("B32", "upstream_relay_failure", "restore_upstream_relay", 0.90,
         "Recuperar o repetidor restaura a cadeia a jusante.",
         "Recovering the relay restores the downstream chain."),
        ("B33", "vlan_misconfiguration", "fix_vlan_allowlist", 0.90,
         "Correcao de configuracao no comutador.",
         "A configuration fix on the switch."),
        ("B34", "congestion", "reroute_traffic", 0.80,
         "Desviar trafego alivia a fila enquanto a capacidade nao muda.",
         "Rerouting relieves the queue while capacity is unchanged."),
        ("B35", "healthy", "no_action", 0.90,
         "Nenhuma acao e a acao correta na linha de base.",
         "No action is the right action at the baseline."),
    ):
        r(Rule(rule_id, (_cond("diagnosis", "=", diagnosis),),
               Conclusion("recommended_action", action), cf, pt, en))

    # ---- layer 5: authorisation gate -------------------------------------
    for rule_id, action in (
        ("B36", "change_channel"),
        ("B37", "restore_path_budget"),
        ("B38", "inspect_connectors"),
        ("B39", "restore_bench_power"),
        ("B40", "restore_upstream_relay"),
        ("B41", "fix_vlan_allowlist"),
        ("B42", "reroute_traffic"),
    ):
        r(Rule(rule_id, (_cond("recommended_action", "=", action),),
            Conclusion("authorization_required", "yes"), 1.00,
            "Toda alteracao no cenario exige janela de experimento autorizada.",
            "Any change to the scenario requires an authorised experiment window."))
    # ---- containment: a STOP condition, not a restoration one -------------
    # The lab's concepts note: a conducted path is not zero power, residual
    # leakage always exists, and if it exceeds the test's acceptance criterion the
    # transmission must be interrupted. That inverts the governance model used
    # everywhere else in this base - see B46.
    r(Rule("B44", (_cond("residual_leakage_dbm", ">", t["leakage_limit_dbm"]),),
        Conclusion("diagnosis", "containment_breach"), 0.98,
        "Vazamento residual acima do criterio de aceitacao do ensaio.",
        "Residual leakage above the test's acceptance criterion."))
    r(Rule("B45", (_cond("residual_leakage_dbm", "<=", t["leakage_limit_dbm"]),),
        Conclusion("diagnosis", "containment_breach"), -0.95,
        "Vazamento medido dentro do criterio e evidencia CONTRA violacao de contencao.",
        "Measured leakage within the criterion is evidence AGAINST a breach."))
    r(Rule("B46", (_cond("diagnosis", "=", "containment_breach"),),
        Conclusion("recommended_action", "halt_transmission"), 1.00,
        "Interromper a transmissao precede qualquer outra acao.",
        "Interrupting transmission precedes every other action."))
    # The inversion: every other action waits for an authorised window. This one
    # does not, because the safe act is to STOP. Authorisation gates changes to
    # the plant; it must never gate ceasing to transmit.
    r(Rule("B47", (_cond("recommended_action", "=", "halt_transmission"),),
        Conclusion("authorization_required", "no"), 1.00,
        "Parar nao altera a planta: interromper primeiro, reportar depois.",
        "Stopping changes nothing on the plant: halt first, report after."))

    r(Rule("B43", (_cond("recommended_action", "=", "no_action"),),
        Conclusion("authorization_required", "no"), 1.00,
        "Nenhuma acao, nenhuma janela.",
        "No action, no window."))

    return kb


#: One case per inducible condition. Each corresponds to a run the bench can
#: actually perform, which is what makes these labelled rather than imagined.
BENCH_CASES: Dict[str, Dict[str, object]] = {
    "rf_interference": {
        "rssi_dbm": -97.0, "snr_db": 6.0, "attenuation_db": 6.0,
        "packet_loss_pct": 12.0, "rtt_ms": 180.0, "traffic_load_pct": 35.0,
        "link_state": "up", "node_power": "ok", "spectrum_scan": "occupied",
        "neighbours_affected": "many", "recent_change": "none",
        "vlan_trunk_ok": "yes", "upstream_relay_reachable": "yes",
    },
    "excess_attenuation": {
        "rssi_dbm": -99.0, "snr_db": 5.0, "attenuation_db": 45.0,
        "packet_loss_pct": 9.0, "rtt_ms": 200.0, "traffic_load_pct": 30.0,
        "link_state": "up", "node_power": "ok", "spectrum_scan": "clean",
        "neighbours_affected": "one", "recent_change": "none",
        "vlan_trunk_ok": "yes", "upstream_relay_reachable": "yes",
    },
    "cabling_fault": {
        "rssi_dbm": -98.0, "snr_db": 5.0, "attenuation_db": 6.0,
        "packet_loss_pct": 8.0, "rtt_ms": 190.0, "traffic_load_pct": 25.0,
        "link_state": "up", "node_power": "ok", "spectrum_scan": "clean",
        "neighbours_affected": "one", "recent_change": "cabling",
        "vlan_trunk_ok": "yes", "upstream_relay_reachable": "yes",
    },
    "node_power_failure": {
        "rssi_dbm": -110.0, "snr_db": 0.0, "attenuation_db": 6.0,
        "packet_loss_pct": 100.0, "rtt_ms": 5000.0, "traffic_load_pct": 0.0,
        "link_state": "down", "node_power": "failed", "spectrum_scan": "clean",
        "neighbours_affected": "none", "recent_change": "none",
        "vlan_trunk_ok": "yes", "upstream_relay_reachable": "yes",
    },
    "upstream_relay_failure": {
        "rssi_dbm": -105.0, "snr_db": 3.0, "attenuation_db": 6.0,
        "packet_loss_pct": 100.0, "rtt_ms": 4000.0, "traffic_load_pct": 0.0,
        "link_state": "down", "node_power": "ok", "spectrum_scan": "clean",
        "neighbours_affected": "many", "recent_change": "none",
        "vlan_trunk_ok": "yes", "upstream_relay_reachable": "no",
    },
    "vlan_misconfiguration": {
        "rssi_dbm": -78.0, "snr_db": 22.0, "attenuation_db": 6.0,
        "packet_loss_pct": 0.0, "rtt_ms": 40.0, "traffic_load_pct": 10.0,
        "link_state": "up", "node_power": "ok", "spectrum_scan": "clean",
        "neighbours_affected": "none", "recent_change": "config",
        "vlan_trunk_ok": "no", "upstream_relay_reachable": "yes",
    },
    "congestion": {
        "rssi_dbm": -80.0, "snr_db": 19.0, "attenuation_db": 6.0,
        "packet_loss_pct": 3.0, "rtt_ms": 420.0, "traffic_load_pct": 93.0,
        "link_state": "up", "node_power": "ok", "spectrum_scan": "clean",
        "neighbours_affected": "none", "recent_change": "none",
        "vlan_trunk_ok": "yes", "upstream_relay_reachable": "yes",
    },
    "containment_breach": {
        "rssi_dbm": -80.0, "snr_db": 20.0, "attenuation_db": 6.0,
        "residual_leakage_dbm": -42.0,
        "packet_loss_pct": 0.0, "rtt_ms": 38.0, "traffic_load_pct": 20.0,
        "link_state": "up", "node_power": "ok", "spectrum_scan": "clean",
        "neighbours_affected": "none", "recent_change": "none",
        "vlan_trunk_ok": "yes", "upstream_relay_reachable": "yes",
    },
    "healthy": {
        "rssi_dbm": -74.0, "snr_db": 25.0, "attenuation_db": 6.0,
        "residual_leakage_dbm": -88.0,
        "packet_loss_pct": 0.0, "rtt_ms": 35.0, "traffic_load_pct": 22.0,
        "link_state": "up", "node_power": "ok", "spectrum_scan": "clean",
        "neighbours_affected": "none", "recent_change": "none",
        "vlan_trunk_ok": "yes", "upstream_relay_reachable": "yes",
    },
}
