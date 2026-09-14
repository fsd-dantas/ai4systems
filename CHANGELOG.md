# Changelog

Formato baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/); o projeto segue [versionamento semântico](https://semver.org/lang/pt-BR/).
Format based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); the project follows [semantic versioning](https://semver.org/).

## [0.10.0] — 2026-09-14

### Added
- Multi-expert blackboard (`aisg blackboard`): eleven knowledge sources over a levelled blackboard — seven rule experts split from the simulated knowledge base with rule ids unchanged, an incident correlator, an A* access router, a multi-RAT arbiter and a STRIPS restoration planner. See [experiment 002](experiments/002-multi-expert-blackboard/).
- Research framing under `research/` (problem statement, research questions, methodology, roadmap) and repository documentation under `docs/`.
- `CONTRIBUTING.md` with the open-configuration sanitisation checklist, `CODE_OF_CONDUCT.md`, `Makefile`.

### Changed
- Repository restructured from a collection of topics into a research compendium: the `aisg` package moved to `software/`, the diagnosis → plan → route study to `experiments/001-symbolic-restoration-chain/`, figures to `docs/assets/figures/`, and the package configuration to the repository root.
- Presentation material (deck, speaking script, presentation notebook) is no longer tracked.

### Removed
- The field knowledge base and the 17-node base topology; the 60-node dual-homed scenario is the default.

## [0.9.0] — 2026-09-09

### Added
- Rule-based expert system with forward and backward chaining, certainty factors, conflict-resolution policies and why/how explanation.
- STRIPS planning solved by GPS means-ends analysis and by A* progression search, validated by planning-graph analysis.
- A* routing with an admissible, consistent straight-line heuristic, checked against Floyd–Warshall.
