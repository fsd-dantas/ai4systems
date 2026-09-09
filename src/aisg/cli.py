"""
Command-line interface / Interface de linha de comando.

PT-BR: Quatro subcomandos: ``diagnose`` (sistema especialista), ``plan``
       (planejamento STRIPS/GPS/A*), ``route`` (busca A*) e ``pipeline``, que executa
       os tres em sequencia sobre o mesmo incidente.

EN:    Four subcommands: ``diagnose`` (expert system), ``plan`` (STRIPS/GPS/A*
       planning), ``route`` (A* search), and ``pipeline``, which runs all three in
       sequence over the same incident.

    python -m aisg diagnose --case interference --trace
    python -m aisg diagnose --interactive --mode backward
    python -m aisg route --from NOC --to RECLOSER_7 --compare
    python -m aisg plan --diagnosis congestion --node SAF_A2 --solver both
    python -m aisg pipeline --case congestion --node SAF_A2
"""

from __future__ import annotations

import argparse
import sys
from typing import Optional, Sequence, Tuple

from aisg import __version__
from aisg.domain import load_default_topology
from aisg.expert_system import (
    CASES,
    ConflictResolution,
    Consultation,
    InferenceEngine,
    Variable,
    VariableKind,
    build_knowledge_base,
)
from aisg.i18n import t
from aisg.planning import (
    fault_literals,
    format_state,
    plan_with_astar,
    plan_with_gps,
    problem_from_diagnosis,
)
from aisg.search import RoutingProblem, astar, compare
from aisg.search.algorithms import SearchResult

RULE = "=" * 78
THIN = "-" * 78


def _header(text: str) -> str:
    return f"\n{RULE}\n{text}\n{RULE}"


# ---------------------------------------------------------------------------
# expert system
# ---------------------------------------------------------------------------
def _make_asker(lang: str, engine_holder: dict):
    """Build the interactive question callback for backward chaining."""

    def ask(variable: Variable, _why_stack) -> Optional[Tuple[object, float]]:
        engine = engine_holder.get("engine")
        while True:
            print()
            print(variable.prompt(lang))
            if variable.kind is VariableKind.NUMERIC:
                lo, hi = variable.bounds or (None, None)
                hint = f"  [{lo}, {hi}] {variable.unit}".rstrip()
            else:
                hint = "  " + " | ".join(variable.labels)
            print(f"{hint}   {t('value_unknown_hint', lang)}  ('?' = why / por que)")
            raw = input("> ").strip()

            if raw == "":
                return None
            if raw == "?":
                print()
                print(t("es_why", lang))
                if engine is not None:
                    print(engine.why(lang))
                continue

            # An optional trailing certainty: "rain 0.6"
            cf = 1.0
            parts = raw.rsplit(" ", 1)
            if len(parts) == 2:
                try:
                    candidate = float(parts[1])
                except ValueError:
                    pass
                else:
                    if -1.0 <= candidate <= 1.0:
                        raw, cf = parts[0].strip(), candidate

            if variable.kind is VariableKind.NUMERIC:
                try:
                    value: object = float(raw)
                except ValueError:
                    print(t("invalid_option", lang))
                    continue
            else:
                value = raw
            try:
                variable.validate_value(value)
            except ValueError as exc:
                print(f"{t('invalid_option', lang)} ({exc})")
                continue
            return value, cf

    return ask


def _report_consultation(consultation: Consultation, lang: str, *, show_trace: bool,
                         show_explanation: bool) -> None:
    kb = consultation.kb

    if show_trace:
        print(_header(f"TRACE ({consultation.strategy})"))
        print(consultation.render_trace())

    print(_header(t("es_conclusion", lang)))
    conclusions = consultation.conclusions()
    if not conclusions:
        print(t("es_no_conclusion", lang))
    else:
        for goal, facts in conclusions.items():
            variable = kb.variables[goal]
            print(f"\n{variable.label(lang)}:")
            for fact in facts:
                bar = "#" * max(0, int(round(abs(fact.cf) * 20)))
                sign = " " if fact.cf >= 0 else "-"
                print(f"  {str(fact.value):<26} CF {fact.cf:+.2f} {sign}{bar}")

    if show_explanation and conclusions:
        print(_header(t("es_how", lang)))
        for goal, facts in conclusions.items():
            print(consultation.how(goal, facts[0].value, lang))
            print()

    print(THIN)
    print(kb.validity_note(lang))
    print(THIN)


