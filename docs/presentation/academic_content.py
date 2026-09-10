"""Single editorial source for the academic deck and its Portuguese speaking script."""

SLIDES = []


def add(section, title, kind, content, speech, cue="", source=""):
    SLIDES.append(dict(section=section, title=title, kind=kind, content=content,
                       speech=speech.strip(), cue=cue, source=source))


add("ABERTURA", "Sistema especialista, planejamento automático e busca A*", "cover",
    {"subtitle": "Gerenciamento de falhas em redes sem fio simuladas"},
    """Nesta apresentação, examino três problemas complementares de inteligência artificial: formular hipóteses de diagnóstico, construir uma sequência de ações e encontrar um caminho de menor custo. O domínio comum é uma representação computacional de testes de comunicação em ambiente interno.

O trabalho utiliza regras de produção, planejamento simbólico e busca heurística. O objetivo é apresentar as decisões de modelagem, demonstrar o comportamento dos algoritmos e delimitar o alcance dos resultados. Há uma distinção que acompanhará toda a exposição: um resultado correto no modelo não constitui, por si só, evidência de desempenho em uma instalação real.

As demonstrações foram organizadas para permitir a inspeção das entradas, das decisões intermediárias e das saídas. Assim, a avaliação pode considerar não apenas se o programa produz uma resposta, mas também se essa resposta corresponde ao problema formalizado e se pode ser reproduzida.""",
    "Apresentar o tema e explicitar que os exemplos são computacionais e ilustrativos.")

add("ÍNDICE", "Estrutura da apresentação", "agenda", [
    ["1", "Fundamentos e domínio", "Problema, cenário e grandezas de comunicação"],
    ["2", "Sistema especialista", "Representação, inferência e fatores de certeza"],
    ["3", "Planejamento automático", "STRIPS, análise meios-fins e busca progressiva"],
    ["4", "Busca A*", "Caminho, garantias e comparação experimental"],
    ["5", "Integração e avaliação", "Contratos, reprodução e limites de validade"],
    ["6", "Síntese e continuidade", "Contribuições e agenda de investigação"],
    ["7", "Referências e discussão", "Fundamentação e questões para debate"],
], """A exposição está dividida em sete partes. Primeiro, estabeleço o problema e a semântica das grandezas utilizadas. Em seguida, apresento os três minissistemas, mantendo uma sequência comum: representação, procedimento de solução, demonstração e limites.

No sistema especialista, a questão central é como justificar uma hipótese diante de evidências incompletas. No planejamento, é como ordenar ações que possuem precondições e efeitos. Na busca A*, é como obter uma rota de menor custo com uma heurística cuja validade possa ser demonstrada.

Ao final, reúno os módulos em um incidente e discuto a metodologia de avaliação. O roteiro reserva tempo para examinar os resultados das demonstrações; não é necessário ler integralmente o código durante a apresentação. As notas detalhadas e os comandos ficam disponíveis no roteiro em Markdown, com numeração correspondente aos slides.""")

add("1 · FUNDAMENTOS E DOMÍNIO", "Problema e questão de investigação", "statement", {
    "statement": "Como produzir recomendações justificáveis de diagnóstico, intervenção e roteamento sob hipóteses explícitas?",
    "items": ["Diagnóstico: quais hipóteses são sustentadas pelas evidências?",
              "Planejamento: quais ações satisfazem o objetivo e as restrições?",
              "Busca: qual caminho minimiza o custo definido no modelo?"],
    "takeaway": "A integração exige coerência entre evidências, estados, ações e objetivos."},
    """A questão de investigação não é simplesmente se três algoritmos podem ser implementados em Python. Ela trata da coerência entre diferentes formas de representar e resolver um mesmo incidente.

O diagnóstico trabalha com observações e graus de suporte. O planejador recebe uma descrição discreta do estado e considera efeitos determinísticos. O roteador opera sobre um grafo ponderado. Essas representações não são equivalentes e a transformação entre elas precisa ser explicitada.

Por exemplo, um fator de certeza elevado para congestionamento não demonstra automaticamente que existe uma rota alternativa. Essa existência depende de uma consulta ao grafo. Da mesma forma, uma rota existente não demonstra que a intervenção recuperará o serviço em uma rede real. A contribuição do trabalho consiste em tornar verificáveis essas relações dentro do modelo adotado, preservando a diferença entre hipótese, condição de planejamento e resultado calculado.""")

add("1 · FUNDAMENTOS E DOMÍNIO", "Escopo: testes internos representados em software", "cards", [
    ["Implementação disponível", "Regras em Python; estados STRIPS; topologia sintética; algoritmos e testes automatizados."],
    ["Exemplos ilustrativos", "Casos definidos manualmente, limiares nominais e custos convencionais. Não são medições experimentais."],
    ["Extensão experimental", "Execuções de simulador, traços por pacote, replicações e calibração exigem uma campanha própria."],
], """O cenário principal desta apresentação é uma simulação em software de testes internos. No estágio documentado, o repositório oferece uma camada simbólica em Python e uma topologia sintética. Os casos de diagnóstico foram construídos como exemplos ilustrativos.

A referência ao ns-3 indica uma possível infraestrutura para uma campanha de simulação de redes. Entretanto, a presença desse nome em comentários ou diagramas não comprova que tenham sido executados experimentos nesse simulador. Não apresento os valores dos exemplos como saídas de uma execução de ns-3.

Também não utilizo fenômenos meteorológicos como explicação principal, pois eles não integram o recorte escolhido. A exclusão é uma decisão de modelagem; não é uma afirmação geral sobre tudo o que um simulador poderia representar. Essa delimitação permite avaliar com precisão o que já foi implementado e o que depende de trabalho experimental adicional.""")

add("1 · FUNDAMENTOS E DOMÍNIO", "Topologia sintética e unidade de análise", "topology", {
    "items": ["60 nós e 74 enlaces ativos no cenário selecionado.",
              "Quinze sites com duplo acesso: pLTE e 900 MHz.",
              "Coordenadas e qualidades convencionais.",
              "Unidade de análise: incidente associado a um nó ou fluxo."],
    "takeaway": "Esquema lógico do cenário; não constitui planta de laboratório nem traço de simulação."},
    """A topologia organiza sessenta nós em duas redes de acesso independentes que alcançam os mesmos quinze sites da rede elétrica. De um lado, uma estrela de LTE privativo com dois eNodeBs e um nível de repetidores. Do outro, uma malha de 900 MHz do tipo armazena-e-encaminha. As duas se encontram apenas no roteador de borda de cada site.

Essa estrutura é deliberada, e corrige um defeito do cenário anterior. Ali o eNodeB aparecia como vértice de trânsito, o que permitia caminhos que entravam pelo LTE e saíam por outro meio sem passar pelo núcleo. Um eNodeB é nó de acesso, não roteador de trânsito entre assinantes.

O roteador de borda também não faz trânsito. Ele é a fronteira da rede elétrica, e um site não transporta o tráfego de backhaul de um site vizinho. Essa restrição está declarada no modelo e é respeitada tanto pela busca quanto pelo oráculo de verificação.

Os identificadores permitem acompanhar um incidente entre os módulos. ER_03 será utilizado no exemplo de contenção, enquanto outros pares ilustrarão a seleção de rotas. As coordenadas pertencem ao modelo e não descrevem posicionamento de equipamentos reais.

É importante separar o tamanho do grafo da quantidade de observações de diagnóstico. Ter sessenta nós não significa dispor de sessenta amostras independentes de falha. Avaliar todos os pares de roteamento examina um conjunto de problemas sobre o mesmo grafo, e não uma coleção de redes independentes.""",
    "Identificar NOC, um ponto de acesso, um repetidor e uma rota alternativa.",
    "Repositório: src/aisg/domain/data/backhaul-topology-30.json")

add("1 · FUNDAMENTOS E DOMÍNIO", "Grandezas físicas: definição e interpretação", "table", {
    "headers": ["Grandeza", "Definição técnica", "Interpretação"],
    "rows": [
        ["RSSI (dBm)", "Indicador de potência recebida, referido a 1 mW.", "Valores mais negativos indicam menor potência recebida."],
        ["SNR (dB)", "Relação entre a potência do sinal de interesse e a potência do ruído.", "Valores reduzidos podem elevar a ocorrência de erros de recepção."],
        ["Perda de percurso (dB)", "Atenuação no percurso de propagação modelado.", "Maior perda reduz a potência recebida, mantidas as demais condições."],
    ], "widths": [2.25, 4.65, 4.85],
    "takeaway": "excess_path_loss_db representa perda adicional configurada; não a perda total do percurso."},
    """Antes de interpretar os indicadores, precisamos distinguir as grandezas físicas. RSSI é um indicador de potência recebida. Quando expresso em dBm, utiliza um miliwatt como referência. Portanto, menos noventa dBm representa uma potência menor do que menos setenta dBm.

A SNR expressa uma razão entre sinal e ruído. Ela não é sinônimo de potência recebida: é possível receber um sinal relativamente forte e, ainda assim, enfrentar uma relação sinal-ruído inadequada. Quando a interferência é explicitamente incluída no denominador, a grandeza correspondente é a SINR; não devemos trocar esses nomes sem especificar a medição.

A perda de percurso descreve atenuação. No repositório, a variável de interesse é a perda adicional configurada, indicada pelo prefixo excess. Essa distinção evita interpretar zero decibel de perda adicional como ausência de toda perda de propagação. Os valores são entradas do exemplo e seus limiares ainda precisam de calibração.""")

add("1 · FUNDAMENTOS E DOMÍNIO", "Indicadores de acesso ao meio e desempenho", "table", {
    "headers": ["Indicador", "Definição operacional", "Possíveis associações"],
    "rows": [
        ["Retransmissões MAC (%)", "Percentual segundo a unidade e o denominador de contagem definidos.", "Contenção, colisões ou falhas de recepção."],
        ["Perda de pacotes (%)", "Pacotes não recebidos em relação aos enviados, com prazo de avaliação.", "Descarte, falhas de enlace ou indisponibilidade de rota."],
        ["RTT (ms)", "Intervalo entre o envio e o recebimento da resposta correspondente.", "Filas, retransmissões, processamento e percurso."],
        ["Carga oferecida (%)", "Taxa de tráfego oferecida dividida pela capacidade de referência.", "Pressão sobre a capacidade efetiva e possível saturação."],
    ], "widths": [2.5, 5.1, 4.15],
    "takeaway": "Um indicador de degradação não identifica isoladamente sua causa."},
    """Na camada de acesso ao meio, a taxa de retransmissões informa que transmissões precisaram ser repetidas. Contudo, é necessário declarar o denominador: tentativas totais, quadros originais ou quadros que sofreram pelo menos uma repetição produzem métricas diferentes.

A perda de pacotes é uma propriedade da entrega segundo um critério temporal. Um pacote atrasado pode ser considerado perdido se ultrapassar o prazo definido. Já o RTT mede ida e volta, e não deve ser confundido com atraso unidirecional.

A carga oferecida depende da capacidade escolhida como referência. Cem por cento não é um limiar universal de saturação, porque a capacidade efetiva pode ser menor em função de sobrecargas e condições do meio.

Esses indicadores motivam hipóteses, mas não são identificadores causais exclusivos. Retransmissões elevadas, por exemplo, podem decorrer de contenção ou de falhas de recepção. É justamente a combinação das evidências que o sistema especialista procura explicitar.""")

