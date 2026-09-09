# Roteiro de apresentacao — 30 minutos por tema / Presentation script — 30 minutes per topic

Tres temas, **30 minutos cada**: sistema especialista, geracao automatica de planos e busca A*.
Com esse tempo, cada tema comporta teoria, demonstracao ao vivo e discussao de limitacoes — nao apenas
uma corrida pela demo.

**Antes de comecar:** `python -m pytest` — 99 testes verdes na tela sao um bom cartao de visita.

**Material de apoio:** [`notebooks/apresentacao.ipynb`](../notebooks/apresentacao.ipynb) executa tudo o que
esta abaixo, com as figuras. Rode os comandos de terminal quando quiser mostrar o sistema como ferramenta;
use o notebook quando quiser mostrar o raciocinio.

---

# TEMA 1 — Sistema especialista (30 min)

### 0:00–4:00 — O dominio e a escolha do metodo

**O dominio.** A rede de comunicacao que liga ativos distribuidos de um sistema eletrico ao centro de
operacao: nucleo em fibra, dois setores de radio 900 MHz, uma cadeia de repetidores armazena-e-encaminha
e uma sobreposicao LTE privativa. 17 nos, 24 enlaces.

> Diga explicitamente: **a topologia e sintetica**, um modelo didatico da *classe* de cenarios estudada em
> laboratorios de backhaul sem fio. Nao ha inventario real, enderecamento nem identificacao de equipamento.

**A escolha do metodo — o argumento mais forte da apresentacao inteira.**

> Nao existe conjunto de dados rotulado de falhas para este dominio. Rotular um enlace como *degradado* ou
> *em falha* exige um instrumento de degradacao controlada e uma linha de base de observabilidade
> autenticada. Sem os dois, o rotulo nao vem da medicao. Um metodo indutivo treinado apenas em estado
> normal nao infere degradacao de modo confiavel.
>
> Quando nao ha dados rotulados, o caminho honesto e codificar conhecimento de engenharia em regras
> explicitas, **auditaveis e contestaveis**. Um especialista pode discordar da regra R14 e mudar so ela.
> Nao se discute assim com um peso de rede neural.

Esse e o contraste entre metodos **dedutivos** e **indutivos** — o mesmo que a disciplina retoma na aula
de inducao, regras de associacao e classificacao.

### 4:00–10:00 — Representacao do conhecimento

Mostre a base: 18 variaveis, 43 regras, cinco camadas.

| Camada | Regras | Papel |
|---|---|---|
| 1 | R01–R04 | Medicoes de RF → `signal_quality` |
| 2 | R05–R09 | Estado e desempenho → `link_symptom` |
| 3 | R10–R24 | Evidencia → `diagnosis` (8 hipoteses) |
| 3b | R25–R27 | **Contra-evidencia** (CF negativo) |
| 4 | R28–R35 | `diagnosis` → `recommended_action` |
| 5 | R36–R43 | `recommended_action` → `authorization_required` |

> **Por que estratificar?** As regras de diagnostico nunca leem `rssi_dbm` direto, so `signal_quality`.
> Trocar o sensor de RF muda a camada 1 e **nada mais**. Isso e modularidade do conhecimento, e e uma das
> vantagens praticas de regras sobre codigo procedural.

Mostre uma regra de cada tipo (celula 1.1 do notebook), incluindo a justificativa em linguagem natural que
cada regra carrega — e ela que aparece depois na explicacao.

**Fale das variaveis perguntaveis e nao perguntaveis.** `signal_quality` nunca e perguntada: e sempre
derivada. `rssi_dbm` e sempre perguntada ou medida. A validacao estatica da base rejeita variaveis que nao
sao nem perguntaveis nem concluiveis — becos sem saida.

### 10:00–16:00 — Encadeamento progressivo, ao vivo

```bash
aisg diagnose --case interference --trace --explain
```

1. **Ciclo reconhecer-agir.** O motor monta o conjunto de conflito, resolve o conflito e dispara **uma**
   regra por ciclo. Uma, e nao todas, para que a ordem do raciocinio fique visivel — e para que a
   resolucao de conflito tenha efeito observavel.
2. Percorra o trace regra a regra: R01 conclui sinal ruim, R10 conclui interferencia, R28 recomenda mudar
   de canal, R36 exige autorizacao. A cadeia inteira e legivel.
3. Este e o modo **alarme de monitoramento**: chega telemetria, o sistema conclui sozinho.

### 16:00–21:00 — Fatores de certeza

Faca a aritmetica no quadro, nao so no slide:

