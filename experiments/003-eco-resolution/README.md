[ai4systems](../../README.md) › [experiments](../../docs/experiment-catalogue.md) › **003 Eco-resolution**

# 003 — Eco-resolução / Eco-resolution

> **PT-BR** — Resolução de problemas por interação de agentes reativos (Ferber). Cada agente busca satisfazer o próprio objetivo; quem impede a satisfação é agredido e foge; quem não consegue fugir agride quem bloqueia a fuga. Primeiro no exemplo clássico do mundo dos blocos, com análise exaustiva de convergência; depois nos fluxos de tráfego do backhaul em duplo acesso.
>
> **EN** — Problem solving by the interaction of reactive agents (Ferber). Each agent seeks to satisfy its own goal; whoever prevents satisfaction is attacked and flees; an agent that cannot flee attacks whoever blocks its flight. First on the classic Blocks World example, with an exhaustive convergence analysis; then on the traffic flows of the dual-homed backhaul.

Questão / Question: [RQ5](../../research/research-questions.md) · Código / Code: [`software/aisg/eco/`](../../software/aisg/eco/) · Testes / Tests: [`test_eco_blocks_world.py`](../../software/tests/test_eco_blocks_world.py), [`test_eco_network.py`](../../software/tests/test_eco_network.py)

## Execução / Run

```bash
aisg eco --problem blocks                                   # exemplo da aula / course example
aisg eco --problem blocks --sweep                           # análise de convergência / convergence analysis
aisg eco --problem network --scenario saf-chain-outage --trace
```

## Modelo / Model

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

## Mundo dos blocos / Blocks World

Exemplo da aula / course example: C sobre B sobre A sobre T2 → B sobre T3, C sobre B, A sobre C / C on B on A on T2 → B on T3, C on B, A on C.

```
B  attack    [BuscandoSatisfacao] C blocks B -> T3; C must avoid ~B~T3
C  attacked  [BuscandoFuga] must avoid ~B~T3
C  flee      [Fuga] C -> T1
B  satisfy   [Satisfacao] B -> T3
C  satisfy   [Satisfacao] C -> B
A  satisfy   [Satisfacao] A -> C
```

Quatro movimentos, a sequência mínima para este problema. / Four moves, the shortest sequence for this problem.

### Análise de convergência / Convergence analysis

Cada sequência de ações é reexecutada por um verificador que não compartilha código com o motor. / Every action sequence is replayed by a checker that shares no code with the engine.

| Problema / Problem | Casos / Cases | Convergem / Converge | Movimentos / Moves |
|---|---|---|---|
| 3 blocos, 3 mesas, todo estado inicial × todo objetivo / 3 blocks, 3 tables, every initial state × every goal | 3600 | **3600 (100%)** | média / mean 4,5; máx. / max 17 |
| 4 blocos, 4 mesas, todo estado inicial → torre / 4 blocks, 4 tables, every initial state → tower | 840 | **840 (100%)** | máx. / max 14 |
| 4 blocos, **3 mesas**, todo estado inicial → torre / 4 blocks, **3 tables**, every initial state → tower | 360 | **316 (87,8%)** | 42 ciclos, 2 sem progresso / 42 cycles, 2 no progress |

**Achado / Finding.** Com espaço livre suficiente, a eco-resolução converge em todos os casos testados. Com espaço escasso, os agentes podem se deslocar mutuamente em ciclo: sem planejamento, nada garante a convergência. O motor detecta e declara o ciclo em vez de girar indefinidamente. As soluções também não são ótimas: um caso de 3 blocos precisou de 17 movimentos. / With enough free space, eco-resolution converges in every case tested. With scarce space, agents can displace each other in cycles: without planning, nothing guarantees convergence. The engine detects and declares the cycle instead of spinning forever. Solutions are not optimal either: one 3-block case needed 17 moves.

Duas correções vieram da verificação exaustiva / Two fixes came from the exhaustive check:

1. Um agressor pode ser agredido mais adiante na cadeia (o bloco sobre a vítima precisa sair); só é laço o mesmo agente agredido com as mesmas restrições. / An attacker may be attacked further down the chain (the block on its victim must move); only the same agent attacked with the same constraints is a loop.
2. Quem bloqueia uma fuga evita apenas quem foge e o destino da fuga, como na regra da aula; herdar todas as restrições da cadeia deixava o último agente sem lugar. De 342 falhas para 36 e depois para 0. / Whoever blocks a flight avoids only the fleeing agent and the flight's destination, as in the course rule; inheriting every constraint in the chain left the last agent nowhere to go. From 342 failures to 36, then to 0.

## Aplicação na rede / Network application