add("1 · FUNDAMENTOS E DOMÍNIO", "Observações, intervenções e informação desconhecida", "cards", [
    ["Observação", "Valor, unidade, sujeito, janela temporal e procedência devem identificar a evidência."],
    ["Intervenção", "Parâmetros configurados e falhas introduzidas pertencem ao controle do experimento."],
    ["Desconhecido", "Ausência de observação não equivale a valor zero nem à negação de uma hipótese."],
], """Uma entrada numérica não está completamente definida apenas pelo seu valor. Para interpretar um RTT, por exemplo, precisamos conhecer o par de comunicação, a janela de observação e o procedimento de agregação. Esses metadados são parte do contrato experimental proposto.

Também separo observações de intervenções. Saber que um emissor interferente foi ativado é informação do controle do cenário. Essa informação pode ser utilizada em um diagnóstico assistido, desde que isso seja declarado. Se o objetivo for avaliar diagnóstico apenas por telemetria, fornecer ao sistema o parâmetro que introduziu a falha pode revelar indiretamente o rótulo esperado.

Por fim, o desconhecido deve permanecer explícito. A falta de resposta a uma pergunta não deve ser convertida automaticamente em condição saudável. O motor admite premissas desconhecidas, enquanto o planejador usa uma representação discreta com outra semântica. A passagem entre essas duas representações requer uma política de seleção e validação.""")

add("1 · FUNDAMENTOS E DOMÍNIO", "Três representações, três critérios de correção", "cards", [
    ["Sistema especialista", "Fatos e regras → hipóteses graduadas\nCritério: aplicação rastreável da base de conhecimento."],
    ["Planejamento", "Estado, ações e objetivo → plano\nCritério: aplicabilidade e satisfação do objetivo."],
    ["Busca A*", "Grafo e custos → caminho\nCritério: conectividade e custo mínimo sob as condições da heurística."],
], """Os três módulos compartilham um domínio, mas seus critérios de correção são diferentes. Para o sistema especialista, verifico se a conclusão decorre das regras e dos fatos segundo a álgebra adotada. Isso não comprova que a hipótese seja verdadeira no mundo.

No planejamento, verifico se cada ação é aplicável no estado em que ocorre e se o estado final satisfaz o objetivo. Essa validação pressupõe que os efeitos declarados descrevem adequadamente as ações.

Na busca, verifico se os pares consecutivos pertencem ao grafo e se o custo corresponde ao mínimo para aquela instância. A otimalidade se refere à função de custo especificada, não a toda dimensão possível de qualidade de serviço.

A integração, portanto, não elimina as diferenças entre os módulos. Ela deve preservar essas diferenças e tornar explícitas as condições sob as quais uma saída pode ser utilizada como entrada da etapa seguinte.""")

add("1 · FUNDAMENTOS E DOMÍNIO", "Escolha metodológica e alcance das evidências", "table", {
    "headers": ["Decisão", "Justificativa", "Limite"],
    "rows": [
        ["Regras explícitas", "Conhecimento inspecionável e exemplos reproduzíveis.", "Regras e limiares podem incorporar erros e lacunas."],
        ["Planejamento simbólico", "Precondições e efeitos permitem validar sequências.", "Efeitos determinísticos simplificam a execução."],
        ["A* com limite inferior", "Busca informada com condições de otimalidade explicitadas.", "Garantia condicionada ao modelo de custo."],
        ["Casos ilustrativos", "Verificação de comportamento e comunicação dos conceitos.", "Não estimam acurácia em uma população operacional."],
    ], "widths": [2.4, 4.8, 4.55]},
    """A escolha por regras explícitas é adequada ao objetivo didático de inspecionar a inferência. Ela não implica que métodos de aprendizagem sejam inviáveis ou necessariamente menos explicáveis. Regras também podem produzir respostas incorretas com elevado suporte quando a base está equivocada.

O planejamento simbólico permite tratar restrições de ordem como propriedades verificáveis. Em contrapartida, pressupõe um modelo simplificado de execução. A busca A* oferece uma relação clara entre função de avaliação e garantia de custo, desde que as condições da heurística sejam atendidas.

Os casos ilustrativos sustentam verificações internas, como a aplicação de uma regra ou a sequência de reparo. Eles não constituem uma amostra independente para estimar desempenho de diagnóstico. Uma investigação posterior precisará produzir dados, separar desenvolvimento e avaliação e analisar a sensibilidade aos parâmetros. Com essa delimitação, passo ao primeiro minissistema.""")

add("2 · SISTEMA ESPECIALISTA", "Diagnóstico baseado em regras de produção", "statement", {
    "statement": "Uma hipótese deve ser acompanhada das evidências e regras que a sustentam.",
    "items": ["41 regras na base do cenário simulado.", "Oito casos ilustrativos, incluindo a condição saudável.", "Encadeamento progressivo e regressivo sobre o mesmo motor."],
    "takeaway": "A rastreabilidade da inferência é verificável; a validade diagnóstica exige avaliação independente."},
    """O primeiro minissistema representa conhecimento por regras de produção. A base selecionada para o cenário simulado contém quarenta e uma regras e contempla oito situações ilustrativas, incluindo a condição saudável.

As regras relacionam indicadores de comunicação, qualificações intermediárias e hipóteses de falha. Outras regras associam hipóteses a ações recomendadas e à necessidade de autorização. A base é separada do mecanismo de inferência, o que permite executar diferentes conhecimentos sobre o mesmo motor.

A saída inclui graus de suporte e mecanismos de explicação. Isso permite responder de que fatos uma conclusão dependeu e quais regras foram aplicadas. Entretanto, explicar o procedimento não equivale a validar o conhecimento. Uma regra inadequada continua sendo inadequada mesmo quando sua aplicação é perfeitamente rastreável. Por isso, a análise do sistema considera tanto a implementação quanto a procedência e a validação futura das regras.""",
    source="Implementação: src/aisg/expert_system/kb_simulated.py")

add("2 · SISTEMA ESPECIALISTA", "Arquitetura e separação de responsabilidades", "flow", {
    "steps": [["Entradas", "Valores e respostas"], ["Memória", "Fatos e suporte"], ["Inferência", "Seleção e aplicação"], ["Saídas", "Hipóteses e explicação"]],
    "items": ["Base de conhecimento: variáveis, regras e limiares.", "Motor: avaliação de condições, conflito e propagação de suporte.", "Explicação: procedência das conclusões e justificativa das perguntas."],
    "takeaway": "Alterar o conhecimento do domínio não exige substituir o algoritmo de inferência."},
    """A arquitetura separa o que é conhecimento específico do domínio do que é procedimento geral. A base define as variáveis, os limiares e as regras. A memória de trabalho armazena os fatos da consulta e suas contribuições de suporte.

O motor avalia condições, constrói o conjunto de regras aplicáveis e seleciona qual regra será disparada. O resultado atualiza a memória e pode habilitar novas inferências. O módulo de explicação utiliza essa procedência para apresentar a justificativa das conclusões.

Essa separação facilita manutenção e análise. Podemos examinar uma alteração de limiar sem atribuí-la a uma mudança no algoritmo. Também podemos comparar políticas de resolução de conflito preservando a mesma base. Na prática, ainda é necessário controlar a versão de ambos, porque o resultado depende tanto das regras quanto da semântica implementada pelo motor. A demonstração registra os dois componentes para permitir sua reprodução.""")

add("2 · SISTEMA ESPECIALISTA", "Organização da base de conhecimento", "flow", {
    "steps": [["Qualidade", "RSSI e SNR"], ["Sintomas", "Perda e atraso"], ["Diagnóstico", "Hipóteses concorrentes"], ["Recomendação", "Ação e autorização"]],
    "items": ["Condições intermediárias reduzem repetição de conhecimento.", "Regras de contraevidência podem reduzir o suporte de hipóteses.", "Indicadores correlacionados exigem cuidado na agregação."],
    "takeaway": "A estrutura em camadas organiza o raciocínio; não demonstra independência causal."},
    """A base utiliza conclusões intermediárias para organizar a inferência. RSSI e SNR contribuem para uma classificação de qualidade do sinal. Perda e atraso contribuem para a identificação de sintomas. Essas conclusões, combinadas com informações do cenário, sustentam hipóteses de diagnóstico.

Há também regras de contraevidência. Elas representam condições que enfraquecem uma hipótese segundo o conhecimento codificado. Por exemplo, uma taxa baixa de retransmissão reduz o suporte à hipótese de contenção na base atual.

A organização em camadas evita repetir as mesmas condições em várias regras, mas cria dependências entre conclusões. Dois caminhos de inferência podem reutilizar a mesma observação original. Consequentemente, o fato de haver duas regras favoráveis não significa que existam duas evidências independentes. A análise de dependência e redundância é parte importante da revisão de uma base que utiliza agregação numérica de suporte.""")

add("2 · SISTEMA ESPECIALISTA", "Variáveis observáveis e parâmetros do cenário", "table", {
    "headers": ["Grupo", "Exemplos no código", "Papel na inferência"],
    "rows": [
        ["Condições de recepção", "rssi_dbm; snr_db", "Qualificação do sinal."],
        ["Desempenho", "retry_rate_pct; packet_loss_pct; rtt_ms", "Sintomas e hipóteses concorrentes."],
        ["Carga", "offered_load_pct", "Pressão sobre a capacidade de referência."],
        ["Controle do cenário", "excess_path_loss_db; co_channel_emitter", "Informação assistida sobre a intervenção."],
        ["Disponibilidade", "node_responding; route_present", "Distinção entre nó, percurso e encaminhamento."],
    ], "widths": [2.5, 5.25, 4.0],
    "takeaway": "Os intervalos aceitos pela implementação não são faixas validadas de operação."},
    """Esta tabela mostra grupos de entradas, não uma lista de sensores já integrados. No estágio atual, os exemplos fornecem valores diretamente ao motor. Uma conexão experimental exigirá definir como cada variável será extraída e agregada.

As entradas de recepção ajudam a qualificar o sinal. Os indicadores de desempenho descrevem consequências observáveis. Os parâmetros de controle, como a perda adicional configurada, podem fornecer informação direta sobre uma intervenção. Isso torna a consulta assistida mais informativa, mas modifica a dificuldade do problema de diagnóstico.

As variáveis de disponibilidade também precisam de interpretação contextual. Um nó que não responde pode estar parado ou inacessível pelo percurso utilizado. O sistema representa essas possibilidades por hipóteses distintas, mas não prova sua exclusividade. Para avaliar diagnóstico cego, eu separaria os parâmetros conhecidos pelo experimentador das variáveis disponibilizadas ao sistema e registraria essa separação no protocolo.""")

add("2 · SISTEMA ESPECIALISTA", "Regra de diagnóstico e contraevidência", "code", {
    "code": "S14: SE retry_rate_pct > 30\n     E signal_quality != poor\n     E co_channel_emitter = no\n     ENTÃO diagnosis = mac_contention    CF = +0,85\n\nS25: SE retry_rate_pct <= 30\n     ENTÃO diagnosis = mac_contention    CF = −0,80",
    "items": ["Os limiares e pesos são nominais.", "A regra expressa uma associação heurística explicitamente revisável."],
    "takeaway": "O diagnóstico é uma hipótese sustentada pelo modelo, não uma identificação causal exclusiva."},
    """A regra S14 associa retransmissão elevada, ausência de classificação pobre do sinal e ausência de emissor cocanal à hipótese de contenção. O peso positivo indica a intensidade de suporte atribuída a essa associação.

A regra S25 tem outra função: retransmissão abaixo do limiar é contraevidência para a mesma hipótese. Seu fator de certeza negativo pode reduzir o suporte agregado.

Há dois cuidados conceituais. Primeiro, o limiar de trinta por cento não deve ser apresentado como constante universal de comunicação sem fio. Ele é um parâmetro nominal da base. Segundo, a expressão diferente de poor não autoriza concluir que qualquer condição desconhecida é boa. Sua avaliação depende da semântica implementada e dos fatos disponíveis.

Essas regras são úteis porque tornam discutível uma decisão que, de outra forma, poderia ficar implícita. Podemos revisar o limiar, o peso ou as condições e observar como isso altera as hipóteses produzidas.""",
    "Ler a primeira regra e solicitar uma interpretação antes de mostrar a função da contraevidência.")

