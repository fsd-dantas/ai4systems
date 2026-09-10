# Protocolo de avaliação e proposta de rubrica

**Versão 1.0 — 10/09/2026. Status: proposta de autoavaliação, sem endosso docente registrado.**

Este protocolo torna a avaliação dos três trabalhos rastreável: cada requisito deve
apontar para uma implementação, uma demonstração e uma evidência verificável.
O professor continua responsável pela nota oficial. A ausência de uma rubrica
fornecida pelo professor não significa aprovação dos pesos propostos aqui.

O autor confirmou os três trabalhos e a duração autorizada de **90 minutos,
30 por tema**. A autorização da duração não implica endosso desta rubrica.

## 1. Escopo e requisitos da disciplina

| Trabalho | Requisito de referência | Evidência no projeto |
|---|---|---|
| Sistema especialista | Minissistema em SINTA ou Python; ao menos 10 regras; demonstração | Base de conhecimento, encadeamento e explicação em `src/aisg/expert_system/`; casos no notebook |
| Planejamento | Gerar automaticamente planos para um domínio escolhido | Representação STRIPS, GPS, planejamento progressivo e validação em `src/aisg/planning/` |
| Busca A* | Implementar a busca e retornar o caminho do estado inicial ao objetivo | Algoritmo em `src/aisg/search/algorithms.py`; roteamento, caminho e custo no notebook |

Fontes fornecidas na disciplina: *AULA 01 EXPERT SYSTEM*, p. 62; *AULA 02 BUSCA
AStar e STRIPS*, pp. 104–105; *cronograma*, seção de 11/09/2026. Os documentos
originais permanecem no material da disciplina; não são redistribuídos aqui.

A integração, o segundo planejador, a comparação entre estratégias e a topologia
de escala enriquecem a demonstração. Não são apresentados como exigências
adicionais impostas pelo professor. Dados de campo e contribuição científica
inédita não são requisitos desta avaliação prática.

## 2. Rubrica proposta: 100 pontos

Os dois primeiros trabalhos recebem 30 pontos cada por envolverem representação
e raciocínio específicos do domínio. A busca recebe 25 pontos, centrados em
correção e análise. Documentação e defesa recebem 15 pontos. Essa distribuição é
uma escolha de autoavaliação, sujeita à apreciação do professor.

| Área | Critério | Máximo |
|---|---|---:|
| Sistema especialista | Regras, variáveis, domínios e rastreabilidade do conhecimento | 8 |
| | Correção do encadeamento e propagação dos fatores de certeza | 12 |
| | Explicação, casos demonstrados e tratamento de entradas desconhecidas | 10 |
| Planejamento | Estados, precondições, efeitos e hipóteses do domínio | 10 |
| | Planos executáveis, objetivo correto e restrições respeitadas | 12 |
| | Integração com diagnóstico/rota e comportamento quando não há solução | 8 |
| Busca A* | Caminho válido, custo correto e tratamento de falha | 12 |
| | Heurística, condições de otimalidade e justificativa | 8 |
| | Comparação de estratégias e interpretação dos resultados | 5 |
| Documentação e defesa | Instalação, execução e reprodução dos resultados | 5 |
| | Clareza, domínio dos conceitos e demonstração no tempo autorizado | 5 |
| | Coerência entre código, slides, fontes e limitações declaradas | 5 |
| **Total** | | **100** |

Para cada critério, atribuir um fator de atendimento: **0** (sem evidência ou
incorreto), **0,25** (incipiente), **0,50** (parcial, com falhas relevantes),
**0,75** (substancial, com lacunas delimitadas) ou **1,00** (atende ao critério
com evidência reproduzível). Pontos = máximo × fator. Somar antes de arredondar
a nota final para uma casa decimal; dividir por 10 para a escala de 0 a 10.

Registrar justificativa e evidência por critério. Uma mesma falha tem uma
dedução principal; só descontar em outra área quando houver um efeito distinto
e explicado, como um resultado incorreto também publicado nos slides.
Critérios ainda não observados, como a defesa oral, ficam **pendentes**, sem
presumir nota máxima nem atribuir zero automaticamente. Nesse caso, reportar
pontos avaliados e máximo avaliado, sem extrapolar uma nota final sobre 100.

## 3. Procedimento de validação e endosso

