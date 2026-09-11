# 3 — Busca A* / A* search

> Roteamento de menor custo no backhaul, com prova de admissibilidade e comparacao
> contra busca em largura, em profundidade, custo uniforme e gulosa.
>
> Least-cost routing over the backhaul, with an admissibility proof and a comparison
> against breadth-first, depth-first, uniform-cost, and greedy search.

Codigo / code: [`src/aisg/search/`](../src/aisg/search/)

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/fsd-dantas/ai4systems/main/docs/assets/04-astar-dark.svg">
    <img src="https://raw.githubusercontent.com/fsd-dantas/ai4systems/main/docs/assets/04-astar-light.svg" alt="On the left, the optimal path A* finds. On the right, the heuristic, its admissibility and consistency proofs, and the comparison table for five search strategies." width="100%">
  </picture>
</p>

---

## Português

### Problema

Qual o caminho de **menor custo de transporte** entre dois nos da rede? O requisito da disciplina e explicito: o programa deve retornar **o caminho exato** entre o estado inicial e o estado objetivo.

### O algoritmo

O A* (Hart, Nilsson e Raphael, 1968) ordena a fronteira por

```
f(n) = g(n) + h(n)
```

onde `g(n)` e o custo ja pago para chegar a `n` e `h(n)` e a estimativa do custo restante ate o objetivo. As duas metades importam: so `g` da o custo uniforme (otimo, porem cego); so `h` da a busca gulosa (rapida, porem sem garantia).

**Detalhes de implementacao que mudam o resultado:**

- **Desempate.** Empates em `f` sao resolvidos preferindo o maior `g` (no mais profundo) e, depois, a ordem de insercao. Isso mantem as execucoes reproduzíveis — importante para uma apresentacao.
- **Reabertura.** Um estado ja fechado e reaberto se surgir um caminho mais barato. Com heuristica consistente isso nunca acontece, mas tratamos o caso geral em vez de supor a consistencia.
- **Custos negativos** sao recusados explicitamente, com erro claro: o A* nao os admite.

### A heuristica

```
h(n) = distancia_em_linha_reta(n, objetivo) / VELOCIDADE_MAXIMA
```

com `VELOCIDADE_MAXIMA = 150 m/ms`, a maior velocidade efetiva do registro de tipos de enlace (a fibra).

### Prova de admissibilidade

Uma heuristica e **admissivel** se nunca superestima o custo real restante.

Todo salto de `u` a `v` custa

```
custo(u, v) = sobrecarga(tipo) + d(u, v) / (velocidade(tipo) * qualidade)
```

Como `sobrecarga >= 0`, `qualidade <= 1` e `velocidade(tipo) <= VELOCIDADE_MAXIMA` para todo tipo, segue que

```
custo(u, v) >= d(u, v) / VELOCIDADE_MAXIMA
```

Somando ao longo de qualquer caminho de `n` ate o objetivo, o custo total e ao menos a **distancia total percorrida** dividida por `VELOCIDADE_MAXIMA`. Pela desigualdade triangular, a distancia total percorrida e ao menos a distancia em linha reta. Logo

```
custo_otimo(n, objetivo) >= d(n, objetivo) / VELOCIDADE_MAXIMA = h(n)     ∎
```

### Prova de consistencia

Uma heuristica e **consistente** se `h(u) <= custo(u, v) + h(v)` para toda aresta.

Pela desigualdade triangular, `d(u, objetivo) <= d(u, v) + d(v, objetivo)`. Dividindo por `VELOCIDADE_MAXIMA`:

```
h(u) <= d(u, v)/VELOCIDADE_MAXIMA + h(v) <= custo(u, v) + h(v)     ∎
```

A consistencia implica a admissibilidade e garante que nenhum no precise ser reaberto.

**Isto nao e acidente.** O modelo de custo do dominio foi **projetado** para que a prova se sustente: as distancias sao derivadas das coordenadas (nunca armazenadas em separado, para que geometria e heuristica nao possam divergir) e o custo tem um termo proporcional a distancia com velocidade limitada.

**E verificado, nao apenas argumentado.** Dois testes checam as duas propriedades exaustivamente, para **todos** os 17 × 17 pares origem-objetivo e todas as arestas, comparando contra o custo otimo obtido por busca de custo uniforme.

### Resultado: `NOC` → `RECLOSER_7`

| Estrategia | Passos | Custo (ms) | Expandidos | Gerados | Pico da fronteira | Otimo? |
|---|---|---|---|---|---|---|
| Largura (BFS) | 4 | 357,35 | 15 | 41 | 7 | em passos |
| Profundidade (DFS) | 5 | 343,06 | 19 | 48 | 6 | nao |
| Custo uniforme | 4 | **92,22** | 13 | 36 | 9 | **sim** |
| Gulosa | 4 | 357,35 | **5** | 16 | 8 | nao |
| **A\*** | 4 | **92,22** | 11 | 32 | 7 | **sim** |

