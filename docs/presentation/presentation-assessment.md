# Avaliação da revisão da apresentação

Data: 10 de setembro de 2026. Objeto: qualidade acadêmica, coerência técnica, demonstrações e preparação da exposição. Esta avaliação não atribui nota oficial à disciplina e não pressupõe uma rubrica ou endosso docente.

## Decisão de escopo

A inspeção inicial identificou que os dois arquivos denominados `mini-systems-presentation` continham 21 slides com uma revisão de artigos sobre agentes baseados em modelos de linguagem, embora a capa já apresentasse os três minissistemas. O material pertinente ao projeto estava em `ai-for-smartgrids-apresentacao.pptx`, com 57 slides e notas.

Após a confirmação do uso de aproximadamente 57 slides e a solicitação de um roteiro detalhado sincronizado, a definição editorial tornou-se suficientemente clara para superar o limiar de 95% de certeza solicitado para iniciar a edição. Trata-se de um julgamento de alinhamento com o pedido, não de uma estimativa estatística de correção científica.

O resultado utiliza o cenário de testes internos representados em software nos três trabalhos. Casos ilustrativos, execução simbólica em Python e proposta de experimentação com simulador permanecem explicitamente distinguidos. A identidade visual institucional, os mestres, as cores, a hierarquia e a organização em seções do arquivo de referência foram preservados como base.

## Avaliação anterior e tratamento aplicado

| Área | Constatação na leitura inicial | Tratamento na revisão |
| --- | --- | --- |
| Alinhamento temático | O corpo dos arquivos indicados pertencia a outro assunto. | Substituição por uma exposição completa dos três minissistemas, mantendo a estrutura visual institucional. |
| Coerência de domínio | O material de projeto alternava referências a campo, bancada, ações físicas e simulação. | Cenário computacional unificado; operações apresentadas conforme as instâncias simuladas. |
| Terminologia | Expressões coloquiais e analogias substituíam definições em diversos slides. | Redação acadêmica; definições operacionais de RSSI, SNR, perda adicional, retransmissões, perda de pacotes, RTT e carga oferecida. |
| Sistema especialista | Contagens divergentes; interpretação excessiva de CF; generalizações sobre aprendizagem e independência. | 41 regras na base selecionada; CF como suporte; limites de dependência, calibração, controle de inferência e diagnóstico assistido. |
| Planejamento | Autorização e verificação simbólicas apareciam como garantias operacionais; condição suficiente de heurística era chamada de necessária. | Semântica STRIPS explícita, efeitos assumidos, custo convencional, restrições por falha e condição suficiente de admissibilidade. |
| Busca | Resultados de duas topologias eram apresentados como tendência geral; custo podia ser confundido com latência medida. | Prova condicionada ao modelo, comparação sobre instâncias identificadas e resultados agregados com alcance descritivo. |
| Demonstrações | O comando de planejamento anunciado falhava por argumento desatualizado. | Script acompanhante chama a API com `simulated=True`, verifica saídas e explicita a composição dos módulos. |
| Exposição oral | O modelo institucional não possuía notas; o material de projeto continha notas sem correspondência com esse modelo. | Roteiro de 8.127 palavras, numerado por slide, com fala sugerida, condução, referências e tempo de ensaio. |
| Manutenção | Risco de divergência entre apresentação, roteiro e resultados. | Fonte editorial compartilhada, manifesto de hashes e comando de verificação de sincronização e tabelas numéricas. |

## Estrutura final

| Slides | Conteúdo |
| --- | --- |
| 01–02 | Abertura e estrutura da apresentação. |
| 03–10 | Problema, domínio, grandezas, observações e critérios de correção. |
| 11–24 | Base de conhecimento, CF, inferência, explicação, demonstração e avaliação crítica. |
| 25–38 | STRIPS, hipóteses, operadores, GPS, busca progressiva, demonstração e integração com rotas. |
| 39–49 | A*, função de custo, garantias, comparação, perturbação e aprendizagem como possibilidade futura. |
| 50–53 | Contratos de integração, demonstração completa, protocolo proposto e interpretação das evidências. |
| 54–57 | Contribuições, agenda de investigação, referências e discussão. |

O tempo de ensaio soma 90 minutos, incluindo demonstrações, interpretação de diagramas e discussão. É uma previsão que precisa ser ajustada em ensaio com o apresentador. Os 57 slides estão visíveis; não há apêndices ocultos.

## Evidências reproduzidas

As verificações utilizam Python 3.13.12. A geração utiliza `python-pptx` 1.0.2; a suíte do projeto foi executada com pytest 9.1.1. O commit de referência no momento da geração é `77041711d4fff79303634085acdb62c62fa08870`; o repositório também continha trabalho em andamento. O [manifesto](presentation-manifest.json) registra hashes dos arquivos efetivamente utilizados, evitando tratar o commit isolado como descrição completa do ambiente.

