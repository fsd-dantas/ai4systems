[ai4systems](../../README.md) › [experiments](../../docs/experiment-catalogue.md) › **003 Eco-resolution**

# 003 — Eco-resolução / Eco-resolution

> **PT-BR** — Resolução de problemas por interação de agentes reativos (Ferber). Cada agente busca satisfazer o próprio objetivo; quem impede a satisfação é agredido e foge; quem não consegue fugir agride quem bloqueia a fuga. Primeiro no exemplo clássico do mundo dos blocos, com análise exaustiva de convergência; depois nos fluxos de tráfego do backhaul em duplo acesso.
>
> **EN** — Problem solving by the interaction of reactive agents (Ferber). Each agent seeks to satisfy its own goal; whoever prevents satisfaction is attacked and flees; an agent that cannot flee attacks whoever blocks its flight. First on the classic Blocks World example, with an exhaustive convergence analysis; then on the traffic flows of the dual-homed backhaul.

Questão / Question: [RQ5](../../research/research-questions.md) · Código / Code: [`software/aisg/eco/`](../../software/aisg/eco/) · Testes / Tests: [`test_eco_blocks_world.py`](../../software/tests/test_eco_blocks_world.py), [`test_eco_network.py`](../../software/tests/test_eco_network.py) · Estado / Status: **concluído no modelo / complete on the model**

---

## Objetivo / Objective

Aplicar a eco-resolução de Ferber — agentes puramente reativos, sem planejamento — primeiro ao exemplo didático do mundo dos blocos, com uma varredura exaustiva de convergência, e depois aos fluxos de tráfego SCADA e telemetria que disputam meio no backhaul em duplo acesso, para observar o que regras puramente locais conseguem — e não conseguem — resolver sem nenhum plano central.

Apply Ferber's eco-resolution — purely reactive agents, no planning — first to the didactic Blocks World example, with an exhaustive convergence sweep, and then to the SCADA and telemetry traffic flows competing for medium on the dual-homed backhaul, to observe what purely local rules can — and cannot — resolve with no central plan.

## Questão de pesquisa / Research question

> **RQ5 — Resolução descentralizada.** Agentes reativos (eco-resolução), sob regras explícitas de prioridade e dependência, convergem para uma restauração válida? Como se comparam ao planejador central?
>
> **RQ5 — Decentralised resolution.** Do reactive agents (eco-resolution), under explicit priority and dependency rules, converge to a valid restoration? How do they compare with the central planner?

Ver [`research/research-questions.md`](../../research/research-questions.md) para as demais subquestões (RQ1–RQ6).
See [`research/research-questions.md`](../../research/research-questions.md) for the other sub-questions (RQ1–RQ6).

## Hipótese / Hypothesis

Com espaço livre suficiente, agentes reativos sob as regras de satisfação/agressão/fuga/dependência de Ferber convergem para uma resolução válida a partir de qualquer estado inicial testado, sem qualquer planejamento central. Com espaço escasso, nada garante a convergência — agentes podem se deslocar mutuamente em ciclo — e o motor deve detectar e declarar o ciclo em vez de girar indefinidamente. Na rede, o mesmo mecanismo, guiado por prioridade e dependência entre fluxos do mesmo site, produz uma alocação de meio válida, mas não necessariamente ótima, e pode oscilar quando as duas extremidades de um fluxo decidem separadamente — ao contrário do plano central do quadro-negro (experimento 002), que decide as duas pontas de uma vez.

With enough free space, reactive agents under Ferber's satisfaction/aggression/flight/dependency rules converge to a valid resolution from every initial state tested, with no central planning at all. With scarce space, nothing guarantees convergence — agents can displace each other in cycles — and the engine must detect and declare the cycle instead of spinning forever. On the network, the same mechanism, guided by priority and same-site dependency between flows, produces a valid but not necessarily optimal medium allocation, and can flap when a flow's two ends decide separately — unlike the blackboard's central plan (experiment 002), which decides both ends at once.

Falseabilidade: um único caso convergido com espaço livre suficiente que viole uma restrição de fuga ou de prioridade refuta a hipótese central; a ausência de oscilação em todo cenário testado refutaria a hipótese de comparação com o plano central.

Falsifiability: a single converged case with enough free space that violates a flight or priority constraint refutes the central hypothesis; no flapping in any tested scenario would refute the comparison hypothesis against the central plan.

## Tópicos relacionados / Related topics

