<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/fsd-dantas/ai-for-smartgrids/main/docs/assets/banner-dark.jpg">
    <img src="https://raw.githubusercontent.com/fsd-dantas/ai-for-smartgrids/main/docs/assets/banner-light.jpg" alt="Artificial Intelligence for Smartgrid Networks — an isometric grid fabric with energised traces linking a neural network, a solar array, a transmission tower, smart meters, a wind turbine and an AI processor." width="100%">
  </picture>
</p>

# ai-for-smartgrids

[![tests](https://github.com/fsd-dantas/ai-for-smartgrids/actions/workflows/tests.yml/badge.svg)](https://github.com/fsd-dantas/ai-for-smartgrids/actions/workflows/tests.yml)
[![license: MIT](https://img.shields.io/badge/license-MIT-555555)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-3776ab)](pyproject.toml)

> **PT-BR** — Três sistemas simbólicos de Inteligência Artificial aplicados a um mesmo domínio: redes de comunicação sem fio para sistemas elétricos inteligentes. Um sistema especialista de diagnóstico, um gerador automático de planos de ação (STRIPS / GPS) e uma implementação de busca A*.
>
> **EN** — Three symbolic Artificial Intelligence systems applied to a single domain: wireless networks for smart grid systems. A diagnostic expert system, an automated action-plan generator (STRIPS / GPS), and an A* search implementation.

[Português](#português) · [English](#english)

---

## Os três sistemas / The three systems

| # | Sistema / System | Técnica / Technique | Código / Code |
|---|---|---|---|
| 1 | Sistema especialista / Expert system | Regras de produção, encadeamento progressivo e regressivo, fatores de certeza / Production rules, forward and backward chaining, certainty factors | [`expert_system/`](src/aisg/expert_system/) |
| 2 | Geração de planos / Plan generation | STRIPS + GPS (análise meios-fins) + planejamento progressivo por A* / STRIPS + GPS (means-ends analysis) + A* progression planning | [`planning/`](src/aisg/planning/) |
| 3 | Busca A* / A* search | A*, custo uniforme, gulosa, largura, profundidade / A*, uniform cost, greedy, breadth-first, depth-first | [`search/`](src/aisg/search/) |

**Os três se conectam.** O diagnóstico produzido pelo sistema especialista vira o estado inicial do planejador; a ação *desviar tráfego* só é aplicável quando a busca A* confirma que existe rota alternativa; e o planejador progressivo usa **a mesma função A***, sem cópia, que resolve o roteamento.

**The three connect.** The expert system's diagnosis becomes the planner's initial state; the *reroute traffic* action is applicable only when A* search confirms an alternative route exists; and the progression planner uses **the same A\* function**, not a copy, that solves routing.

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/fsd-dantas/ai-for-smartgrids/main/docs/assets/01-integration-dark.svg">
    <img src="https://raw.githubusercontent.com/fsd-dantas/ai-for-smartgrids/main/docs/assets/01-integration-light.svg" alt="The expert system produces a diagnosis that becomes the planner's initial state; the planner asks A* whether an alternative route exists; and the progression planner reuses the same A* function that solves routing." width="100%">
  </picture>
</p>

| Diagrama / Diagram                                                                                         | Conteudo / Contents                                                                |
|------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------|
| [Integration](docs/assets/01-integration-light.svg) · [dark](docs/assets/01-integration-dark.svg)          | How the three systems exchange information                                         |
| [Expert system](docs/assets/02-expert-system-light.svg) · [dark](docs/assets/02-expert-system-dark.svg)    | The five rule layers and both chaining directions                                  |
| [Planning](docs/assets/03-planning-light.svg) · [dark](docs/assets/03-planning-dark.svg)                   | STRIPS operator anatomy and the GPS means-ends recursion                           |
| [A* search](docs/assets/04-astar-light.svg) · [dark](docs/assets/04-astar-dark.svg)                        | f = g + h, the admissibility proof, and the strategy comparison                    |
| [Scenario, 30 nodes](docs/assets/05-simulated-30-light.svg) · [dark](docs/assets/05-simulated-30-dark.svg) | The simulated scenario and the A* route across it                                  |
| [Scenario, 60 nodes](docs/assets/06-dual-60-light.svg) · [dark](docs/assets/06-dual-60-dark.svg)           | 15 dual-homed sites reached by both a pLTE star and a 900 MHz mesh                 |
| [State machine](docs/assets/07-state-machine-light.svg) · [dark](docs/assets/07-state-machine-dark.svg)    | The restoration state space, and why the goal is unreachable while a fault is live |

---

## Instalação / Install

Não há dependências externas no núcleo: apenas a biblioteca padrão do Python 3.10+.
The core has no third-party dependencies: only the Python 3.10+ standard library.

```bash
git clone https://github.com/fsd-dantas/ai-for-smartgrids.git
cd ai-for-smartgrids
python -m pip install -e .

# 1 — sistema especialista / expert system
aisg diagnose --case interference --trace --explain
aisg diagnose --interactive --mode backward      # consulta guiada por objetivo

# 2 — planejamento / planning
aisg plan --diagnosis mac_contention --node AP_C --solver both --trace

# 3 — busca A* / A* search  (o caminho mais barato tem MAIS saltos)
aisg --topology simulated route --from LTE_ENB --to AP_B --compare --expansion

# os três em sequência / all three in sequence
aisg pipeline --case congestion --node SAF_A2
```

Sem instalar / without installing: `PYTHONPATH=src python -m aisg ...`
Em inglês / in English: acrescente `--lang en` / add `--lang en`.

Testes / tests: `python -m pytest` (202 testes / 202 tests).

Apresentação / presentation:
[`docs/presentation/ai-for-smartgrids-apresentacao.pptx`](docs/presentation/ai-for-smartgrids-apresentacao.pptx)
(57 slides, 90 min, com notas do apresentador /
57 slides, 90 min, with speaker notes)
· [`notebooks/apresentacao.ipynb`](notebooks/apresentacao.ipynb) — já executado, renderiza no GitHub sem rodar nada / pre-executed, renders on GitHub with no kernel
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/fsd-dantas/ai-for-smartgrids/blob/main/notebooks/apresentacao.ipynb)

Wiki com a teoria da disciplina / course theory wiki:
[github.com/fsd-dantas/ai-for-smartgrids/wiki](https://github.com/fsd-dantas/ai-for-smartgrids/wiki)


---

## Português

### Questão de pesquisa

> Na ausência de um conjunto de dados rotulado de falhas, é possível construir um
> encadeamento **diagnóstico → plano → rota** que seja simultaneamente *auditável*
> — cada conclusão rastreável até a evidência que a sustenta — e *verificável*,
> isto é, cujas propriedades de correção sejam asseguradas por testes e não
> apenas afirmadas em prosa?

A pergunta é metodológica antes de ser técnica. Ela nasce de uma restrição real
do laboratório, e não de uma preferência estética por métodos simbólicos: a
condição de contorno é a **indisponibilidade de rótulo derivado de medição**, e a
resposta precisa ser honesta quanto ao que essa restrição permite concluir.

Três subquestões organizam os três sistemas:

1. **Representação do conhecimento.** Como codificar julgamento de engenharia sob
   incerteza de modo que a cadeia de inferência permaneça inspecionável e
   contestável? *(regras de produção com fatores de certeza)*
2. **Deliberação.** Como derivar a **ordem** de intervenção — e não apenas o
   conjunto de ações — expressando restrições como precondições formais, e não
   como verificações em tempo de execução? *(STRIPS, GPS, planejamento progressivo)*
3. **Otimalidade demonstrável.** Sob que condições uma busca informada garante o
   caminho de menor custo, e como *demonstrar* que a heurística adotada satisfaz
   essas condições neste domínio? *(A\*, admissibilidade, consistência)*

### Posicionamento metodológico

O trabalho adota três compromissos declarados, herdados da disciplina de medição
que se espera de um artefato de pesquisa:

**(i) Declaração de incerteza.** Todo limiar numérico usado por regra vive num
único bloco (`THRESHOLDS`) e está marcado como **nominal e não calibrado**.
Nenhuma medição de laboratório o sustenta. A separação entre *estrutura* (as
regras) e *parâmetro* (os limiares) é deliberada: a calibração futura ajusta
valores sem reescrever conhecimento.

**(ii) Verificação por oráculo independente.** Propriedades de correção não são
argumentadas — são testadas contra um procedimento que **não compartilha código**
com o artefato verificado. A otimalidade do A\* é conferida contra
Floyd–Warshall; a consistência do domínio de planejamento, contra a análise por
grafo de planejamento (Graphplan). Verificar o A\* com custo uniforme seria
circular, pois `uniform_cost` é literalmente `astar` com `h = 0`.

**(iii) Falseabilidade e resultado negativo.** O projeto registra o que **não**
conseguiu demonstrar com o mesmo cuidado com que registra o que demonstrou. Dois
exemplos vivem na documentação: a não-otimalidade do GPS é uma propriedade real,
porém **este domínio não é capaz de exibi-la** (nenhum literal tem mais de um
operador que o produza, logo a análise meios-fins não tem escolha para errar); e
o ganho do A\* sobre o custo uniforme (9,4% e 25,9% de nós expandidos a menos, em
17 e 30 nós) é uma **medição em dois pontos**, não uma lei de escala.

### O domínio

O domínio é a rede de comunicação que liga ativos distribuídos de um sistema
elétrico ao centro de operação: um núcleo em fibra, setores de rádio em 900 MHz,
uma cadeia de repetidores *armazena-e-encaminha* e uma sobreposição de LTE
privativo. O cenário base tem 17 nós e 24 enlaces; o cenário simulado, usado nas
demonstrações e na apresentação, tem **30 nós e 44 enlaces** distribuídos em três
setores.

**A topologia é SINTÉTICA.** É um modelo didático da *classe* de cenários
estudada em laboratórios de pesquisa em backhaul sem fio. Não contém inventário
real, endereçamento, identificação de equipamento, configuração de RF nem
topologia de campo de qualquer laboratório ou concessionária. Ver
[`docs/domain-model.md`](docs/domain-model.md).

**Simulado, e não de campo — por escolha metodológica.** O cenário é simulado em
ns-3, o que inverte a relação usual entre validade interna e externa a favor
deste trabalho: uma condição de falha *comandada* é repetível e rotulável, ao
passo que uma condição *observada* em campo é apenas provável. Cada diagnóstico
declara, no bloco `INDUCIBLE_BY`, **como é induzido no simulador** — o que torna
o conjunto de casos reprodutível por terceiros. O custo dessa escolha é explícito
e está declarado: os resultados valem para o modelo, não para uma planta.

### Por que o DIAGNÓSTICO não é aprendido

A afirmação central é uma restrição de **validade de medição**, não um juízo
sobre métodos indutivos. Não existe, para este domínio, conjunto de dados
rotulado de falhas. Rotular um enlace como *degradado* ou *em falha* exige um
instrumento de degradação controlada e uma linha de base de observabilidade
autenticada; sem ambos, nenhum rótulo deriva de medição — deriva de suposição. Um
método indutivo treinado apenas sobre o estado normal não infere degradação de
modo confiável, e um classificador ajustado a rótulos supostos herdaria a
suposição sem tornar visível que a herdou. É precisamente essa invisibilidade que
o método simbólico evita: uma regra errada pode ser lida, discutida e refutada
por um engenheiro; um peso errado, não.

> **O escopo desta afirmação é a tarefa de diagnóstico** — não o projeto inteiro. Aprender a *heurística* da busca, por exemplo, é uma tarefa diferente e perfeitamente viável: o alvo de regressão é o custo real restante `h*(n)`, calculável exatamente com uma busca de custo uniforme a partir do objetivo. A supervisão é gratuita e exata, e não depende de rótulo de falha nenhum. O que impede seu uso direto não é a falta de dados, e sim a **admissibilidade**: uma heurística aprendida por regressão pode superestimar, e então o A* perde a otimalidade em silêncio. Ver [`docs/03-astar.md`](docs/03-astar.md).
>
> **The scope of this claim is the diagnosis task**, not the whole project. Learning the search *heuristic* is a different and perfectly viable task: the regression target is the true remaining cost `h*(n)`, computable exactly by uniform-cost search from the goal. Supervision is free and exact, and needs no fault labels. What stands in the way is not data but **admissibility**.

Quando não há dados rotulados, o caminho defensável é codificar **conhecimento
de engenharia** em regras explícitas, auditáveis e contestáveis — que é
exatamente o que um sistema especialista faz. O sistema declara a limitação na
própria saída, e não apenas na documentação.

Duas consequências de projeto decorrem disso:

- **A cadeia de inferência é recuperável.** O motor responde *por que* pergunta
  algo durante a consulta e *como* chegou a uma conclusão depois dela,
  percorrendo as regras de apoio até os fatos fornecidos pelo usuário.
- **Restrições viram precondições.** `authorized(?n)` é precondição dos
  operadores que alteram o cenário, o que torna a restrição uma propriedade do
  espaço de estados em vez de uma verificação em tempo de execução. É uma
  técnica de modelagem STRIPS, exercitada aqui sobre um cenário simulado.

### Estratégia de validação

| Propriedade afirmada | Como é verificada | Oráculo |
|---|---|---|
| O A\* devolve o caminho de custo mínimo | todos os pares ordenados, nos dois cenários | Floyd–Warshall |
| A heurística é admissível e consistente | todos os pares ordenados | comparação com o `h*` exato |
| O plano é executável e atinge o objetivo | reexecução passo a passo desde o estado inicial | `Plan.validate` |
| O domínio não declara sucesso sobre falha viva | exclusão mútua no ponto fixo | grafo de planejamento |
| Nenhum operador é inalcançável | presença nos níveis de ação | grafo de planejamento |
| Limite inferior do tamanho do plano | nível do objetivo sem exclusão mútua | grafo de planejamento |

São **202 testes**, que asseguram *propriedades* — admissibilidade, validade de
plano, invariantes do domínio — e não apenas saídas esperadas.

### Documentação

| Documento | Conteúdo |
|---|---|
| [`docs/01-expert-system.md`](docs/01-expert-system.md) | Variáveis, regras (43 na base de campo, 41 na simulada), fatores de certeza, encadeamentos, resolução de conflito, explicação |
| [`docs/02-planning.md`](docs/02-planning.md) | STRIPS, GPS e análise meios-fins, planejador A*, limitações do GPS |
| [`docs/planner-design-process.md`](docs/planner-design-process.md) | **Como o domínio de planejamento foi definido**, e a análise por grafo de planejamento que o valida |
| [`docs/03-astar.md`](docs/03-astar.md) | A*, prova de admissibilidade e consistência, comparação entre estratégias |
| [`docs/domain-model.md`](docs/domain-model.md) | Topologia, modelo de custo e limites de validade |
| [`docs/presentation-script.md`](docs/presentation-script.md) | Roteiro da apresentação — 30 minutos por tema |
| [`docs/assessment-protocol.md`](docs/assessment-protocol.md) | Protocolo de avaliação, rubrica proposta e procedimento de evidência |

---

## English

### Research question

> In the absence of a labelled fault dataset, can a **diagnosis → plan → route**
> chain be built that is both *auditable* — every conclusion traceable to the
> evidence supporting it — and *verifiable*, meaning its correctness properties
> are asserted by tests rather than merely claimed in prose?

The question is methodological before it is technical. It arises from a real
laboratory constraint rather than an aesthetic preference for symbolic methods:
the boundary condition is the **unavailability of measurement-derived labels**,
and the answer has to be honest about what that constraint permits concluding.

Three sub-questions organise the three systems:

1. **Knowledge representation.** How can engineering judgement under uncertainty
   be encoded so the inference chain stays inspectable and contestable?
   *(production rules with certainty factors)*
2. **Deliberation.** How is the **order** of intervention derived — not merely
   the set of actions — expressing constraints as formal preconditions rather
   than as runtime checks? *(STRIPS, GPS, progression planning)*
3. **Demonstrable optimality.** Under what conditions does an informed search
   guarantee the least-cost path, and how is the chosen heuristic *shown* to meet
   them in this domain? *(A\*, admissibility, consistency)*

### Methodological stance

Three declared commitments, inherited from the measurement discipline expected
of a research artefact:

**(i) Declared uncertainty.** Every numeric threshold used by a rule lives in one
block (`THRESHOLDS`) and is marked **nominal and uncalibrated**. No laboratory
measurement supports it. Separating *structure* (the rules) from *parameter* (the
thresholds) is deliberate: future calibration adjusts values without rewriting
knowledge.

**(ii) Verification by an independent oracle.** Correctness properties are not
argued — they are tested against a procedure that **shares no code** with the
artefact under test. A\*'s optimality is checked against Floyd–Warshall; the
planning domain's consistency, against planning-graph (Graphplan) analysis.
Checking A\* against uniform cost would be circular, since `uniform_cost` is
literally `astar` with `h = 0`.

**(iii) Falsifiability and negative results.** The project records what it could
**not** demonstrate as carefully as what it could. Two examples live in the
documentation: GPS non-optimality is a real property, yet **this domain cannot
exhibit it** (no literal has more than one producing operator, so means-ends
analysis has no choice to get wrong); and A\*'s advantage over uniform cost
(9.4% and 25.9% fewer nodes expanded, at 17 and 30 nodes) is a **two-point
measurement**, not a scaling law.

### The domain

The domain is the communication network linking distributed assets of an
electric system to the operations centre: a fibre core, 900 MHz radio sectors, a
*store-and-forward* relay chain, and a private LTE overlay. The base scenario has
17 nodes and 24 links; the simulated scenario used in the demonstrations and the
presentation has **30 nodes and 44 links** across three sectors.

**The topology is SYNTHETIC.** It is a didactic model of the *class* of scenarios
studied in wireless backhaul research testbeds. It contains no real inventory,
addressing, equipment identification, RF configuration, or field topology of any
laboratory or utility. See [`docs/domain-model.md`](docs/domain-model.md).

**Simulated rather than field, by methodological choice.** The scenario runs in
ns-3, which inverts the usual internal/external validity trade-off in this work's
favor: a *commanded* fault condition is repeatable and labellable, whereas an
*observed* field condition is merely probable. Each diagnosis declares in the
`INDUCIBLE_BY` block **how it is induced in the simulator**, which makes the case
set reproducible by third parties. The cost of that choice is explicit and
declared: the results hold for the model, not for a plant.

### Why the DIAGNOSIS is not learned

The central claim is a **measurement-validity** constraint, not a judgement about
inductive methods. No labelled fault dataset exists for this domain. Labelling a
link as *degraded* or *failed* requires a controlled degradation instrument and
an authenticated observability baseline; without both, no label derives from
measurement — it derives from assumption. An inductive method trained only on the
normal state cannot reliably infer degradation, and a classifier fitted to
assumed labels would inherit the assumption without making that inheritance
visible. It is precisely that invisibility the symbolic method avoids: a wrong
rule can be read, argued with, and refuted by an engineer; a wrong weight cannot.

When labelled data does not exist, the defensible path is to encode **engineering
knowledge** as explicit, auditable, contestable rules — which is exactly what an
expert system does. The system declares the limitation in its own output, not
only in the documentation.

Two design consequences follow:

- **The inference chain is recoverable.** The engine answers *why* it asks
  something during a consultation and *how* it reached a conclusion afterwards,
  walking the supporting rules down to the facts the user supplied.
- **Constraints become preconditions.** `authorized(?n)` is a precondition of the
  operators that change the scenario, which makes the constraint a property of
  the state space rather than a runtime check. It is a STRIPS modelling
  technique, exercised here over a simulated scenario.

### Validation strategy

| Claimed property | How it is checked | Oracle |
|---|---|---|
| A\* returns the least-cost path | every ordered pair, both scenarios | Floyd–Warshall |
| The heuristic is admissible and consistent | every ordered pair | comparison against exact `h*` |
| A plan is executable and reaches the goal | step-by-step replay from the initial state | `Plan.validate` |
| The domain never declares success over a live fault | mutual exclusion at the fixpoint | planning graph |
| No operator is unreachable | presence in the action levels | planning graph |
| Lower bound on plan length | goal level free of mutexes | planning graph |

There are **202 tests**, asserting *properties* — admissibility, plan validity,
domain invariants — rather than merely expected outputs.

### Documentation

| Document | Contents |
|---|---|
| [`docs/01-expert-system.md`](docs/01-expert-system.md) | Variables, rules (43 in the field base, 41 in the simulated one), certainty factors, both chainings, conflict resolution, explanation |
| [`docs/02-planning.md`](docs/02-planning.md) | STRIPS, GPS and means-ends analysis, the A* planner, GPS's limitations |
| [`docs/planner-design-process.md`](docs/planner-design-process.md) | **How the planning domain was defined**, and the planning-graph analysis that validates it |
| [`docs/03-astar.md`](docs/03-astar.md) | A*, admissibility and consistency proofs, strategy comparison |
| [`docs/domain-model.md`](docs/domain-model.md) | Topology, cost model, and validity limits |
| [`docs/presentation-script.md`](docs/presentation-script.md) | Presentation script — 30 minutes per topic |
| [`docs/assessment-protocol.md`](docs/assessment-protocol.md) | Assessment protocol, proposed rubric, and evidence procedure |

---

## Estrutura / Layout

```
src/aisg/
  domain/          modelo compartilhado: topologia e custo / shared model: topology and cost
  expert_system/   motor de inferência + base de conhecimento / inference engine + knowledge base
  planning/        STRIPS, GPS, planejador A*, grafo de planejamento / STRIPS, GPS, A* planner, planning graph
  search/          A* e as demais estratégias / A* and the other strategies
  cli.py           interface de linha de comando / command-line interface
tests/             202 testes / 202 tests
docs/              documentação bilíngue / bilingual documentation
  assets/          figuras (SVG + PNG) e seus geradores / figures and their generators
notebooks/         roteiro executável da apresentação / executable presentation script
```

## Referências / References

- FIKES, R. E.; NILSSON, N. J. STRIPS: a new approach to the application of theorem proving to problem solving. *Artificial Intelligence*, v. 2, n. 3-4, p. 189-208, 1971.
- NEWELL, A.; SIMON, H. A. *GPS, a program that simulates human thought*. Santa Monica: RAND Corporation, 1961.
- HART, P. E.; NILSSON, N. J.; RAPHAEL, B. A formal basis for the heuristic determination of minimum cost paths. *IEEE Transactions on Systems Science and Cybernetics*, v. 4, n. 2, p. 100-107, 1968.
- SHORTLIFFE, E. H.; BUCHANAN, B. G. A model of inexact reasoning in medicine. *Mathematical Biosciences*, v. 23, n. 3-4, p. 351-379, 1975.
- TURING, A. M. Computing machinery and intelligence. *Mind*, v. LIX, n. 236, p. 433-460, 1950.
- RUSSELL, S.; NORVIG, P. *Artificial intelligence*: a modern approach. 4. ed. Harlow: Pearson, 2021.

## Como citar / How to cite

Use [`CITATION.cff`](CITATION.cff). No GitHub, o botao **Cite this repository** gera BibTeX e APA a partir dele.
Use [`CITATION.cff`](CITATION.cff). On GitHub, the **Cite this repository** button generates BibTeX and APA from it.

## Autor / Author

Fernando Sabino Dantas — trabalhos praticos da disciplina de Introducao a Inteligencia Artificial (mestrado/doutorado).
Practical assignments for the Introduction to Artificial Intelligence course (MSc/PhD).

## Licença / License

[MIT](LICENSE).