```
CF da premissa   = minimo entre as condicoes        (o elo mais fraco)
CF da conclusao  = CF da premissa x CF da regra
disparo          = so acima do limiar 0,2           (evidencia fraca nao se propaga)

combinacao de duas conclusoes independentes sobre o mesmo fato:
   ambos >= 0:      cf1 + cf2 * (1 - cf1)
   ambos <= 0:      cf1 + cf2 * (1 + cf1)
   sinais opostos:  (cf1 + cf2) / (1 - min(|cf1|, |cf2|))
```

> Duas evidencias de 0,8 dao **0,96** — mais forte que qualquer uma isolada, e ainda assim longe da
> certeza. Evidencias contraditorias de +0,8 e -0,8 se cancelam exatamente em zero.

**A contra-evidencia e o ponto alto.** Na saida do caso de interferencia, `rain_fade` aparece com CF
**negativo**: tempo limpo e evidencia *contra* atenuacao por chuva (R25).

> Regras puramente booleanas obrigariam a escolher entre ignorar a evidencia e afirmar demais. O fator de
> certeza permite dizer "isto torna a hipotese menos provavel" — que e o que um especialista realmente faz.

Mostre tambem o caso `rain_fade`, que conclui com CF 0,56: o sistema **admite** que a evidencia e fraca em
vez de fingir confianca.

### 21:00–26:00 — Encadeamento regressivo e explicacao

```bash
aisg diagnose --interactive --mode backward
```

Responda `down`, depois `failed`; numa das perguntas, digite `?` para mostrar o **`por que`**.

> Este e o modo **engenheiro as duas da manha** — e o modo do Expert SINTA. Pergunta so o que o objetivo
> exige. Duas propriedades encurtam a consulta:
>
> 1. **Curto-circuito:** assim que uma condicao e falsa, a regra e abandonada e as condicoes restantes
>    **nao sao perguntadas**.
> 2. **Corte por suficiencia:** quando o objetivo atinge CF 0,9, o motor para de buscar mais apoio.
>
> O caso de falha de energia conclui perguntando **6 das 13** variaveis.

Feche com o **`como`** (`--explain`): a explicacao recursiva desce das conclusoes ate os fatos informados
pelo usuario, citando a regra e a justificativa em cada nivel.

> Um sistema que so responde nao e utilizavel em operacao critica. Um que **mostra o caminho** pode ser
> auditado, contestado e corrigido.

### 26:00–30:00 — Resolucao de conflito, validacao e limites

```bash
aisg diagnose --case interference --strategy recency --trace
```

> Quando varias regras estao prontas, qual dispara primeiro? Tres politicas: primeira correspondencia,
> especificidade (mais condicoes primeiro) e recencia (fatos mais novos primeiro). A politica muda a
> **ordem do raciocinio**, nao o ponto fixo — e ha teste para **as duas metades** dessa afirmacao: que a
> ordem difere e que o diagnostico nao.

Feche pelos limites:

> Os limiares sao **nominais e nao calibrados**, reunidos num unico bloco para que a calibracao futura
> ajuste valores **sem reescrever regras**. O sistema **recomenda, nao atua**.

---

# TEMA 2 — Geracao automatica de planos (30 min)

### 0:00–3:00 — O problema

O sistema especialista diagnosticou e recomendou. **Em que sequencia executar?** Uma equipe nao realinha
uma antena antes de chegar ao local, e nada toca a planta antes da autorizacao.

Objetivo: `service-restored(N)` **e** `logged(N)` — a evidencia faz parte do objetivo, nao e um extra.

### 3:00–9:00 — STRIPS: a representacao

```
change_channel(?n)
  precondicoes:  authorized(?n), interference(?n)
  adiciona:      fault-cleared(?n)
  remove:        interference(?n)
  custo:         2
```

Explique os tres conjuntos e a **hipotese do mundo fechado**: o estado e o conjunto de literais
verdadeiros; o que nao esta la e falso. Percorra a tabela dos doze operadores, destacando as colunas de
custo e de "exige equipe no local".

> **O custo de `dispatch_crew` (4) faz o planejamento importar.** Se toda acao custasse 1, planejar seria
> contar passos. Com deslocamento a 4 e troca de fonte a 5, o planejador precisa pesar de verdade: uma
> correcao remota barata pode vencer uma correcao local aparentemente mais simples.

**Governanca como precondicao, nao como recomendacao:**