- [RQ5](../../research/research-questions.md) — questão respondida por este experimento / the question this experiment answers.
- [Experimento 002](../002-multi-expert-blackboard/) — o estado inicial dos agentes de rede vem dos incidentes que o quadro-negro diagnostica, não da falha comandada diretamente / the network agents' initial state comes from the incidents the blackboard diagnoses, not directly from the commanded fault.
- [Experimento 004](../004-multi-rat-simulation/) — seu failover local oscila exatamente pelo problema de coordenação que este experimento trata; ver [Resultados](#resultados--results) / its local failover flaps for exactly the coordination problem this experiment addresses; see [Results](#resultados--results).

## Modelo do sistema / System model

| Comportamento / Behaviour | Regra / Rule |
|---|---|
| Objetivo satisfeito / Goal satisfied | não fazer nada / do nothing |
| Objetivo não satisfeito / Goal not satisfied | tentar satisfazê-lo / try to satisfy it |
| Alguém impede a satisfação / Someone prevents satisfaction | agredi-lo, com restrições: o agredido não pode fugir para o agressor nem para o objetivo dele (`~B~T3`) / attack them, with constraints: the attacked agent may not flee onto the attacker or its goal (`~B~T3`) |
| Agredido / Attacked | fugir / flee |
| Alguém impede a fuga / Someone prevents the flight | agredir o bloqueador, que evita quem foge e o destino da fuga / attack the blocker, which must avoid the fleeing agent and the flight's destination |
| Dependência (CASPER) / Dependency (CASPER) | esperar até que os agentes de quem depende estejam satisfeitos / wait until the agents it depends on are satisfied |

Estados, com os nomes da máquina de estados da aula / States, with the course state machine's names: `waiting` (Esperando), `seeking-satisfaction` (BuscandoSatisfacao), `satisfied` (Satisfacao), `seeking-flight` (BuscandoFuga), `fled` (Fuga).

O motor não planeja: só executa o comportamento local de cada agente. A resolução para quando todos estão satisfeitos, quando uma rodada não muda o mundo, quando um estado se repete (ciclo) ou no limite de movimentos — e o resultado diz qual. / The engine does not plan: it only runs each agent's local behaviour. Resolution stops when every agent is satisfied, when a round changes nothing, when a state repeats (cycle) or at the move limit — and the result says which.

Na rede, cada site do backhaul em duplo acesso tem dois fluxos-agentes: SCADA (prioridade 2) e telemetria (prioridade 1). Os lugares são os dois meios de acesso; cada meio consome capacidade dos seus gargalos (a célula do eNodeB; cada repetidor armazena-e-encaminha do caminho).

On the network, each site of the dual-homed backhaul has two flow agents: SCADA (priority 2) and telemetry (priority 1). The places are the two access media; each medium uses capacity at its bottlenecks (the eNodeB's cell; every store-and-forward relay on the path).

| Regra / Rule | Na rede / On the network |
|---|---|
| Satisfação / Satisfaction | num meio sem nó parado ou degradado, dentro da capacidade por ordem de prioridade / on a medium with no stopped or degraded node, within capacity in priority order |
| Agressão / Aggression | só contra fluxo de prioridade estritamente menor / only against a flow of strictly lower priority |
| Fuga / Flight | para o outro meio, se couber; senão estacionar (deixar de transmitir) / to the other medium if it fits; otherwise park (stop transmitting) |
| Dependência / Dependency | a telemetria de um site espera o SCADA do mesmo site / a site's telemetry waits for the same site's SCADA flow |

**Diferença em relação ao quadro-negro / Difference from the blackboard.** O árbitro decide por site; aqui cada fluxo decide por si, e a decisão vale para as duas extremidades do fluxo ao mesmo tempo. É isso que falta ao failover local do [experimento 004](../004-multi-rat-simulation/), cujas extremidades decidem separadamente e oscilam. / The arbiter decides per site; here each flow decides for itself, and the decision holds for both ends of the flow at once. That is what the local failover of [experiment 004](../004-multi-rat-simulation/) lacks: its ends decide separately and flap.

## Cenário e premissas / Scenario and assumptions

**Mundo dos blocos / Blocks World** — exemplo da aula: C sobre B sobre A sobre T2 → B sobre T3, C sobre B, A sobre C. / course example: C on B on A on T2 → B on T3, C on B, A on C.

**Rede / Network** — a topologia `dual` de 60 nós dos experimentos 002 e 004. O estado do mundo vem dos **incidentes diagnosticados pelo quadro-negro** ([experimento 002](../002-multi-expert-blackboard/)), não da falha comandada diretamente — uma premissa deliberada: os agentes reagem à mesma interpretação da rede que um operador veria, não a um oráculo de falha. / the same 60-node `dual` topology as experiments 002 and 004. The world state comes from the **incidents diagnosed by the blackboard** ([experiment 002](../002-multi-expert-blackboard/)), not from the commanded fault directly — a deliberate assumption: agents react to the same network interpretation an operator would see, not to a fault oracle.

Capacidades nominais: célula com 6 fluxos (2 congestionada), repetidor com 12 (3 congestionado) — as três células mais carregadas operam cheias antes da falha. / Nominal capacities: a cell holds 6 flows (2 when congested), a relay 12 (3 when congested) — the three busiest cells run full before the fault.

Topologia sintética; resultados valem para o modelo — ver [Limitações](#limitações--limitations).
Synthetic topology; results hold for the model — see [Limitations](#limitações--limitations).

## Software e versões / Software and versions

Mesmo núcleo dos experimentos 001 e 002: Python 3.10+, sem dependências de terceiros; `pytest` como extra de desenvolvimento. Pacote `aisg`, versão 0.11.0.

Same core as experiments 001 and 002: Python 3.10+, no third-party dependencies; `pytest` as a development extra. Package `aisg`, version 0.11.0.

## Configuração / Configuration

Prioridades fixas (SCADA 2, telemetria 1), capacidades nominais de célula e repetidor (ver [Cenário e premissas](#cenário-e-premissas--scenario-and-assumptions)) e a regra de dependência CASPER (telemetria espera o SCADA do mesmo site) são parâmetros declarados, não calibrados por medição. Limite de movimentos e critério de ciclo são parâmetros do motor, em [`software/aisg/eco/`](../../software/aisg/eco/).

Fixed priorities (SCADA 2, telemetry 1), nominal cell and relay capacities (see [Scenario and assumptions](#cenário-e-premissas--scenario-and-assumptions)) and the CASPER dependency rule (telemetry waits for the same site's SCADA) are declared parameters, not measurement-calibrated. The move limit and cycle criterion are engine parameters, in [`software/aisg/eco/`](../../software/aisg/eco/).

## Dados de entrada / Input data

| Problema / Problem | Casos / Cases |
|---|---|
| 3 blocos, 3 mesas, todo estado inicial × todo objetivo / 3 blocks, 3 tables, every initial state × every goal | 3600 |
| 4 blocos, 4 mesas, todo estado inicial → torre / 4 blocks, 4 tables, every initial state → tower | 840 |
| 4 blocos, **3 mesas**, todo estado inicial → torre / 4 blocks, **3 tables**, every initial state → tower | 360 |

Rede / Network: os três cenários de falha comandada do experimento 002 (`saf-chain-outage`, `dual-outage`, `independent-faults`), reinterpretados como incidentes pelo quadro-negro. / experiment 002's three commanded-fault scenarios (`saf-chain-outage`, `dual-outage`, `independent-faults`), reinterpreted as incidents by the blackboard.

## Procedimento de execução / Execution procedure

```bash
aisg eco --problem blocks                                   # exemplo da aula / course example
aisg eco --problem blocks --sweep                           # análise de convergência / convergence analysis
aisg eco --problem network --scenario saf-chain-outage --trace
```

## Métricas / Metrics

- Taxa de convergência (%) e movimentos até a resolução (média, máximo) / Convergence rate (%) and moves to resolution (mean, max).
- Ciclos detectados e casos sem progresso / Cycles detected and no-progress cases.
- Violações de restrição de fuga e de prioridade (esperado: zero) / Flight and priority constraint violations (expected: zero).
- Fluxos satisfeitos/insatisfeitos por cenário de rede / Satisfied/unsatisfied flows per network scenario.

## Resultados / Results

| Problema / Problem | Casos / Cases | Convergem / Converge | Movimentos / Moves |
|---|---|---|---|
| 3 blocos, 3 mesas, todo estado inicial × todo objetivo / 3 blocks, 3 tables, every initial state × every goal | 3600 | **3600 (100%)** | média / mean 4,5; máx. / max 17 |
| 4 blocos, 4 mesas, todo estado inicial → torre / 4 blocks, 4 tables, every initial state → tower | 840 | **840 (100%)** | máx. / max 14 |
| 4 blocos, **3 mesas**, todo estado inicial → torre / 4 blocks, **3 tables**, every initial state → tower | 360 | **316 (87,8%)** | 42 ciclos, 2 sem progresso / 42 cycles, 2 no progress |

**Achado / Finding.** Com espaço livre suficiente, a eco-resolução converge em todos os casos testados. Com espaço escasso, os agentes podem se deslocar mutuamente em ciclo: sem planejamento, nada garante a convergência. O motor detecta e declara o ciclo em vez de girar indefinidamente. As soluções também não são ótimas: um caso de 3 blocos precisou de 17 movimentos. / With enough free space, eco-resolution converges in every case tested. With scarce space, agents can displace each other in cycles: without planning, nothing guarantees convergence. The engine detects and declares the cycle instead of spinning forever. Solutions are not optimal either: one 3-block case needed 17 moves.

Duas correções vieram da verificação exaustiva / Two fixes came from the exhaustive check:

1. Um agressor pode ser agredido mais adiante na cadeia (o bloco sobre a vítima precisa sair); só é laço o mesmo agente agredido com as mesmas restrições. / An attacker may be attacked further down the chain (the block on its victim must move); only the same agent attacked with the same constraints is a loop.
2. Quem bloqueia uma fuga evita apenas quem foge e o destino da fuga, como na regra da aula; herdar todas as restrições da cadeia deixava o último agente sem lugar. De 342 falhas para 36 e depois para 0. / Whoever blocks a flight avoids only the fleeing agent and the flight's destination, as in the course rule; inheriting every constraint in the chain left the last agent nowhere to go. From 342 failures to 36, then to 0.

| Cenário / Scenario | Comportamento emergente / Emergent behaviour | Resultado / Outcome |
|---|---|---|
| SAF_02 parado / down | ER_06/scada agride ER_07/telemetry na célula cheia de RELAY_5; a telemetria estaciona (seu 900 MHz também passa por SAF_02) / ER_06/scada attacks ER_07/telemetry in RELAY_5's full cell; the telemetry parks (its 900 MHz also crosses SAF_02) | SCADA de ER_06 restaurado; 2 telemetrias sem serviço / ER_06's SCADA restored; 2 telemetry flows unserved |
| SAF_02 + RELAY_5 parados / down | os SCADA dos quatro sites isolados desistem; suas telemetrias esperam / the four isolated sites' SCADA flows give up; their telemetry waits | 8 fluxos insatisfeitos, nenhum outro fluxo se move / 8 flows unsatisfied, no other flow moves |
| Interferência RM_07 + congestionamento RELAY_5 | a telemetria de ER_03 e ER_04 cede a célula ao SCADA e passa a 900 MHz; ER_07 não tem meio limpo / ER_03's and ER_04's telemetry yields the cell to SCADA and moves to 900 MHz; ER_07 has no clean medium | ER_07 sem serviço / ER_07 unserved |

| Propriedade / Property | Como / How |
|---|---|
| Convergência / Convergence | varredura exaustiva, sequências reexecutadas por verificador independente / exhaustive sweep, sequences replayed by an independent checker |
| Restrições de fuga / Flight constraints | nenhum agredido foge para um lugar proibido / no attacked agent flees onto a forbidden place |
| Parada honesta / Honest stopping | todo caso não convergido para com motivo explícito, sem movimento ilegal / every non-converged case stops with an explicit reason, with no illegal move |
| Prioridade / Priority | nenhum fluxo agride outro de prioridade igual ou maior / no flow attacks one of equal or higher priority |
| Coerência / Coherence | todo fluxo satisfeito está em meio utilizável e dentro da capacidade / every satisfied flow is on a usable medium within capacity |
| Dependência / Dependency | telemetria nunca satisfeita sem o SCADA do próprio site / telemetry never satisfied without its own site's SCADA |

## Limitações / Limitations

- Sem garantia de convergência nem de otimalidade; ambas são medidas, não asseguradas. / No convergence or optimality guarantee; both are measured, not assured.
- A ordem dos agentes influencia o resultado (qual telemetria é deslocada primeiro). / Agent order influences the outcome (which telemetry is displaced first).
- Capacidades em fluxos são nominais; o plano ainda não foi aplicado no simulador. / Capacities in flows are nominal; the plan has not yet been applied in the simulator.

## Estado de reprodutibilidade / Reproducibility status

**Reproduzível.** A varredura do mundo dos blocos é uma enumeração total (3600, 840 e 360 casos, sem amostragem), e cada sequência é reexecutada por um verificador que não compartilha código com o motor. Os cenários de rede herdam o diagnóstico determinístico do experimento 002. `test_eco_blocks_world.py` e `test_eco_network.py` rodam no mesmo workflow de CI dos demais experimentos.

**Reproducible.** The Blocks World sweep is a total enumeration (3600, 840 and 360 cases, no sampling), and every sequence is replayed by a checker sharing no code with the engine. The network scenarios inherit experiment 002's deterministic diagnosis. `test_eco_blocks_world.py` and `test_eco_network.py` run in the same CI workflow as the other experiments.

## Material de manuscrito relacionado / Related manuscript material

`manuscripts/presentations/` — deck, roteiro de fala e notebook: locais, não publicados neste repositório; a wiki é a companhia pública. / deck, speaking script and notebook: local, not published in this repository; the wiki is the public companion.