add("2 · SISTEMA ESPECIALISTA", "Fatores de certeza: significado e limites", "cards", [
    ["Escala de suporte", "CF ∈ [−1, +1]\nValores positivos apoiam; negativos contrariam a conclusão no formalismo."],
    ["Interpretação", "CF = 0,94 não significa 94% de probabilidade de acerto nem confiança estatística de 94%."],
    ["Validação", "Pesos e limiares precisam de revisão; evidências dependentes podem inflar o suporte agregado."],
], """O fator de certeza é uma escala de suporte utilizada pelo mecanismo de inferência. Valores positivos representam apoio à conclusão e valores negativos representam oposição. Os extremos são estados do formalismo; não garantem verdade ou falsidade empírica.

Essa distinção é essencial ao apresentar um valor como zero vírgula noventa e quatro. Não afirmo que a hipótese tenha noventa e quatro por cento de probabilidade de estar correta, nem que o resultado possua um intervalo de confiança de noventa e quatro por cento. Essas interpretações exigiriam uma modelagem e uma calibração diferentes.

A inspiração histórica está nos sistemas baseados em regras associados ao MYCIN. No projeto, essa escolha favorece uma demonstração explícita de combinação de suporte. Contudo, ela não elimina a necessidade de tratar dependência entre evidências. Também não impede alternativas probabilísticas: probabilidades e priors podem ser estimados ou elicitados, desde que suas hipóteses e fontes sejam justificadas.""",
    source="Shortliffe e Buchanan (1975), reimpresso em Rule-Based Expert Systems, cap. 11.")

add("2 · SISTEMA ESPECIALISTA", "Propagação e combinação de suporte", "formula", {
    "formula": "CFpremissa = min(CF₁, …, CFₖ)\nCFcontribuição = CFpremissa × CFregra",
    "items": ["Premissa acima de 0,2: regra elegível ao disparo.",
              "Duas contribuições positivas: a ⊕ b = a + b(1 − a).",
              "Exemplo: 0,60 × 0,80 = 0,48; 0,48 ⊕ 0,30 = 0,636."],
    "takeaway": "O cálculo demonstra a álgebra adotada; não calibra o significado empírico do resultado."},
    """A implementação atribui à conjunção o menor suporte de suas condições. Trata-se de uma escolha do formalismo, que representa a premissa como limitada por sua condição menos sustentada. O suporte da contribuição é o produto desse valor pelo peso da regra.

No exemplo, uma premissa com suporte de zero vírgula sessenta e uma regra com peso de zero vírgula oitenta produzem uma contribuição de zero vírgula quarenta e oito. Se outra regra contribui com zero vírgula trinta para a mesma conclusão, a combinação positiva resulta em zero vírgula seiscentos e trinta e seis.

O aumento é subaditivo e permanece limitado pela escala. Isso não significa que a segunda contribuição seja independente da primeira. Essa é uma questão da base de conhecimento. O sistema também utiliza um limiar de disparo, acima de zero vírgula dois, que deve ser incluído em análises de sensibilidade porque pode alterar quais cadeias de inferência são exploradas.""",
    "Calcular 0,48 + 0,30 × 0,52 com a audiência; separar cálculo e interpretação.")

add("2 · SISTEMA ESPECIALISTA", "Contraevidência e dependência entre regras", "formula", {
    "formula": "Sinais opostos: a ⊕ b = (a + b) / [1 − min(|a|, |b|)]",
    "items": ["Exemplo: +0,80 combinado com −0,50 resulta em +0,60.",
              "Para dois valores negativos: a ⊕ b = a + b(1 + a).",
              "Conflito extremo (+1, −1): a implementação adota 0 por convenção."],
    "takeaway": "Reutilizar uma observação em várias regras não cria novas evidências independentes."},
    """Quando as contribuições possuem sinais opostos, a combinação reduz o suporte de acordo com a expressão apresentada. Com zero vírgula oitenta e menos zero vírgula cinquenta, o numerador é zero vírgula trinta e o denominador é zero vírgula cinquenta. O resultado é zero vírgula sessenta.

No conflito entre mais um e menos um, o denominador se anula. O código trata esse caso retornando zero. É uma convenção de implementação que deve ser documentada, e não uma resolução epistemológica automática da contradição.

Uma limitação adicional é a dependência entre regras. Se perda elevada e retransmissão elevada decorrem do mesmo mecanismo, agregá-las como apoios separados pode amplificar o suporte. Uma avaliação mais rigorosa pode remover regras redundantes, introduzir casos contraditórios e comparar o resultado antes e depois da remoção. A finalidade é examinar se a conclusão permanece sustentada quando a mesma informação deixa de ser contada por múltiplos caminhos.""")

add("2 · SISTEMA ESPECIALISTA", "Encadeamento progressivo e resolução de conflito", "table", {
    "headers": ["Etapa ou política", "Procedimento", "Consequência"],
    "rows": [
        ["Ciclo de inferência", "Avaliar condições; selecionar e disparar uma regra.", "Atualização inspecionável da memória."],
        ["Ordem de declaração", "Priorizar a primeira regra elegível.", "Dependência explícita da organização da base."],
        ["Especificidade", "Priorizar regras com mais condições; desempates definidos.", "Favorecimento de antecedentes mais específicos."],
        ["Recência", "Priorizar regras apoiadas em fatos mais recentes.", "Ênfase na atualização da memória."],
    ], "widths": [2.65, 5.0, 4.1],
    "takeaway": "A invariância do resultado entre políticas deve ser testada, especialmente com contraevidência."},
    """O encadeamento progressivo parte dos fatos disponíveis. Em cada ciclo, o motor identifica as regras cujas premissas possuem suporte suficiente, seleciona uma delas e atualiza a memória.

A seleção utiliza uma política de resolução de conflito. A ordem de declaração é simples e previsível. A especificidade prioriza regras com mais condições. A recência considera os fatos mais recentes. Essas políticas não devem ser confundidas com critérios de verdade: uma regra mais específica não é necessariamente mais correta.

A implementação permite novo disparo quando a premissa se fortalece, substituindo a contribuição associada à regra. Entretanto, esse mecanismo não equivale a um sistema geral de revisão de crenças capaz de propagar qualquer enfraquecimento ou retração. Também há um limite de ciclos. Portanto, não afirmo invariância universal em relação à ordem de disparo. A propriedade deve ser examinada para as condições efetivamente avaliadas.""")

add("2 · SISTEMA ESPECIALISTA", "Demonstração: hipótese de contenção MAC", "code", {
    "code": "python docs/presentation/presentation_demo.py diagnose\n\ndiagnosis             mac_contention       CF +0,94125\nrecommended_action    separate_channels    CF +0,80006\nauthorization_required yes",
    "items": ["Entrada: caso ilustrativo mac_contention.", "Saída: hipótese, ação recomendada e necessidade de autorização.", "A autorização exigida não significa autorização concedida."],
    "takeaway": "Valores calculados pela base simulada em Python; não são medições de acurácia."},
    """Nesta demonstração, forneço ao motor os fatos do caso ilustrativo de contenção. O resultado principal é a hipótese mac_contention, com suporte aproximado de zero vírgula noventa e quatro. A ação recomendada é separar os canais, cujo suporte deriva da cadeia de inferência correspondente.

O campo de autorização informa que a intervenção exige autorização. Ele não concede uma permissão e não substitui um processo de controle externo. Essa distinção evita transformar uma recomendação lógica em uma aprovação operacional.

Ao executar o exemplo, observo a procedência das conclusões e a relação entre os suportes. O valor da ação não precisa ser igual ao do diagnóstico, porque há um peso adicional na regra que os relaciona. O resultado apresentado é reproduzível a partir dos fatos e da base disponíveis. Ele demonstra o funcionamento da inferência nesse caso, mas não estima a frequência de acerto em situações novas.""",
    "Executar o comando; examinar o diagnóstico e a explicação. Reservar tempo para comparar com o slide.")

add("2 · SISTEMA ESPECIALISTA", "Encadeamento regressivo e consulta orientada", "flow", {
    "steps": [["Objetivo", "Variável a estabelecer"], ["Regras", "Conclusões pertinentes"], ["Premissas", "Perguntas necessárias"], ["Resultado", "Suporte e justificativa"]],
    "items": ["Condição refutada interrompe a avaliação da regra.", "O usuário pode declarar desconhecimento.", "O corte de suficiência, por padrão CF ≥ 0,9, limita a exploração."],
    "takeaway": "Encerrar uma consulta por suficiência não prova que evidências futuras sejam irrelevantes."},
    """O encadeamento regressivo começa pela variável que se deseja estabelecer. O motor examina regras que podem concluí-la e procura obter as premissas necessárias. Quando uma condição é refutada, as demais condições daquela regra podem deixar de ser perguntadas.

Isso torna a consulta potencialmente mais econômica, porque ela não precisa coletar todas as variáveis antes de iniciar o raciocínio. O mecanismo de justificativa permite explicar por que uma pergunta está sendo feita, relacionando-a à regra em avaliação.

A implementação utiliza um corte de suficiência. Quando uma conclusão atinge o suporte configurado, a exploração pode terminar. Esse corte é uma decisão de controle computacional. Ele não demonstra que outra regra, uma contraevidência ou uma observação posterior seria incapaz de mudar a conclusão. Portanto, uma comparação entre os modos progressivo e regressivo deve considerar tanto o número de perguntas quanto as diferenças de suporte e de hipóteses exploradas.""")

add("2 · SISTEMA ESPECIALISTA", "Explicação, hipótese e identificação causal", "cards", [
    ["Como?", "Quais fatos, regras e contribuições produziram a conclusão?"],
    ["Por quê?", "Qual regra em avaliação motivou a solicitação de uma informação?"],
    ["Com que validade?", "A justificativa interna deve ser confrontada com intervenções e casos independentes."],
], """A explicação possui pelo menos dois usos. O primeiro é retrospectivo: mostrar como uma conclusão foi produzida. O segundo é prospectivo: justificar por que determinada informação está sendo solicitada durante uma consulta.

Esses recursos tornam a inferência auditável e ajudam a identificar regras inadequadas. Contudo, a explicação continua sendo interna ao modelo. Se uma regra associa um conjunto de sintomas a uma hipótese, a apresentação dessa regra não demonstra que a hipótese seja a única causa possível.

Para investigar identificação causal, seria necessário controlar intervenções, comparar condições e observar alternativas. Em uma simulação, por exemplo, podemos variar a carga mantendo outros parâmetros fixos e examinar se a resposta do sistema acompanha a mudança esperada. Também precisamos de casos em que mecanismos diferentes produzem sintomas semelhantes. A qualidade científica da explicação depende dessa possibilidade de contestação, e não apenas da legibilidade do texto gerado.""")