Cada site do backhaul em duplo acesso tem dois fluxos-agentes: SCADA (prioridade 2) e telemetria (prioridade 1). Os lugares são os dois meios de acesso; cada meio consome capacidade dos seus gargalos (a célula do eNodeB; cada repetidor armazena-e-encaminha do caminho). / Each site of the dual-homed backhaul has two flow agents: SCADA (priority 2) and telemetry (priority 1). The places are the two access media; each medium uses capacity at its bottlenecks (the eNodeB's cell; every store-and-forward relay on the path).

| Regra / Rule | Na rede / On the network |
|---|---|
| Satisfação / Satisfaction | num meio sem nó parado ou degradado, dentro da capacidade por ordem de prioridade / on a medium with no stopped or degraded node, within capacity in priority order |
| Agressão / Aggression | só contra fluxo de prioridade estritamente menor / only against a flow of strictly lower priority |
| Fuga / Flight | para o outro meio, se couber; senão estacionar (deixar de transmitir) / to the other medium if it fits; otherwise park (stop transmitting) |
| Dependência / Dependency | a telemetria de um site espera o SCADA do mesmo site / a site's telemetry waits for the same site's SCADA flow |

O estado do mundo vem dos **incidentes diagnosticados pelo quadro-negro** ([experimento 002](../002-multi-expert-blackboard/)), não da falha comandada. Capacidades nominais: célula com 6 fluxos (2 congestionada), repetidor com 12 (3 congestionado) — as três células mais carregadas operam cheias antes da falha. / The world state comes from the **incidents diagnosed by the blackboard** ([experiment 002](../002-multi-expert-blackboard/)), not from the commanded fault. Nominal capacities: a cell holds 6 flows (2 when congested), a relay 12 (3 when congested) — the three busiest cells run full before the fault.

| Cenário / Scenario | Comportamento emergente / Emergent behaviour | Resultado / Outcome |
|---|---|---|
| SAF_02 parado / down | ER_06/scada agride ER_07/telemetry na célula cheia de RELAY_5; a telemetria estaciona (seu 900 MHz também passa por SAF_02) / ER_06/scada attacks ER_07/telemetry in RELAY_5's full cell; the telemetry parks (its 900 MHz also crosses SAF_02) | SCADA de ER_06 restaurado; 2 telemetrias sem serviço / ER_06's SCADA restored; 2 telemetry flows unserved |
| SAF_02 + RELAY_5 parados / down | os SCADA dos quatro sites isolados desistem; suas telemetrias esperam / the four isolated sites' SCADA flows give up; their telemetry waits | 8 fluxos insatisfeitos, nenhum outro fluxo se move / 8 flows unsatisfied, no other flow moves |
| Interferência RM_07 + congestionamento RELAY_5 | a telemetria de ER_03 e ER_04 cede a célula ao SCADA e passa a 900 MHz; ER_07 não tem meio limpo / ER_03's and ER_04's telemetry yields the cell to SCADA and moves to 900 MHz; ER_07 has no clean medium | ER_07 sem serviço / ER_07 unserved |

**Diferença em relação ao quadro-negro / Difference from the blackboard.** O árbitro decide por site; aqui cada fluxo decide por si, e a decisão vale para as duas extremidades do fluxo ao mesmo tempo. É isso que falta ao failover local do [experimento 004](../004-multi-rat-simulation/), cujas extremidades decidem separadamente e oscilam. / The arbiter decides per site; here each flow decides for itself, and the decision holds for both ends of the flow at once. That is what the local failover of [experiment 004](../004-multi-rat-simulation/) lacks: its ends decide separately and flap.

## Verificação / Verification

| Propriedade / Property | Como / How |
|---|---|
| Convergência / Convergence | varredura exaustiva, sequências reexecutadas por verificador independente / exhaustive sweep, sequences replayed by an independent checker |
| Restrições de fuga / Flight constraints | nenhum agredido foge para um lugar proibido / no attacked agent flees onto a forbidden place |
| Parada honesta / Honest stopping | todo caso não convergido para com motivo explícito, sem movimento ilegal / every non-converged case stops with an explicit reason, with no illegal move |
| Prioridade / Priority | nenhum fluxo agride outro de prioridade igual ou maior / no flow attacks one of equal or higher priority |
| Coerência / Coherence | todo fluxo satisfeito está em meio utilizável e dentro da capacidade / every satisfied flow is on a usable medium within capacity |
| Dependência / Dependency | telemetria nunca satisfeita sem o SCADA do próprio site / telemetry never satisfied without its own site's SCADA |

## Limites / Limits

- Sem garantia de convergência nem de otimalidade; ambas são medidas, não asseguradas. / No convergence or optimality guarantee; both are measured, not assured.
- A ordem dos agentes influencia o resultado (qual telemetria é deslocada primeiro). / Agent order influences the outcome (which telemetry is displaced first).
- Capacidades em fluxos são nominais; o plano ainda não foi aplicado no simulador. / Capacities in flows are nominal; the plan has not yet been applied in the simulator.
