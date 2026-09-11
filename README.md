<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/fsd-dantas/ai4systems/main/docs/assets/banner-dark.jpg">
    <img src="https://raw.githubusercontent.com/fsd-dantas/ai4systems/main/docs/assets/banner-light.jpg" alt="Artificial Intelligence for Systems — research on cyber-physical and networked systems. An isometric lattice with energised traces wiring a search tree, a network router, a transmission tower, a gauge, a feedback controller and a network mesh to one AI processor." width="100%">
  </picture>
</p>

# ai4systems

**AI for Systems** — métodos de Inteligência Artificial para sistemas ciber-físicos e em rede.
*Artificial Intelligence methods for cyber-physical and networked systems.*

[![tests](https://github.com/fsd-dantas/ai4systems/actions/workflows/tests.yml/badge.svg)](https://github.com/fsd-dantas/ai4systems/actions/workflows/tests.yml)
[![license: MIT](https://img.shields.io/badge/license-MIT-555555)](LICENSE)
[![wiki](https://img.shields.io/badge/wiki-fundamentos%20%2F%20foundations-555555)](https://github.com/fsd-dantas/ai4systems/wiki)

> **PT-BR** — Este repositório reúne estudos de pesquisa que aplicam métodos de IA a sistemas ciber-físicos e em rede, começando pelas redes de comunicação de sistemas elétricos inteligentes. Cada **tópico** é um estudo autocontido: questão de pesquisa, código, testes, documentação e material de apresentação.
>
> **EN** — This repository gathers research studies that apply AI methods to cyber-physical and networked systems, starting with the communication networks of smart electric grids. Each **topic** is a self-contained study: research question, code, tests, documentation, and presentation material.

## Tópicos / Topics

| Tópico / Topic | Questão de pesquisa / Research question | Métodos / Methods | Estado / Status |
|---|---|---|---|
| [**Symbolic AI for Network Restoration**](topics/symbolic-network-restoration/) | Sem um conjunto de dados rotulado de falhas, é possível construir um encadeamento diagnóstico → plano → rota auditável e verificável? / Without a labelled fault dataset, can a diagnosis → plan → route chain be both auditable and verifiable? | Regras de produção com fatores de certeza, STRIPS e GPS, busca A* / Production rules with certainty factors, STRIPS and GPS, A* search | v0.9.0 · ativo / active |

## Fundamentos / Foundations

A [wiki](https://github.com/fsd-dantas/ai4systems/wiki) reúne a teoria que sustenta os tópicos — raciocínio, busca, planejamento, representação do conhecimento, agentes e aprendizagem — e liga cada conceito ao código que o realiza.

The [wiki](https://github.com/fsd-dantas/ai4systems/wiki) gathers the theory behind the topics — reasoning, search, planning, knowledge representation, agents and learning — and ties each concept to the code that realises it.

## Organização / Layout

```
topics/
  symbolic-network-restoration/   README, pyproject.toml, src/, tests/, docs/, notebooks/, examples/
```

Cada tópico tem o próprio `pyproject.toml` e as próprias dependências, de modo que um tópico novo nunca impõe dependências aos existentes. Para instalar e executar um tópico, siga o README dele.

Each topic has its own `pyproject.toml` and its own dependencies, so a new topic never imposes dependencies on the existing ones. To install and run a topic, follow its README.

## Como citar / How to cite

Use [`CITATION.cff`](CITATION.cff). No GitHub, o botão **Cite this repository** gera BibTeX e APA a partir dele.
Use [`CITATION.cff`](CITATION.cff). On GitHub, the **Cite this repository** button generates BibTeX and APA from it.

## Autor / Author

Fernando Sabino Dantas.

## Licença / License

[MIT](LICENSE).