add("2 · SISTEMA ESPECIALISTA", "Resultados dos oito casos ilustrativos", "table", {
    "headers": ["Caso / hipótese principal", "CF", "Ação recomendada"],
    "rows": [
        ["Interferência cocanal", "+0,9295", "change_channel"],
        ["Perda adicional de percurso", "+0,9240", "restore_path_budget"],
        ["Contenção MAC", "+0,9413", "separate_channels"],
        ["Nó indisponível", "+0,8000", "restart_node"],
        ["Repetidor a montante indisponível", "+0,9750", "restore_upstream_relay"],
        ["Configuração de roteamento", "+0,9000", "fix_routing"],
        ["Congestionamento", "+0,8880", "reroute_traffic"],
        ["Condição saudável", "+0,8100", "no_action"],
    ], "widths": [5.1, 1.45, 5.2], "size": 17,
    "takeaway": "Resultados de casos construídos para verificação; não constituem estimativa de acurácia."},
    """A tabela reúne os resultados dos oito casos fornecidos com a base simulada. Em cada linha, apresento a hipótese principal, o suporte calculado e a ação recomendada. Os valores foram reproduzidos pela execução do motor.

É necessário interpretar corretamente o significado dessa coincidência entre o caso e a hipótese. Os exemplos foram construídos de forma compatível com as regras. Eles são úteis para verificar se a implementação realiza o comportamento pretendido, mas não formam um conjunto independente para avaliar generalização.

Também não interpreto a hipótese principal como prova de que todas as demais causas estão ausentes. A memória pode conter hipóteses concorrentes com suporte positivo ou negativo. Para um experimento de diagnóstico, seria preciso definir como selecionar uma saída, quando abster-se e como avaliar situações de múltiplas falhas. A próxima etapa de validação deve incluir casos ambíguos e observações não utilizadas na construção da base.""")

add("2 · SISTEMA ESPECIALISTA", "Avaliação crítica do sistema especialista", "table", {
    "headers": ["Dimensão", "Evidência disponível", "Avaliação adicional"],
    "rows": [
        ["Implementação", "Regras, CF, consultas e explicações executáveis.", "Casos contraditórios, retração e variação de políticas."],
        ["Conhecimento", "Limiar e peso explicitamente identificados.", "Revisão especializada e sensibilidade dos parâmetros."],
        ["Diagnóstico", "Oito casos ilustrativos com resultados reproduzíveis.", "Casos independentes, abstenção e falhas simultâneas."],
        ["Experimento", "Intervenções descritas como possibilidades do cenário.", "Traços, replicações e separação entre controle e observação."],
    ], "widths": [2.2, 4.65, 4.9]},
    """A avaliação do primeiro sistema distingue quatro dimensões. Na implementação, há procedimentos executáveis e testes que verificam aspectos da inferência. No conhecimento, os limiares e pesos são explícitos, mas permanecem nominais.

No diagnóstico, os casos ilustrativos demonstram comportamento esperado. Falta, entretanto, avaliar a resposta a casos independentes, perturbações e mecanismos concorrentes. Uma taxa de acerto calculada apenas sobre exemplos construídos junto com as regras produziria uma interpretação excessivamente favorável.

No experimento, existe uma descrição de condições que se pretende introduzir, mas uma descrição não substitui os registros de execução. O avanço metodológico consiste em produzir observações com procedência, separar a informação disponível ao sistema e definir previamente as métricas. Com essa distinção, é possível reconhecer a contribuição do protótipo sem atribuir a ele uma validação diagnóstica que ainda não foi realizada.""")

add("3 · PLANEJAMENTO AUTOMÁTICO", "Do diagnóstico à sequência de ações", "statement", {
    "statement": "Uma ação recomendada não determina, por si só, uma sequência executável.",
    "items": ["Estado inicial: diagnóstico selecionado e condições do cenário.", "Objetivo: service-restored(N) ∧ logged(N).", "Restrições: autorização modelada, parada, retomada e verificação."],
    "takeaway": "A seleção de hipóteses para o estado inicial é uma decisão explícita de integração."},
    """O segundo minissistema começa onde a recomendação isolada deixa de ser suficiente. Separar canais pode ser uma ação pertinente, mas precisamos determinar em que estado ela pode ocorrer e quais etapas devem precedê-la e sucedê-la.

O planejador recebe um estado inicial que contém uma ou mais falhas selecionadas. No cenário simulado, esse estado também identifica se a execução está ativa. O objetivo combina recuperação do serviço e registro da intervenção.

Há uma mudança de representação: o fator de certeza do diagnóstico não se transforma automaticamente em uma probabilidade de sucesso de ação. A interface seleciona uma hipótese e a converte em um predicado discreto. O plano é condicionado a essa escolha. Se o diagnóstico estiver errado ou incompleto, um plano formalmente válido pode ser inadequado ao incidente real. Essa condição precisa ser preservada na interpretação de todos os resultados apresentados.""")

add("3 · PLANEJAMENTO AUTOMÁTICO", "Modelo formal de planejamento STRIPS", "formula", {
    "formula": "P = ⟨F, A, I, G, c⟩\ns ⊆ F;  Pre(a) ⊆ s\nγ(s, a) = [s ∖ Del(a)] ∪ Add(a)",
    "items": ["F: fatos possíveis; A: ações; I: estado inicial; G: objetivo.", "Uma ação é aplicável quando suas precondições estão satisfeitas.", "Um plano é solução quando G ⊆ sfinal."],
    "takeaway": "O projeto usa uma representação proposicional após a instanciação dos operadores."},
    """Formalizo o problema por um conjunto de fatos possíveis, ações, estado inicial, objetivo e função de custo. Cada estado é um conjunto de fatos verdadeiros. Uma ação possui precondições, efeitos de adição e efeitos de remoção.

A transição remove os fatos da lista de exclusão e acrescenta os fatos da lista de adição. A aplicabilidade exige que todas as precondições estejam presentes no estado. Depois de aplicar a sequência, verificamos se o objetivo está contido no estado final.

Os operadores podem ser escritos com parâmetros e depois instanciados para objetos concretos, como ER_03. Essa representação é inspirada em STRIPS, mas não reproduz toda a expressividade do sistema histórico. O trabalho adota uma forma simplificada, apropriada à busca sobre conjuntos finitos de predicados. A vantagem é que podemos executar novamente cada transição e verificar a validade do plano de maneira direta.""",
    source="Fikes e Nilsson (1971); implementação: src/aisg/planning/strips.py")

add("3 · PLANEJAMENTO AUTOMÁTICO", "Hipóteses de planejamento e suas consequências", "table", {
    "headers": ["Hipótese", "Uso no modelo", "Consequência"],
    "rows": [
        ["Mundo fechado", "Fatos ausentes são falsos no estado de planejamento.", "Não deve ser aplicado automaticamente à telemetria desconhecida."],
        ["Efeitos determinísticos", "Uma ação aplicável produz os efeitos declarados.", "Falha de execução exigiria monitoramento e replanejamento."],
        ["Estado discreto", "Condições são representadas por predicados.", "Tempos, filas e recursos contínuos são abstraídos."],
        ["Custo aditivo", "O custo do plano soma os custos das ações.", "Custos são unidades convencionais, não duração medida."],
    ], "widths": [2.5, 4.4, 4.85]},
    """O modelo depende de hipóteses que simplificam o problema. A hipótese de mundo fechado permite tratar como falso um fato ausente do estado de planejamento. Essa convenção não pode ser aplicada sem cuidado à memória do diagnóstico, na qual uma informação pode estar desconhecida.

Os efeitos são determinísticos. Quando a ação de reparo é aplicada, seu predicado de falha é removido e um predicado de correção é acrescentado. O modelo não sorteia falhas de execução nem acompanha automaticamente a evolução de filas.

O custo também é convencional e aditivo. Ele permite comparar sequências, mas não deve ser apresentado como tempo de manutenção, consumo de energia ou risco medido sem uma calibração correspondente.

Essas simplificações são legítimas para estudar planejamento clássico. O rigor está em declará-las e reconhecer que uma futura execução em simulador precisará de observação posterior, tratamento de falhas e eventual replanejamento.""")

add("3 · PLANEJAMENTO AUTOMÁTICO", "Operador: separar canais no cenário simulado", "code", {
    "code": "separate_channels(?n)\n\nPre = { authorized(?n), mac-contention(?n),\n        run-stopped(?n) }\nAdd = { cleared-mac-contention(?n) }\nDel = { mac-contention(?n) }\ncusto = 3",
    "items": ["A execução precisa estar parada para esta alteração de parâmetro.", "O predicado de correção identifica a falha específica."],
    "takeaway": "Exigência de parada é uma escolha deste domínio, não uma propriedade universal de simuladores."},
    """Este operador permite examinar a semântica do planejamento em um caso concreto. Para separar os canais, o estado deve conter autorização, contenção e execução parada. Se qualquer uma dessas condições estiver ausente, a ação não é aplicável.

O efeito remove a contenção e registra a correção dessa falha específica. A ação recebe custo três na escala convencional do domínio. Esse custo permite comparar diferentes sequências, inclusive quando várias alterações compartilham uma única parada.

A exigência de interromper a execução foi escolhida para representar alterações de configuração no experimento. Não afirmo que todo simulador exija parada para qualquer mudança de canal. Outra implementação poderia representar uma reconfiguração dinâmica. Nesse caso, seria necessário alterar precondições, efeitos e custos e reavaliar os planos. A formalização torna essa decisão de engenharia visível e permite investigar suas consequências.""",
    "Perguntar quais precondições ainda faltam no estado inicial do caso mac_contention.")

add("3 · PLANEJAMENTO AUTOMÁTICO", "Operadores pertinentes à demonstração", "table", {
    "headers": ["Operador / etapa", "Custo", "Condição principal"],
    "rows": [
        ["request_authorization", "1", "Diagnóstico estabelecido no modelo."],
        ["stop_run / start_run", "2 / 2", "Execução ativa e autorizada / execução parada."],
        ["restore_path_budget", "1", "Perda adicional, autorização e execução parada."],
        ["separate_channels", "3", "Contenção, autorização e execução parada."],
        ["restart_node / fix_routing", "1 / 1", "Falha correspondente e autorização."],
        ["verify_link / record_logbook / close_work_order", "1 / 1 / 1", "Correções concluídas; verificação e registro."],
    ], "widths": [5.2, 1.25, 5.3], "size": 17,
    "takeaway": "Seleção de operadores relevantes; a tabela não pretende enumerar todo o catálogo compartilhado."},
    """Apresento aqui os operadores necessários para compreender a demonstração, e não uma contagem de todo o catálogo. O código compartilha operadores entre cenários, de modo que parte do catálogo não é pertinente ao caso simulado selecionado.

A solicitação de autorização antecede as alterações controladas. A parada e a retomada possuem custos próprios. Restaurar o orçamento de percurso e separar canais exigem execução parada. Outras correções foram modeladas como ações que não precisam desse ciclo.

As etapas finais verificam o enlace, registram o resultado e encerram a ordem. No modelo, verificar o enlace exige as correções previstas e, no cenário simulado, a execução novamente ativa.

É importante observar que stop_run exige execução ativa; ele não exige que a execução já esteja parada. A distinção entre condição de entrada e efeito de saída é fundamental para evitar uma descrição circular dos operadores.""")