def cmd_diagnose(args: argparse.Namespace) -> int:
    lang = args.lang
    kb = build_knowledge_base()
    holder: dict = {}
    engine = InferenceEngine(
        kb,
        ask=_make_asker(lang, holder) if args.interactive else None,
        strategy=ConflictResolution(args.strategy),
    )
    holder["engine"] = engine

    print(_header(f"{t('es_title', lang)}  [{kb.name(lang)}]"))

    if args.case:
        if args.case not in CASES:
            print(f"unknown case: {args.case}; available: {', '.join(sorted(CASES))}")
            return 2
        for variable, value in CASES[args.case].items():
            engine.given(variable, value)
        print(f"{t('es_known_facts', lang)}: {args.case}")
        for fact in engine.memory.all_facts():
            print(f"  {fact.render(kb, lang)}")
    elif not args.interactive:
        print("Use --case NAME or --interactive.")
        return 2

    mode_label = t("es_backward" if args.mode == "backward" else "es_forward", lang)
    print(f"\n[{mode_label}]")

    if args.mode == "backward":
        consultation = engine.backward_chain(args.goal)
    else:
        consultation = engine.forward_chain()

    _report_consultation(
        consultation, lang, show_trace=args.trace, show_explanation=args.explain
    )
    return 0


# ---------------------------------------------------------------------------
# routing
# ---------------------------------------------------------------------------
def _print_search_result(result: SearchResult, problem: RoutingProblem, lang: str,
                         *, show_expansion: bool) -> None:
    print(result.describe(lang))
    if show_expansion and result.expansion_order:
        order = " ".join(str(s) for s in result.expansion_order)
        label = "ordem de expansao" if lang == "pt" else "expansion order"
        print(f"  {label}: {order}")


def cmd_route(args: argparse.Namespace) -> int:
    lang = args.lang
    topology = load_default_topology()

    for spec in args.disable_link or []:
        try:
            a, b = spec.split("-", 1)
            topology.disable_link(a, b)
        except (ValueError, KeyError) as exc:
            print(f"--disable-link {spec}: {exc}")
            return 2

    print(_header(t("se_title", lang)))
    print(topology.summary(lang))

    try:
        problem = RoutingProblem(topology, args.source, args.target, tuple(args.avoid or ()))
    except (KeyError, ValueError) as exc:
        print(exc)
        return 2

    print()
    if args.compare:
        for result in compare(problem, problem.heuristic()):
            _print_search_result(result, problem, lang, show_expansion=args.expansion)
            print()
        return 0

    result = astar(problem, problem.heuristic())
    if not result.found:
        print(t("se_no_path", lang, start=args.source, goal=args.target))
        return 1
    _print_search_result(result, problem, lang, show_expansion=args.expansion)
    print()
    print(problem.explain_path(result.path, lang))
    return 0


# ---------------------------------------------------------------------------
# planning
# ---------------------------------------------------------------------------
def _report_plan(plan, lang: str, *, label: str) -> None:
    print(f"\n[{label}]")
    if plan is None:
        print(t("pl_no_plan", lang))
        return
    print(t("pl_plan_found", lang, n=plan.length))
    print(plan.render(lang))
    ok, reason = plan.validate()
    print(t("pl_validation_ok", lang) if ok else t("pl_validation_fail", lang, reason=reason))
    if plan.stats:
        stats = ", ".join(f"{k}={v:g}" for k, v in sorted(plan.stats.items()))
        print(f"  ({stats})")


def cmd_plan(args: argparse.Namespace) -> int:
    lang = args.lang
    topology = load_default_topology()
    try:
        problem = problem_from_diagnosis(args.diagnosis, args.node, topology=topology)
    except (ValueError, KeyError) as exc:
        print(exc)
        return 2

    print(_header(t("pl_title", lang)))
    print(f"{t('pl_initial_state', lang)}:")
    print(format_state(problem.initial))
    print(f"\n{t('pl_goal_state', lang)}:")
    print(format_state(problem.goal))
    faults = fault_literals(problem)
    if faults:
        label = "falha diagnosticada" if lang == "pt" else "diagnosed fault"
        print(f"\n{label}: {', '.join(str(f) for f in faults)}")

    if args.solver in ("gps", "both"):
        plan, trace = plan_with_gps(problem, lang=lang)
        if args.trace:
            print(_header("GPS — means-ends analysis trace"))
            print(trace.render())
        _report_plan(plan, lang, label="GPS (means-ends analysis)")

    if args.solver in ("astar", "both"):
        plan, result = plan_with_astar(problem, heuristic=args.heuristic)
        _report_plan(plan, lang, label=result.algorithm)

    return 0


