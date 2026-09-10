"""
Content of the 90-minute deck: three topics of 30 minutes.

Slide text is in Portuguese with full orthography. The repository's source files
avoid accented characters for terminal-encoding reasons; that rationale does not
apply to a deck rendered by PowerPoint, and in Portuguese the accent carries
meaning - "e" and "é" are different words.

The detailed argument sits in the speaker notes rather than on the slide.
"""

from __future__ import annotations

from build_deck import AMBER, ASSETS, BLUE, GREEN, RED, Deck


def build_slides(d: Deck) -> None:
    # ======================================================================
    # ABERTURA — 5 min
    # ======================================================================
    d.title_slide(
        ASSETS / "banner-dark.png",
        "Sistema especialista · Planejamento automático · Busca A*",
        "Fernando Sabino Dantas  ·  Introdução à Inteligência Artificial  ·  2026",
        """Abertura. Não comece pelo código: comece pelo domínio e pela escolha do
método. Os três trabalhos partilham um único domínio, e isso é proposital —
permite mostrar que os sistemas se integram, em vez de apenas coexistirem.

Antes de começar, deixe rodando "python -m pytest": 155 testes verdes na tela
são um bom cartão de visita.""",
    )

    d.bullets(
        "Os três trabalhos, um único domínio",
        [
            "Sistema especialista: 43 regras, encadeamento nos dois sentidos, fatores de certeza",
            "Geração automática de planos: STRIPS, resolvido por GPS e por A* progressivo",
            "Busca A*: caminho exato, com prova de admissibilidade",
            "Domínio comum: o cenário SIMULADO em ns-3 — 30 nós, três setores",
            ("Os três se integram: o diagnóstico vira o estado inicial do plano, e o plano consulta a busca", 1),
        ],
        """Diga o roteiro: 30 minutos por tema, com demonstração ao vivo em cada um.

O ponto a plantar já aqui: os três não são exercícios separados. O diagnóstico
produzido pelo trabalho 1 é a entrada do trabalho 2, e o trabalho 2 chama a
função do trabalho 3. Ao final voltaremos a isso com um comando só.

Em cerca de 20 segundos, explique a avaliação: requisitos, correção e evidência
reproduzível; pesos propostos 30/30/25/15, ainda sem endosso docente registrado.
O exemplo principal usa um diagnóstico selecionado por nó. Falhas simultâneas
são uma extensão avaliada separadamente. Consulte docs/assessment-protocol.md
e os dois slides de apêndice, ocultos para preservar os 90 minutos autorizados.""",
        accent=BLUE,
    )

    d.figure(
        "O domínio: o cenário simulado (ns-3)",
        ASSETS / "05-simulated-30-light.png",
        """O cenário: 30 nós sem fio em três setores, cada um com estrela de rádio de
900 MHz e uma cadeia armazena-e-encaminha até um dispositivo de campo, sobre um
núcleo em fibra e uma sobreposição LTE.

Duas coisas a dizer antes que perguntem, porque as duas seriam perguntadas:

A topologia é SINTÉTICA — não contém inventário, endereçamento nem identificação
de equipamento de laboratório algum.

E isto é um MODELO de topologia, não saída de simulação. Nenhuma execução
produziu estes números: o cenário ns-3 para esta banda ainda não está construído,
porque o ns-3.48 de estoque não sintetiza espectro em 902-928 MHz com lr-wpan.
Dizer isso é mais forte do que deixar alguém descobrir.""",
        accent=BLUE,
        caption="Modelo de topologia — 30 nós, três setores. Nao e saida de simulacao.",
    )

    d.statement(
        "Como recomendar diagnóstico e ação sem dados rotulados de falha?",
        "De forma auditável, e sob restrições explícitas de autorização — numa rede "
        "de comunicação de sistema elétrico.",
        """A pergunta de pesquisa. Enuncie-a e deixe-a no ar por um instante antes de
seguir.

Ela tem três qualificadores, e cada um é uma restrição real, não retórica:

"sem dados rotulados de falha" — não há conjunto rotulado neste domínio, e não há
como produzi-lo sem instrumento de degradação controlada. Isso elimina a via
indutiva para o diagnóstico.

"de forma auditável" — em operação crítica, uma recomendação que não pode ser
justificada não é utilizável. Toda conclusão precisa apontar para a regra e o
fato que a sustentam.

"sob restrições explícitas de autorização" — nada pode alcançar a planta sem
janela, autorização e operador responsável.

A pergunta decompõe-se em três, uma por trabalho:
  1. Por que o enlace degradou, e com que confiança?      -> sistema especialista
  2. Em que sequência agir, respeitando as restrições?    -> planejamento STRIPS/GPS
  3. Existe caminho alternativo, e qual o de menor custo? -> busca A*

Diga isso: os três trabalhos não foram escolhidos por serem os temas da
disciplina — eles são as três partes de uma pergunta só.""",
        accent=BLUE, kicker="PERGUNTA DE PESQUISA",
    )

    d.table(
        "Antes dos KPIs: o que cada grandeza significa",
        ["Grandeza", "Em linguagem simples", "Quando piora"],
        [
            ["RSSI (dBm)", "Quão FORTE o sinal chega", "o receptor mal escuta o transmissor"],
            ["SNR (dB)", "Quão LIMPO o sinal chega, acima do ruído",
             "o sinal existe, mas o ruído o encobre"],
            ["Perda de percurso (dB)", "Quanto o sinal enfraquece no caminho",
             "distância, obstáculo ou atenuação comandada"],
            ["Retransmissão MAC (%)", "Quantas vezes é preciso repetir o envio",
             "vários rádios falam ao mesmo tempo e colidem"],
            ["Perda de pacotes (%)", "Quanta informação não chega", "consequência, não causa"],
            ["Atraso / RTT (ms)", "Quanto tempo a informação leva para ir e voltar",
             "fila cheia, ou caminho longo"],
            ["Carga oferecida (%)", "Quanto se pede do enlace, em relação ao que ele aguenta",
             "acima de 100 % pede-se mais do que existe"],
        ],
        """Este slide existe porque nem todos na sala são engenheiros de redes, e sem
ele os próximos vinte minutos viram vocabulário.

Use uma analogia só, e mantenha-a: uma conversa numa sala.

RSSI é o VOLUME da voz que chega. SNR é quanto essa voz se destaca do barulho de
fundo — dá para ter volume alto e ainda assim não entender nada, se o barulho for
maior. Perda de percurso é o quanto a voz enfraquece pela distância ou por uma
parede no meio.

Retransmissão é quantas vezes você precisa REPETIR a frase — e é a grandeza que
distingue as duas situações que mais se confundem: se você repete muito mas sua
voz chega alta e limpa, o problema não é a voz, é que várias pessoas falam ao
mesmo tempo.

Perda de pacotes e atraso são CONSEQUÊNCIAS: a informação não chegou, ou demorou.
Elas dizem que algo está errado, nunca o quê. É por isso que o sistema precisa
das três primeiras para diagnosticar, e não só destas duas.

Carga oferecida é quanto se está pedindo do enlace. Acima de 100 % pede-se mais
do que ele comporta — e a fila cresce por definição, não por defeito.""",
        accent=BLUE, widths=[3.0, 5.2, 4.4],
    )

    d.two_up(
        "Como isto é medido: dois níveis de KPI",
        "KPIs do domínio — a entrada", [
            "PHY: RSSI (dBm), SNR (dB), perda de percurso comandada (dB)",
            "MAC: taxa de retransmissão (%) — o discriminador",
            "Fluxo: perda (%), atraso (ms), carga oferecida (%)",
            "Custo de transporte (ms) — derivado, alimenta a busca",
            "⚠ Limiares NOMINAIS e NÃO calibrados",
        ],
        "KPIs de avaliação — o veredito", [
            "Diagnóstico: fator de certeza (CF) da conclusão",
            "Plano: custo total, e validade (executável + atinge o objetivo)",
            "Busca: nós expandidos, custo do caminho, otimalidade",
            "Transversal: 155 testes; admissibilidade verificada em todos os pares",
        ],
        """Distinga os dois níveis com clareza — eles respondem a perguntas diferentes.

Os KPIs do DOMÍNIO são as grandezas que o simulador realmente produz: PHY pelo
espectro, MAC pelo contador de retransmissão, e fluxo pelo FlowMonitor.

Destaque a taxa de retransmissão do MAC. Sem ela, perda por meio disputado e
perda por sinal fraco parecem idênticas no nível de fluxo — as duas aparecem como
perda. A retransmissão é o que separa um meio ocupado de um sinal fraco, e é uma
grandeza que só existe em rede sem fio.

Os KPIs de AVALIAÇÃO são como julgamos se os sistemas funcionam. Note que cada
trabalho tem um critério próprio e verificável: o fator de certeza diz quanta
confiança há na conclusão; a validade do plano é reexecutada desde o estado
inicial; a otimalidade da busca é comparada contra custo uniforme, que não usa
heurística e serve de verdade de referência.

O aviso da coluna esquerda é o que mantém a apresentação honesta: os limiares do
domínio vieram de faixas de folha de dados e de prática comum de telecom. São
ponto de partida para calibração, não valores medidos numa instalação. Por isso
estão reunidos num único bloco, prontos para serem ajustados quando existir linha
de base medida.

Em resumo: os KPIs de avaliação estão verificados; os do domínio estão
declarados, e declarados como não calibrados.""",
        accent=BLUE, left_colour=AMBER, right_colour=GREEN,
    )

    d.statement(
        "Por que o DIAGNÓSTICO não é aprendido?",
        "No simulador os rótulos são gratuitos. O problema não é o rótulo — é o que "
        "o modelo aprenderia.",
        """Este argumento mudou quando o cenário passou a ser simulado, e a versão
nova é mais interessante. Não repita a antiga.

No simulador, o operador COMANDA a condição: sobe a perda de percurso, injeta um
emissor, para um nó. Portanto conhece o rótulo por construção, e pode repetir a
execução quantas vezes quiser. Rótulos não faltam — são gratuitos e ilimitados.

O problema é outro: um modelo treinado assim aprende O SIMULADOR, não a planta.
O MAC simulado é CSMA-CA do 802.15.4; o rádio real usa o MAC proprietário do
fabricante. Um classificador treinado nos rótulos do simulador aprenderia a
assinatura do modelo — e não há evidência de que ela transfira.

O sistema especialista faz o inverso: codifica conhecimento de engenharia que
vale para a planta, e que pode ser contestado regra a regra. Onde há rótulos, a
indução é possível; onde eles não representam o alvo, ela é apenas confiante.

Para a rede de CAMPO o argumento antigo continua valendo, e por isso a segunda
base de conhecimento existe: lá não há rótulo algum.""",
        accent=RED,
    )

    d.two_up(
        "Dedutivo × indutivo: a escolha depende do que existe",
        "Dedutivo (regras)", [
            "Conhecimento vem do especialista",
            "Não exige dados históricos",
            "Auditável regra a regra",
            "Contestável: discute-se uma regra",
            "Falha por omissão — sem conclusão",
        ],
        "Indutivo (aprendizagem)", [
            "Conhecimento vem de exemplos rotulados",
            "Exige dados históricos",
            "Auditabilidade variável",
            "Difícil discutir um peso",
            "Falha em silêncio — conclusão errada e confiante",
        ],
        """Nenhuma das colunas é superior em abstrato. A escolha depende do que se tem.

Onde não há dados rotulados, o caminho honesto é codificar conhecimento de
engenharia em regras explícitas. A vantagem não é só de disponibilidade: um
especialista pode discordar da regra R14 e mudar apenas ela. Não se discute
assim com um peso de rede neural.

Se perguntarem "e quando houver dados?", a resposta está na próxima decisão de
projeto: os limiares estão num único bloco, prontos para calibração.""",
        accent=RED, left_colour=BLUE, right_colour=AMBER,
    )

    # ======================================================================
    # TEMA 1 — SISTEMA ESPECIALISTA — 30 min
    # ======================================================================
    d.section("TEMA 1", "Sistema especialista",
              "Regras de produção, encadeamento progressivo e regressivo, fatores de certeza",
              BLUE, "30 minutos",
              """Transição: sabemos por que é simbólico. Agora, como se constrói.""")

    d.bullets(
        "O problema",
        [
            "Um enlace do backhaul degradou ou caiu",
            "Duas perguntas: por quê? e o que fazer?",
            "Oito hipóteses concorrentes de diagnóstico",
            "A resposta precisa vir com um grau de confiança, não como certeza absoluta",
        ],
        """Enquadre como um problema de classificação com evidência incerta. Sensores
são imperfeitos, dados são incompletos, fenômenos variam.

Guarde a última linha: "recomenda, não atua". Voltaremos a ela no tema 2, onde
ela deixa de ser um princípio e vira uma precondição.""",
        accent=BLUE,
    )

    d.bullets(
        "Arquitetura de um sistema especialista",
        [
            "Base de conhecimento — fatos, regras, heurísticas do domínio",
            "Memória de trabalho — fatos do problema em curso",
            "Motor de inferência — aplica as regras e conclui",
            "Módulo de explicação — justifica as conclusões",
            "Interface — entrada de dados e consulta",
            ("A separação entre conhecimento e inferência é a característica definidora", 1),
        ],
        """Insista na separação entre base de conhecimento e motor de inferência: é ela
que permite trocar o conhecimento sem reescrever o raciocínio.

No repositório essa separação é real, não nominal: o motor não sabe nada sobre
redes. Se ele funciona aqui, funciona em qualquer domínio que se escreva em
regras — e essa é a condição para reutilizá-lo como fonte de conhecimento no
trabalho multiespecialista de 25/09.""",
        accent=BLUE,
    )

    d.table(
        "As variáveis observáveis — o que o simulador produz",
        ["Variável", "Nível", "Domínio"],
        [
            ["rssi_dbm", "PHY", "[-120, -30] dBm"],
            ["snr_db", "PHY", "[-5, 40] dB"],
            ["excess_path_loss_db", "PHY (comandado)", "[0, 80] dB"],
            ["retry_rate_pct", "MAC", "[0, 100] %  <- o discriminador"],
            ["packet_loss_pct", "fluxo", "[0, 100] %"],
            ["rtt_ms", "fluxo", "[0, 5000] ms"],
            ["offered_load_pct", "fluxo", "[0, 200] %"],
            ["node_responding", "cenário", "yes | no"],
            ["upstream_relay_reachable", "cenário", "yes | no"],
            ["route_present", "cenário", "yes | no"],
            ["co_channel_emitter", "cenário", "yes | no"],
            ["nodes_sharing_channel", "cenário", "few | many"],
            ["neighbours_affected", "cenário", "none | one | many"],
        ],
        """Treze variáveis em três níveis: PHY pelo espectro, MAC pelo contador de
retransmissão, fluxo pelo FlowMonitor. Não leia a tabela — aponte a estrutura.

A linha a destacar é retry_rate_pct. É o único valor que separa "o meio está
disputado" de "o sinal está fraco": no nível de fluxo as duas causas produzem
perda e ficam indistinguíveis. E é uma grandeza que só existe porque a rede é
sem fio e o meio é compartilhado.

Note também excess_path_loss_db: no simulador a perda de percurso é COMANDADA,
não observada — é isso que torna a condição repetível, e rotulável.""",
        accent=BLUE, widths=[4, 2, 4],
    )

    d.figure(
        "As 41 regras em cinco camadas",
        ASSETS / "02-expert-system-light.png",
        """A figura é a base simulada, S01 a S42 — as mesmas regras que rodaram nas
demonstrações desta apresentação.

Percorra as camadas de baixo para cima: medição vira qualidade de sinal,
estado e desempenho viram sintoma, evidência vira diagnóstico, diagnóstico vira
ação, ação vira exigência de autorização.

A pergunta a fazer em voz alta: por que estratificar? Porque as regras de
diagnóstico nunca leem rssi_dbm diretamente — leem signal_quality. Trocar o
sensor de RF muda a camada 1 e nada mais. Isso é modularidade do conhecimento, e
é uma vantagem prática de regras sobre código procedural.""",
        accent=BLUE,
        caption="A camada 3b traz contra-evidência: regras com fator de certeza negativo.",
    )

    d.code(
        "Três regras, três papéis",
        [
            "S14:  SE  retransmissão_MAC > 30 %",
            "      E   qualidade_do_sinal != poor",
            "      E   emissor_co_canal = no",
            "      ENTÃO diagnóstico = mac_contention           (CF +0,85)",
            "      <- perda COM sinal saudável: o meio está disputado",
            "",
            "S25:  SE  retransmissão_MAC <= 30 %",
            "      ENTÃO diagnóstico = mac_contention           (CF -0,80)",
            "      <- contra-evidência: torna a hipótese MENOS provável",
            "",
            "S37:  SE  ação_recomendada = separate_channels",
            "      ENTÃO exige_autorização = yes                (CF +1,00)",
        ],
        """S14 é a regra mais própria deste domínio: perda alta COM sinal saudável e sem
emissor concorrente não é propagação — é disputa pelo meio. Num enlace com fio
essa hipótese não existiria; é o CSMA-CA que a cria.

S25 é a contra-evidência. O fator de certeza negativo diz "retransmissão baixa é
evidência CONTRA contenção". Regras booleanas obrigariam a escolher entre ignorar
essa evidência e afirmar demais. O especialista real raciocina assim: certas
observações reduzem a suspeita sem eliminá-la.

S37 é a porta de governança, e prepara o tema 2: alterar o cenário durante uma
campanha invalida a execução, portanto exige janela autorizada.""",
        accent=BLUE,
    )

    d.code(
        "Fatores de certeza: a álgebra do MYCIN",
        [
            "CF está em [-1, +1]:  +1 confirmado   -1 refutado   0 sem evidência",
            "",
            "CF da premissa    = MÍNIMO entre as condições      (o elo mais fraco)",
            "CF da conclusão   = CF da premissa  ×  CF da regra",
            "disparo           = só acima do limiar 0,2",
            "",
            "combinação de duas conclusões independentes:",
            "   ambos >= 0        cf1 + cf2 × (1 - cf1)",
            "   ambos <= 0        cf1 + cf2 × (1 + cf1)",
            "   sinais opostos    (cf1 + cf2) / (1 - min(|cf1|, |cf2|))",
        ],
        """Faça a aritmética no quadro, não só no slide.

Duas evidências de 0,8 dão 0,96: mais forte que qualquer uma isolada, e ainda
assim longe da certeza. Evidências contraditórias de +0,8 e -0,8 cancelam-se
exatamente em zero.

Se perguntarem por que não probabilidade bayesiana: fatores de certeza não
exigem probabilidades a priori nem independência condicional — que, sem dados,
não há como estimar. O preço é que a álgebra é heurística, não
probabilisticamente fundamentada. É o mesmo compromisso do MYCIN, e a mesma
limitação. Diga a limitação; ela fortalece a apresentação, não a enfraquece.""",
        accent=BLUE,
        caption="O mínimo modela o elo mais fraco: uma premissa não é mais forte que sua condição mais fraca.",
    )

    d.bullets(
        "Encadeamento progressivo — dirigido por dados",
        [
            "Parte dos fatos e deriva tudo o que puder",
            "Ciclo reconhecer-agir: monta o conjunto de conflito, resolve, dispara",
            "Uma regra por ciclo — e não todas",
            ("assim a ordem do raciocínio fica visível no trace, e a resolução de conflito tem efeito observável", 1),
            "É o modo alarme de monitoramento: chega telemetria, o sistema conclui",
        ],
        """Explique por que disparar uma regra por ciclo e não todas de uma vez: se o
motor disparasse tudo simultaneamente, a resolução de conflito não teria efeito
observável e o trace não contaria uma história.

Este é o modo em que o sistema seria acoplado a um sistema de monitoramento
real: a telemetria chega, o motor conclui sozinho.""",
        accent=BLUE,
    )

    d.code(
        "Demonstração: encadeamento progressivo",
        [
            "$ aisg diagnose --kb simulated --case mac_contention --trace --explain",
            "",
            "* S04: premissa CF +1,00 × regra CF +0,90 => signal_quality = good",
            "* S14: premissa CF +1,00 × regra CF +0,85 => diagnosis = mac_contention",
            "* S29: premissa CF +0,94 × regra CF +0,85 => ação = separate_channels",
            "* S37: premissa CF +0,80 × regra CF +1,00 => autorização = yes",
            "",
            "diagnóstico:",
            "  mac_contention         CF +0,94  ###################",
            "  excess_path_loss       CF -0,85  -#################",
        ],
        """Rode ao vivo. Percorra o trace regra a regra com o dedo na tela: a cadeia
inteira é legível, da medição até a exigência de autorização.

Aponte a última linha: excess_path_loss aparece com CF NEGATIVO. O sistema não
apenas escolheu uma hipótese — registrou evidência contra outra. Isso é o que
distingue um sistema com incerteza de um classificador que só devolve um rótulo.

E note o que a conclusão significa: o sinal está BOM e mesmo assim há perda. Um
diagnóstico de propagação estaria errado aqui, e a retransmissão do MAC é o que
impede o sistema de cometer esse erro.""",
        accent=BLUE,
    )

    d.bullets(
        "Encadeamento regressivo — dirigido por objetivo",
        [
            "Parte da pergunta “o diagnóstico é X?” e busca só a evidência que a sustenta",
            "É o modo do Expert SINTA — e o modo do engenheiro às duas da manhã",
            "Curto-circuito: condição falsa abandona a regra — as demais NÃO são perguntadas",
            "Corte por suficiência: objetivo com CF ≥ 0,9 encerra a busca",
            ("Resultado: o caso de falha de energia conclui com 6 de 13 perguntas", 1),
        ],
        """O curto-circuito é o ponto técnico que vale explicar. Sem ele, o modo
regressivo pergunta quase tanto quanto o progressivo — e perde a razão de
existir. Foi, aliás, um defeito real: um teste apanhou o motor perguntando todas
as 13 variáveis, e a correção foi abandonar a regra assim que uma condição se
mostra falsa.

Mencione que o teste
test_backward_chaining_matches_forward_chaining_on_the_same_evidence
verifica que os dois sentidos, com a mesma evidência, concluem o mesmo.""",
        accent=BLUE,
    )

    d.code(
        "Demonstração: consulta guiada por objetivo",
        [
            "$ aisg diagnose --kb simulated --interactive --mode backward",
            "",
            "O nó responde [yes, no]?",
            "  (Enter = não sei)   ('?' = por quê)",
            "> no",
            "",
            "O repetidor a montante responde [yes, no]?",
            "> ?",
            "",
            "Por que esta pergunta está sendo feita:",
            "  S17: SE repetidor_a_montante = no E nó_responde = no",
            "       ENTÃO upstream_relay_failure (CF +0,90)",
            "> no",
            "",
            "diagnóstico: upstream_relay_failure (CF +0,97)  —  poucas perguntas",
        ],
        """Este é o único momento não roteirizado da apresentação. Ensaie antes.

Digite "?" numa das perguntas para mostrar o "por quê": o motor exibe a cadeia
de regras que o levou até ali. Um sistema que só responde não é utilizável em
operação crítica; um que mostra o caminho pode ser auditado e contestado.

Aceita também uma certeza junto da resposta: "no 0.6" informa a resposta com
confiança 0,6 em vez de certeza.""",
        accent=BLUE,
    )

    d.table(
        "Resolução de conflito: qual regra dispara primeiro?",
        ["Política", "Critério", "Efeito"],
        [
            ["first-match", "Ordem de declaração na base", "Previsível, ingênua"],
            ["specificity", "Mais condições primeiro (padrão)", "Prefere a regra mais informada"],
            ["recency", "Fatos mais recentes primeiro", "Segue a evidência nova"],
        ],
        """Quando várias regras estão prontas, é preciso escolher. As três políticas são
selecionáveis em tempo de execução — mostre com --strategy recency que a ordem
de disparo muda.

A afirmação a fazer, e que é verificada em teste: com regras monotônicas, a
política muda a ORDEM do raciocínio, não o ponto fixo. Há teste para as duas
metades: que as ordens diferem entre políticas, e que o diagnóstico final é o
mesmo.

Este é o diferencial barato da apresentação: a maioria dos trabalhos não trata
resolução de conflito.""",
        accent=BLUE, widths=[2.2, 4, 3.5], highlight=1,
    )

    d.code(
        "Explicação: como a conclusão foi obtida",
        [
            "diagnóstico = node_power_failure (CF +0,95, R16)",
            "  <= R16: SE alimentação_do_nó = failed",
            "          ENTÃO diagnóstico = node_power_failure (CF +0,95)",
            "     Falha de alimentação explica a perda do nó independentemente do rádio.",
            "      alimentação_do_nó = failed (CF +1,00, fato inicial)",
        ],
        """O "como" desce recursivamente das conclusões até os fatos informados pelo
usuário, citando em cada nível a regra e a justificativa em linguagem natural
que ela carrega.

Contraste com ELIZA, que abrimos na primeira aula: ELIZA produzia respostas
convincentes sem modelo do domínio. Aqui, toda conclusão é rastreável até a
regra e o fato que a sustentam. É a diferença entre parecer e poder mostrar.""",
        accent=BLUE,
    )

    d.table(
        "Os oito casos comandáveis no simulador",
        ["Caso comandado", "Diagnóstico", "CF", "Ação recomendada", "Autoriza?"],
        [
            ["rf_interference", "rf_interference", "+0,93", "change_channel", "sim"],
            ["excess_path_loss", "excess_path_loss", "+0,92", "restore_path_budget", "sim"],
            ["mac_contention", "mac_contention", "+0,94", "separate_channels", "sim"],
            ["node_failure", "node_failure", "+0,80", "restart_node", "sim"],
            ["upstream_relay_failure", "upstream_relay_failure", "+0,97", "restore_upstream_relay", "sim"],
            ["routing_misconfiguration", "routing_misconfiguration", "+0,90", "fix_routing", "sim"],
            ["congestion", "congestion", "+0,89", "reroute_traffic", "sim"],
            ["healthy", "healthy", "+0,81", "no_action", "não"],
        ],
        """Oito casos, oito diagnósticos corretos. Mas o ponto não é o acerto — é que
o nome do caso É o rótulo verdadeiro, porque o operador comandou a condição
antes de executar.

Isso é o que a bancada de campo não pode oferecer: no campo ninguém sabe, no
momento da medição, o que causou a perda. Aqui sabe-se por construção, e a
execução pode ser repetida.

Aponte node_failure: CF +0,80, o mais baixo. Não é defeito — é o sistema
admitindo que um nó calado tem mais de uma explicação possível.""",
        accent=BLUE, widths=[2.2, 3.2, 1.1, 3.3, 1.5], highlight=2,
    )

    d.statement(
        "Os limiares são nominais e não calibrados",
        "Reunidos num único bloco, para que a calibração futura ajuste valores sem reescrever regras.",
        """Feche o tema 1 pelos limites, e não pelos resultados.

Os limiares vieram de faixas de folha de dados de rádio sub-GHz e de prática
comum de telecom — são ponto de partida para calibração, não valores medidos.

A decisão de projeto que importa: eles estão todos num único dicionário
THRESHOLDS. Quando existir linha de base medida, ajustam-se os valores e as
regras não mudam. É por isso que o bloco está declarado num lugar só.

O sistema diz isso na própria saída, ao fim de cada consulta.""",
        accent=RED,
    )

    # ======================================================================
    # TEMA 2 — PLANEJAMENTO — 30 min
    # ======================================================================
    d.section("TEMA 2", "Geração automática de planos",
              "STRIPS, GPS por análise meios-fins, e planejamento como busca",
              GREEN, "30 minutos",
              """Transição: o sistema especialista disse o que fazer. Agora, em que ordem.""")

    d.bullets(
        "O problema: sequenciamento sob restrições",
        [
            "O diagnóstico já foi feito e a ação já foi recomendada",
            "Falta decidir em que sequência executá-la",
            "Uma equipe não realinha uma antena antes de chegar ao local",
            "Nada toca a planta antes da autorização",
            "Objetivo: service-restored(N) E logged(N)",
            ("a evidência faz parte do objetivo — não é um extra", 1),
        ],
        """Chame a atenção para o objetivo duplo: o serviço restaurado E o registro
feito. Fechar a ordem de serviço sem registrar não satisfaz o objetivo.

Isso é disciplina de evidência expressa como objetivo de planejamento — a mesma
lógica de um laboratório que só aceita um resultado se ele estiver registrado.""",
        accent=GREEN,
    )

    d.figure(
        "STRIPS: a representação, e GPS: a estratégia",
        ASSETS / "03-planning-light.png",
        """À esquerda, a anatomia de um operador: precondições, lista de adição, lista
de remoção. À direita, a recursão do GPS.

Deixe claro que STRIPS e GPS não competem: STRIPS diz COMO DESCREVER uma ação,
GPS diz COMO ESCOLHER a próxima. A mesma representação STRIPS pode ser resolvida
por meios-fins, por busca progressiva ou por um planejador de ordem parcial — e
neste trabalho ela é resolvida de duas maneiras.""",
        accent=GREEN,
        caption="Três conjuntos definem uma ação. O estado é o conjunto dos literais verdadeiros.",
    )

    d.code(
        "Um operador STRIPS",
        [
            "separate_channels(?n)                              custo 3",
            "",
            "  precondições:   authorized(?n)",
            "                  mac-contention(?n)",
            "                  run-stopped(?n)",
            "",
            "  adiciona:     + cleared-mac-contention(?n)",
            "",
            "  remove:       - mac-contention(?n)",
            "",
            "  estado = { diagnosed(N), run-active(N), mac-contention(N) }",
            "  hipótese do mundo fechado: o que não está no conjunto é falso",
        ],
        """Leia os três conjuntos. Depois explique a hipótese do mundo fechado: o estado
é o conjunto dos literais VERDADEIROS, e tudo o que não está lá é considerado
falso. Não precisamos dizer que a antena não está desalinhada — basta não dizer
que está.

Isso é o que torna o estado finito e a busca tratável.""",
        accent=GREEN,
    )

    d.table(
        "Os doze operadores",
        ["Operador", "Custo", "Exige execução parada?", "Autorização?"],
        [
            ["request_authorization(?n)", "1", "não", "—"],
            ["stop_run(?n)", "2", "SIM", "sim"],
            ["start_run(?n)", "2", "—", "—"],
            ["restore_path_budget(?n)", "1", "SIM", "sim"],
            ["separate_channels(?n)", "3", "SIM", "sim"],
            ["restart_node(?n)", "1", "não", "sim"],
            ["fix_routing(?n)", "1", "não", "sim"],
            ["restore_relay(?n)", "2", "não", "sim"],
            ["reroute_traffic(?n)", "2", "não", "sim + rota alternativa"],
            ["verify_link / record_logbook / close_work_order", "1", "—", "—"],
        ],
        """Não leia a tabela inteira. Aponte três coisas:

Primeiro: ninguém se desloca até um simulador, então o custo que importa não é
a viagem da equipe — é a EXECUÇÃO. Alterar um parâmetro do cenário (o orçamento
de percurso, o plano de canais) invalida a execução em curso, logo exige pará-la
e retomá-la: 2 + 2 antes de qualquer reparo desse tipo.

Segundo: reparos de tempo de execução — reativar um nó, corrigir uma rota — não
exigem nada disso.

Terceiro, e é o ponto: dois reparos de parâmetro cabem numa MESMA parada. O
planejador agrupa. É a mesma decisão que a viagem da equipe forçava antes.""",
        accent=GREEN, widths=[5.2, 1.2, 2.2, 3.0], highlight=8,
    )

    d.statement(
        "Governança como precondição, não como recomendação",
        "Agir sem autorização não é desaconselhado: é um estado INALCANÇÁVEL.",
        """Este é o ponto de projeto mais forte do tema 2.

Poderíamos ter escrito na documentação "não aja sem autorização". Em vez disso,
authorized(?n) é precondição de todo operador que alcança a planta. O planejador
não pode produzir um plano que aja sem autorização — não porque foi instruído a
não fazê-lo, mas porque esse plano não existe no espaço de estados.

Há um teste que verifica essa invariante em todos os oito diagnósticos.

A exceção é start_run: retomar a execução não altera o cenário, apenas o repõe.""",
        accent=GREEN,
    )

    d.bullets(
        "GPS: análise meios-fins",
        [
            "Olhe a DIFERENÇA entre o estado atual e o objetivo",
            "Escolha um operador que REDUZA essa diferença",
            "Recursivamente, satisfaça as precondições desse operador",
            "Aplique o operador",
            ("Toda ação existe para eliminar uma diferença concreta — por isso o trace se lê como justificativa, não como log de busca", 1),
        ],
        """Newell e Simon, 1959. A contribuição conceitual é dupla.

Primeiro, o vocabulário: estados, operadores, objetivos, subobjetivos — que o
planejamento usa até hoje.

Segundo, e mais importante para nós: o porquê de cada ação fica explícito. Cada
ação existe para eliminar uma diferença concreta. Compare com a saída de um
solver moderno, que devolve um plano ótimo sem dizer por que cada passo está
ali.""",
        accent=GREEN,
    )

    d.code(
        "O trace do GPS: uma justificativa",
        [
            "DIFERENÇA a reduzir: service-restored(RM_A5)",
            "  operador candidato: close_work_order(RM_A5)",
            "  precondições: link-up(RM_A5), logged(RM_A5)",
            "    DIFERENÇA a reduzir: link-up(RM_A5)",
            "      operador candidato: verify_link(RM_A5)",
            "        DIFERENÇA a reduzir: fault-cleared(RM_A5)",
            "          operador candidato: separate_channels(RM_A5)",
            "            DIFERENÇA a reduzir: run-stopped(RM_A5)",
            "              APLICA stop_run(RM_A5)",
            "            já satisfeito: run-active(RM_A5)",
        ],
        """Percorra o trace com o dedo. Cada linha "DIFERENÇA a reduzir" é uma pergunta;
cada "operador candidato" é uma tentativa de resposta; e a recursão termina
quando a diferença desaparece — aqui, quando descobrimos que a equipe já está na
base.

O plano final é a pilha desfeita na ordem inversa.

$ aisg plan --simulated --diagnosis mac_contention --node RM_A5 --solver gps --trace""",
        accent=GREEN,
    )

    d.bullets(
        "As limitações do GPS — ditas antes que perguntem",
        [
            "O GPS não é completo nem ótimo",
            "Adota o primeiro operador que reduz a diferença; só revisa por retrocesso",
            "Anomalia de Sussman: com subobjetivos que interagem, atingir um pode desfazer outro",
            ("Nossa defesa mínima: reverificar os subobjetivos ao final e falhar explicitamente, em vez de devolver plano inválido", 1),
        ],
        """Diga as limitações você mesmo. Um trabalho que apresenta só os acertos convida
a pergunta; um que apresenta os limites demonstra domínio.

A anomalia de Sussman merece a explicação: alcançar o objetivo A e depois o
objetivo B pode destruir A. Nossa implementação não resolve o problema — adota a
defesa mínima de reverificar ao final e falhar explicitamente. Falhar de forma
visível é melhor que devolver um plano que não funciona.""",
        accent=GREEN,
    )

    d.code(
        "A não-otimalidade do GPS, demonstrada",
        [
            "O GPS ordena os operadores pelo custo PRÓPRIO,",
            "sem olhar o custo das PRECONDIÇÕES.",
            "",
            "  conserto_barato_no_local   custo  1   exige: on-site(N)",
            "  deslocar_equipe            custo 10",
            "  conserto_remoto            custo  3   exige: nada",
            "",
            "GPS:  deslocar_equipe (10) + conserto_barato (1)   =  custo 11",
            "A* :  conserto_remoto (3)                          =  custo  3",
        ],
        """Este caso está num teste do repositório, não é hipotético:
test_gps_can_be_suboptimal_when_a_cheap_action_has_expensive_preconditions.

O GPS vê um operador de custo 1 e escolhe-o. Não vê que ele exige um
deslocamento de custo 10. O A*, que raciocina sobre o custo acumulado do caminho
inteiro, encontra o plano de custo 3.

DIGA ISTO EM VOZ ALTA, porque é a parte honesta: esse é um problema CONSTRUÍDO
para isolar a propriedade. No domínio de restauração deste trabalho o GPS NUNCA
perde — comparei as 55 combinações de falhas solúveis dos dois cenários e o
custo é idêntico ao do A* em todas. O motivo é estrutural: nenhum literal do
domínio tem mais de um operador que o produz, então a análise meios-fins não
tem escolha para errar.

Ou seja: o GPS é não-ótimo em geral, e este domínio em particular não é capaz de
mostrá-lo. Os dois planejadores convivem no repositório porque um explica e o
outro garante — mas a garantia só passa a valer a pena quando o domínio tiver
mais de uma forma de alcançar o mesmo objetivo.""",
        accent=GREEN,
    )

    d.table(
        "Planejamento é busca: o mesmo problema",
        ["Busca", "Planejamento"],
        [
            ["estado", "conjunto de literais verdadeiros"],
            ["ação sucessora", "qualquer ação aplicável"],
            ["custo do passo", "custo da ação"],
            ["teste de objetivo", "o objetivo está contido no estado"],
        ],
        """Feito esse mapeamento, QUALQUER algoritmo de busca resolve o planejamento.

E aqui está o ponto que liga os temas 2 e 3: a mesma função astar do terceiro
trabalho resolve o planejamento. Não é uma cópia adaptada — é a mesma função,
importada de aisg.search.algorithms. Uma implementação, dois espaços de estados.

Se houver uma única coisa a lembrar deste tema, é esta.""",
        accent=GREEN, widths=[4, 6],
    )

    d.bullets(
        "A heurística do planejador, e sua condição",
        [
            "goal_count: h(s) = número de literais do objetivo ainda não satisfeitos",
            "Admissível APENAS SE nenhuma ação satisfaz mais de um literal do objetivo e toda ação custa ao menos 1",
            "Neste domínio a condição vale: service-restored e logged vêm de operadores diferentes",
            "Declaramos a condição em vez de supô-la",
            ("uma heurística inadmissível custaria a otimalidade em silêncio", 1),
        ],
        """Este slide é sobre honestidade técnica.

Seria fácil escrever "usamos a heurística de contagem de objetivos" e seguir em
frente. Mas ela só é admissível sob duas condições, e essas condições precisam
ser verificadas no domínio — o que fizemos.

A frase final é a que importa: uma heurística inadmissível não quebra o A*. Ele
continua rodando e passa a devolver soluções subótimas SEM AVISAR. Por isso a
admissibilidade se demonstra, não se presume.""",
        accent=GREEN,
    )

    d.code(
        "Demonstração: os dois planejadores",
        [
            "$ aisg plan --simulated --diagnosis mac_contention --node RM_A5 --solver both",
            "",
            " 1. request_authorization(RM_A5)   [1]",
            " 2. stop_run(RM_A5)                [2]",
            " 3. separate_channels(RM_A5)       [3]",
            " 4. start_run(RM_A5)               [2]",
            " 5. verify_link(RM_A5)             [1]",
            " 6. record_logbook(RM_A5)          [1]",
            " 7. close_work_order(RM_A5)        [1]",
            "    custo total: 11",
            "",
            "Validação: o plano é executável e atinge o objetivo.",
        ],
        """Rode ao vivo. Note a ordem: autorização, parar a execução, alterar o parâmetro,
retomar, verificar, registrar, encerrar. A verificação só é possível com a
execução ativa — por isso parar é um custo, e não uma precaução gratuita.

Sobre validação: um plano só vale se for executável passo a passo E atingir o
objetivo. Plan.validate() reexecuta o plano desde o estado inicial e aponta o
primeiro passo inaplicável com a precondição que faltou.

Dois testes corrompem planos de propósito — um remove a autorização, outro
remove o encerramento — para provar que a validação apanha os dois defeitos.""",
        accent=GREEN,
    )

    d.statement(
        "O sistema também sabe quando NÃO prometer",
        "Se uma das falhas não tem reparo disponível, ele não devolve um plano parcial.",
        """Rode o caso de congestionamento com um destino inalcançável:

  aisg pipeline --case congestion --node AP_A --target SUB_S1

O diagnóstico sai, a ação recomendada sai — e o planejador responde "nenhum plano
encontrado". Porque não existe rota alternativa até aquele destino evitando o nó
congestionado, e desviar é a única forma de resolver congestionamento.

Ele poderia ter reparado outra coisa e declarado serviço restaurado. Não o faz.

Este é o comportamento que mais custa a construir e que menos se nota: recusar-se
a prometer. Num sistema de recomendação operacional é a diferença entre útil e
perigoso — e há teste que o verifica, porque foi um defeito real antes de ser uma
garantia.""",
        accent=GREEN,
    )

    d.bullets(
        "Integração com a busca A*",
        [
            "reroute_traffic exige o literal alternate-route(?n)",
            "Esse literal NÃO é inventado",
            "Quando o diagnóstico é congestionamento, o planejador consulta o A* sobre a topologia, evitando o nó afetado",
            "Se não houver rota, a ação fica inaplicável",
            ("e o planejador falha honestamente, em vez de propor um desvio impossível", 1),
        ],
        """Este é o segundo ponto de contato entre os trabalhos, e o mais concreto.

O planejador poderia simplesmente assumir que existe rota alternativa. Em vez
disso, ele pergunta ao A*: existe caminho de NOC até o dispositivo de campo que
não passe pelo nó congestionado? Se a resposta é não, o literal não entra no
estado inicial e o desvio deixa de ser uma opção.

Há teste para os dois lados: com rota e sem rota.""",
        accent=GREEN,
    )

    # ======================================================================
    # TEMA 3 — BUSCA A* — 30 min
    # ======================================================================
    d.section("TEMA 3", "Busca A*",
              "f(n) = g(n) + h(n), prova de admissibilidade, e comparação entre estratégias",
              AMBER, "30 minutos",
              """Transição: já usamos o A* duas vezes sem explicá-lo. Agora explicamos.""")

    d.bullets(
        "O problema",
        [
            "Qual o caminho de menor custo de transporte entre dois nós?",
            "O requisito da disciplina é explícito: retornar o CAMINHO EXATO entre o estado inicial e o objetivo",
            "custo(u,v) = sobrecarga(tipo) + distância / (velocidade(tipo) × qualidade)",
            "Um repetidor armazena-e-encaminha TERMINA e retransmite o quadro",
            ("por isso paga 25 ms de sobrecarga, contra 0,5 ms da fibra", 1),
        ],
        """Explique o modelo de custo antes do algoritmo, porque a prova depende dele.

A velocidade é uma velocidade EFETIVA de transporte, não uma velocidade física
de propagação: é uma abstração que reúne serialização, enfileiramento e o fato
de que saltos de rádio mais longos operam com modulação mais robusta — e
portanto mais lenta.

Diga que é uma abstração. Um revisor que perceba isso sozinho vai desconfiar do
resto.""",
        accent=AMBER,
    )

    d.figure(
        "f(n) = g(n) + h(n)",
        ASSETS / "04-astar-light.png",
        """À esquerda, o caminho ótimo com os custos salto a salto. À direita, a
heurística, as duas provas, e a tabela comparativa.

As duas metades de f importam: só g dá o custo uniforme, que é ótimo mas cego; só
h dá a busca gulosa, que é rápida mas sem garantia. O A* é a combinação — e a
tabela mostra exatamente isso.""",
        accent=AMBER,
        caption="O caminho ótimo evita inteiramente a cadeia armazena-e-encaminha.",
    )

    d.bullets(
        "Três detalhes que separam um A* correto de um A* de brinquedo",
        [
            "Desempate: empates em f resolvem-se preferindo o maior g, depois a ordem de inserção",
            ("as execuções ficam reprodutíveis — importante numa apresentação", 1),
            "Reabertura: um estado fechado é reaberto se surgir caminho mais barato",
            ("com heurística consistente isso nunca ocorre, mas tratamos o caso geral", 1),
            "Custos negativos são recusados com erro explícito",
        ],
        """Estes três pontos costumam faltar em implementações de sala de aula.

O desempate importa para a reprodutibilidade: sem ele, duas execuções podem
devolver caminhos diferentes de mesmo custo, e a demonstração fica instável.

A reabertura é o caso geral: nossa heurística é consistente, então nunca
acontece — mas tratamos, em vez de SUPOR a consistência. Supor é como se
introduzem defeitos silenciosos.""",
        accent=AMBER,
    )

    d.code(
        "Prova de admissibilidade",
        [
            "h(n) = distância_em_linha_reta(n, objetivo) / VELOCIDADE_MÁXIMA",
            "",
            "Como  sobrecarga >= 0,  qualidade <= 1,  velocidade(tipo) <= MÁXIMA:",
            "",
            "    custo(u,v)  >=  d(u,v) / VELOCIDADE_MÁXIMA",
            "",
            "Somando ao longo de qualquer caminho de n até o objetivo, o custo total",
            "é ao menos a distância TOTAL PERCORRIDA dividida pela velocidade máxima.",
            "Pela desigualdade triangular, a distância percorrida é ao menos a linha reta.",
            "",
            "    custo_ótimo(n)  >=  h(n)          admissível   ∎",
        ],
        """Este é o momento de nível de doutorado da apresentação. Vá devagar.

A chave é dividir pela velocidade MÁXIMA do sistema — a da fibra. Como nenhum
enlace pode ser mais rápido que o mais rápido de todos, e como a sobrecarga
nunca é negativa, cada salto custa pelo menos a distância percorrida dividida
por esse máximo. A desigualdade triangular fecha o argumento.

E não é acidente: o modelo de custo foi PROJETADO para que a prova se sustente.
As distâncias são derivadas das coordenadas, nunca armazenadas em separado, de
modo que geometria e heurística não podem divergir.""",
        accent=AMBER,
    )

    d.code(
        "Prova de consistência, e a verificação",
        [
            "Pela desigualdade triangular:",
            "    d(u, objetivo)  <=  d(u,v) + d(v, objetivo)",
            "",
            "Dividindo pela velocidade máxima:",
            "    h(u)  <=  custo(u,v) + h(v)       consistente   ∎",
            "",
            "A consistência implica a admissibilidade,",
            "e garante que nenhum nó precise ser reaberto.",
            "",
            "VERIFICADO, não apenas argumentado:",
            "  272 pares no cenário base + 870 no de escala",
            "  todas as arestas, todos os objetivos — zero violações",
        ],
        """Termine a matemática e passe imediatamente à verificação. Não paramos no
argumento: dois testes checam as duas propriedades exaustivamente, comparando
contra o custo ótimo obtido por busca de custo uniforme — que não usa heurística
nenhuma e serve de verdade de referência.

Se alguém perguntar "como você sabe que a prova está certa?", a resposta é que a
prova e o teste concordam em mais de mil pares.""",
        accent=AMBER,
    )

    d.table(
        "Cinco estratégias, o mesmo problema: LTE_ENB → AP_B",
        ["Estratégia", "Passos", "Custo (ms)", "Expandidos", "Ótimo?"],
        [
            ["Largura (BFS)", "2", "381,46", "7", "só em passos"],
            ["Custo uniforme", "3", "70,51", "6", "sim"],
            ["Gulosa", "2", "381,46", "3", "não"],
            ["A*", "3", "70,51", "4", "sim"],
        ],
        """Esta tabela é o centro do tema 3. Leia as três lições:

Primeira, e este exemplo é melhor que o anterior: a busca em largura minimiza
SALTOS, não custo — e aqui o caminho ÓTIMO TEM MAIS SALTOS. A largura acha 2
saltos por 381 ms; o A* acha 3 saltos por 70. Cinco vezes mais barato, com um
salto a mais. Não há demonstração mais direta de que salto não é custo.

Segunda: a gulosa é a mais rápida E ESTÁ ERRADA. Cinco expansões contra onze do
A*, e um caminho 3,9 vezes mais caro. É o argumento mais direto a favor do termo
g(n).

Terceira: o A* alcança o mesmo ótimo do custo uniforme expandindo menos nós. A
heurística não muda a resposta; muda o trabalho necessário para chegar a ela.""",
        accent=AMBER, widths=[3.2, 1.4, 2.0, 2.0, 2.2], highlight=4,
    )

    d.code(
        "O caminho ótimo, salto a salto",
        [
            "LTE_ENB -> LTE_CORE -> NOC -> AP_B                       70,51 ms",
            "",
            "salto                  meio                 qual.   custo    acum.",
            "LTE_ENB -> LTE_CORE    fibra óptica          0,96    13,86    13,86",
            "LTE_CORE -> NOC        ethernet local        1,00     9,41    23,27",
            "NOC -> AP_B            fibra óptica          0,97    47,23    70,51",
            "",
            "a largura preferiu: LTE_ENB -> RM_B4 -> AP_B  =  381,46 ms",
            "dois saltos, um deles de radio — e cinco vezes mais caro",
        ],
        """O caminho ótimo desce pelo núcleo — fibra e ethernet — em vez de atravessar um
salto de rádio direto.

A largura escolhe o caminho de 2 saltos porque conta saltos. Mas aquele salto de
rádio custa sozinho mais do que os três saltos do núcleo somados. É exatamente
o erro que a tabela anterior mede.

Este é o tipo de conclusão que um operador de rede tiraria de um estudo de
planejamento — e o algoritmo chegou a ela sozinho.""",
        accent=AMBER,
    )

    d.table(
        "A vantagem da heurística cresce com o grafo",
        ["Cenário", "Nós", "A* expandidos", "Custo uniforme", "Economia"],
        [
            ["campo", "17", "2 342", "2 584", "9,4 %"],
            ["simulado", "30", "10 310", "13 920", "25,9 %"],
        ],
        """Um único par pode ser sorte. Estes números somam todos os pares ORDENADOS
(origem, destino) de cada cenário — 272 no de campo, 870 no simulado. Diga
"ordenados": a contagem muda pela metade se forem não ordenados, e a pergunta
vai ser feita.

A economia é bem maior NESTE exemplo maior. Não diga que isso é uma lei de
escala: são dois grafos, e dois pontos não estabelecem uma tendência. O que se
pode afirmar é o que foi medido, e o teste verifica a RELAÇÃO entre os dois, não
os números.

O teste test_the_heuristic_saves_more_work_as_the_graph_grows verifica essa
RELAÇÃO — que a economia cresce — e não os números específicos, que mudariam a
cada ajuste na topologia.

$ aisg --topology scale route --compare""",
        accent=AMBER, widths=[2.4, 1.4, 2.8, 2.8, 2.0], highlight=1,
    )

    d.code(
        "Falha e recálculo de rota",
        [
            "$ aisg --topology simulated route --from LTE_ENB --to AP_B \\",
            "         --disable-link LTE_CORE-LTE_ENB",
            "",
            "antes :  70,51 ms   LTE_ENB -> LTE_CORE -> NOC -> AP_B",
            "depois: 345,80 ms   LTE_ENB -> RM_C4 -> AP_C -> NOC -> AP_B",
            "",
            "Sem o enlace de núcleo, o caminho entra por um salto de rádio",
            "— e o custo quase quintuplica.",
        ],
        """Demonstre a injeção de falha ao vivo. É assim que a integração com o
planejador funciona: quando o plano inclui desviar tráfego, a rota é recalculada
evitando o nó afetado.

O teste test_disabling_a_link_changes_the_optimal_route verifica exatamente
isso: que o custo sobe e que o caminho muda.

Este slide também responde a uma pergunta provável: o sistema lida com mudança?
Lida — recalculando, não consultando uma tabela fixa.""",
        accent=AMBER,
    )

    d.two_up(
        "Onde o aprendizado de máquina ENTRARIA: a heurística",
        "Por que é uma tarefa diferente", [
            "O alvo é h*(n), o custo real restante",
            "Calculável exatamente: Dijkstra a partir do objetivo",
            "Supervisão gratuita e exata — não é rótulo de falha",
            "Não exige instrumento de degradação nem campo",
            "Vale mais no PLANEJADOR: goal_count é fraca e o espaço não tem geometria",
        ],
        "Por que ainda não está aqui", [
            "Uma heurística aprendida NÃO é admissível por construção",
            "Regressão pode superestimar → A* perde a otimalidade em silêncio",
            "Saídas: usá-la só como desempate (preserva o ótimo)...",
            "...ou em busca limitadamente subótima, com fator de garantia",
            "Nossos testes de admissibilidade seriam o instrumento de medida",
        ],
        """Este slide existe porque a pergunta é boa e vai ser feita.

Aprender a heurística NÃO esbarra no obstáculo do diagnóstico. O alvo de
regressão é o custo real restante, e esse custo é calculável exatamente rodando
Dijkstra a partir do objetivo. A supervisão é gratuita, exata e ilimitada — nada
a ver com rotular falhas em campo.

O ponto onde isso realmente pagaria não é o roteamento: ali a distância em linha
reta já é quase perfeita e custa nada. É o PLANEJADOR, onde goal_count vale no
máximo 2 e o espaço de estados não tem geometria para explorar. É exatamente o
caso em que a literatura usa heurísticas aprendidas.

O preço é a admissibilidade. Uma rede treinada por regressão pode superestimar, e
aí o A* continua rodando e devolve planos subótimos SEM AVISAR — o mesmo risco
que discutimos no slide da heurística goal_count.

E aqui está o que torna este repositório bem posicionado para o experimento: já
temos testes que verificam admissibilidade exaustivamente. Eles nao seriam
apenas uma proteção — seriam o instrumento para MEDIR quantas vezes a heurística
aprendida viola a admissibilidade, e em quanto. Isso é um resultado publicável,
não um detalhe de implementação.""",
        accent=AMBER, left_colour=GREEN, right_colour=RED,
    )

    d.statement(
        "Uma implementação, dois espaços de estados",
        "A mesma função astar() resolve o roteamento na rede e o planejamento de ações.",
        """Feche o tema 3 amarrando-o ao tema 2.

A busca está definida sobre um PROBLEMA ABSTRATO: estado inicial, teste de
objetivo, função sucessora. Nada nela sabe o que é um nó de rede.

Por isso a mesma função serve para achar um caminho num grafo de comunicação e
para achar uma sequência de ações num espaço de estados de planejamento. Não há
duas implementações de A* neste repositório — há uma, usada duas vezes.

É o tipo de reuso que só aparece quando a abstração está certa.""",
        accent=AMBER,
    )

    # ======================================================================
    # FECHAMENTO — 5 min
    # ======================================================================
    d.section("FECHAMENTO", "Integração e limites",
              "Os três sistemas num único incidente",
              BLUE, "5 minutos",
              """Último bloco, e o único em que os três trabalhos aparecem juntos.

Até aqui cada tema foi apresentado isoladamente. Agora mostre que eles formam um
sistema: um incidente atravessa os três, e o que sai de um é a entrada do
seguinte.

Reserve tempo para as perguntas — com três temas de trinta minutos, elas tendem
a concentrar-se no fim.""")

    d.code(
        "Um comando, os três sistemas",
        [
            "$ aisg --topology simulated pipeline --case congestion --node SAF_A1",
            "",
            "1/3  diagnóstico ......... congestion (CF +0,89)",
            "     ação recomendada .... reroute_traffic (CF +0,71)",
            "",
            "2/3  rota alternativa confirmada pelo A*: True",
            "     plano validado",
            "",
            "3/3  rota evitando SAF_A1:",
            "     NOC -> LTE_CORE -> LTE_ENB -> FD_A               267,06 ms",
        ],
        """A demonstração final. Um comando só.

O sistema especialista diagnostica congestionamento. O diagnóstico vira o estado
inicial do planejador. O planejador só pode propor desvio porque a busca A*
CONFIRMOU que existe rota alternativa evitando o nó. E o plano sai com
autorização, verificação e registro.

Os três trabalhos não são três exercícios: são um sistema.""",
        accent=BLUE,
    )

    d.bullets(
        "Limites de validade",
        [
            "A topologia é sintética — não representa nenhuma instalação real",
            "Os limiares são nominais e não calibrados",
            "Não existe conjunto de dados rotulado de falhas para este domínio",
            "Restrições viram precondições — a restrição fica no espaço de estados, não num teste em tempo de execução",
            ("Uma conclusão obtida aqui vale para ESTE MODELO, não para uma planta física", 1),
        ],
        """Feche pelos limites, e não pelos resultados. É o que separa um trabalho de
engenharia de uma demonstração.

Cada uma destas linhas é uma afirmação que o sistema faz sobre si mesmo — a
última aparece impressa ao fim de cada consulta.

Se houver tempo, mencione o que vem a seguir: o sistema multiespecialista e a
eco-resolução em 25/09, e a análise do artigo sobre encadeamento em 02/10.""",
        accent=RED,
    )

    d.table(
        "Perguntas prováveis",
        ["Pergunta", "Resposta curta"],
        [
            ["Por que não aprendizado de máquina?",
             "Não há dados rotulados de falha, nem como produzi-los sem instrumento de degradação"],
            ["Como escolhe entre regras concorrentes?",
             "Três políticas selecionáveis; a padrão é especificidade. Muda a ordem, não a conclusão"],
            ["A heurística é admissível?",
             "Sim — prova por desigualdade triangular e verificação exaustiva em teste"],
            ["O GPS sempre acha o melhor plano?",
             "Não. Há um teste que exibe um caso concreto de não-otimalidade"],
            ["Qual banco de dados?",
             "Nenhum. JSON versionado, regras em código, memória de trabalho em RAM"],
            ["E se não houver rota alternativa?",
             "A ação fica inaplicável e o planejador falha honestamente. Há teste"],
            ["Por que CF e não probabilidade?",
             "CF não exige priors nem independência condicional — que sem dados não se estimam"],
        ],
        """Não mostre este slide na apresentação — ele é a sua cola. Deixe-o oculto ou
pule-o rapidamente.

Se uma pergunta não estiver aqui e você não souber, a melhor resposta é a
honesta: dizer o que sabe, dizer o que não verificou, e oferecer verificar.""",
        accent=BLUE, widths=[4.5, 7.0],
    )

    d.statement(
        "Obrigado",
        "github.com/fsd-dantas/ai-for-smartgrids   ·   155 testes   ·   wiki com a teoria da disciplina",
        """Encerramento.

O repositório é público, tem 155 testes verdes em integração contínua para
Python 3.10 a 3.13, documentação bilíngue, e uma wiki que liga cada conceito da
disciplina ao ponto do código que o implementa.

Convide perguntas.""",
        accent=BLUE,
    )

    # Optional reference material: hidden in the timed slide show.
    rubric = d.table(
        "Apêndice — proposta de avaliação",
        ["Área", "Pontos", "Evidência principal"],
        [
            ["Sistema especialista", "30", "Regras, encadeamento, CF e explicação"],
            ["Planejamento", "30", "Modelo, plano executável e integração"],
            ["Busca A*", "25", "Caminho, custo, heurística e comparação"],
            ["Documentação e defesa", "15", "Reprodução, clareza e limites"],
        ],
        """Material de consulta; não adiciona tempo à apresentação de 90 minutos.
Esta é uma proposta de autoavaliação, não uma rubrica oficial.

Procedimento: relacionar requisitos à evidência; identificar o commit e qualquer
diff local; executar as verificações; justificar a pontuação por critério;
registrar eventual manifestação explícita do professor. Sem resposta, manter o
status de proposta. O endosso dos critérios não endossa automaticamente a nota.

Detalhamento, matriz de evidências e texto sugerido para solicitar apreciação:
docs/assessment-protocol.md. A revisão preliminar de 85/100 pertence ao commit
8d47ced, anterior a esta rubrica detalhada, e não é nota docente. Defesa oral
ainda não observada permanece pendente.""",
        accent=BLUE, widths=[3.2, 1.0, 7.6],
        subtitle="Autoavaliação proposta • sem endosso docente registrado",
    )
    rubric._element.set("show", "0")

    scope = d.bullets(
        "Apêndice — escopo das falhas",
        [
            "Demonstração principal: um diagnóstico selecionado por nó",
            "Hipóteses concorrentes não confirmam falhas simultâneas",
            "Extensão: um predicado de reparo para cada falha fornecida",
            "Só verificar e encerrar após resolver todas as falhas do escopo",
            "Validar a extensão separadamente; resultados valem para o modelo",
        ],
        """A simplificação é uma escolha didática: permite concentrar a defesa em
regras, estados, precondições e busca. Não descreve todas as falhas de uma rede.

Para a extensão, demonstrar interferência com falha de alimentação; preservar os
casos de falha única e saudável; rejeitar falhas desconhecidas; impedir fechamento
quando uma falha não puder ser resolvida. Considerar interações e restrições das
ações. Planejar várias falhas fornecidas não demonstra diagnóstico multicausal.

Autorização e verificação são efeitos assumidos no modelo determinístico;
o planejador não obtém aprovação humana nem mede recuperação física.
Os 90 minutos foram confirmados pelo autor como autorizados pelo professor.
Este apêndice é opcional; não amplia a duração.""",
        accent=GREEN,
    )
    scope._element.set("show", "0")