add("3 · PLANEJAMENTO AUTOMÁTICO", "Autorização e validação pertencem ao modelo", "cards", [
    ["Requisito", "Ações de alteração especificadas exigem authorized(N) entre suas precondições."],
    ["Abstração", "request_authorization adiciona o predicado por efeito determinístico; não consulta uma autoridade externa."],
    ["Validação", "verify_link altera o estado simbólico; não comprova recuperação por medição automática."],
], """O planejamento representa autorização como precondição de ações específicas. Isso permite verificar se uma sequência respeita a restrição no modelo. Porém, o predicado é produzido por um operador determinístico de solicitação de autorização.

Portanto, o plano não implementa um sistema externo de concessão de permissões. A presença do predicado não comprova que uma pessoa ou instituição aprovou a intervenção. Para executar ações reais, seria necessário um mecanismo que vinculasse esse estado a uma autorização efetivamente concedida.

O mesmo cuidado se aplica à verificação do enlace. O operador verify_link produz um fato no estado simbólico. Ele não realiza, por si só, uma campanha de medição que comprove recuperação do serviço. A contribuição atual é formalizar a ordem e os requisitos. Uma integração operacional exigiria transformar esses pontos em contratos verificáveis com o ambiente, preservando a possibilidade de recusa ou falha.""")

add("3 · PLANEJAMENTO AUTOMÁTICO", "GPS: análise meios-fins", "flow", {
    "steps": [["Diferença", "Objetivo ainda ausente"], ["Operador", "Efeito que o estabelece"], ["Subobjetivos", "Precondições necessárias"], ["Aplicação", "Novo estado e revisão"]],
    "items": ["Seleciona ações pertinentes ao objetivo corrente.", "Resolve precondições recursivamente e realiza retrocesso local.", "Reverifica objetivos para detectar efeitos que desfazem conquistas anteriores."],
    "takeaway": "A estratégia implementada não oferece garantia geral de completude ou de custo mínimo."},
    """A análise meios-fins começa pela diferença entre o estado atual e o objetivo. Se service-restored ainda não está presente, o procedimento procura uma ação capaz de adicioná-lo. As precondições dessa ação tornam-se novos subobjetivos.

O processo continua recursivamente até encontrar condições já satisfeitas ou ações aplicáveis. Depois de aplicar uma ação, o estado é atualizado. O código utiliza controle de profundidade, prevenção de ciclos e retrocesso em ramos locais.

Esse procedimento produz uma justificativa intuitiva: cada ação aparece porque contribui para um subobjetivo. Entretanto, uma escolha local não considera necessariamente o custo total das precondições. Além disso, resolver subobjetivos em determinada ordem pode gerar interações difíceis de recuperar. A reverificação final detecta alguns desses problemas, mas não transforma a estratégia em um planejador completo. Por isso, comparo seu comportamento com a busca progressiva.""")

add("3 · PLANEJAMENTO AUTOMÁTICO", "Interação entre subobjetivos", "formula", {
    "formula": "Objetivo: p ∧ q\na₁: adiciona p\na₂: adiciona q e remove p",
    "items": ["Alcançar q pode invalidar p obtido anteriormente.", "A satisfação sequencial isolada não garante a conjunção final.", "Reverificar o objetivo detecta o conflito; resolver o conflito exige outra busca."],
    "takeaway": "Exemplo didático de interação de objetivos; não é uma execução do domínio de redes."},
    """Este exemplo abstrato ilustra por que não basta alcançar cada subobjetivo uma vez. Suponha que uma ação estabeleça p e que outra estabeleça q removendo p. Depois das duas ações, q está satisfeito, mas a conjunção desejada não está.

A dificuldade não decorre de uma ação individual inválida. Cada ação pode ter sido aplicável. O problema está na interação entre seus efeitos ao longo da sequência.

A literatura de planejamento discute esse tipo de interação, com exemplos clássicos como a anomalia de Sussman no mundo dos blocos. O exemplo deste slide é mais simples e não pretende reproduzir aquela instância específica.

No projeto, a estratégia meios-fins reverifica os subobjetivos e pode rejeitar uma sequência que desfez uma condição necessária. Essa defesa melhora a correção da saída, mas detectar um plano inválido é diferente de encontrar uma solução alternativa. A busca no espaço de estados trata explicitamente outras sequências.""")

add("3 · PLANEJAMENTO AUTOMÁTICO", "Não otimalidade: custo local e custo total", "table", {
    "headers": ["Alternativa abstrata", "Custo da ação", "Custo total necessário"],
    "rows": [["Preparar ambiente e aplicar correção A", "Correção A: 1", "Preparação: 10; total: 11"],
             ["Aplicar correção B diretamente", "Correção B: 3", "Sem preparação; total: 3"],
             ["GPS com preferência por custo próprio", "Prioriza a ação de custo 1", "Pode devolver o plano de custo 11"],
             ["Busca progressiva A*", "Avalia o custo do percurso", "Obtém custo 3 nesta instância"]],
    "widths": [4.7, 3.2, 3.85],
    "takeaway": "Contraexemplo abstrato e reproduzível; custos não são durações experimentais."},
    """A não otimalidade pode ser demonstrada sem depender de uma instância complexa. Construo duas maneiras de alcançar o mesmo objetivo. A primeira utiliza uma ação de custo um, mas exige uma preparação de custo dez. A segunda custa três e pode ser aplicada imediatamente.

Uma preferência baseada no custo próprio do operador pode escolher a primeira alternativa. O plano resultante custa onze. A busca progressiva considera a sequência e encontra a alternativa de custo três.

O exemplo não afirma que GPS sempre será pior, nem que nunca encontrará a solução ótima. Ele refuta a afirmação universal de otimalidade para a estratégia utilizada. No caso de contenção apresentado adiante, ambos os planejadores encontram o mesmo custo. A combinação dessas duas evidências é mais informativa do que selecionar apenas um caso favorável: coincidência em uma instância não estabelece uma garantia geral.""",
    "Executar presentation_demo.py gps-counterexample se houver tempo; comparar 11 e 3.")

add("3 · PLANEJAMENTO AUTOMÁTICO", "Planejamento como busca progressiva", "table", {
    "headers": ["Componente da busca", "Correspondência no planejamento"],
    "rows": [["Estado", "Conjunto de predicados verdadeiros."],
             ["Sucessor", "Estado produzido por uma ação aplicável."],
             ["Custo de transição", "Custo convencional da ação."],
             ["Teste de objetivo", "Inclusão de G no estado corrente."],
             ["Solução", "Sequência de ações e trajetória de estados."]],
    "widths": [4.0, 7.75],
    "takeaway": "O planejador e o roteador reutilizam a mesma função astar()."},
    """A busca progressiva transforma o planejamento em um problema de percurso sobre estados. A partir do estado inicial, cada ação aplicável gera um sucessor. O teste de objetivo verifica a inclusão dos predicados desejados.

O caminho encontrado corresponde à sequência de ações. Seu custo é a soma dos custos das transições. Dessa forma, a mesma implementação genérica de A* pode resolver planejamento e roteamento, desde que cada domínio forneça a interface de estado inicial, sucessores e teste de objetivo.

A reutilização é conceitualmente importante, mas não torna os dois espaços igualmente simples. No roteamento, o estado é um identificador de nó. No planejamento, ele é um conjunto de predicados, e o número de combinações pode crescer rapidamente. Assim, uma topologia pequena e um domínio de planejamento com poucos objetos podem apresentar dificuldades computacionais distintas. O desempenho deve ser medido em cada espaço de estados.""")

add("3 · PLANEJAMENTO AUTOMÁTICO", "Heurística de objetivos não satisfeitos", "formula", {
    "formula": "h(s) = |G ∖ s|\nCondição suficiente: c(a) ≥ |Add(a) ∩ G|",
    "items": ["Caso particular: cada ação satisfaz no máximo um objetivo e custa pelo menos 1.", "No objetivo utilizado, logged e service-restored são adicionados por ações distintas.", "Comparação de controle: h(s) = 0, equivalente à busca de custo uniforme."],
    "takeaway": "A condição é suficiente; não é uma caracterização necessária de toda heurística admissível."},
    """A heurística conta quantos predicados do objetivo ainda estão ausentes. Para justificá-la como limite inferior, precisamos relacionar a quantidade de objetivos que uma ação pode acrescentar ao seu custo.

Uma condição suficiente é que o custo de cada ação seja pelo menos o número de predicados do objetivo que ela pode adicionar. Assim, o custo necessário para obter todos os objetivos ausentes não pode ser menor do que essa contagem. Remover objetivos já satisfeitos não invalida o limite inferior; pode apenas aumentar o trabalho necessário.

Um caso particular simples ocorre quando cada ação adiciona no máximo um objetivo e custa pelo menos uma unidade. Essa condição vale para os dois predicados finais utilizados na demonstração. O cuidado acadêmico é chamá-la de suficiente, evitando apresentá-la como a única situação possível de admissibilidade. A comparação com heurística zero fornece um controle para medir o efeito da informação adicional.""")

add("3 · PLANEJAMENTO AUTOMÁTICO", "Demonstração: plano para contenção MAC", "code", {
    "code": "python docs/presentation/presentation_demo.py plan\n\n1  request_authorization(ER_03)   1\n2  stop_run(ER_03)                2\n3  separate_channels(ER_03)       3\n4  start_run(ER_03)               2\n5  verify_link(ER_03)             1\n6  record_logbook(ER_03)          1\n7  close_work_order(ER_03)        1\n                                 total = 11",
    "items": ["GPS e A*: plano válido de custo 11 nesta instância.", "Demonstração pela API Python com simulated=True."],
    "takeaway": "Validade: todas as ações aplicáveis e objetivo final satisfeito no modelo."},
    """O exemplo utiliza a API de planejamento para construir explicitamente o cenário simulado. Primeiro, o modelo solicita autorização. Em seguida, interrompe a execução, separa os canais e retoma a execução. Só então verifica o enlace, registra a intervenção e encerra a ordem.

A soma dos custos é onze. Tanto GPS quanto A* encontram um plano válido com esse custo nesta instância. Durante a demonstração, a validação reaplica as ações e verifica o estado final. Esse procedimento permite examinar a solução independentemente da forma como ela foi encontrada.

Utilizo um script de apresentação que chama a API porque a auditoria identificou um argumento desatualizado no comando de planejamento da interface original. Não apresento um comando que falha como se estivesse validado. Essa escolha mantém a demonstração reproduzível sem alterar o código de aplicação que está sendo desenvolvido em paralelo.""",
    "Executar o comando, conferir custo 11 e validação. Mostrar a posição de stop_run e start_run.")

add("3 · PLANEJAMENTO AUTOMÁTICO", "Falhas simultâneas e correção específica", "flow", {
    "steps": [["Diagnóstico", "Duas falhas selecionadas"], ["Parada", "Uma interrupção"], ["Correções", "Um predicado por falha"], ["Verificação", "Todas corrigidas e execução ativa"]],
    "items": ["verify_link exige cleared-… para cada falha declarada na instância.", "Perda adicional e contenção podem compartilhar uma parada e uma retomada.", "Diagnósticos concorrentes não comprovam, por si só, múltiplas falhas."],
    "takeaway": "A garantia de completude do reparo é relativa ao conjunto de falhas fornecido ao planejador."},
    """Na extensão para múltiplas falhas, um único indicador genérico de reparo seria insuficiente. Se corrigir uma falha ativasse esse indicador, o plano poderia verificar o enlace enquanto outra falha permanecesse presente.

O modelo utiliza um predicado de correção para cada falha declarada. A verificação exige a conjunção desses predicados. Para perda adicional e contenção, ambas as alterações podem ocorrer durante uma única interrupção, seguida de uma retomada. Essa possibilidade introduz uma decisão de sequenciamento e custo.

Entretanto, o conjunto de falhas é uma entrada da instância. A presença de várias hipóteses na memória do sistema especialista não demonstra automaticamente que elas ocorram simultaneamente. É necessária uma política para selecionar quais hipóteses serão tratadas como condições do planejamento. Além disso, verificar todas as falhas fornecidas não garante que falhas desconhecidas ou omitidas tenham sido eliminadas.""",
    "Executar presentation_demo.py multifault; verificar custo 12 e uma única parada/retomada.")

