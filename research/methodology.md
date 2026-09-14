# Metodologia / Methodology

## Compromissos declarados / Declared commitments

**(i) Declaração de incerteza / Declared uncertainty.** Todo limiar numérico usado por regra vive num único bloco e está marcado como **nominal e não calibrado**. Estrutura (as regras) e parâmetro (os limiares) ficam separados: calibrar ajusta valores sem reescrever conhecimento.
Every numeric threshold a rule uses lives in one block, marked **nominal and uncalibrated**. Structure (the rules) and parameter (the thresholds) are kept apart: calibration adjusts values without rewriting knowledge.

**(ii) Verificação por oráculo independente / Verification by an independent oracle.** Propriedades de correção são testadas contra procedimentos que **não compartilham código** com o artefato verificado — por exemplo, a otimalidade do A\* contra Floyd–Warshall.
Correctness properties are tested against procedures that **share no code** with the artefact under test — for example, A\* optimality against Floyd–Warshall.

**(iii) Falseabilidade e resultado negativo / Falsifiability and negative results.** O que não foi possível demonstrar é registrado com o mesmo cuidado do que foi demonstrado.
What could not be demonstrated is recorded as carefully as what could.

## Cenários sintéticos / Synthetic scenarios

Os cenários são simulados por escolha metodológica: uma falha **comandada** é repetível e rotulável; uma falha **observada** em campo é apenas provável. Cada diagnóstico declara como é induzido no simulador. O custo é explícito: os resultados valem para o modelo, não para uma planta.

Scenarios are simulated by methodological choice: a **commanded** fault is repeatable and labellable; a fault **observed** in the field is merely probable. Every diagnosis declares how it is induced in the simulator. The cost is explicit: results hold for the model, not for a plant.

**A verdade comandada serve só para avaliar.** Nenhum componente de decisão lê a falha que o cenário comandou; ela é usada exclusivamente para pontuar o resultado.
**Commanded ground truth is for scoring only.** No decision component reads the fault a scenario commanded; it is used exclusively to score the result.

## Estratégia de validação / Validation strategy

| Propriedade / Property | Verificação / Check | Oráculo / Oracle | Exp. |
|---|---|---|---|
| O A\* devolve o caminho de custo mínimo / A\* returns the least-cost path | todos os pares, dois cenários / every pair, both scenarios | Floyd–Warshall | 001 |
| A heurística é admissível e consistente / The heuristic is admissible and consistent | todos os pares / every pair | `h*` exato / exact `h*` | 001 |
| O plano é executável e atinge o objetivo / A plan is executable and reaches the goal | reexecução passo a passo / step-by-step replay | `Plan.validate` | 001 |
| O domínio não declara sucesso sobre falha viva / The domain never declares success over a live fault | exclusão mútua no ponto fixo / mutex at the fixpoint | grafo de planejamento / planning graph | 001 |
| Dividir a base em especialistas não muda conclusões / Splitting the base into experts changes no conclusion | 8 casos, todos os objetivos, CF idêntico / 8 cases, every goal, identical CF | base única / single base | 002 |
| Uma causa comum explica as interrupções a jusante / One common cause explains the downstream outages | conjuntos escritos à mão / hand-written sets | alcançabilidade por BFS / BFS reachability | 002 |
| O controlador chega à quiescência / The controller reaches quiescence | segunda execução sem agenda / second pass with an empty agenda | ponto fixo / fixpoint | 002 |

## Estrutura de um experimento / Experiment structure

Cada experimento declara sua questão, o método, como executar e como os resultados são verificados, no seu `README.md`. Ver [CONTRIBUTING.md](../CONTRIBUTING.md).
Every experiment states its question, method, how to run it and how its results are checked, in its `README.md`. See [CONTRIBUTING.md](../CONTRIBUTING.md).