Tres licoes numa tabela so:

1. **A busca em largura minimiza saltos, nao custo.** Ela acha um caminho de 4 saltos que custa 357 ms, quase quatro vezes o otimo — porque conta um salto de fibra e um salto de radio armazena-e-encaminha como iguais.
2. **A gulosa e a mais rapida e esta errada.** Expande 5 nos, menos da metade do A*, e devolve um caminho 3,9 vezes mais caro. E o argumento mais direto a favor do termo `g(n)`.
3. **A\* alcanca o mesmo otimo do custo uniforme expandindo menos nos** (11 contra 13). A heuristica nao muda a resposta; muda o trabalho para chega-la.

O caminho otimo evita inteiramente a cadeia armazena-e-encaminha e desce pela sobreposicao LTE:

```
NOC -> LTE_CORE -> LTE_ENB -> RM_A5 -> RECLOSER_7        92,22 ms

salto                  meio                  qual.   custo(ms)   acum.(ms)
NOC -> LTE_CORE        ethernet local         1,00        5,99        5,99
LTE_CORE -> LTE_ENB    fibra optica           0,95       10,55       16,54
LTE_ENB -> RM_A5       LTE privativo          0,80       69,94       86,48
RM_A5 -> RECLOSER_7    ethernet local         1,00        5,74       92,22
```

### A vantagem da heuristica cresce com o grafo

O cenario de escala (30 nos, 44 enlaces) existe para medir isso.

Num unico par — `NOC` ate o dispositivo de campo mais distante:

| Cenario | Nos | A* expandidos | Custo uniforme expandidos | Economia |
|---|---|---|---|---|
| `base` | 17 | 11 | 13 | 15% |
| `scale` | 30 | 14 | 25 | **44%** |

Um unico par pode ser sorte. Somando **todos** os pares origem-objetivo de cada cenario:

| Cenario | Nos | A* expandidos (total) | Custo uniforme (total) | Economia |
|---|---|---|---|---|
| `base` | 17 | 1382 | 1519 | 9,0% |
| `scale` | 30 | 5571 | 7657 | **27,2%** |

A economia agregada triplica ao passar de 17 para 30 nos.

```bash
aisg --topology scale route --compare
```

Nos dois cenarios a resposta e a mesma — o caminho otimo. O que muda e o trabalho para chega-la, e a diferenca aumenta com o tamanho do grafo. E o argumento pratico a favor do A* quando a rede cresce: num grafo pequeno, a busca cega e barata; num grande, deixa de ser.

O teste `test_the_heuristic_saves_more_work_as_the_graph_grows` verifica essa relacao somando **todos** os pares origem-objetivo de cada cenario, e nao apenas o par escolhido para a apresentacao.

### Heuristicas aprendidas: onde o aprendizado de maquina entraria

O repositorio nao usa aprendizado de maquina, e a razao declarada em
[`01-expert-system.md`](01-expert-system.md) — a ausencia de dados rotulados de
falha — vale para o **diagnostico**, nao para a heuristica.

Aprender `h(n)` e uma tarefa de natureza diferente:

| | Diagnosticar a causa | Aprender a heuristica |
|---|---|---|
| Alvo | Rotulo de falha | `h*(n)`, o custo real restante |
| Origem do rotulo | Medicao em campo | **Calculavel**: custo uniforme a partir do objetivo |
| Precisa de instrumento de degradacao | Sim | **Nao** |
| Quantidade de exemplos | Zero hoje | Ilimitada — um por par no grafo |

Ou seja: a supervisao e **gratuita e exata**. O obstaculo que impede aprender o
diagnostico simplesmente nao existe aqui.

**O que realmente impede o uso direto e a admissibilidade.** Uma heuristica
obtida por regressao pode **superestimar** o custo restante, e nesse caso o A*
continua funcionando e passa a devolver caminhos subotimos **sem avisar** — o
mesmo modo de falha silenciosa discutido em [`02-planning.md`](02-planning.md).

Tres formas de conviver com isso, em ordem de garantia:

1. **Como criterio de desempate apenas.** A ordenacao principal continua sendo
   `g + h_admissivel`; a heuristica aprendida so decide empates. A otimalidade e
   preservada exatamente.
2. **Busca limitadamente subotima** (A* ponderado, *focal search*). Mantem-se a
   heuristica admissivel para o limite e usa-se a aprendida para ordenar dentro
   da faixa. Perde-se a otimalidade, mas com **fator de garantia declarado**.
3. **Regressao com perda assimetrica**, penalizando mais a superestimacao. Reduz
   a violacao, mas **nao a elimina** — nao ha garantia, apenas tendencia.