add("3 · PLANEJAMENTO AUTOMÁTICO", "Rota alternativa como precondição verificável", "cards", [
    ["Consulta", "A* procura um caminho entre a origem e o destino, excluindo o nó afetado."],
    ["Contrato", "A existência desse caminho sustenta alternate-route(N) para o incidente considerado."],
    ["Limite", "Conectividade no grafo não comprova capacidade residual, autorização externa ou recuperação medida."],
], """O operador de desvio de tráfego exige uma rota alternativa. O planejador consulta a busca sobre a topologia para verificar se existe um caminho que evite o nó afetado.

Essa verificação precisa utilizar o mesmo destino que será mostrado na saída. Caso contrário, poderíamos certificar a existência de uma rota para um dispositivo e apresentar uma solução destinada a outro. A identidade da origem, do destino, do nó excluído e da versão da topologia é parte do contrato entre os módulos.

Se não existir caminho, a precondição não deve ser adicionada. Na instância em que o desvio é a única correção disponível, o planejador deve informar ausência de solução.

Mesmo quando o caminho existe, a garantia é de conectividade no grafo e custo segundo o modelo. Capacidade residual, interferência dinâmica e estabilidade do fluxo não são demonstradas pela simples existência de uma sequência de enlaces.""")

add("4 · BUSCA A*", "Busca de caminhos em um grafo ponderado", "statement", {
    "statement": "Encontrar um caminho de custo mínimo entre uma origem e um destino.",
    "items": ["Estado: nó corrente; ação: percorrer um enlace disponível.", "Solução: sequência explícita de nós e transições.", "Custo: soma dos pesos dos enlaces do caminho."],
    "takeaway": "Menor número de saltos e menor custo são objetivos diferentes."},
    """O terceiro minissistema resolve um problema de caminho mínimo em um grafo ponderado. O estado é o nó corrente e cada transição corresponde a um enlace disponível. A solução deve apresentar o caminho, não apenas informar que o destino é alcançável.

O custo do caminho é a soma dos custos dos enlaces. Como os meios possuem pesos diferentes, a menor quantidade de saltos pode não produzir o menor custo. Um percurso curto em número de enlaces pode utilizar uma conexão cara, enquanto um percurso mais longo pode passar por enlaces de menor peso.

Essa diferença permite comparar estratégias de busca de maneira concreta. Busca em largura, busca gulosa, custo uniforme e A* respondem de formas diferentes à informação de custo. A comparação deve manter a mesma instância e deixar claro qual objetivo cada estratégia otimiza ou procura aproximar.""")

add("4 · BUSCA A*", "Função de custo e significado dos parâmetros", "formula", {
    "formula": "c(u,v) = bₜ + d(u,v) / (vₜ × qᵤᵥ)",
    "items": ["bₜ ≥ 0: sobrecarga convencional por enlace do tipo t.", "vₜ > 0: velocidade efetiva abstrata; 0 < qᵤᵥ ≤ 1: qualidade.", "Os valores em ms pertencem à escala do modelo; não são RTTs medidos."],
    "takeaway": "vₜ não representa a velocidade física de propagação eletromagnética."},
    """A função de custo combina uma sobrecarga fixa por tipo de enlace com um termo proporcional à distância e inversamente proporcional à velocidade efetiva e à qualidade.

Esses parâmetros são abstrações. O valor denominado velocidade efetiva organiza a preferência entre meios no modelo; não representa a velocidade da luz na fibra ou a propagação física no rádio. Por isso, não utilizo os custos calculados para afirmar latências reais de uma tecnologia.

A qualidade está limitada ao intervalo maior que zero e menor ou igual a um. Reduzi-la aumenta o termo de transporte. A sobrecarga não negativa também contribui para o custo. Essas condições têm uma função adicional: elas permitirão demonstrar que a distância dividida pela maior velocidade efetiva é um limite inferior.

Caso a função de custo seja substituída por medições ou por um objetivo não aditivo, a prova precisa ser revisada. Não se deve conservar a heurística apenas por conveniência visual.""",
    source="Modelo: src/aisg/domain/topology.py")

add("4 · BUSCA A*", "Função de avaliação e fronteira de busca", "formula", {
    "formula": "f(n) = g(n) + h(n)",
    "items": ["g(n): menor custo conhecido da origem até n.", "h(n): estimativa do custo restante até o objetivo.", "A fronteira prioriza o menor f; a solução é reconhecida na remoção do objetivo."],
    "takeaway": "A* combina custo acumulado e estimativa restante; a busca gulosa utiliza apenas h."},
    """A função de avaliação soma duas informações. O termo g representa o custo do melhor caminho conhecido até o estado. O termo h estima o custo que ainda falta para alcançar o objetivo.

A fronteira é uma fila de prioridade ordenada por f. Ao remover um estado, o algoritmo verifica se ele é objetivo e, caso contrário, examina seus sucessores. Se um caminho melhora o custo conhecido de um sucessor, o registro é atualizado.

A busca gulosa usa apenas a estimativa restante e pode ignorar um custo já elevado. A busca de custo uniforme utiliza apenas o custo acumulado, o que corresponde a A* com heurística zero. Essas relações ajudam a interpretar os resultados comparativos.

A garantia de A* depende das propriedades da heurística e do tratamento de estados repetidos. Portanto, a equação sozinha não é uma prova de correção. É necessário relacioná-la à implementação e às condições do problema.""",
    source="Hart, Nilsson e Raphael (1968).")

add("4 · BUSCA A*", "Condições e decisões de implementação", "table", {
    "headers": ["Aspecto", "Decisão", "Papel"],
    "rows": [
        ["Instância", "Grafo finito e custos não negativos.", "Condições do problema considerado."],
        ["Desempate", "Maior g; depois ordem de inserção.", "Comportamento reprodutível com entradas ordenadas."],
        ["Reabertura", "Estado retorna à fronteira se seu custo melhora.", "Suporte a heurísticas admissíveis inconsistentes."],
        ["Entradas obsoletas", "Descartar registros superados da fila.", "Evitar expansão com custo já melhorado."],
        ["Reconstrução", "Armazenar predecessor e ação.", "Retornar o caminho e verificar seu custo."],
    ], "widths": [2.3, 4.6, 4.85],
    "takeaway": "Para a garantia discutida: 0 ≤ h(n) ≤ h*(n), com h(objetivo) = 0."},
    """A implementação utiliza uma fila de prioridade e mantém o melhor custo conhecido para cada estado. Quando surge um caminho mais barato, atualiza o predecessor e permite reabrir o estado.

Esse mecanismo é importante porque uma heurística pode ser admissível sem ser consistente. Com consistência, um estado não precisa de reabertura para melhorar seu custo após expansão. Ainda assim, implementar o caso mais geral torna explícita a hipótese utilizada.

O desempate prefere maior custo acumulado entre estados com o mesmo f e depois utiliza a ordem de inserção. Essa escolha pode afetar o esforço observado, especialmente quando vários estados compartilham o mesmo valor de avaliação.

As garantias discutidas se referem a um grafo finito com custos não negativos e uma heurística não negativa que não superestima o custo restante e vale zero no objetivo. Problemas infinitos ou modelos com outros tipos de custo exigem hipóteses adicionais.""")

add("4 · BUSCA A*", "Admissibilidade da heurística geométrica", "formula", {
    "formula": "h(n) = d(n,g) / vmax\nc(u,v) ≥ d(u,v) / vmax\nΣ c(u,v) ≥ Σ d(u,v)/vmax ≥ d(n,g)/vmax",
    "items": ["vmax é a maior velocidade efetiva do catálogo.", "A primeira desigualdade usa as condições da função de custo.", "A segunda utiliza a desigualdade triangular."],
    "takeaway": "Para qualquer caminho até g: custo ≥ h(n). Portanto, h(n) ≤ h*(n)."},
    """A prova começa por um enlace. Como a sobrecarga é não negativa e o produto entre velocidade efetiva e qualidade não supera a maior velocidade do catálogo, o custo do enlace é pelo menos sua distância dividida por essa velocidade máxima.

Agora considero qualquer caminho entre o nó corrente e o objetivo. A soma dos custos é pelo menos a soma das distâncias dos enlaces dividida pela velocidade máxima. Pela desigualdade triangular, a soma dessas distâncias não pode ser menor que a distância direta entre os extremos.

Assim, o custo de qualquer caminho é maior ou igual ao valor da heurística. Isso também vale para o caminho de menor custo. Portanto, a heurística é admissível para o modelo adotado.

A prova depende da correspondência entre coordenadas, distâncias e custos. Se o peso de um enlace for substituído por um valor abaixo desse limite, a conclusão deixa de decorrer automaticamente das mesmas premissas.""",
    "Apontar cada desigualdade e pedir que a audiência identifique a hipótese utilizada.")

add("4 · BUSCA A*", "Consistência e verificação independente", "formula", {
    "formula": "d(u,g) ≤ d(u,v) + d(v,g)\nh(u) ≤ c(u,v) + h(v)",
    "items": ["A desigualdade triangular também estabelece consistência.", "Verificar cada aresta e objetivo examina as instâncias fornecidas.", "Um oráculo independente, como Floyd–Warshall, reduz dependência do próprio A*."],
    "takeaway": "Prova estabelece a propriedade sob hipóteses; testes verificam implementação e instâncias."},
    """A consistência compara a estimativa de um estado com o custo de uma transição e a estimativa do sucessor. A desigualdade triangular fornece a relação entre as distâncias. Ao dividir pela velocidade máxima e usar o limite inferior do custo do enlace, obtemos a condição de consistência.

Com valor zero no objetivo, essa propriedade implica admissibilidade nos estados que podem alcançar o objetivo. Ela também explica por que não é necessário reabrir estados para essa heurística consistente.

A prova não substitui testes. Um erro na leitura da topologia, no cálculo da distância ou na reconstrução do caminho poderia violar o comportamento esperado. Por outro lado, testar alguns grafos não demonstra uma propriedade universal.

Há ainda um cuidado na escolha do oráculo. No repositório, custo uniforme reutiliza a mesma função de A* com heurística zero. Comparar as duas versões é útil para avaliar a heurística, mas um algoritmo independente oferece uma verificação adicional da correção dos custos.""")

