# Contribuindo / Contributing

Issues e pull requests são bem-vindos. Antes de propor uma mudança grande, abra uma issue descrevendo o problema.
Issues and pull requests are welcome. Before proposing a large change, open an issue describing the problem.

## Ambiente / Setup

```bash
python -m pip install -e ".[dev]"
make check        # testes + verificação da CLI / tests + CLI smoke check
```

O núcleo usa apenas a biblioteca padrão do Python 3.10+. Dependências de terceiros ficam em extras opcionais.
The core uses only the Python 3.10+ standard library. Third-party dependencies live in optional extras.

## Convenções / Conventions

- **Bilíngue / Bilingual.** Docstrings de módulo e classe em pt-BR e inglês; identificadores, mensagens de commit e nomes de teste em inglês. Module and class docstrings in pt-BR and English; identifiers, commit messages and test names in English.
- **Sem acentos no código-fonte / No accented characters in source files.** Evita problemas de codificação em terminais; a documentação Markdown usa acentuação completa. Avoids terminal encoding issues; Markdown documentation uses full accents.
- **Testes afirmam propriedades / Tests assert properties** — admissibilidade, validade de plano, invariantes — e não apenas saídas esperadas. Admissibility, plan validity, invariants — not just expected outputs.
- **Limiares declarados / Declared thresholds.** Todo parâmetro numérico usado por regra vive num único bloco, marcado como nominal e não calibrado. Every numeric parameter a rule uses lives in one block, marked nominal and uncalibrated.
- **Figuras / Figures** em inglês, com variantes clara e escura, em `docs/assets/figures/`. In English, with light and dark variants, under `docs/assets/figures/`.

## Estrutura de um experimento / Experiment layout

Cada experimento em `experiments/NNN-nome/` tem um `README.md` com a questão, o método, como executar e como os resultados são verificados. Pastas como `configuration/`, `scripts/`, `results/` e `report.md` só existem quando têm conteúdo.

Each experiment under `experiments/NNN-name/` has a `README.md` stating the question, the method, how to run it and how its results are checked. Folders such as `configuration/`, `scripts/`, `results/` and `report.md` exist only when they have content.

## Configurações e dados abertos / Open configurations and data

Configurações e dados que sustentam artigos são publicados. Por isso, nada que identifique uma rede real pode entrar no repositório. Antes de cada commit com configuração, confira:

Configurations and data behind articles are published. Nothing that identifies a real network may therefore enter the repository. Before any commit containing configuration, check:

- [ ] nenhuma chave de assinante real (`Ki`, `OPc`), IMSI ou IMEI / no real subscriber key (`Ki`, `OPc`), IMSI or IMEI;
- [ ] nenhum PLMN (MCC/MNC) de operadora real / no real operator PLMN (MCC/MNC);
- [ ] nenhum endereçamento IP, hostname, número de série ou identificador de equipamento real / no real IP addressing, hostname, serial number or equipment identifier;
- [ ] nenhuma coordenada, nome de subestação ou topologia de campo real / no real coordinate, substation name or field topology;
- [ ] identificadores sintéticos e declarados como tal / identifiers are synthetic and declared as such.

## Versões / Releases

1. Atualize a versão em `pyproject.toml`, `software/aisg/__init__.py` e `CITATION.cff`, e mova as notas de `[Unreleased]` para a nova versão no `CHANGELOG.md`. / Bump the version in `pyproject.toml`, `software/aisg/__init__.py` and `CITATION.cff`, and move the `[Unreleased]` notes to the new version in `CHANGELOG.md`.
2. Crie e envie a tag / create and push the tag: `git tag vX.Y.Z && git push origin vX.Y.Z`.
3. O workflow `release` testa, gera o wheel, o arquivo-fonte e o pacote ns-3, e publica a versão no GitHub. / The `release` workflow tests, builds the wheel, source archive and ns-3 bundle, and publishes the GitHub Release.

## Commits

Mensagens em inglês, no imperativo, com um parágrafo explicando o porquê quando não for óbvio.
Messages in English, imperative mood, with a paragraph explaining why when it is not obvious.