1. **Apresentar a proposta antes da avaliação final.** Compartilhar este documento
   com o professor e pedir confirmação de escopo, critérios e pesos. A revisão
   preliminar já ocorreu; esta rubrica detalhada não foi pré-registrada antes
   dela. A versão 1.0 deve orientar uma nova avaliação, sem recalcular o passado
   para reproduzir uma nota desejada.
2. **Identificar a entrega.** Registrar SHA do commit, data, versão do Python,
   sistema operacional, topologias e comandos. Se houver alterações locais,
   registrar também o diff ou avaliar uma versão limpa. O SHA isolado não
   identifica código ainda não commitado.
3. **Executar e guardar evidências.** Usar a matriz abaixo. Registrar resultados
   esperados e observados, inclusive falhas; quantidade de testes aprovados não
   substitui a avaliação do que esses testes cobrem.
4. **Revisar a correspondência entre afirmação e evidência.** Conferir tabelas,
   caminhos, custos, contagens e limites da apresentação contra a entrega
   identificada. Distinguir propriedades provadas do modelo, resultados dos
   exemplos e hipóteses ainda não validadas em campo.
5. **Preencher a rubrica e justificar a nota.** Um colega pode reproduzir os
   comandos e revisar as deduções, se disponível. Registrar quem executou e
   quem revisou; não atribuir revisão a uma pessoa que não participou. A revisão
   de um colega não equivale a endosso do professor.
6. **Registrar a manifestação do professor.** Transcrever ou resumir a resposta
   com data e referência autorizada. Marcar como aceita, aceita com alterações,
   ou não aceita somente após resposta explícita. Sem resposta, manter
   **proposta de autoavaliação**. Endosso dos critérios não significa aprovação
   dos resultados nem atribuição automática de nota.

Esse procedimento pode ser executado para preparar a entrega mesmo enquanto a
rubrica aguarda manifestação docente. Não exige suspender o desenvolvimento.

## 4. Matriz mínima de evidências

| Verificação | Evidência a registrar | Condição de aceitação |
|---|---|---|
| Reprodução | Instalação e `python -m pytest`; execução do notebook | Ambiente identificado; comandos e células executam; falhas registradas |
| Diagnóstico | Casos predefinidos, evidência incompleta, CF e explicações | Conclusões sustentadas pelas regras e cálculo demonstrável; CF não é probabilidade de acerto |
| Políticas de inferência | Mesmo caso nas três políticas; diagnóstico e ações, com CF | Se alegada invariância, comparar todas as conclusões relevantes; diferenças exigem correção ou limitação explícita |
| Planejamento | Reexecutar ações desde o estado inicial | Toda precondição satisfeita; objetivo alcançado; autorização precede intervenção; nenhuma falha do escopo permanece |
| Reroteamento | Caso possível e impossível para o destino solicitado | Planejador e roteador usam os mesmos endpoints e exclusões; não validar restauração com rota inviável |
| Busca A* | Caminho, soma de custos e referência independente | Arestas válidas, extremos corretos e custo ótimo; referência como Floyd–Warshall evita comparar somente variantes da mesma função |
| Heurística | Prova e verificação nos dois grafos | `h(goal)=0`, admissibilidade e consistência sob as hipóteses do modelo |
| Comparação | Expandidos e definição de pares amostrados | Distinguir pares ordenados de não ordenados; não generalizar dois grafos como lei de escala |
| Apresentação | Ensaio e conferência de números nos slides | 90 minutos autorizados; afirmações compatíveis com resultados reproduzidos |

Exemplos de comandos para a ficha de evidências:

```bash
git rev-parse HEAD
git status --short
python --version
python -m pytest
aisg diagnose --case rain_fade --strategy first-match --trace
aisg diagnose --case rain_fade --strategy specificity --trace
aisg plan --diagnosis node_power_failure --node RM_A5 --solver both
aisg --lang en pipeline --case congestion --node AP_A --target SUB_S1
aisg route --from NOC --to RECLOSER_7 --compare
aisg route --from NOC --to RECLOSER_7 --disable-link LTE_ENB-RM_A5
```

Esses comandos incluem verificações de regressão; sua presença não afirma que
todos os comportamentos já estão corretos na versão em desenvolvimento.

## 5. Simplificação de falhas e extensão recomendada

