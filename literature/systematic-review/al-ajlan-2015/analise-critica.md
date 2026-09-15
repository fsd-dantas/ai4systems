# Análise crítica — *The Comparison between Forward and Backward Chaining*

**Artigo:** AL-AJLAN, A. The Comparison between Forward and Backward Chaining. *International Journal of Machine Learning and Computing*, v. 5, n. 2, p. 106–113, 2015.
**Autor da análise:** Fernando Sabino Dantas.

## 1. Síntese

O artigo compara o encadeamento progressivo (orientado por dados) e o regressivo (orientado por objetivo) num sistema especialista de admissão em pós-graduação (GAES). Após revisar estratégias de busca e a arquitetura de um sistema especialista, aplica os dois encadeamentos a doze regras do GAES, percorrendo à mão um caso em cada modo. A comparação é resumida numa tabela de atributos (Tabela II) e a conclusão aplica os critérios de Luger: como os dados do candidato são fornecidos de antemão, há muitos objetivos possíveis e é difícil formular uma hipótese inicial, o progressivo seria o mais adequado ao GAES.

## 2. Contribuições

O mérito do artigo é didático. Explica com clareza que a escolha entre as estratégias depende da natureza do problema — se os dados chegam antes da pergunta ou se a pergunta guia a coleta de dados — e não de uma superioridade absoluta. Os critérios de Luger levam a uma conclusão justificada pelas características do domínio, e não por preferência.

## 3. Limitações

**Inconsistências internas.** A Tabela II classifica o progressivo como *top-down* e o regressivo como *bottom-up*, o inverso do que a Seção III define. Na Seção V.A, os números das regras citadas não correspondem à lista: "R3" conclui a decisão integral, que é a R2; "R8" admite com status integral, que é a R10; "R9" trata da consideração do GPR, que é a R5. Na Seção III.A, um candidato com GPR menor que 3 dispara a Regra 2, cuja premissa exige GPR maior que 3 e diploma não britânico.

**Erros na revisão de busca.** O A\* é descrito como combinação de busca em profundidade e em largura, quando é uma busca pela melhor estimativa *f*(*n*) = *g*(*n*) + *h*(*n*); afirma-se que a busca em profundidade garante solução, o que falha em espaços infinitos ou com ciclos; e que a busca em largura "facilmente perde uma solução", embora seja completa.

**Afirmações sem medição.** "Rápido", "lento", "faz poucas perguntas" e "testa todas as regras" são afirmados, não medidos. Há um único caso ilustrativo por estratégia, a resolução de conflito é sempre a primeira regra e não há tratamento de incerteza. A Tabela II diz ainda que o progressivo não facilita explicação; porém a explicação depende de registrar a proveniência de cada conclusão, e não da direção do encadeamento — o "como" do MYCIN explica conclusões obtidas por qualquer estratégia.

## 4. Evidência complementar

Para testar as afirmações da Tabela II, os dois encadeamentos foram executados sobre a mesma base de conhecimento — 41 regras de produção com fatores de certeza, 13 variáveis observáveis, diagnóstico de enlaces de rede — nos 8 casos da base. No progressivo, os 13 fatos são fornecidos; no regressivo, o motor pergunta só o que o objetivo exige.

| Medida (média em 8 casos) | Progressivo | Regressivo |
|---|---|---|
| Perguntas / fatos consultados | 13,0 | **7,1** |
| Regras disparadas | 9,4 | **4,1** |
| Fatos derivados | 8,5 | 3,6 |
| Mesmo melhor diagnóstico | 8/8 | 8/8 |

Os números confirmam a direção da Tabela II — o regressivo consulta cerca de metade dos dados e dispara menos da metade das regras — mas acrescentam duas nuances que o artigo não discute. Primeiro, **economia tem custo**: num caso (falha do repetidor a montante), o regressivo para ao atingir certeza suficiente (FC 0,90), enquanto o progressivo acumula toda a evidência (FC 0,97). Segundo, **o custo relevante depende de quem paga pela pergunta**: se a telemetria já foi coletada, perguntar não custa nada e o progressivo é natural para monitoramento; se cada dado exige uma medição ou uma pergunta a um operador, o regressivo evita trabalho. Ambos os modos explicaram suas conclusões, o que contradiz a linha da Tabela II sobre explicação.

## 5. Relação com a disciplina e contextos de aplicação

Os dois encadeamentos reaparecem ao longo da disciplina. O Expert SINTA consulta o usuário de forma regressiva; a análise meios-fins do GPS é orientada por objetivo; os especialistas de um quadro-negro reagem aos dados postados, de forma progressiva; e o A\* mostra que a busca orientada por objetivo só é eficiente quando a heurística é admissível. No diagnóstico de redes, a divisão é prática: o progressivo serve ao alarme contínuo, sobre dados que chegam sozinhos; o regressivo serve à investigação de um incidente, quando o operador precisa decidir o que medir. Sistemas reais combinam os dois — o progressivo levanta hipóteses a partir da telemetria e o regressivo as confirma.

## 6. Conclusão

A conclusão do artigo para o GAES é razoável, e o critério de adequação ao problema é o ensinamento correto. O suporte, porém, é frágil: inconsistências na numeração das regras e na própria tabela comparativa, erros na revisão de busca e nenhuma medição. A escolha entre encadeamentos deveria combinar os critérios de Luger com medidas simples — perguntas feitas, regras disparadas e certeza final —, que mostram tanto a economia do regressivo quanto o seu custo.

## Referências

AL-AJLAN, A. The Comparison between Forward and Backward Chaining. *International Journal of Machine Learning and Computing*, v. 5, n. 2, p. 106–113, 2015. DOI: 10.7763/IJMLC.2015.V5.492.

LUGER, G. F. *Artificial Intelligence*: structures and strategies for complex problem solving. 6. ed. Boston: Pearson, 2009.

RUSSELL, S.; NORVIG, P. *Artificial Intelligence*: a modern approach. 4. ed. Harlow: Pearson, 2021.

SHORTLIFFE, E. H.; BUCHANAN, B. G. A model of inexact reasoning in medicine. *Mathematical Biosciences*, v. 23, n. 3-4, p. 351–379, 1975.

DANTAS, F. S. *ai4systems*: artificial intelligence methods for cyber-physical and networked systems. Versão 0.11.0. 2026. Software. Medições: `literature/systematic-review/al-ajlan-2015/measure_chaining.py`.