| Verificação | Resultado observado |
| --- | --- |
| Oito casos de diagnóstico | Hipóteses e ações reproduzidas; CF conferidos contra a tabela do slide 23. |
| Contenção MAC | GPS e A*: sete ações, custo 11, plano válido. |
| Contraexemplo de custo local | GPS: custo 11; A*: custo 3; ambos os planos válidos na instância abstrata. |
| Duas falhas selecionadas | Custo 12; uma parada e uma retomada; plano válido. |
| LTE_ENB → AP_B | Custo ótimo 70,51; três saltos; A* expande quatro estados e custo uniforme seis. |
| Remoção de LTE_ENB–LTE_CORE | Nova rota de custo 345,80, excluindo o enlace removido. |
| 870 pares ordenados | A*: 10.310 expansões; custo uniforme: 13.920; redução agregada de 25,93%. |
| Oráculo independente | Floyd–Warshall confirma os custos; nenhuma divergência nas consultas avaliadas. |
| Heurística | Nenhuma violação de admissibilidade ou consistência nas instâncias verificadas. |
| Incidente integrado | Base simulada, estado simulado e destino FD_A explícitos; plano válido; rota evita SAF_A1; custo 267,06. |
| Destino isolado | Nenhuma rota alternativa certificada; nenhum plano de desvio devolvido. |
| Suíte do repositório | 183 testes passaram na primeira avaliação; 202 passaram na execução posterior, após acréscimos concorrentes ao projeto. O aumento não é atribuído à revisão dos slides. |
| Sincronização | 57 títulos e 57 notas conferidos; falas correspondentes no Markdown; tabelas numéricas confrontadas com o registro de execução. |
| Renderização | 57 slides renderizados pelo PowerPoint; inspeção visual da sequência e dos slides densos; nenhuma extrapolação de altura de texto detectada na verificação final de caixas e células. |

Os valores de custo de roteamento estão expressos na escala em milissegundos do modelo. Eles não são resultados medidos de RTT ou de uma campanha de ns-3. O [registro das demonstrações](presentation-evidence.json) contém valores antes do arredondamento.

## Limitações e pendências do projeto

O trabalho acadêmico foi aprimorado pela explicitação das hipóteses e pelo fortalecimento da correspondência entre afirmações e evidências. A revisão documental não produz calibração de limiares, avaliação independente de diagnóstico ou validade externa. Essas etapas permanecem como trabalho experimental.

A auditoria identificou `indoor=args.simulated` no comando de planejamento da interface original, enquanto a API utiliza `simulated`. Também identificou que selecionar a topologia simulada no comando `pipeline` não selecionava automaticamente a base simulada e o domínio simulado de planejamento. Essas observações foram consideradas na escolha dos comandos apresentados. O script acompanhante compõe as APIs explicitamente; a revisão não modifica esses caminhos do código da aplicação.

O mecanismo de inferência permite atualizar contribuições quando premissas se fortalecem, mas isso não demonstra revisão completa diante de retração ou enfraquecimento. O corte de suficiência do modo regressivo é uma política de controle. O roteiro evita alegações universais de invariância entre políticas ou irrelevância de evidências futuras.

O planejador modela concessão de autorização e verificação como efeitos simbólicos. Não existe, nesta demonstração, uma autoridade externa consultada pelo operador nem um ciclo de execução e medição de recuperação. Essas distinções são discutidas nos slides 27, 30, 50 e 53.

## Arquivos e procedimento de atualização

- [Apresentação revisada](mini-systems-presentation-1.pptx).
- [Roteiro detalhado sincronizado](mini-systems-presentation-1-script.md).
- [Original preservado como base visual](mini-systems-presentation-1.baseline.pptx).
- [Fonte editorial](academic_content.py) e [gerador](build_academic_deck.py).
- [Demonstrações verificáveis](presentation_demo.py), [resultados](presentation-evidence.json) e [manifesto](presentation-manifest.json).

Para alterar a fala, os títulos ou o conteúdo visual, editar `academic_content.py`. A geração atualiza simultaneamente a apresentação e o Markdown. As notas do PowerPoint recebem a mesma fala sugerida. Para alterar o desenho, editar o gerador.

```powershell
python docs/presentation/build_academic_deck.py
python docs/presentation/build_academic_deck.py --check
```

Quando o código de aplicação mudar, reproduzir as demonstrações antes de atualizar o material:

```powershell
python docs/presentation/presentation_demo.py all --json docs/presentation/presentation-evidence.json
python docs/presentation/build_academic_deck.py
python docs/presentation/build_academic_deck.py --check
```

O script de demonstração contém expectativas para os resultados apresentados e interrompe a execução se elas deixarem de valer. Uma falha exige reavaliar o resultado e a explicação; não basta substituir números sem análise. A verificação de sincronização também detecta alterações manuais no PPTX, no Markdown e nos arquivos de origem registrados. Após mudanças de layout, é necessário repetir a inspeção visual no PowerPoint.