> Todo operador que alcanca a planta exige `authorized(?n)`. Isso torna "agimos sem autorizacao" um estado
> **inalcancavel**, e nao apenas desaconselhado. Ha teste da invariante para todos os diagnosticos. A unica
> excecao e `monitor_and_wait`, porque observar nao altera a planta.

### 9:00–16:00 — GPS: analise meios-fins

```bash
aisg plan --diagnosis node_power_failure --node RM_A5 --solver gps --trace
```

O algoritmo em quatro passos:

1. olhe a **diferenca** entre o estado atual e o objetivo;
2. escolha um operador que a **reduza** (o objetivo esta na sua lista de adicao);
3. **recursivamente**, satisfaca as precondicoes desse operador;
4. aplique o operador.

Percorra o trace com o dedo na tela: `DIFERENCA a reduzir: service-restored(RM_A5)` → candidato
`close_work_order` → suas precondicoes viram novas diferencas → e assim por diante ate `crew-at(BASE)`,
que ja e verdade.

> **Toda acao existe para eliminar uma diferenca concreta.** E por isso que o trace do GPS se le como uma
> **justificativa**, e nao como um log de busca. Essa e a contribuicao conceitual de Newell e Simon:
> o programa nao so resolve, ele exibe o raciocinio no vocabulario de quem resolve.

### 16:00–20:00 — As limitacoes do GPS, ditas por voce antes de perguntarem

> O GPS **nao e completo nem otimo**. Ele adota o primeiro operador que reduz a diferenca e so revisa por
> retrocesso, em caso de falha.

**Anomalia de Sussman.** Com subobjetivos que interagem, atingi-los um a um pode desfazer trabalho ja
feito. Nossa defesa minima: apos satisfazer todos os subobjetivos, o planejador **reverifica** se algum foi
desfeito e, se foi, falha explicitamente em vez de devolver um plano invalido.

**Nao-otimalidade, demonstrada ao vivo** (celula 2.5 do notebook):

> O GPS ordena os operadores relevantes pelo custo **proprio**, sem olhar o custo das **precondicoes**.
> Se a acao barata custa 1 mas exige um deslocamento de 10, e existe uma correcao remota de 3, o GPS
> devolve o plano de custo **11**; o A* encontra o de custo **3**.

E por isso que os dois planejadores convivem no mesmo repositorio.

### 20:00–26:00 — Planejamento progressivo por A*

| Busca | Planejamento |
|---|---|
| estado | conjunto de literais verdadeiros |
| sucessor | qualquer acao aplicavel |
| custo do passo | custo da acao |
| teste de objetivo | o objetivo esta contido no estado |

> Com esse mapeamento, **a mesma funcao `astar`** do tema 3 resolve o planejamento. Nao e uma copia
> adaptada: e a mesma funcao, importada. Uma implementacao, dois espacos de estados.

**A heuristica `goal_count`** conta literais do objetivo ainda nao satisfeitos. Diga a condicao em voz
alta:

> Ela e admissivel **apenas se** nenhuma acao satisfizer mais de um literal do objetivo e toda acao custar
> ao menos 1. Neste dominio a condicao vale — `service-restored` e `logged` vem de operadores diferentes,
> cada um de custo unitario. **Declaramos a condicao em vez de supo-la**: uma heuristica inadmissivel
> custaria a otimalidade em silencio.

```bash
aisg plan --diagnosis node_power_failure --node RM_A5 --solver both
```

### 26:00–30:00 — Validacao e o contraste elegante

**Validacao.** `Plan.validate()` reexecuta o plano desde o estado inicial e aponta o primeiro passo
inaplicavel com a precondicao que faltou. Dois testes corrompem planos de proposito — um remove a
autorizacao, outro remove o fechamento — para provar que a validacao pega os dois defeitos.

**O contraste elegante:**

```bash
aisg plan --diagnosis rain_fade --node RM_A5 --solver astar
```

> O plano correto para atenuacao por chuva **nao toca a planta e nao desloca equipe**. A causa e
> transitoria; intervir seria tratar o clima. O sistema sabe **quando nao agir** — e isso e tao
> importante quanto saber agir.

Mostre a tabela dos oito diagnosticos (celula 2.4) e feche com a integracao: `reroute_traffic` exige
`alternate-route`, e esse literal so entra no estado inicial quando **a busca A* confirma** que a rota
existe. Sem rota, a acao fica inaplicavel e o planejador **falha honestamente**.

---

# TEMA 3 — Busca A* (30 min)

### 0:00–3:00 — O problema