# ---------------------------------------------------------------------------
# pipeline: expert system -> planner -> A*
# ---------------------------------------------------------------------------
def cmd_pipeline(args: argparse.Namespace) -> int:
    lang = args.lang
    topology = load_default_topology()
    kb = build_knowledge_base()

    if args.case not in CASES:
        print(f"unknown case: {args.case}; available: {', '.join(sorted(CASES))}")
        return 2

    # --- 1. diagnose -----------------------------------------------------
    print(_header(f"1/3  {t('es_title', lang)}"))
    engine = InferenceEngine(kb)
    for variable, value in CASES[args.case].items():
        engine.given(variable, value)
    consultation = engine.forward_chain()
    conclusions = consultation.conclusions()
    if "diagnosis" not in conclusions:
        print(t("es_no_conclusion", lang))
        return 1

    diagnosis = conclusions["diagnosis"][0]
    action = conclusions.get("recommended_action", [None])[0]
    print(f"  {kb.variables['diagnosis'].label(lang)}: "
          f"{diagnosis.value} (CF {diagnosis.cf:+.2f})")
    if action is not None:
        print(f"  {kb.variables['recommended_action'].label(lang)}: "
              f"{action.value} (CF {action.cf:+.2f})")

    # --- 2. plan ---------------------------------------------------------
    print(_header(f"2/3  {t('pl_title', lang)}"))
    problem = problem_from_diagnosis(str(diagnosis.value), args.node, topology=topology)
    plan, result = plan_with_astar(problem)
    _report_plan(plan, lang, label=result.algorithm)

    # --- 3. route --------------------------------------------------------
    print(_header(f"3/3  {t('se_title', lang)}"))
    reroute = plan is not None and any(
        a.operator.name == "reroute_traffic" for a in plan.actions
    )
    target = args.target or next(
        (n.id for n in topology.nodes.values() if n.kind == "field_device"), None
    )
    source = next(
        (n.id for n in topology.nodes.values() if n.kind == "control_centre"),
        next(iter(topology.nodes)),
    )
    if target is None:
        print("no field device in the topology to route towards")
        return 0

    avoid = (args.node,) if reroute else ()
    if reroute:
        note = (f"O plano inclui desviar trafego: recalculando a rota evitando {args.node}."
                if lang == "pt"
                else f"The plan includes rerouting: recomputing the route avoiding {args.node}.")
        print(note)
    try:
        routing = RoutingProblem(topology, source, target, avoid)
    except ValueError as exc:
        print(exc)
        return 0
    search = astar(routing, routing.heuristic())
    if not search.found:
        print(t("se_no_path", lang, start=source, goal=target))
        return 1
    print(search.describe(lang))
    print()
    print(routing.explain_path(search.path, lang))
    return 0


# ---------------------------------------------------------------------------
def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="aisg",
        description=(
            "AI for smart grids: expert system, automated planning, and A* search. / "
            "IA para redes eletricas inteligentes: sistema especialista, planejamento "
            "automatico e busca A*."
        ),
    )
    parser.add_argument("--version", action="version", version=f"aisg {__version__}")
    parser.add_argument(
        "--lang", choices=("pt", "en"), default="pt", help="output language / idioma"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # diagnose
    d = sub.add_parser("diagnose", help="run the expert system / executar o sistema especialista")
    d.add_argument("--case", help=f"preset case: {', '.join(sorted(CASES))}")
    d.add_argument("--interactive", action="store_true", help="ask the user for facts")
    d.add_argument("--mode", choices=("forward", "backward"), default="forward")
    d.add_argument("--goal", default="diagnosis", help="goal variable for backward chaining")
    d.add_argument(
        "--strategy",
        choices=[s.value for s in ConflictResolution],
        default=ConflictResolution.SPECIFICITY.value,
        help="conflict-resolution policy / politica de resolucao de conflito",
    )
    d.add_argument("--trace", action="store_true", help="show the reasoning trace")
    d.add_argument("--explain", action="store_true", help="explain HOW each conclusion was reached")
    d.set_defaults(func=cmd_diagnose)

    # route
    r = sub.add_parser("route", help="A* routing / roteamento por A*")
    r.add_argument("--from", dest="source", default="NOC")
    r.add_argument("--to", dest="target", default="RECLOSER_7")
    r.add_argument("--avoid", nargs="*", help="nodes the route must not traverse")
    r.add_argument("--disable-link", nargs="*", metavar="A-B", help="take links out of service")
    r.add_argument("--compare", action="store_true", help="compare BFS, DFS, UCS, greedy, A*")
    r.add_argument("--expansion", action="store_true", help="print the expansion order")
    r.set_defaults(func=cmd_route)

    # plan
    p = sub.add_parser("plan", help="automated planning / planejamento automatico")
    p.add_argument("--diagnosis", default="rf_interference")
    p.add_argument("--node", default="RM_A5")
    p.add_argument("--solver", choices=("gps", "astar", "both"), default="both")
    p.add_argument("--heuristic", choices=("goal_count", "zero"), default="goal_count")
    p.add_argument("--trace", action="store_true", help="show the means-ends trace")
    p.set_defaults(func=cmd_plan)

    # pipeline
    pl = sub.add_parser(
        "pipeline", help="diagnose -> plan -> route / diagnosticar -> planejar -> rotear"
    )
    pl.add_argument("--case", default="congestion", help=f"one of: {', '.join(sorted(CASES))}")
    pl.add_argument("--node", default="SAF_A2")
    pl.add_argument("--target", help="routing destination / destino do roteamento")
    pl.set_defaults(func=cmd_pipeline)

    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.func(args))
    except KeyboardInterrupt:
        print("\ninterrupted / interrompido")
        return 130


if __name__ == "__main__":
    sys.exit(main())
