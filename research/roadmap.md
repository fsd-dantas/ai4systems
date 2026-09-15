# Roteiro / Roadmap

Pastas são criadas quando recebem conteúdo; este roteiro registra o que está planejado.
Folders are created when they receive content; this roadmap records what is planned.

## Experimentos / Experiments

| # | Experimento / Experiment | Estado / Status |
|---|---|---|
| 001 | Encadeamento simbólico diagnóstico → plano → rota / Symbolic diagnosis → plan → route chain | concluído / complete |
| 002 | Sistema multiespecialista com quadro-negro / Multi-expert blackboard | concluído / complete |
| 003 | Eco-resolução: agentes reativos em conflito por recursos da rede multi-RAT / Eco-resolution: reactive agents in conflict over multi-RAT network resources | concluído no modelo / complete on the model |
| 004 | Simulação multi-RAT em ns-3 (LTE privativo + 900 MHz) com injeção de falhas e verificação / Multi-RAT ns-3 simulation (private LTE + 900 MHz) with fault injection and verification | concluído no modelo / complete on the model |

## Simulador / Simulator (experiment 004)

| Etapa / Step | Descrição / Description |
|---|---|
| Gerador de cenário / Scenario generator | topologia declarada → cenário ns-3 / declared topology → ns-3 scenario |
| LTE privativo / Private LTE | módulo LTE com EPC; banda 31 (450 MHz) acrescentada à tabela EARFCN / LTE module with EPC; band 31 (450 MHz) added to the EARFCN table |
| 900 MHz | abstração declarada de rádio armazena-e-encaminha / declared store-and-forward radio abstraction |
| Tráfego / Traffic | SCADA, comandos, leitura de medição, firmware (padrões de tráfego) / SCADA, commands, meter reads, firmware (traffic patterns) |
| Falhas / Faults | parada de nó, interferência, congestionamento / node stop, interference, congestion |
| Telemetria / Telemetry | exportação para registros de observação / export to observation records |
| Failover | local no roteador de borda e central no centro de operação / local at the edge router and central at the operations centre |
| Verificação / Verification | execução de resolução e animação / resolution run and animation |

## Revisão de literatura / Literature review (`literature/`)

`literature/systematic-review/` guarda uma pasta por artigo revisado; hoje contém apenas `al-ajlan-2015/`. Os demais arquivos abaixo entram quando tiverem conteúdo real.
`literature/systematic-review/` holds one folder per reviewed paper; today it holds only `al-ajlan-2015/`. The files below arrive once they carry real content.

| Arquivo planejado / Planned file | Conteúdo / Contents |
|---|---|
| `review-protocol.md` | protocolo da revisão sistemática (pergunta, método, papéis) / systematic review protocol (question, method, roles) |
| `search-strategy.md` | bases de dados, strings de busca, período / databases, search strings, date range |
| `inclusion-exclusion-criteria.md` | critérios de inclusão e exclusão / inclusion and exclusion criteria |
| `evidence-matrix.csv` | matriz de evidência por artigo revisado / evidence matrix per reviewed paper |
| `annotated-bibliography.md` | bibliografia anotada, um resumo por referência / annotated bibliography, one summary per reference |

## Tópicos de literatura planejados / Planned literature topics

Smart-grid architectures · utility communications · LTE and private LTE · band 31 and 900 MHz · SDN and NFV · network resilience · machine learning for networks · fuzzy logic · ICCP and grid protocols · network simulation.