**Escopo recomendado para a demonstração principal:** um nó por incidente e um
diagnóstico principal selecionado para gerar o plano; o caso saudável não exige
reparo. O sistema especialista pode manter hipóteses concorrentes. Hipóteses
concorrentes não são automaticamente falhas simultâneas confirmadas.

Essa simplificação concentra a apresentação nos conceitos de representação,
encadeamento e busca. Ela não descreve toda a complexidade de uma rede real.

**Extensão opcional:** permitir várias falhas explicitamente fornecidas ao
planejador, com um predicado de reparo para cada falha e uma conjunção de todas
as reparações necessárias antes de verificar o enlace e encerrar a ordem.
Isso amplia o planejamento; não demonstra diagnóstico automático de múltiplas
causas. Avaliar a extensão separadamente da demonstração principal.

Antes de declarar a extensão validada, demonstrar pelo menos: interferência +
falha de alimentação, preservação dos casos de falha única e saudável, rejeição
de falha desconhecida e ausência de restauração quando uma falha não pode ser
resolvida. Incluir interações de efeitos e restrições de ações; remover todos os
literais de falha ainda é uma garantia do modelo, não de restauração física.

Também declarar que `request_authorization` e `verify_link` representam resultados
assumidos das ações no modelo determinístico. A execução do planejador não
obtém autorização humana real nem mede a recuperação de um equipamento.

## 6. Registro de revisão e modelo de solicitação

A revisão preliminar de 10/09/2026 atribuiu **85/100** ao commit
`8d47ceded1fc4f73c21d254268f4152e10afda4d`, com pesos de área 30/30/25/15.
Foi uma revisão assistida por IA, não uma nota docente nem uma observação da
defesa oral. A rubrica detalhada acima foi elaborada depois dessa revisão.
Alterações posteriores precisam de nova avaliação; não herdam a nota.

Evidências históricas daquela revisão: 108 testes aprovados; 25 células de código
executadas em memória; 1.142 pares dirigidos verificados contra Floyd–Warshall,
sem erros de caminho/custo ou violações de admissibilidade/consistência.
Esses resultados não eliminam os defeitos encontrados fora dos testes existentes.
Não representam promessa de 99% de acerto diagnóstico ou de certeza na nota.

| Campo para a avaliação final | Registro |
|---|---|
| Versão da rubrica e status docente | 1.0; proposta, sem endosso registrado |
| SHA da entrega e alterações locais | A preencher |
| Data e ambiente de execução | A preencher |
| Evidências e falhas por critério | A preencher |
| Avaliador / revisor que efetivamente participou | A preencher |
| Critérios pendentes, incluindo defesa oral | A preencher |
| Pontuação e justificativas | A preencher |
| Manifestação docente, data e referência | Não registrada |

**Texto sugerido para o autor apresentar ao professor — não enviado:**

> Professor, para documentar a avaliação dos três trabalhos, proponho uma rubrica
> de 100 pontos: sistema especialista 30, planejamento 30, busca A* 25 e
> documentação/defesa 15. Cada critério terá evidência reproduzível vinculada à
> versão entregue. A demonstração principal considera um diagnóstico selecionado
> por nó; o planejamento com falhas simultâneas será identificado como extensão.
> Mantemos os 90 minutos autorizados. O senhor concorda com o escopo, os critérios
> e os pesos, ou recomenda ajustes? Até sua manifestação, registrarei a rubrica
> apenas como proposta de autoavaliação.

**Fala curta para a apresentação:**

> Avaliamos os três trabalhos por requisitos, correção e evidência reproduzível.
> Propomos os pesos 30/30/25/15; eles ainda não têm endosso docente registrado.
> O exemplo principal seleciona um diagnóstico por nó, e falhas simultâneas são
> uma extensão avaliada separadamente. Os resultados valem para a versão e o
> modelo apresentados.

## English summary

This is a proposed self-assessment rubric, not an instructor-approved grading
policy. Weights are expert system 30, planning 30, A* 25, and documentation/oral
defence 15. Record requirements, the exact submission, reproducible evidence,
criterion-level scores, and any explicit instructor response. Pending oral
assessment remains unscored. The author confirmed the approved 90-minute format.
The recommended main demonstration uses one selected diagnosis per node;
explicit multiple-fault planning is a separately validated extension. The earlier
85/100 was an AI-assisted preliminary review of a historical commit, not an
official grade or a score for subsequent changes.