Qual o caminho de **menor custo de transporte** entre dois nos? O requisito da disciplina e explicito: o
programa deve retornar **o caminho exato** entre o estado inicial e o estado objetivo.

Mostre a figura da topologia (celula 3.1) e o modelo de custo:

```
custo(u, v) = sobrecarga(tipo) + distancia(u, v) / (velocidade(tipo) * qualidade)
```

> A `velocidade` e uma **velocidade efetiva de transporte**, nao uma velocidade fisica de propagacao: e
> uma abstracao que reune serializacao, enfileiramento e modulacao mais robusta em saltos longos. Um
> repetidor armazena-e-encaminha **termina e retransmite** o quadro — por isso paga sobrecarga de 25 ms
> contra 0,5 ms da fibra.

### 3:00–8:00 — O algoritmo

```
f(n) = g(n) + h(n)
```

> As duas metades importam. So `g` da o custo uniforme: otimo, porem cego. So `h` da a busca gulosa:
> rapida, porem sem garantia. O A* e a combinacao — e a tabela daqui a pouco mostra exatamente isso.

Tres detalhes de implementacao que valem ser ditos, porque separam um A* de brinquedo de um A* correto:

1. **Desempate.** Empates em `f` sao resolvidos preferindo o maior `g`, depois a ordem de insercao. As
   execucoes ficam reproduzíveis — importante numa apresentacao.
2. **Reabertura.** Um estado fechado e reaberto se surgir caminho mais barato. Com heuristica consistente
   isso nunca acontece, mas tratamos o caso geral em vez de **supor** a consistencia.
3. **Custos negativos** sao recusados com erro explicito: o A* nao os admite.

### 8:00–14:00 — A heuristica e as duas provas

```
h(n) = distancia_em_linha_reta(n, objetivo) / VELOCIDADE_MAXIMA      (150 m/ms, a fibra)
```

**Admissibilidade.** Como `sobrecarga >= 0`, `qualidade <= 1` e `velocidade(tipo) <= VELOCIDADE_MAXIMA`:

```
custo(u, v) >= d(u, v) / VELOCIDADE_MAXIMA
```

Somando ao longo de qualquer caminho de `n` ate o objetivo, o custo total e ao menos a distancia total
percorrida dividida pela velocidade maxima. Pela **desigualdade triangular**, a distancia percorrida e ao
menos a distancia em linha reta. Logo `h` nunca superestima. ∎

**Consistencia.** `d(u, objetivo) <= d(u, v) + d(v, objetivo)`; dividindo pela velocidade maxima:

```
h(u) <= custo(u, v) + h(v)     ∎
```

A consistencia implica a admissibilidade e garante que nenhum no precise ser reaberto.

> **Isto nao e acidente.** O modelo de custo foi **projetado** para que a prova se sustente: as distancias
> sao derivadas das coordenadas, nunca armazenadas em separado, de modo que geometria e heuristica **nao
> podem** divergir.

### 14:00–19:00 — Verificado, nao apenas argumentado

Rode as celulas 3.3 do notebook:

> Nao paramos no argumento. Dois testes verificam as duas propriedades **exaustivamente**: admissibilidade
> para todos os 272 pares origem-objetivo, contra o custo otimo obtido por busca de custo uniforme, e
> consistencia para todas as arestas e todos os objetivos. Zero violacoes.

Mostre tambem a razao `h/otimo` mais alta: quanto mais perto de 1, mais informativa a heuristica.

### 19:00–25:00 — Comparacao entre as estrategias

```bash
aisg route --from NOC --to RECLOSER_7 --compare --expansion
```

| Estrategia | Passos | Custo (ms) | Expandidos | Otimo? |
|---|---|---|---|---|
| Largura | 4 | 357,35 | 15 | so em passos |
| Profundidade | 5 | 343,06 | 19 | nao |
| Custo uniforme | 4 | **92,22** | 13 | **sim** |
| Gulosa | 4 | 357,35 | **5** | nao |
| **A\*** | 4 | **92,22** | 11 | **sim** |

**As tres licoes — o centro do tema:**

1. **A busca em largura minimiza saltos, nao custo.** Quatro saltos por 357 ms, quase 4x o otimo, porque
   conta um salto de fibra e um salto de radio armazena-e-encaminha como iguais.
2. **A gulosa e a mais rapida e esta errada.** Cinco expansoes contra onze — e um caminho 3,9x mais caro.
   E o argumento mais direto a favor do termo `g(n)`.
3. **O A\* alcanca o mesmo otimo do custo uniforme expandindo menos nos.** A heuristica **nao muda a
   resposta**; muda o trabalho necessario para chegar a ela.

