# Modelo de domínio / Domain model

## Português

### O que é modelado

A rede de comunicação que liga ativos distribuídos de um sistema elétrico ao centro de operação, com **duas redes de acesso independentes** (multi-RAT). O cenário de trabalho tem **60 nós e 74 enlaces**, declarados em [`backhaul-topology-60.json`](../software/aisg/domain/data/backhaul-topology-60.json):

| Elemento | Nós | Papel |
|---|---|---|
| Núcleo | `NOC` | Centro de operação; liga-se por fibra às duas redes de acesso |
| LTE privativo | `eNB_A`, `eNB_B`, `RELAY_1`–`RELAY_5`, `CPE_01`–`CPE_15` | Estrela LTE com dois eNodeBs, uma camada de repetidores e um CPE por site |
| Malha 900 MHz | `SAF_01`–`SAF_07`, `RM_01`–`RM_15` | Cadeia de repetidores *armazena-e-encaminha* alimentada por fibra, e um rádio remoto por site |
| Sites | `ER_01`–`ER_15` | Roteador de borda de cada site: fronteira da rede elétrica e único ponto onde as duas redes se encontram |

Cada roteador de borda é **stub**: uma rota pode começar ou terminar nele, mas nunca atravessá-lo, porque um site não transporta o backhaul de outro.

### Cenários

| Nome | Nós | Enlaces | Uso |
|---|---|---|---|
| `dual` (padrão) | 60 | 74 | 15 sites em duplo acesso; base dos experimentos 001 e 002 |
| `simulated` | 30 | 44 | Três setores; usado para comparar o esforço de busca em dois grafos |

```bash
aisg --topology simulated route --compare
```

Um caminho de arquivo também é aceito, para cenários próprios mantidos fora do repositório.

### A topologia é sintética — uma afirmação, não uma ressalva

Identificadores, coordenadas e qualidades de enlace foram inventados para este modelo. Não há inventário real, endereçamento, identificação de equipamento, parâmetros de RF nem topologia de campo de qualquer laboratório ou concessionária.

### Modelo de custo

O custo de atravessar um enlace é um **custo de transporte em milissegundos**:

```
custo(u, v) = sobrecarga(tipo) + distância(u, v) / (velocidade(tipo) × qualidade)
```

| Tipo de enlace | Velocidade (m/ms) | Sobrecarga (ms) |
|---|---|---|
| `fiber` | 150,0 | 0,5 |
| `ethernet` | 120,0 | 0,4 |
| `lte` | 60,0 | 8,0 |
| `radio_900mhz` | 25,0 | 12,0 |
| `radio_900mhz_saf` | 25,0 | 25,0 |

A `velocidade` é uma **velocidade efetiva de transporte**, e não uma velocidade física de propagação: reúne serialização, enfileiramento e o fato de saltos de rádio mais longos operarem com modulação mais robusta, e portanto mais lenta. A `qualidade`, em (0, 1], degrada essa velocidade. A `sobrecarga` cobra um preço fixo por salto; um repetidor armazena-e-encaminha termina e retransmite o quadro, por isso paga mais.

Duas consequências de projeto:

1. As distâncias são **derivadas das coordenadas**, nunca armazenadas à parte, para que geometria e heurística do A\* não divirjam.
2. A forma do custo torna a heurística em linha reta **admissível e consistente** — prova em [`astar.md`](../experiments/001-symbolic-restoration-chain/astar.md).

### Limites de validade

É um modelo de topologia, não a saída de uma simulação ou medição. Qualidades de enlace são nominais e não calibradas; custos são estimativas de tempo de transporte, não latência medida. Não há capacidade nem tráfego neste modelo — isso entra com a simulação multi-RAT planejada no [roteiro](../research/roadmap.md).

---

## English

### What is modelled

The communication network linking distributed assets of an electric system to the operations centre, with **two independent access networks** (multi-RAT). The working scenario has **60 nodes and 74 links**, declared in [`backhaul-topology-60.json`](../software/aisg/domain/data/backhaul-topology-60.json):

| Element | Nodes | Role |
|---|---|---|
| Core | `NOC` | Operations centre; fibre to both access networks |
| Private LTE | `eNB_A`, `eNB_B`, `RELAY_1`–`RELAY_5`, `CPE_01`–`CPE_15` | LTE star with two eNodeBs, a relay tier, and one CPE per site |
| 900 MHz mesh | `SAF_01`–`SAF_07`, `RM_01`–`RM_15` | Fibre-fed chain of *store-and-forward* relays, and one remote radio per site |
| Sites | `ER_01`–`ER_15` | Each site's edge router: the grid boundary and the only point where the two networks meet |

Every edge router is a **stub**: a route may begin or end there but never cross it, because a site does not carry another site's backhaul.

### Scenarios

| Name | Nodes | Links | Use |
|---|---|---|---|
| `dual` (default) | 60 | 74 | 15 dual-homed sites; basis of experiments 001 and 002 |
| `simulated` | 30 | 44 | Three sectors; used to compare search effort across two graphs |

A file path is also accepted, for private scenarios kept outside the repository.

### The topology is synthetic — a claim, not a caveat

Identifiers, coordinates and link qualities were invented for this model. There is no real inventory, addressing, equipment identification, RF parameter or field topology of any laboratory or utility.

### Cost model

The cost of traversing a link is a **transport cost in milliseconds**:

```
cost(u, v) = overhead(type) + distance(u, v) / (speed(type) × quality)
```

`speed` is an **effective transport speed**, not a physical propagation speed: it folds serialisation, queueing, and the slower, more robust modulation of longer radio hops into one term. `quality`, in (0, 1], degrades that speed. `overhead` charges a fixed price per hop; a store-and-forward relay terminates and retransmits the frame, so it pays more.

Two design consequences:

1. Distances are **derived from the coordinates**, never stored separately, so the geometry and the A\* heuristic cannot disagree.
2. The cost shape makes the straight-line heuristic **admissible and consistent** — proof in [`astar.md`](../experiments/001-symbolic-restoration-chain/astar.md).

### Validity limits

This is a topology model, not the output of a simulation or measurement. Link qualities are nominal and uncalibrated; costs are transport-time estimates, not measured latency. The model has no capacity and no traffic — those arrive with the multi-RAT simulation planned in the [roadmap](../research/roadmap.md).
