"""
Knowledge base: diagnosis of a degraded communication link in the backhaul.

PT-BR: Base de conhecimento dirigida por CONHECIMENTO, nao por dados. Nao existe
       conjunto rotulado de falhas para este dominio: sem instrumento de degradacao
       controlada e sem linha de base de observabilidade autenticada, nao ha como
       rotular 'degradado' ou 'em falha' a partir de medicao. As regras codificam
       conhecimento de engenharia; os limiares sao NOMINAIS e NAO CALIBRADOS.

EN:    A KNOWLEDGE-driven knowledge base, not a data-driven one. No labelled fault
       dataset exists for this domain: without a controlled degradation instrument
       and an authenticated observability baseline there is no way to label
       'degraded' or 'failed' from measurement. The rules encode engineering
       knowledge; the thresholds are NOMINAL and UNCALIBRATED.

Calibration / Calibracao
------------------------
Every numeric threshold used by the rules lives in :data:`THRESHOLDS`. When a
measured baseline becomes available, those values are re-fitted; the rules that use
them do not change. This separation is the whole point of keeping the block
declared in one place.
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

#: NOMINAL, UNCALIBRATED thresholds. Sources: sub-GHz industrial radio datasheet
#: ranges and common utility-telecom practice. They are starting points for
#: calibration, not measured values for any specific installation.
THRESHOLDS: Dict[str, Number] = {
    "rssi_poor_dbm": -95.0,      # below this, the link budget is effectively spent
    "rssi_marginal_dbm": -85.0,  # below this, fade margin is thin
    "snr_poor_db": 8.0,          # below this, robust modulation is already in use
    "snr_marginal_db": 15.0,
    "loss_high_pct": 5.0,        # sustained loss that breaks SCADA polling
    "loss_low_pct": 1.0,
    "rtt_high_ms": 250.0,        # above this, protection-adjacent traffic suffers
    "load_high_pct": 80.0,       # sustained utilisation where queueing dominates
}

VALIDITY_PT = (
    "LIMITE DE VALIDADE: os limiares desta base sao NOMINAIS e NAO CALIBRADOS. Nao "
    "existe, para este dominio, conjunto de dados rotulado de falhas: sem instrumento "
    "de degradacao controlada e sem linha de base de observabilidade autenticada, nao "
    "ha rotulo de 'degradado' ou 'em falha' derivado de medicao. O sistema RECOMENDA, "
    "nao atua: toda acao sobre a planta exige autorizacao, janela e operador "
    "responsavel."
)

VALIDITY_EN = (
    "VALIDITY LIMIT: the thresholds in this base are NOMINAL and UNCALIBRATED. No "
    "labelled fault dataset exists for this domain: without a controlled degradation "
    "instrument and an authenticated observability baseline, no 'degraded' or "
    "'failed' label can be derived from measurement. The system RECOMMENDS, it does "
    "not act: any change to the plant requires authorisation, a window, and an "
    "accountable operator."
)


def _cond(variable: str, operator: str, value: object) -> Condition:
    return Condition(variable, Operator(operator), value)


def build_knowledge_base() -> KnowledgeBase:
    """Assemble the variables and the 41 production rules."""
    kb = KnowledgeBase(
        name_pt="Diagnostico de enlace de backhaul de comunicacao",
        name_en="Communication backhaul link diagnosis",
        goal_variables=("diagnosis", "recommended_action", "authorization_required"),
        thresholds=dict(THRESHOLDS),
        validity_note_pt=VALIDITY_PT,
        validity_note_en=VALIDITY_EN,
    )
    add = kb.add_variable

    # ---- observable evidence / evidencia observavel ---------------------
    add(Variable(
        "rssi_dbm", VariableKind.NUMERIC,
        "potencia do sinal recebido", "received signal strength",
        bounds=(-120.0, -30.0), unit="dBm",
        prompt_pt="Qual a potencia recebida no enlace, em dBm [-120, -30]?",
        prompt_en="What is the received signal strength on the link, in dBm [-120, -30]?",
    ))
    add(Variable(
        "snr_db", VariableKind.NUMERIC,
        "relacao sinal-ruido", "signal-to-noise ratio",
        bounds=(-5.0, 40.0), unit="dB",
        prompt_pt="Qual a relacao sinal-ruido, em dB [-5, 40]?",
        prompt_en="What is the signal-to-noise ratio, in dB [-5, 40]?",
    ))
    add(Variable(
        "packet_loss_pct", VariableKind.NUMERIC,
        "perda de pacotes", "packet loss",
        bounds=(0.0, 100.0), unit="%",
        prompt_pt="Qual a perda de pacotes observada, em % [0, 100]?",
        prompt_en="What packet loss is observed, in % [0, 100]?",
    ))
    add(Variable(
        "rtt_ms", VariableKind.NUMERIC,
        "tempo de ida e volta", "round-trip time",
        bounds=(0.0, 5000.0), unit="ms",
        prompt_pt="Qual o tempo de ida e volta medido, em ms [0, 5000]?",
        prompt_en="What is the measured round-trip time, in ms [0, 5000]?",
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
        prompt_pt="Qual a situacao de alimentacao do no [ok, on-battery, failed]?",
        prompt_en="What is the node's power situation [ok, on-battery, failed]?",
    ))
    add(Variable(
        "weather", VariableKind.CATEGORICAL,
        "condicao meteorologica", "weather condition",
        labels=("clear", "rain", "storm"),
        prompt_pt="Qual a condicao meteorologica no percurso [clear, rain, storm]?",
        prompt_en="What is the weather along the path [clear, rain, storm]?",
    ))
    add(Variable(
        "spectrum_scan", VariableKind.CATEGORICAL,
        "varredura de espectro", "spectrum scan",
        labels=("clean", "occupied"),
        prompt_pt="O que mostra a varredura de espectro no canal [clean, occupied]?",
        prompt_en="What does the spectrum scan show on the channel [clean, occupied]?",
    ))
    add(Variable(
        "neighbours_affected", VariableKind.CATEGORICAL,
        "vizinhos afetados", "affected neighbours",
        labels=("none", "one", "many"),
        prompt_pt="Quantos enlaces vizinhos estao afetados [none, one, many]?",
        prompt_en="How many neighbouring links are affected [none, one, many]?",
    ))
    add(Variable(
        "recent_change", VariableKind.CATEGORICAL,
        "mudanca recente", "recent change",
        labels=("none", "config", "firmware", "antenna"),
        prompt_pt="Houve mudanca recente no no [none, config, firmware, antenna]?",
        prompt_en="Was there a recent change on the node [none, config, firmware, antenna]?",
    ))
    add(Variable(
        "vlan_trunk_ok", VariableKind.BOOLEAN,
        "tronco de VLAN correto", "VLAN trunk correct",
        labels=("yes", "no"),
        prompt_pt="A lista de VLANs permitidas no tronco esta correta [yes, no]?",
        prompt_en="Is the allowed-VLAN list on the trunk correct [yes, no]?",
    ))
    add(Variable(
        "upstream_relay_reachable", VariableKind.BOOLEAN,
        "repetidor a montante alcancavel", "upstream relay reachable",
        labels=("yes", "no"),
        prompt_pt="O repetidor a montante responde [yes, no]?",
        prompt_en="Does the upstream relay respond [yes, no]?",
    ))

    # ---- intermediate conclusions / conclusoes intermediarias -----------
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

    # ---- goals / objetivos ----------------------------------------------
    add(Variable(
        "diagnosis", VariableKind.CATEGORICAL,
        "diagnostico", "diagnosis",
        labels=(
            "rf_interference",
            "path_obstruction",
            "rain_fade",
            "node_power_failure",
            "upstream_relay_failure",
            "vlan_misconfiguration",
            "congestion",
            "healthy",
        ),
        askable=False,
    ))
    add(Variable(
        "recommended_action", VariableKind.CATEGORICAL,
        "acao recomendada", "recommended action",
        labels=(
            "change_channel",
            "realign_antenna",
            "wait_and_monitor",
            "dispatch_power_team",
            "restore_upstream_relay",
            "fix_vlan_allowlist",
            "reroute_traffic",
            "no_action",
        ),
        askable=False,
    ))
    add(Variable(
        "authorization_required", VariableKind.BOOLEAN,
        "exige autorizacao", "authorisation required",
        labels=("yes", "no"), askable=False,
    ))

    t = THRESHOLDS
    r = kb.add_rule

    # ---- layer 1: signal quality ----------------------------------------
    r(Rule("R01",
        (_cond("rssi_dbm", "<", t["rssi_poor_dbm"]), _cond("snr_db", "<", t["snr_poor_db"])),
        Conclusion("signal_quality", "poor"), 0.90,
        "Potencia e relacao sinal-ruido ambas abaixo do limiar: o orcamento de enlace esta esgotado.",
        "Both signal strength and SNR below threshold: the link budget is spent."))
    r(Rule("R02",
        (_cond("rssi_dbm", ">=", t["rssi_poor_dbm"]), _cond("rssi_dbm", "<", t["rssi_marginal_dbm"])),
        Conclusion("signal_quality", "marginal"), 0.70,
        "Potencia recebida na faixa de margem estreita.",
        "Received power in the thin-margin band."))
    r(Rule("R03",
        (_cond("snr_db", ">=", t["snr_poor_db"]), _cond("snr_db", "<", t["snr_marginal_db"])),
        Conclusion("signal_quality", "marginal"), 0.60,
        "Relacao sinal-ruido suficiente para modulacao robusta, insuficiente para taxa plena.",
        "SNR sufficient for robust modulation, insufficient for full rate."))
    r(Rule("R04",
        (_cond("rssi_dbm", ">=", t["rssi_marginal_dbm"]), _cond("snr_db", ">=", t["snr_marginal_db"])),
        Conclusion("signal_quality", "good"), 0.90,
        "Potencia e relacao sinal-ruido dentro da faixa esperada.",
        "Signal strength and SNR both within the expected band."))

    # ---- layer 2: symptom -----------------------------------------------
    r(Rule("R05", (_cond("link_state", "=", "down"),),
        Conclusion("link_symptom", "outage"), 1.00,
        "Enlace fora do ar e indisponibilidade por definicao.",
        "A link that is down is an outage by definition."))
    r(Rule("R06", (_cond("link_state", "=", "flapping"),),
        Conclusion("link_symptom", "unstable"), 0.90,
        "Oscilacao de estado indica instabilidade, nao indisponibilidade permanente.",
        "State oscillation indicates instability, not permanent unavailability."))
    r(Rule("R07",
        (_cond("link_state", "=", "up"), _cond("packet_loss_pct", ">", t["loss_high_pct"])),
        Conclusion("link_symptom", "degraded"), 0.80,
        "Enlace ativo com perda sustentada acima do limiar de sondagem SCADA.",
        "Link up with sustained loss above the SCADA polling threshold."))
    r(Rule("R08",
        (_cond("link_state", "=", "up"), _cond("rtt_ms", ">", t["rtt_high_ms"])),
        Conclusion("link_symptom", "degraded"), 0.70,
        "Latencia acima do limiar penaliza trafego sensivel a tempo.",
        "Latency above threshold penalises time-sensitive traffic."))
    r(Rule("R09",
        (_cond("link_state", "=", "up"),
         _cond("packet_loss_pct", "<=", t["loss_low_pct"]),
         _cond("rtt_ms", "<=", t["rtt_high_ms"])),
        Conclusion("link_symptom", "none"), 0.90,
        "Enlace ativo, perda baixa e latencia dentro do esperado.",
        "Link up, low loss, and latency within expectation."))

    # ---- layer 3: diagnosis ---------------------------------------------
    r(Rule("R10",
        (_cond("signal_quality", "=", "poor"), _cond("spectrum_scan", "=", "occupied")),
        Conclusion("diagnosis", "rf_interference"), 0.85,
        "Sinal degradado com canal ocupado por emissao de terceiros: interferencia co-canal.",
        "Degraded signal with the channel occupied by a third-party emission: co-channel interference."))
    r(Rule("R11",
        (_cond("spectrum_scan", "=", "occupied"), _cond("neighbours_affected", "=", "many")),
        Conclusion("diagnosis", "rf_interference"), 0.70,
        "Varios enlaces afetados ao mesmo tempo apontam para causa no meio compartilhado.",
        "Several links affected at once point to a cause in the shared medium."))
    r(Rule("R12",
        (_cond("signal_quality", "=", "poor"),
         _cond("spectrum_scan", "=", "clean"),
         _cond("weather", "=", "clear")),
        Conclusion("diagnosis", "path_obstruction"), 0.75,
        "Sinal ruim sem interferencia e sem chuva: o percurso mudou (obstrucao ou desalinhamento).",
        "Poor signal with no interference and no rain: the path changed (obstruction or misalignment)."))
    r(Rule("R13",
        (_cond("recent_change", "=", "antenna"), _cond("signal_quality", "!=", "good")),
        Conclusion("diagnosis", "path_obstruction"), 0.80,
        "Degradacao logo apos intervencao em antena sugere desalinhamento.",
        "Degradation right after antenna work suggests misalignment."))
    r(Rule("R14",
        (_cond("weather", "=", "storm"),
         _cond("link_symptom", "=", "degraded"),
         _cond("spectrum_scan", "=", "clean")),
        Conclusion("diagnosis", "rain_fade"), 0.70,
        "Degradacao durante tempestade, sem interferencia: atenuacao por chuva.",
        "Degradation during a storm with no interference: rain attenuation."))
    r(Rule("R15",
        (_cond("weather", "=", "rain"), _cond("signal_quality", "=", "marginal")),
        Conclusion("diagnosis", "rain_fade"), 0.45,
        "Chuva com margem estreita: evidencia fraca, nao conclusiva.",
        "Rain with a thin margin: weak evidence, not conclusive."))
    r(Rule("R16", (_cond("node_power", "=", "failed"),),
        Conclusion("diagnosis", "node_power_failure"), 0.95,
        "Falha de alimentacao explica a perda do no independentemente do radio.",
        "A power failure explains the loss of the node regardless of the radio."))
    r(Rule("R17",
        (_cond("node_power", "=", "on-battery"), _cond("link_symptom", "=", "unstable")),
        Conclusion("diagnosis", "node_power_failure"), 0.50,
        "No em bateria com enlace oscilante sugere autonomia se esgotando.",
        "A node on battery with an oscillating link suggests autonomy running out."))
    r(Rule("R18",
        (_cond("upstream_relay_reachable", "=", "no"), _cond("link_state", "=", "down")),
        Conclusion("diagnosis", "upstream_relay_failure"), 0.85,
        "Numa cadeia armazena-e-encaminha, a queda do repetidor derruba tudo a jusante.",
        "In a store-and-forward chain, losing the relay drops everything downstream."))
    r(Rule("R19",
        (_cond("upstream_relay_reachable", "=", "no"), _cond("neighbours_affected", "=", "many")),
        Conclusion("diagnosis", "upstream_relay_failure"), 0.70,
        "Perda simultanea a jusante do mesmo repetidor.",
        "Simultaneous loss downstream of the same relay."))
    r(Rule("R20",
        (_cond("vlan_trunk_ok", "=", "no"), _cond("recent_change", "=", "config")),
        Conclusion("diagnosis", "vlan_misconfiguration"), 0.90,
        "Lista de VLANs incorreta apos mudanca de configuracao.",
        "Incorrect VLAN list after a configuration change."))
    r(Rule("R21",
        (_cond("vlan_trunk_ok", "=", "no"), _cond("link_state", "=", "up")),
        Conclusion("diagnosis", "vlan_misconfiguration"), 0.60,
        "Radio em pe e payload que nao passa apontam para a camada 2, nao para a RF.",
        "A radio that is up while payload does not pass points at layer 2, not at RF."))
    r(Rule("R22",
        (_cond("traffic_load_pct", ">", t["load_high_pct"]),
         _cond("rtt_ms", ">", t["rtt_high_ms"]),
         _cond("signal_quality", "!=", "poor")),
        Conclusion("diagnosis", "congestion"), 0.80,
        "Latencia alta com RF saudavel e utilizacao alta: enfileiramento, nao propagacao.",
        "High latency with healthy RF and high utilisation: queueing, not propagation."))
    r(Rule("R23",
        (_cond("traffic_load_pct", ">", t["load_high_pct"]),
         _cond("packet_loss_pct", ">", t["loss_low_pct"]),
         _cond("spectrum_scan", "=", "clean")),
        Conclusion("diagnosis", "congestion"), 0.60,
        "Perda por descarte de fila em enlace carregado, sem interferencia.",
        "Loss from queue drops on a loaded link, with no interference."))
    r(Rule("R24",
        (_cond("link_symptom", "=", "none"), _cond("signal_quality", "=", "good")),
        Conclusion("diagnosis", "healthy"), 0.90,
        "Sem sintoma e com sinal bom: nada a corrigir.",
        "No symptom and good signal: nothing to correct."))

    # ---- counter-evidence / contra-evidencia (negative CFs) -------------
    r(Rule("R25", (_cond("weather", "=", "clear"),),
        Conclusion("diagnosis", "rain_fade"), -0.80,
        "Tempo limpo e evidencia CONTRA atenuacao por chuva.",
        "Clear weather is evidence AGAINST rain attenuation."))
    r(Rule("R26", (_cond("node_power", "=", "ok"),),
        Conclusion("diagnosis", "node_power_failure"), -0.90,
        "Alimentacao normal e evidencia CONTRA falha de energia.",
        "Normal power is evidence AGAINST a power failure."))
    r(Rule("R27", (_cond("spectrum_scan", "=", "clean"),),
        Conclusion("diagnosis", "rf_interference"), -0.70,
        "Espectro limpo e evidencia CONTRA interferencia.",
        "A clean spectrum is evidence AGAINST interference."))

    # ---- layer 4: recommended action ------------------------------------
    r(Rule("R28", (_cond("diagnosis", "=", "rf_interference"),),
        Conclusion("recommended_action", "change_channel"), 0.90,
        "Mudar de canal afasta a emissao interferente sem intervencao fisica.",
        "Changing channel moves away from the interferer without physical intervention."))
    r(Rule("R29", (_cond("diagnosis", "=", "path_obstruction"),),
        Conclusion("recommended_action", "realign_antenna"), 0.85,
        "Percurso obstruido ou desalinhado exige equipe em campo.",
        "An obstructed or misaligned path requires a field crew."))
    r(Rule("R30", (_cond("diagnosis", "=", "rain_fade"),),
        Conclusion("recommended_action", "wait_and_monitor"), 0.80,
        "Atenuacao por chuva e transitoria: intervir seria tratar o clima.",
        "Rain attenuation is transient: intervening would be treating the weather."))
    r(Rule("R31", (_cond("diagnosis", "=", "node_power_failure"),),
        Conclusion("recommended_action", "dispatch_power_team"), 0.95,
        "Restabelecer alimentacao precede qualquer acao de radio.",
        "Restoring power precedes any radio action."))
    r(Rule("R32", (_cond("diagnosis", "=", "upstream_relay_failure"),),
        Conclusion("recommended_action", "restore_upstream_relay"), 0.90,
        "Recuperar o repetidor restaura toda a cadeia a jusante.",
        "Recovering the relay restores the whole downstream chain."))
    r(Rule("R33", (_cond("diagnosis", "=", "vlan_misconfiguration"),),
        Conclusion("recommended_action", "fix_vlan_allowlist"), 0.90,
        "Correcao de configuracao, sem deslocamento de equipe.",
        "A configuration fix, with no crew dispatch."))
    r(Rule("R34", (_cond("diagnosis", "=", "congestion"),),
        Conclusion("recommended_action", "reroute_traffic"), 0.80,
        "Desviar trafego para rota alternativa alivia a fila enquanto a capacidade nao muda.",
        "Rerouting traffic relieves the queue while capacity is unchanged."))
    r(Rule("R35", (_cond("diagnosis", "=", "healthy"),),
        Conclusion("recommended_action", "no_action"), 0.90,
        "Nenhuma acao e a acao correta quando nao ha falha.",
        "No action is the right action when there is no fault."))

    # ---- layer 5: authorisation gate ------------------------------------
    for rule_id, action in (
        ("R36", "change_channel"),
        ("R37", "realign_antenna"),
        ("R38", "dispatch_power_team"),
        ("R39", "restore_upstream_relay"),
        ("R40", "fix_vlan_allowlist"),
        ("R41", "reroute_traffic"),
    ):
        r(Rule(rule_id, (_cond("recommended_action", "=", action),),
            Conclusion("authorization_required", "yes"), 1.00,
            "Toda mudanca que alcanca a planta exige autorizacao, janela e operador.",
            "Any change reaching the plant requires authorisation, a window, and an operator."))
    r(Rule("R42", (_cond("recommended_action", "=", "wait_and_monitor"),),
        Conclusion("authorization_required", "no"), 0.90,
        "Observar nao altera a planta.",
        "Observing does not change the plant."))
    r(Rule("R43", (_cond("recommended_action", "=", "no_action"),),
        Conclusion("authorization_required", "no"), 1.00,
        "Nenhuma acao, nenhuma autorizacao.",
        "No action, no authorisation."))

    return kb


#: Ready-made cases for the demonstration. Each maps variable -> value.
CASES: Dict[str, Dict[str, object]] = {
    "interference": {
        "rssi_dbm": -97.0, "snr_db": 6.0, "packet_loss_pct": 12.0, "rtt_ms": 180.0,
        "traffic_load_pct": 35.0, "link_state": "up", "node_power": "ok",
        "weather": "clear", "spectrum_scan": "occupied", "neighbours_affected": "many",
        "recent_change": "none", "vlan_trunk_ok": "yes", "upstream_relay_reachable": "yes",
    },
    "obstruction": {
        "rssi_dbm": -98.0, "snr_db": 5.0, "packet_loss_pct": 9.0, "rtt_ms": 200.0,
        "traffic_load_pct": 30.0, "link_state": "up", "node_power": "ok",
        "weather": "clear", "spectrum_scan": "clean", "neighbours_affected": "one",
        "recent_change": "antenna", "vlan_trunk_ok": "yes", "upstream_relay_reachable": "yes",
    },
    "rain_fade": {
        "rssi_dbm": -88.0, "snr_db": 11.0, "packet_loss_pct": 7.0, "rtt_ms": 260.0,
        "traffic_load_pct": 40.0, "link_state": "up", "node_power": "ok",
        "weather": "storm", "spectrum_scan": "clean", "neighbours_affected": "one",
        "recent_change": "none", "vlan_trunk_ok": "yes", "upstream_relay_reachable": "yes",
    },
    "power_failure": {
        "rssi_dbm": -110.0, "snr_db": 0.0, "packet_loss_pct": 100.0, "rtt_ms": 5000.0,
        "traffic_load_pct": 0.0, "link_state": "down", "node_power": "failed",
        "weather": "clear", "spectrum_scan": "clean", "neighbours_affected": "none",
        "recent_change": "none", "vlan_trunk_ok": "yes", "upstream_relay_reachable": "yes",
    },
    "relay_failure": {
        "rssi_dbm": -105.0, "snr_db": 3.0, "packet_loss_pct": 100.0, "rtt_ms": 4000.0,
        "traffic_load_pct": 0.0, "link_state": "down", "node_power": "ok",
        "weather": "clear", "spectrum_scan": "clean", "neighbours_affected": "many",
        "recent_change": "none", "vlan_trunk_ok": "yes", "upstream_relay_reachable": "no",
    },
    "vlan": {
        "rssi_dbm": -78.0, "snr_db": 22.0, "packet_loss_pct": 0.0, "rtt_ms": 40.0,
        "traffic_load_pct": 10.0, "link_state": "up", "node_power": "ok",
        "weather": "clear", "spectrum_scan": "clean", "neighbours_affected": "none",
        "recent_change": "config", "vlan_trunk_ok": "no", "upstream_relay_reachable": "yes",
    },
    "congestion": {
        "rssi_dbm": -80.0, "snr_db": 19.0, "packet_loss_pct": 3.0, "rtt_ms": 420.0,
        "traffic_load_pct": 93.0, "link_state": "up", "node_power": "ok",
        "weather": "clear", "spectrum_scan": "clean", "neighbours_affected": "none",
        "recent_change": "none", "vlan_trunk_ok": "yes", "upstream_relay_reachable": "yes",
    },
    "healthy": {
        "rssi_dbm": -74.0, "snr_db": 25.0, "packet_loss_pct": 0.0, "rtt_ms": 35.0,
        "traffic_load_pct": 22.0, "link_state": "up", "node_power": "ok",
        "weather": "clear", "spectrum_scan": "clean", "neighbours_affected": "none",
        "recent_change": "none", "vlan_trunk_ok": "yes", "upstream_relay_reachable": "yes",
    },
}
