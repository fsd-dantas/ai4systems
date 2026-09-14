# Declaração do problema / Problem statement

## Português

Sistemas elétricos inteligentes dependem de redes de comunicação privadas para supervisionar e comandar ativos distribuídos: subestações, religadores, bancos de capacitores e concentradores de medição. Essas redes combinam mais de uma tecnologia de acesso rádio (**multi-RAT**) — tipicamente LTE privativo e rádio em 900 MHz — sobre um núcleo em fibra, justamente para que a falha de um meio não isole um site.

Quando algo falha, o operador precisa responder a três perguntas encadeadas: **o que falhou** (diagnóstico), **o que fazer e em que ordem** (intervenção) e **por onde o tráfego deve seguir enquanto isso** (roteamento). Duas restrições tornam a resposta difícil:

1. **Não há dados rotulados de falha.** Rotular um enlace como degradado exige instrumentação controlada e uma linha de base de observabilidade; sem elas, qualquer rótulo é suposição. Métodos indutivos treinados sobre rótulos supostos herdariam a suposição sem torná-la visível.
2. **A decisão precisa ser justificável.** Uma recomendação que altera a rede de um sistema elétrico precisa mostrar em que evidência se apoia, sob quais hipóteses vale e como pode ser verificada.

O problema, portanto, é produzir **recomendações justificáveis de diagnóstico, intervenção e roteamento sob hipóteses explícitas**, de modo que cada conclusão seja rastreável até a evidência e cada propriedade de correção seja verificada, e não apenas afirmada.

### Escopo

- Os cenários são **sintéticos**. Os resultados valem para os modelos, não para uma instalação real.
- O foco é a camada de decisão. Parâmetros de rádio, limiares e custos são nominais até existirem medições.

## English

Smart electric grids depend on private communication networks to supervise and command distributed assets: substations, reclosers, capacitor banks and metering collectors. These networks combine more than one radio access technology (**multi-RAT**) — typically private LTE and 900 MHz radio — over a fibre core, precisely so that losing one medium does not isolate a site.

When something fails, the operator must answer three chained questions: **what failed** (diagnosis), **what to do and in which order** (intervention), and **where traffic should go meanwhile** (routing). Two constraints make the answer hard:

1. **There is no labelled fault data.** Labelling a link as degraded requires controlled instrumentation and an observability baseline; without them, any label is an assumption. Inductive methods trained on assumed labels would inherit the assumption without making it visible.
2. **The decision must be justifiable.** A recommendation that changes a grid's network must show which evidence it rests on, under which assumptions it holds, and how it can be checked.

The problem is therefore to produce **justifiable diagnosis, intervention and routing recommendations under explicit assumptions**, so that every conclusion is traceable to its evidence and every correctness property is verified rather than merely claimed.

### Scope

- Scenarios are **synthetic**. Results hold for the models, not for a real installation.
- The focus is the decision layer. Radio parameters, thresholds and costs are nominal until measurements exist.