Mostre a figura com o caminho em vermelho e os nos expandidos circulados (celula 3.2), e depois o
detalhamento salto a salto: o caminho otimo **evita inteiramente** a cadeia armazena-e-encaminha e desce
pela sobreposicao LTE.

### 25:00–30:00 — Falha, recalculo e integracao

```bash
aisg route --from NOC --to RECLOSER_7 --disable-link LTE_ENB-RM_A5
```

> Sem a sobreposicao LTE, o custo otimo sobe e o caminho passa a usar a cadeia armazena-e-encaminha. E
> assim que a integracao com o planejador funciona: quando o plano inclui desviar trafego, a rota e
> recalculada evitando o no afetado.

Feche com o pipeline completo:

```bash
aisg pipeline --case congestion --node SAF_A2
```

> Um comando: o sistema especialista diagnostica congestionamento; o diagnostico vira o estado inicial do
> planejador; o planejador so pode propor desvio porque a busca A* **confirmou** que existe rota
> alternativa; e o plano sai com autorizacao, verificacao e registro.

E encerre pelos limites, nao pelos resultados:

> Limiares nominais e nao calibrados. Nenhum dado rotulado de falha. O sistema recomenda, nao atua. A
> topologia e sintetica: uma conclusao obtida aqui vale para **este modelo**, nao para uma planta fisica.

---

## Perguntas provaveis — respostas curtas

| Pergunta | Resposta |
|---|---|
| Por que nao usou aprendizado de maquina? | Nao ha dados rotulados de falha, e nao ha como produzi-los sem instrumento de degradacao controlada. Um modelo treinado so em estado normal nao infere degradacao. |
| Como o sistema escolhe entre regras concorrentes? | Tres politicas de resolucao de conflito, selecionaveis; a padrao e especificidade. A politica muda a ordem, nao a conclusao — e ha teste para as duas coisas. |
| A heuristica e admissivel? | Sim, com prova por desigualdade triangular sobre o modelo de custo, e verificacao exaustiva em teste para todos os pares. |
| O GPS sempre acha o melhor plano? | Nao. Nao e completo nem otimo, e sofre a anomalia de Sussman. Ha um teste que exibe um caso concreto de nao-otimalidade. Por isso o A* progressivo esta ao lado. |
| Qual banco de dados? | Nenhum. Topologia em JSON versionado, regras declaradas em codigo, memoria de trabalho em RAM. Persistencia so faria sentido para raciocinio baseado em casos. |
| E se nao houver rota alternativa? | A acao de desvio fica inaplicavel e o planejador falha honestamente, em vez de propor um desvio impossivel. Ha teste. |
| Por que os fatores de certeza e nao probabilidade bayesiana? | Fatores de certeza nao exigem probabilidades a priori nem independencia condicional — que nao temos como estimar sem dados. E o mesmo compromisso do MYCIN, e a mesma limitacao: a algebra e heuristica, nao probabilisticamente fundamentada. |
| Os limiares vieram de onde? | De faixas de folha de dados de radio sub-GHz e pratica comum de telecom de concessionaria. Sao **nominais**, ponto de partida para calibracao, nao valores medidos. |

---

## English (condensed)

Three topics, **30 minutes each**.

**Topic 1 — Expert system.** Domain and the method choice (no labelled fault data exists, so encode
auditable engineering knowledge) → knowledge representation in five layers and why stratification matters
→ live forward chaining with the recognise-act cycle → certainty-factor arithmetic worked on the board,
including negative CFs as counter-evidence → backward chaining live with `why` and `how` → conflict
resolution changing order but not the fixed point → validity limits.

**Topic 2 — Planning.** The sequencing problem → STRIPS triples and the closed-world assumption, with
governance as a *precondition* rather than advice → GPS means-ends analysis walked through its trace
(every action removes a concrete difference) → GPS's limitations stated before anyone asks: incompleteness,
the Sussman anomaly, and a live non-optimality demonstration → planning as search, reusing the *same* A*
function, with the admissibility condition of `goal_count` stated rather than assumed → plan validation and
the rain-fade contrast, where the correct plan touches nothing.

**Topic 3 — A\*.** The exact-path requirement and the cost model → `f = g + h` with the three
implementation details that separate a toy A* from a correct one → the admissibility and consistency
proofs → their exhaustive verification over all 272 pairs and every edge → the five-strategy comparison
table and its three lessons → link failure forcing a re-route, then the full pipeline, closing on
validity limits.
