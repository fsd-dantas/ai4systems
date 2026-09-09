# Modelo de dominio / Domain model

## Português

### O que e modelado

A rede de comunicacao que liga ativos distribuidos de um sistema eletrico ao centro de operacao. Sao 17 nos e 24 enlaces, declarados em [`backhaul-topology.json`](../src/aisg/domain/data/backhaul-topology.json):

| Elemento | Nos | Papel |
|---|---|---|
| Nucleo | `NOC`, `LTE_CORE` | Centro de operacao e nucleo LTE privativo |
| Setor A | `AP_A`, `RM_A1`–`RM_A4`, `SUB_S1` | Estrela de radio 900 MHz em torno de um ponto de acesso |
| Cadeia SAF | `SAF_A1`, `SAF_A2`, `RM_A5` | Repetidores *armazena-e-encaminha* ate uma folha distante |
| Setor B | `AP_B`, `RM_B1`–`RM_B3` | Segunda estrela de radio |
| Sobreposicao LTE | `LTE_ENB` | Caminho alternativo independente do radio 900 MHz |
| Campo | `RECLOSER_7` | Dispositivo de campo, destino tipico do trafego |

### Dois cenarios / two scenarios

| Nome | Nos | Enlaces | Uso |
|---|---|---|---|
| `base` | 17 | 24 | Cenario de trabalho. Pequeno o bastante para acompanhar o raciocinio no quadro. |
| `scale` | 30 | 44 | Cenario de escala: tres setores, cada um com estrela de radio e cadeia armazena-e-encaminha ate um dispositivo de campo. |

```bash
aisg --topology scale route --compare
```

O cenario de escala existe para mostrar que **a vantagem da heuristica cresce com o grafo**. Somando todos os pares origem-objetivo, o A* expande menos nos que a busca de custo uniforme nos dois cenarios — mas a economia e nitidamente maior no de 30 nos. Ha teste que verifica exatamente essa relacao.

Ambos sao carregados pelo mesmo codigo: `load_topology("base")` ou `load_topology("scale")`. Um caminho de arquivo tambem e aceito, para cenarios proprios mantidos fora do repositorio.

### A topologia e sintetica — e isso e uma afirmacao, nao uma ressalva

Este e um modelo didatico da *classe* de cenarios estudada em laboratorios de backhaul sem fio. Nao contem inventario real, enderecamento, identificacao de equipamento, parametros de RF nem topologia de campo de qualquer laboratorio ou concessionaria. As distancias sao geometria nominal de alimentador de distribuicao, nao levantamento de campo.

### Modelo de custo

O custo de atravessar um enlace e um **custo de transporte em milissegundos**:

```
custo(u, v) = sobrecarga(tipo) + distancia(u, v) / (velocidade(tipo) * qualidade)
```

| Tipo de enlace | Velocidade (m/ms) | Sobrecarga (ms) |
|---|---|---|
| `fiber` | 150,0 | 0,5 |
| `ethernet` | 120,0 | 0,4 |
| `lte` | 60,0 | 8,0 |
| `radio_900mhz` | 25,0 | 12,0 |
| `radio_900mhz_saf` | 25,0 | 25,0 |

A `velocidade` e uma **velocidade efetiva de transporte**, nao uma velocidade fisica de propagacao. E uma abstracao de modelagem: ela reune serializacao, enfileiramento e o fato de que saltos de radio mais longos operam com modulacao mais robusta — e portanto mais lenta — num unico termo proporcional a distancia. A `qualidade`, em (0, 1], degrada essa velocidade. A `sobrecarga` cobra um preco fixo por salto: um repetidor *armazena-e-encaminha* **termina e retransmite** o quadro, por isso paga mais que um salto comutado.

**Duas consequencias de projeto:**

1. As distancias sao **derivadas das coordenadas**, nunca armazenadas em separado. Assim a geometria e a heuristica do A* nao podem divergir.
2. A forma do custo foi escolhida deliberadamente para que a heuristica em linha reta seja **admissivel e consistente** — a prova esta em [`03-astar.md`](03-astar.md).

### Limites de validade

Os numeros deste modelo nao representam nenhum radio, enlace ou instalacao especifica. Servem para exercitar os algoritmos com um problema de estrutura realista: caminhos concorrentes com perfis de custo diferentes, uma cadeia serial cara e uma sobreposicao que oferece um desvio. Uma conclusao obtida aqui vale para **este modelo**, nao para uma planta fisica.

---

## English

### What is modelled

The communication network linking distributed assets of an electric system to the operations centre: 17 nodes and 24 links, declared in [`backhaul-topology.json`](../src/aisg/domain/data/backhaul-topology.json).

| Element | Nodes | Role |
|---|---|---|
| Core | `NOC`, `LTE_CORE` | Operations centre and private LTE core |
| Sector A | `AP_A`, `RM_A1`–`RM_A4`, `SUB_S1` | 900 MHz radio star around an access point |
| SAF chain | `SAF_A1`, `SAF_A2`, `RM_A5` | *Store-and-forward* relays out to a distant leaf |
| Sector B | `AP_B`, `RM_B1`–`RM_B3` | Second radio star |
| LTE overlay | `LTE_ENB` | Alternative path independent of the 900 MHz radio |
| Field | `RECLOSER_7` | Field device, a typical traffic destination |

### The topology is synthetic — a claim, not a caveat

This is a didactic model of the *class* of scenarios studied in wireless backhaul testbeds. It contains no real inventory, addressing, equipment identification, RF parameters, or field topology of any laboratory or utility. Distances are nominal distribution-feeder geometry, not a field survey.

### Cost model

The cost of traversing a link is a **transport cost in milliseconds**:

```
cost(u, v) = overhead(type) + distance(u, v) / (speed(type) * quality)
```

`speed` is an **effective transport speed**, not a physical propagation speed. It is a modelling abstraction folding serialization, queueing, and the fact that longer radio hops run at more robust — and therefore slower — modulation into a single distance-proportional term. `quality`, in (0, 1], degrades that speed. `overhead` charges a fixed price per hop: a store-and-forward relay **terminates and retransmits** the frame, so it pays more than a switched hop.

**Two design consequences:**

1. Distances are **derived from the coordinates**, never stored separately, so the geometry and the A* heuristic cannot disagree.
2. The cost shape was chosen deliberately so that the straight-line heuristic is **admissible and consistent** — proof in [`03-astar.md`](03-astar.md).

### Validity limits

The numbers in this model represent no specific radio, link, or installation. They exercise the algorithms on a problem with realistic structure: competing paths with different cost profiles, an expensive serial chain, and an overlay offering a detour. A conclusion obtained here holds for **this model**, not for a physical plant.