add("4 · BUSCA A*", "Comparação: NOC → ER_03", "table", {
    "headers": ["Estratégia", "Saltos", "Custo do modelo", "Expandidos", "Garantia geral"],
    "rows": [["Largura", "4", "453,51 ms", "15", "Mínimo de saltos"],
             ["Profundidade", "4", "453,51 ms", "7", "Sem mínimo de custo"],
             ["Custo uniforme", "5", "360,35 ms", "28", "Custo mínimo"],
             ["Gulosa", "5", "360,35 ms", "7", "Sem mínimo de custo"],
             ["A*", "5", "360,35 ms", "23", "Mínimo sob as hipóteses"]],
    "widths": [2.6, 1.0, 2.4, 1.85, 3.9], "size": 18,
    "takeaway": "O caminho mais barato tem MAIS saltos: contar saltos não ordena por custo."},
    """Esta comparação utiliza a mesma origem, o mesmo destino e os mesmos pesos. O ponto central está na primeira linha. A busca em largura encontra quatro saltos, e é o menor número de saltos possível, mas custa quatrocentos e cinquenta e três vírgula cinquenta e um. O caminho de cinco saltos devolvido por custo uniforme e por A* custa trezentos e sessenta vírgula trinta e cinco.

A explicação é física, não numérica. O caminho curto em saltos desce para a malha de 900 MHz, que é lenta e acumula atraso de armazena-e-encaminha a cada repetidor. O caminho com um salto a mais permanece no LTE privativo, que é rápido. Contar saltos e minimizar custo são objetivos diferentes, e neste par eles discordam.

A busca gulosa acerta o custo nesta instância expandindo apenas sete estados, mas essa coincidência não é garantia: a heurística poderia conduzi-la a um caminho caro em outro par. A busca em profundidade encontra o mesmo caminho da largura, dependente da ordem de exploração.

A* e custo uniforme chegam ao mesmo custo, enquanto A* expande vinte e três estados e custo uniforme expande vinte e oito. Essa é uma observação da instância, não uma garantia de economia idêntica em qualquer problema.

Os custos em milissegundos pertencem à escala convencional já definida. A contagem de expansões inclui o estado objetivo removido da fronteira, conforme a instrumentação do código. Declarar essa convenção evita comparar números obtidos por definições diferentes.""",
    "Executar presentation_demo.py route; comparar custo, caminho e expansões.")

add("4 · BUSCA A*", "Caminho ótimo e decomposição do custo", "table", {
    "headers": ["Enlace", "Tipo", "Custo do modelo", "Acumulado"],
    "rows": [["NOC → eNB_A", "Fibra", "60,00 ms", "60,00 ms"],
             ["eNB_A → RELAY_1", "LTE privativo", "128,73 ms", "188,73 ms"],
             ["RELAY_1 → RELAY_5", "LTE privativo", "86,33 ms", "275,05 ms"],
             ["RELAY_5 → CPE_03", "LTE privativo", "76,65 ms", "351,70 ms"],
             ["CPE_03 → ER_03", "Ethernet", "8,65 ms", "360,35 ms"]],
    "widths": [4.7, 2.2, 2.45, 2.4], "size": 17,
    "takeaway": "Cinco enlaces, um por salto; total calculado antes do arredondamento."},
    """O caminho devolvido por A* sai do núcleo pela fibra até o eNodeB, atravessa dois repetidores LTE e termina no CPE do site, que entrega ao roteador de borda por cabo. A tabela decompõe o custo por enlace e mostra o acumulado.

Observe onde está o custo. Os três saltos de rádio LTE somam duzentos e noventa e um vírgula setenta e um, e o último salto por cabo custa oito vírgula sessenta e cinco. O meio domina o custo, e é por isso que a escolha entre LTE e 900 MHz importa mais do que o número de saltos.

Essa decomposição é parte da verificação da solução. Não basta confiar no custo informado pelo algoritmo: podemos conferir se cada enlace existe, se a origem e o destino correspondem à consulta e se a soma dos pesos reproduz o resultado.

Os valores foram arredondados apenas para apresentação. Por isso, a soma visual de parcelas com duas casas decimais pode diferir em um centésimo do total obtido com precisão completa. O script utiliza os valores originais para a verificação.

O exemplo também evidencia a diferença entre caminho exato e caminho único. O algoritmo retorna uma sequência concreta de custo mínimo, mas isso não implica que toda instância tenha apenas uma solução ótima. Empates devem ser interpretados segundo a política de desempate e a estrutura do grafo.""")

add("4 · BUSCA A*", "Perda de um meio e comutação para o outro", "cards", [
    ["Condição inicial", "NOC → eNB_A → RELAY_1 → RELAY_5 → CPE_03 → ER_03\nCusto: 360,35 ms do modelo; acesso por pLTE."],
    ["Perturbação", "Desativar a fibra NOC–eNB_A, o que retira todo o acesso pLTE a partir do núcleo."],
    ["Nova solução", "NOC → SAF_01 → SAF_02 → RM_03 → ER_03\nCusto: 453,51 ms do modelo; acesso por 900 MHz."],
], """Agora altero a instância desativando a fibra entre o núcleo e o eNodeB A. Isso não remove um enlace qualquer: retira do núcleo todo o caminho de LTE privativo, e portanto o meio que servia este site.

O site não fica isolado. A busca encontra a rota pela malha de 900 MHz, e o custo sobe de trezentos e sessenta vírgula trinta e cinco para quatrocentos e cinquenta e três vírgula cinquenta e um. É exatamente isso que o duplo acesso compra, e o preço aparece no custo.

Essa demonstração verifica adaptação a uma alteração explícita de conectividade. Ela não simula automaticamente a detecção temporal de uma falha nem o tempo necessário para convergência de um protocolo de roteamento. O enlace foi desativado como entrada da consulta.

Também é importante incluir o caso em que o destino fica isolado. Nesse caso, a resposta correta é ausência de caminho. Um sistema integrado não deve transformar essa ausência em um plano que pressupõe desvio disponível. A comunicação explícita de insucesso é parte da correção funcional.""",
    "Executar presentation_demo.py reroute; conferir que o enlace removido não aparece no novo caminho.")

add("4 · BUSCA A*", "Esforço de busca no cenário de 60 nós", "bars", {
    "values": [["Custo uniforme", 109740], ["A*", 99963]],
    "items": ["3.540 pares ordenados de origem e destino distintos.", "Redução agregada de expansões: 8,9%.", "Com 30 nós a redução era 25,9%: ela DIMINUIU."],
    "takeaway": "Duas medições em dois grafos; a vantagem não cresceu com o tamanho."},
    """A avaliação agregada considera todos os pares ordenados de nós distintos: sessenta vezes cinquenta e nove, totalizando três mil quinhentas e quarenta consultas.

Nessas consultas, a busca de custo uniforme realiza cento e nove mil setecentas e quarenta expansões, enquanto A* realiza noventa e nove mil novecentas e sessenta e três. A redução agregada é aproximadamente oito vírgula nove por cento. Os custos coincidem em todos os pares verificados.

Peço atenção a este ponto, porque ele contraria a expectativa comum. No cenário de trinta nós a redução era de vinte e cinco vírgula nove por cento. Ao dobrar o número de nós, ela caiu para oito vírgula nove por cento. A vantagem da heurística não cresceu com o tamanho do grafo: diminuiu.

A explicação está na estrutura, não no tamanho. Este cenário tem duas redes de acesso quase paralelas, e a distância em linha reta informa pouco sobre qual meio é mais barato, porque meios diferentes têm velocidades diferentes. Uma heurística geométrica é fraca quando a geometria não prediz o custo.

Se eu tivesse apresentado apenas o resultado de trinta nós, a leitura natural seria que a vantagem cresce com o grafo. Duas medições em dois grafos mostram o contrário e continuam sendo apenas duas medições. Para estudar escalabilidade seria necessário variar sistematicamente tamanho e estrutura, controlar os demais fatores e medir tempo, memória e distribuição do esforço.

Para estudar escalabilidade, seria necessário variar sistematicamente tamanho e estrutura, controlar os demais fatores e medir também tempo, memória e distribuição do esforço por consulta. A estatística apresentada é descritiva e não deve ser ampliada além desse alcance.""",
    "Executar presentation_demo.py benchmark; explicar o cálculo 1 − 10310/13920.")

add("4 · BUSCA A*", "Aprendizagem de heurísticas: possibilidade e cautela", "cards", [
    ["Alvo de aprendizagem", "Estimar h*(s), o custo ótimo restante, em instâncias para as quais seja possível obtê-lo."],
    ["Risco", "Uma estimativa aprendida pode superestimar e invalidar a garantia de custo mínimo."],
    ["Uso conservador", "Utilizar a estimativa apenas em desempates após f admissível; avaliar instâncias não vistas."],
], """A aprendizagem pode ser investigada como forma de estimar o custo restante. No roteamento, distâncias ótimas podem ser calculadas por algoritmos de caminho mínimo. Em grafos dirigidos, calcular distâncias até um objetivo exige considerar as transições invertidas.

Esses rótulos são exatos em relação ao grafo e aos pesos, mas não são gratuitos: produzi-los exige computação. No planejamento, enumerar estados e obter custos ótimos pode ser muito mais caro do que no pequeno grafo de comunicação.

Uma heurística aprendida também pode superestimar o custo restante. Bons resultados médios não demonstram admissibilidade. Uma alternativa conservadora é utilizá-la apenas como desempate depois do valor de f calculado com uma heurística admissível. Outra linha seria estudar busca com subotimalidade limitada, mas a garantia exige condições próprias e não decorre de qualquer regressor.

Essa possibilidade é uma agenda de investigação. Não há treinamento de heurística implementado ou validado na demonstração atual.""")

add("5 · INTEGRAÇÃO E AVALIAÇÃO", "Contrato entre diagnóstico, planejamento e busca", "flow", {
    "steps": [["Evidências", "Sujeito e contexto"], ["Hipótese", "Seleção explícita"], ["Plano", "Condições e ações"], ["Rota", "Mesmos extremos"]],
    "items": ["Fixar nó afetado, origem, destino e versão da topologia.", "Usar a base simulada e simulated=True no planejamento.", "Validar o plano e verificar a rota que fundamenta o desvio."],
    "takeaway": "O script da apresentação explicita a composição pela API; não executa intervenções em ns-3."},
    """A integração precisa preservar a identidade do incidente. O diagnóstico deve referir-se ao mesmo nó que aparece no estado inicial. A consulta de rota deve utilizar os mesmos extremos considerados na verificação de desvio.

O script da apresentação compõe explicitamente as APIs: seleciona a base simulada, constrói o problema com a opção simulated e informa o destino de roteamento. Essa explicitação é importante porque escolher apenas a topologia simulada na interface original não seleciona automaticamente todos os demais componentes do cenário.

Depois de construir o problema, validamos o plano e conferimos a rota usada para fundamentar a precondição. O script também examina se o nó excluído aparece no caminho.

A composição demonstra compatibilidade funcional entre os módulos. Ela não configura uma execução experimental completa do ambiente, pois ainda não envia ações a um simulador nem coleta medições posteriores. O contrato apresentado identifica exatamente onde esses mecanismos precisariam ser conectados.""")

add("5 · INTEGRAÇÃO E AVALIAÇÃO", "Demonstração integrada: congestionamento", "code", {
    "code": "python docs/presentation/presentation_demo.py integrated\n\nCaso: congestion      Nó afetado: SAF_02\nBase: simulated       Planejamento: simulated=True\nOrigem: NOC           Destino: ER_06\n\nDiagnóstico: congestion, CF +0,888\nPlano: contém reroute_traffic; validação positiva\nRota: NOC → eNB_A → RELAY_1 → RELAY_5 → CPE_06 → ER_06\nCusto da rota: 509,55 ms do modelo",
    "takeaway": "O desvio exclui SAF_02 e move o site da malha de 900 MHz para o pLTE."},
    """O incidente integrado utiliza o caso ilustrativo de congestionamento associado a SAF_02, um repetidor da malha de 900 MHz. A origem é NOC e o destino é ER_06, um site normalmente servido por essa malha. O sistema especialista produz a hipótese congestion com suporte zero vírgula oitocentos e oitenta e oito.

A integração converte essa hipótese em uma condição do problema de planejamento. A disponibilidade de rota alternativa é verificada evitando SAF_02 e preservando ER_06 como destino. O plano inclui o operador de desvio e é validado pela reaplicação das ações.

A rota apresentada abandona a malha de 900 MHz e alcança ER_06 pelo LTE privativo, sem atravessar o repetidor afetado. O custo sobe para aproximadamente quinhentos e nove vírgula cinquenta e cinco na escala do modelo, porque o desvio troca o meio de acesso do site.

Durante a demonstração, observamos quatro relações: hipótese e nó; nó e estado inicial; destino e consulta de viabilidade; plano e rota mostrada. A coerência dessas relações é a evidência de integração. A recuperação efetiva do tráfego continua sendo uma questão experimental futura.""",
    "Executar o comando; conferir base, predicado run-active, ação de desvio, destino e nó excluído.")

