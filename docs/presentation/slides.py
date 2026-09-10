"""
Content of the 90-minute deck: three topics of 30 minutes.

Slide text is in Portuguese with full orthography. The repository's source files
avoid accented characters for terminal-encoding reasons; that rationale does not
apply to a deck rendered by PowerPoint, and in Portuguese the accent carries
meaning - "e" and "é" are different words.

The detailed argument sits in the speaker notes rather than on the slide.
"""

from __future__ import annotations

from build_deck import AMBER, BLUE, GREEN, RED, Deck, IMG_DIR


def build_slides(d: Deck) -> None:
    # ======================================================================
    # ABERTURA — 5 min
    # ======================================================================
    d.title_slide(
        IMG_DIR / "banner-dark.png",
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
            "Domínio comum: a rede de comunicação de um sistema elétrico inteligente",
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
        "O domínio: backhaul de comunicação",
        IMG_DIR / "01-integration.png",
        """Descreva o domínio em uma frase: a rede que liga ativos distribuídos de um
sistema elétrico ao centro de operação — núcleo em fibra, setores de rádio de
900 MHz, uma cadeia de repetidores armazena-e-encaminha e uma sobreposição LTE.

Diga explicitamente que a topologia é SINTÉTICA: um modelo didático da classe de
cenários estudada em laboratórios de backhaul sem fio. Não há inventário real,
endereçamento nem identificação de equipamento. Dizer isso antes que perguntem
vale mais do que responder depois.""",
        accent=BLUE,
        caption="17 nós no cenário base, 30 no cenário de escala. Topologia sintética.",
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

    d.two_up(
        "Como isto é medido: dois níveis de KPI",
        "KPIs do domínio — a entrada", [
            "RSSI (dBm) e SNR (dB) — qualidade do enlace",
            "Perda de pacotes (%) e RTT (ms) — sintoma",
            "Utilização do enlace (%) — congestionamento",
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

Os KPIs do DOMÍNIO são as grandezas que um operador de rede realmente observa, e
são a entrada dos sistemas: alimentam as regras do sistema especialista e, no
caso do custo de transporte, a função de custo da busca.

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
        "Não existe, para este domínio, conjunto de dados rotulado de falhas.",
        """Este é o argumento mais forte da apresentação — mas repare no escopo do
título: DIAGNÓSTICO. Não diga "não usamos aprendizado de máquina" como se valesse
para os três sistemas; a afirmação é sobre a tarefa de classificar a causa de uma
falha, e só sobre ela.

Para rotular um enlace como "degradado" ou "em falha" seriam precisas duas
coisas: um instrumento de degradação controlada, capaz de produzir a falha de
forma reprodutível, e uma linha de base de observabilidade autenticada contra a
qual comparar. Sem as duas, nenhum rótulo vem de medição. E um modelo treinado
apenas em estado normal não infere degradação de modo confiável — ele nunca viu
a classe que deveria reconhecer.

Se alguém perguntar "e aprender a heurística da busca?", a resposta é que essa é
uma tarefa DIFERENTE, com supervisão gratuita — e temos um slide sobre ela no
tema 3.""",
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
            ("O sistema recomenda — não atua", 1),
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
        "As variáveis observáveis",
        ["Variável", "Tipo", "Domínio"],
        [
            ["rssi_dbm", "numérica", "[-120, -30] dBm"],
            ["snr_db", "numérica", "[-5, 40] dB"],
            ["packet_loss_pct", "numérica", "[0, 100] %"],
            ["rtt_ms", "numérica", "[0, 5000] ms"],
            ["traffic_load_pct", "numérica", "[0, 100] %"],
            ["link_state", "categórica", "up | down | flapping"],
            ["node_power", "categórica", "ok | on-battery | failed"],
            ["weather", "categórica", "clear | rain | storm"],
            ["spectrum_scan", "categórica", "clean | occupied"],
            ["neighbours_affected", "categórica", "none | one | many"],
            ["recent_change", "categórica", "none | config | firmware | antenna"],
            ["vlan_trunk_ok / upstream_relay_reachable", "booleana", "yes | no"],
        ],
        """Treze variáveis perguntáveis. Não leia a tabela inteira — aponte três ou
quatro e diga que são grandezas que um operador de rede realmente observa.

Note que há dois tipos: medições numéricas com faixa declarada, e categóricas
com domínio fechado. A validação recusa valor fora da faixa e rótulo não
declarado, antes de qualquer inferência.""",
        accent=BLUE, widths=[4, 2, 4],
    )

    d.figure(
        "As 43 regras em cinco camadas",
        IMG_DIR / "02-expert-system.png",
        """Percorra as camadas de baixo para cima: medição vira qualidade de sinal,
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
            "R10:  SE  qualidade_do_sinal = poor",
            "      E   varredura_de_espectro = occupied",
            "      ENTÃO diagnóstico = rf_interference          (CF +0,85)",
            "",
            "R25:  SE  clima = clear",
            "      ENTÃO diagnóstico = rain_fade                (CF -0,80)",
            "      <- contra-evidência: torna a hipótese MENOS provável",
            "",
            "R36:  SE  ação_recomendada = change_channel",
            "      ENTÃO exige_autorização = yes                (CF +1,00)",
        ],
        """R10 é uma regra de diagnóstico comum: duas condições, uma conclusão, uma
confiança.

R25 é a mais interessante. O fator de certeza negativo diz "tempo limpo é
evidência CONTRA atenuação por chuva". Regras booleanas obrigariam a escolher
entre ignorar essa evidência e afirmar demais. E o especialista real raciocina
assim: certas observações reduzem a suspeita sem eliminá-la.

R36 é a porta de governança, e prepara o tema 2.""",
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
            "$ aisg diagnose --case interference --trace --explain",
            "",
            "* R01: premissa CF +1,00 × regra CF +0,90 => signal_quality = poor",
            "* R10: premissa CF +0,90 × regra CF +0,85 => diagnosis = rf_interference",
            "* R28: premissa CF +0,93 × regra CF +0,90 => ação = change_channel",
            "* R36: premissa CF +0,84 × regra CF +1,00 => autorização = yes",
            "",
            "diagnóstico:",
            "  rf_interference        CF +0,93  ###################",
            "  rain_fade              CF -0,80  -################",
        ],
        """Rode ao vivo. Percorra o trace regra a regra com o dedo na tela: a cadeia
inteira é legível, da medição até a exigência de autorização.

Aponte a última linha: rain_fade aparece com CF NEGATIVO. O sistema não apenas
escolheu uma hipótese — ele registrou evidência contra outra. Isso é o que
distingue um sistema com incerteza de um classificador que só devolve um rótulo.""",
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
            "$ aisg diagnose --interactive --mode backward",
            "",
            "Qual o estado do enlace [up, down, flapping]?",
            "  (Enter = não sei)   ('?' = por quê)",
            "> down",
            "",
            "Qual a situação de alimentação do nó [ok, on-battery, failed]?",
            "> ?",
            "",
            "Por que esta pergunta está sendo feita:",
            "  R16: SE alimentação_do_nó = failed ENTÃO node_power_failure (CF +0,95)",
            "> failed",
            "",
            "diagnóstico: node_power_failure (CF +0,95)  —  6 de 13 perguntas",
        ],
        """Este é o único momento não roteirizado da apresentação. Ensaie antes.

Digite "?" numa das perguntas para mostrar o "por quê": o motor exibe a cadeia
de regras que o levou até ali. Um sistema que só responde não é utilizável em
operação crítica; um que mostra o caminho pode ser auditado e contestado.

Aceita também uma certeza junto da resposta: "rain 0.6" informa chuva com
confiança 0,6.""",
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
        "Os oito casos de demonstração",
        ["Caso", "Diagnóstico", "CF", "Ação recomendada", "Autoriza?"],
        [
            ["interference", "rf_interference", "+0,93", "change_channel", "sim"],
            ["obstruction", "path_obstruction", "+0,91", "realign_antenna", "sim"],
            ["rain_fade", "rain_fade", "+0,56", "wait_and_monitor", "não"],
            ["power_failure", "node_power_failure", "+0,95", "dispatch_power_team", "sim"],
            ["relay_failure", "upstream_relay_failure", "+0,95", "restore_upstream_relay", "sim"],
            ["vlan", "vlan_misconfiguration", "+0,96", "fix_vlan_allowlist", "sim"],
            ["congestion", "congestion", "+0,89", "reroute_traffic", "sim"],
            ["healthy", "healthy", "+0,81", "no_action", "não"],
        ],
        """Oito casos, oito diagnósticos corretos. Mas o número a apontar é o de
rain_fade: CF +0,56, nitidamente mais baixo que os demais.

Isso não é um defeito — é o sistema admitindo que a evidência é fraca. Chuva com
margem estreita é mesmo evidência fraca. Um sistema que devolvesse +0,95 nesse
caso estaria mentindo.

Note também as duas linhas que não exigem autorização: observar, e não agir.""",
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
        IMG_DIR / "03-planning.png",
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
            "realign_antenna(?n)                                custo 3",
            "",
            "  precondições:   authorized(?n)",
            "                  crew-at(?n)",
            "                  misaligned(?n)",
            "",
            "  adiciona:     + fault-cleared(?n)",
            "",
            "  remove:       - misaligned(?n)",
            "",
            "  estado = { diagnosed(N), crew-at(BASE), misaligned(N) }",
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
        ["Operador", "Custo", "Equipe no local?", "Autorização?"],
        [
            ["request_authorization(?n)", "1", "não", "—"],
            ["dispatch_crew(?from, ?to)", "4", "—", "sim"],
            ["change_channel(?n)", "2", "não", "sim"],
            ["realign_antenna(?n)", "3", "SIM", "sim"],
            ["replace_power_unit(?n)", "5", "SIM", "sim"],
            ["restore_relay(?n)", "2", "não", "sim"],
            ["fix_vlan(?n)", "1", "não", "sim"],
            ["reroute_traffic(?n)", "2", "não", "sim + rota alternativa"],
            ["monitor_and_wait(?n)", "1", "não", "NÃO"],
            ["verify_link / record_logbook / close_work_order", "1", "não", "—"],
        ],
        """Não leia a tabela inteira. Aponte três coisas:

Primeiro, dispatch_crew custa 4 e replace_power_unit custa 5. Se toda ação
custasse 1, planejar seria contar passos — com custos diferentes, o planejador
precisa realmente pesar, e uma correção remota barata pode vencer uma correção
local aparentemente mais simples.

Segundo, quase toda linha exige autorização.

Terceiro, monitor_and_wait é a única exceção — e isso é deliberado.""",
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

A única exceção é monitor_and_wait, porque observar não altera a planta.""",
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
            "          operador candidato: replace_power_unit(RM_A5)",
            "            DIFERENÇA a reduzir: crew-at(RM_A5)",
            "              APLICA dispatch_crew(BASE, RM_A5)",
            "            já satisfeito: crew-at(BASE)",
        ],
        """Percorra o trace com o dedo. Cada linha "DIFERENÇA a reduzir" é uma pergunta;
cada "operador candidato" é uma tentativa de resposta; e a recursão termina
quando a diferença desaparece — aqui, quando descobrimos que a equipe já está na
base.

O plano final é a pilha desfeita na ordem inversa.

$ aisg plan --diagnosis node_power_failure --node RM_A5 --solver gps --trace""",
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

É exatamente por isso que os dois planejadores convivem no mesmo repositório: um
explica, o outro garante.""",
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
            "$ aisg plan --diagnosis node_power_failure --node RM_A5 --solver both",
            "",
            " 1. request_authorization(RM_A5)   [1]",
            " 2. dispatch_crew(BASE, RM_A5)     [4]",
            " 3. replace_power_unit(RM_A5)      [5]",
            " 4. verify_link(RM_A5)             [1]",
            " 5. record_logbook(RM_A5)          [1]",
            " 6. close_work_order(RM_A5)        [1]",
            "    custo total: 13",
            "",
            "Validação: o plano é executável e atinge o objetivo.",
        ],
        """Rode ao vivo. Note a ordem: autorização primeiro, deslocamento depois, reparo,
verificação, registro, encerramento.

Sobre validação: um plano só vale se for executável passo a passo E atingir o
objetivo. Plan.validate() reexecuta o plano desde o estado inicial e aponta o
primeiro passo inaplicável com a precondição que faltou.

Dois testes corrompem planos de propósito — um remove a autorização, outro
remove o encerramento — para provar que a validação apanha os dois defeitos.""",
        accent=GREEN,
    )

    d.statement(
        "O sistema também sabe quando NÃO agir",
        "Para atenuação por chuva, o plano correto não toca a planta e não desloca equipe.",
        """Rode: aisg plan --diagnosis rain_fade --solver astar

O plano tem quatro ações e nenhuma delas alcança a planta: monitorar, verificar,
registrar, encerrar. Não há deslocamento de equipe e não há autorização, porque
observar não altera nada.

A causa é transitória. Intervir seria tratar o clima.

Saber quando não agir é tão importante quanto saber agir — e num sistema de
recomendação operacional, é a diferença entre útil e perigoso.""",
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
        IMG_DIR / "04-astar.png",
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
        "Cinco estratégias, o mesmo problema: NOC → RECLOSER_7",
        ["Estratégia", "Passos", "Custo (ms)", "Expandidos", "Ótimo?"],
        [
            ["Largura (BFS)", "4", "357,35", "15", "só em passos"],
            ["Profundidade (DFS)", "5", "343,06", "19", "não"],
            ["Custo uniforme", "4", "92,22", "13", "sim"],
            ["Gulosa", "4", "357,35", "5", "não"],
            ["A*", "4", "92,22", "11", "sim"],
        ],
        """Esta tabela é o centro do tema 3. Leia as três lições:

Primeira: a busca em largura minimiza SALTOS, não custo. Quatro saltos por 357
ms, quase quatro vezes o ótimo — porque conta um salto de fibra e um salto de
rádio armazena-e-encaminha como iguais.

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
            "NOC -> LTE_CORE -> LTE_ENB -> RM_A5 -> RECLOSER_7        92,22 ms",
            "",
            "salto                  meio                 qual.   custo    acum.",
            "NOC -> LTE_CORE        ethernet local        1,00     5,99     5,99",
            "LTE_CORE -> LTE_ENB    fibra óptica          0,95    10,55    16,54",
            "LTE_ENB -> RM_A5       LTE privativo         0,80    69,94    86,48",
            "RM_A5 -> RECLOSER_7    ethernet local        1,00     5,74    92,22",
        ],
        """O caminho ótimo evita inteiramente a cadeia armazena-e-encaminha e desce pela
sobreposição LTE.

Repare que o salto LTE domina o custo — 70 dos 92 ms. Ainda assim, é mais barato
que três saltos de repetidor, cada um pagando 25 ms só de sobrecarga por
terminar e retransmitir o quadro.

Este é o tipo de conclusão que um operador de rede tiraria de um estudo de
planejamento — e o algoritmo chegou a ela sozinho.""",
        accent=AMBER,
    )

    d.table(
        "A vantagem da heurística cresce com o grafo",
        ["Cenário", "Nós", "A* expandidos", "Custo uniforme", "Economia"],
        [
            ["base", "17", "1 382", "1 519", "9,0 %"],
            ["escala", "30", "5 571", "7 657", "27,2 %"],
        ],
        """Um único par pode ser sorte. Estes números somam TODOS os pares
origem-objetivo de cada cenário.

A economia agregada triplica ao passar de 17 para 30 nós. É o argumento prático
a favor do A* quando a rede cresce: num grafo pequeno, a busca cega é barata;
num grande, deixa de ser.

O teste test_the_heuristic_saves_more_work_as_the_graph_grows verifica essa
RELAÇÃO — que a economia cresce — e não os números específicos, que mudariam a
cada ajuste na topologia.

$ aisg --topology scale route --compare""",
        accent=AMBER, widths=[2.4, 1.4, 2.8, 2.8, 2.0], highlight=1,
    )

    d.code(
        "Falha e recálculo de rota",
        [
            "$ aisg route --from NOC --to RECLOSER_7 --disable-link LTE_ENB-RM_A5",
            "",
            "antes : 92,22 ms   NOC -> LTE_CORE -> LTE_ENB -> RM_A5 -> RECLOSER_7",
            "depois: ~357 ms    NOC -> AP_B -> RM_B3 -> SAF_A2 -> RECLOSER_7",
            "",
            "Sem a sobreposição LTE, o caminho passa a usar a cadeia",
            "armazena-e-encaminha — e o custo quase quadruplica.",
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
            "$ aisg pipeline --case congestion --node SAF_A2",
            "",
            "1/3  diagnóstico ......... congestion (CF +0,89)",
            "     ação recomendada .... reroute_traffic (CF +0,71)",
            "",
            "2/3  rota alternativa confirmada pelo A*: True",
            "     plano com 5 ações, custo 6, validado",
            "",
            "3/3  rota evitando SAF_A2:",
            "     NOC -> LTE_CORE -> LTE_ENB -> RM_A5 -> RECLOSER_7   92,22 ms",
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
            "O sistema recomenda, não atua — no planejador isso não é conselho: é precondição",
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