**Onde isso pagaria mais.** Nao no roteamento: a distancia em linha reta ja e
quase perfeita e custa nada. O ganho estaria no **planejador**, onde a heuristica
`goal_count` vale no maximo 2 e o espaco de estados nao tem geometria a explorar.

**O repositorio ja tem o instrumento de medida.** Os testes de admissibilidade
percorrem todos os pares origem-objetivo dos dois cenarios. Aplicados a uma
heuristica aprendida, deixam de ser apenas uma protecao e passam a medir *quantas
vezes* ela viola a admissibilidade e *em quanto* — que e precisamente o resultado
que um experimento desses precisa reportar.

### Falhas e recalculo de rota

Um enlace pode ser retirado de servico em tempo de execucao (`--disable-link A-B`) e um no pode ser excluido da rota (`--avoid`). E assim que a integracao com o planejador funciona: quando o plano inclui desviar trafego, a rota e recalculada evitando o no afetado.

```bash
aisg route --from NOC --to RECLOSER_7 --disable-link LTE_ENB-RM_A5
```

Sem a sobreposicao LTE, o custo otimo sobe e o caminho passa a usar a cadeia armazena-e-encaminha — o teste `test_disabling_a_link_changes_the_optimal_route` verifica exatamente isso.

### O mesmo A* resolve os dois problemas

A busca e definida sobre um **problema abstrato** (estado inicial, teste de objetivo, funcao sucessora). Por isso a mesma funcao `astar` serve ao roteamento **e** ao planejamento do trabalho 2. Uma implementacao, dois espacos de estados.

### Como executar

```bash
aisg route --from NOC --to RECLOSER_7 --compare --expansion
aisg route --from AP_B --to SUB_S1
aisg route --from NOC --to RECLOSER_7 --avoid SAF_A2 RM_A5
```

---

## English

### Problem

What is the **least transport cost** path between two nodes? The course requirement is explicit: the program must return **the exact path** between the initial and the goal state.

### The algorithm

A* (Hart, Nilsson and Raphael, 1968) orders the frontier by `f(n) = g(n) + h(n)`, where `g` is the cost already paid and `h` estimates the cost remaining. Both halves matter: `g` alone is uniform-cost search (optimal but blind); `h` alone is greedy search (fast but unguaranteed).

Implementation details that change the outcome: ties on `f` break towards the larger `g` and then insertion order, keeping runs reproducible; a closed state is re-opened if a cheaper path appears (never needed with a consistent heuristic, but we handle the general case); and negative step costs are refused with a clear error.

### The heuristic and its proofs

```
h(n) = straight_line_distance(n, goal) / MAX_SPEED       MAX_SPEED = 150 m/ms
```

**Admissibility.** Every hop costs `overhead + d(u,v) / (speed * quality)`. Since `overhead >= 0`, `quality <= 1`, and `speed <= MAX_SPEED`, each hop costs at least `d(u,v) / MAX_SPEED`. Summing over any path, the total is at least the total travelled distance over `MAX_SPEED`, which by the triangle inequality is at least the straight-line distance over `MAX_SPEED`. Hence `h(n)` never overestimates. ∎

**Consistency.** By the triangle inequality `d(u, goal) <= d(u, v) + d(v, goal)`; dividing by `MAX_SPEED` gives `h(u) <= cost(u,v) + h(v)`. ∎ Consistency implies admissibility and guarantees no node needs re-expansion.

**This is not an accident.** The domain's cost model was *designed* so the proof holds — distances are derived from coordinates so geometry and heuristic cannot disagree. And it is **verified, not merely argued**: two tests check both properties exhaustively over all 17 × 17 source-goal pairs and every edge, against ground truth from uniform-cost search.

### Result: `NOC` → `RECLOSER_7`

See the table in the Portuguese section. Three lessons in one table:

1. **Breadth-first minimises hops, not cost** — 4 hops costing 357 ms, nearly four times the optimum, because it counts a fibre hop and a store-and-forward radio hop alike.
2. **Greedy is fastest and wrong** — 5 nodes expanded, under half of A*, for a path 3.9x more expensive. The most direct argument for the `g(n)` term.
3. **A\* reaches the same optimum as uniform cost while expanding fewer nodes** (11 vs 13). The heuristic does not change the answer; it changes the work needed to reach it.

### Failures and re-routing

A link can be taken out of service at runtime (`--disable-link A-B`) and a node excluded from the route (`--avoid`). That is how the planner integration works: when the plan includes rerouting, the route is recomputed avoiding the affected node.

### One A* for both problems

Search is defined over an **abstract problem** (initial state, goal test, successor function), so the same `astar` function serves routing **and** the planning of assignment 2. One implementation, two state spaces.