add("5 · INTEGRAÇÃO E AVALIAÇÃO", "Procedimento experimental proposto", "table", {
    "headers": ["Etapa", "Procedimento", "Registro necessário"],
    "rows": [
        ["Especificar", "Fixar hipóteses, variáveis, objetivos e critérios de exclusão.", "Protocolo anterior à coleta."],
        ["Executar", "Variar mecanismos e intensidades; repetir com fluxos aleatórios controlados.", "Versões, configuração, sementes e identificadores de execução."],
        ["Avaliar", "Comparar diagnóstico, planos e rotas com referências adequadas.", "Resultados completos, abstenções, falhas e custos."],
        ["Analisar", "Separar ajuste e avaliação; usar unidades independentes para inferência.", "Efeitos, dispersão e limites de validade."],
    ], "widths": [2.0, 5.15, 4.6],
    "takeaway": "Protocolo proposto; não descreve uma campanha de ns-3 já realizada."},
    """Uma campanha experimental deve começar pela definição das perguntas. Para diagnóstico, podemos perguntar se o sistema discrimina mecanismos semelhantes em condições não usadas no ajuste. Para planejamento, se as restrições permanecem satisfeitas sob combinações de falhas. Para busca, como o esforço varia com estrutura e pesos.

As execuções precisam registrar versão, configuração e controle da aleatoriedade. Em ns-3, sementes, números de execução e fluxos aleatórios devem ser tratados conforme a documentação da versão utilizada. Repetir o mesmo fluxo não cria uma nova replicação independente.

A análise deve separar ajuste e avaliação. Se parâmetros forem calibrados em determinados cenários, o desempenho final precisa ser estimado em condições reservadas. Também é necessário registrar insucessos e abstenções, evitando apresentar apenas exemplos bem-sucedidos.

Os indicadores e as unidades de análise precisam ser definidos antes de calcular intervalos ou testes estatísticos. Pacotes da mesma execução e pares do mesmo grafo compartilham dependências que não podem ser ignoradas.""",
    source="ns-3 Manual: Random Variables; protocolo proposto para o projeto.")

add("5 · INTEGRAÇÃO E AVALIAÇÃO", "O que cada evidência permite concluir", "table", {
    "headers": ["Evidência", "Conclusão sustentada", "Conclusão não estabelecida"],
    "rows": [
        ["Testes automatizados", "Propriedades exercitadas passaram nas instâncias verificadas.", "Ausência de todos os defeitos ou desempenho operacional."],
        ["Plano reaplicado", "Sequência aplicável e objetivo atingido no modelo.", "Execução física ou experimental bem-sucedida."],
        ["Prova da heurística", "Limite inferior sob as hipóteses da função de custo.", "Validade para qualquer métrica de rede."],
        ["870 consultas", "Custos e esforço no grafo sintético selecionado.", "Lei geral de escalabilidade ou validade externa."],
    ], "widths": [2.5, 4.65, 4.6]},
    """Esta matriz resume a interpretação das evidências. Os testes automatizados verificam propriedades exercitadas por suas entradas. A auditoria encontrou todos os testes então executados aprovados, mas também identificou uma falha no comando de planejamento. Isso mostra que aprovação da suíte não cobre automaticamente toda interface de uso.

Reaplicar um plano verifica sua consistência com o modelo de transição. Uma prova da heurística estabelece uma propriedade matemática sob hipóteses. As oitocentas e setenta consultas caracterizam o comportamento sobre o grafo escolhido.

Essas evidências são complementares. Nenhuma precisa ser desvalorizada, mas cada uma deve sustentar a conclusão apropriada. A confiabilidade da apresentação depende de preservar essa correspondência.

Na documentação que acompanha o arquivo, registro o estado auditado e os comandos utilizados. Contagens de testes podem mudar com o desenvolvimento do repositório; por isso, a apresentação privilegia as propriedades verificadas e mantém os detalhes da execução no relatório de avaliação.""")

add("6 · SÍNTESE E CONTINUIDADE", "Contribuições e limitações do trabalho", "cards", [
    ["Representação", "Conhecimento, estado e custo são explicitados e podem ser inspecionados."],
    ["Implementação", "Inferência, planejamento e roteamento possuem exemplos reproduzíveis e validação de saídas."],
    ["Validade", "Resultados permanecem condicionados a casos ilustrativos, efeitos assumidos e topologia sintética."],
], """A contribuição do trabalho está na implementação de três métodos clássicos em torno de um domínio comum e na explicitação de suas interfaces. O conhecimento pode ser inspecionado regra por regra; os planos podem ser reaplicados; os caminhos podem ter seus custos recalculados.

Essa organização oferece uma base adequada para discutir correção algorítmica e modelagem. Também permite identificar onde a incerteza foi representada e onde ela foi simplificada. O diagnóstico possui graus de suporte, enquanto planejamento e roteamento operam com condições e custos determinados na instância.

As limitações principais são a ausência de calibração empírica dos limiares, o caráter ilustrativo dos casos e a falta de uma campanha documentada que conecte ações e observações de um simulador. O trabalho não apresenta esses limites como detalhes periféricos. Eles definem o alcance das conclusões e orientam os próximos experimentos.""")

add("6 · SÍNTESE E CONTINUIDADE", "Agenda de investigação e critérios de avanço", "table", {
    "headers": ["Prioridade", "Pergunta", "Critério de avanço"],
    "rows": [
        ["Validação diagnóstica", "A base distingue falhas em casos não usados no ajuste?", "Avaliação independente, com abstenções e ambiguidades."],
        ["Execução e realimentação", "O ambiente confirma os efeitos previstos pelo plano?", "Ações instrumentadas, observação posterior e replanejamento."],
        ["Generalização da busca", "O benefício persiste em outras topologias e pesos?", "Famílias controladas de instâncias e análise de esforço."],
        ["Reprodutibilidade", "Outra pessoa consegue repetir os resultados?", "Configurações, versões, comandos e artefatos completos."],
    ], "widths": [2.8, 4.2, 4.75]},
    """A continuidade pode ser organizada por critérios de avanço observáveis. Para o diagnóstico, o próximo passo é avaliar casos que não participaram da construção das regras. Isso inclui situações ambíguas, informação ausente e combinações de falhas.

Para o planejamento, o avanço é conectar os efeitos simbólicos à execução instrumentada. Uma ação pode falhar ou produzir um resultado diferente do previsto, o que exige observação e replanejamento.

Para a busca, é necessário investigar famílias de grafos e funções de custo. O resultado favorável em uma topologia não basta para caracterizar escalabilidade.

Por fim, a reprodução deve ser tratada como parte do método. A apresentação, o roteiro, os comandos e as configurações precisam corresponder à mesma versão. O objetivo é que outra pessoa consiga repetir o percurso de avaliação e contestar suas conclusões com base em artefatos verificáveis.""")

REFERENCES = [
    ("[1]", "Shortliffe, E. H.; Buchanan, B. G. A Model of Inexact Reasoning in Medicine. Mathematical Biosciences, 23, 351–379, 1975.", "https://www.shortliffe.net/Buchanan-Shortliffe-1984/Chapter-11.pdf"),
    ("[2]", "Fikes, R. E.; Nilsson, N. J. STRIPS: A New Approach to the Application of Theorem Proving to Problem Solving. Artificial Intelligence, 2, 189–208, 1971.", "https://ai.stanford.edu/~nilsson/OnlinePubs-Nils/PublishedPapers/strips.pdf"),
    ("[3]", "Hart, P. E.; Nilsson, N. J.; Raphael, B. A Formal Basis for the Heuristic Determination of Minimum Cost Paths. IEEE TSSC, 4(2), 100–107, 1968.", "https://ai.stanford.edu/~nilsson/OnlinePubs-Nils/PublishedPapers/astar.pdf"),
    ("[4]", "Dijkstra, E. W. A Note on Two Problems in Connexion with Graphs. Numerische Mathematik, 1, 269–271, 1959.", "https://doi.org/10.1007/BF01386390"),
    ("[5]", "ns-3 Project. Manual: Random Variables. Documentação de sementes, execuções e fluxos aleatórios. Consulta: 10 set. 2026.", "https://www.nsnam.org/docs/manual/html/random-variables.html"),
    ("[6]", "Dantas, F. S. AI for Smart Grids: código, topologia, exemplos e testes. Repositório do projeto. Estado auditado registrado no relatório acompanhante.", "https://github.com/fsd-dantas/ai-for-smartgrids"),
]

add("7 · REFERÊNCIAS E DISCUSSÃO", "Referências e procedência dos resultados", "references", REFERENCES,
    """A fundamentação utiliza trabalhos primários sobre fatores de certeza, planejamento e busca heurística. A referência de Shortliffe e Buchanan contextualiza o raciocínio inexato por regras. Fikes e Nilsson fundamentam a representação e a estratégia de planejamento associadas a STRIPS. Hart, Nilsson e Raphael fornecem a referência histórica central de A*.

O artigo de Dijkstra contextualiza o problema de caminhos mínimos. A documentação de ns-3 é utilizada para orientar a proposta de controle da aleatoriedade em uma campanha futura, não como evidência de experimentos já executados.

Os resultados numéricos apresentados provêm do código e das instâncias do repositório. O roteiro contém os comandos correspondentes e o relatório identifica as condições de verificação. As referências são complementares: a literatura fundamenta conceitos, enquanto o repositório fornece evidência da implementação particular examinada nesta apresentação.""",
    "Não ler a bibliografia integralmente. Indicar que os links também constam no roteiro.")

add("7 · REFERÊNCIAS E DISCUSSÃO", "Discussão", "statement", {
    "statement": "Qual evidência adicional seria necessária para transformar uma recomendação válida no modelo em uma decisão confiável no ambiente?",
    "items": ["Validação das hipóteses de diagnóstico.", "Correspondência entre efeitos planejados e observados.", "Adequação da função de custo e do cenário experimental."],
    "takeaway": "Código, roteiro e demonstrações permitem examinar e reproduzir o argumento."},
    """Encerro retomando a distinção central: uma solução pode estar correta em relação ao modelo e ainda exigir evidências adicionais para orientar decisões no ambiente.

No diagnóstico, essa passagem depende de validar as associações entre evidências e hipóteses. No planejamento, depende de verificar se as ações produzem os efeitos previstos. No roteamento, depende de justificar a correspondência entre os pesos escolhidos e o objetivo de comunicação que realmente importa.

Gostaria de propor uma discussão sobre qual dessas interfaces representa a maior limitação no estágio atual e qual experimento seria mais informativo para reduzi-la. Uma resposta pode priorizar a calibração da base; outra pode priorizar a execução instrumentada do plano. O critério que proponho é a capacidade de produzir evidência que possa confirmar ou refutar uma hipótese concreta. Obrigado; fico à disposição para discutir as decisões de modelagem e os resultados.""",
    "Abrir a discussão. Usar o roteiro e o script de demonstração para aprofundar perguntas técnicas.")
