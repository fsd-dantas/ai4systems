"""Reproduce the presentation's illustrative results through the public Python API.

Run from the repository root: python docs/presentation/presentation_demo.py all
This script computes symbolic examples; it neither runs ns-3 nor changes devices.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from aisg.domain import load_topology
from aisg.expert_system import InferenceEngine, SIM_CASES, build_simulated_knowledge_base
from aisg.planning import build_restoration_problem, plan_with_astar, plan_with_gps, problem_from_diagnosis
from aisg.planning.strips import Operator, Problem, make_state
from aisg.search.algorithms import astar, breadth_first, depth_first, greedy_best_first, uniform_cost
from aisg.search.graph_problem import RoutingProblem


def diagnose_case(case):
    engine = InferenceEngine(build_simulated_knowledge_base())
    for variable, value in SIM_CASES[case].items():
        engine.given(variable, value)
    return engine.forward_chain()


def diagnose():
    results = {}
    for case in SIM_CASES:
        consultation = diagnose_case(case)
        conclusions = consultation.conclusions()
        assert conclusions["diagnosis"][0].value == case
        results[case] = {name: {"value": facts[0].value, "cf": facts[0].cf}
                         for name, facts in conclusions.items()}
    print(json.dumps(results, indent=2, ensure_ascii=False))
    consultation = diagnose_case("mac_contention")
    print(consultation.how("diagnosis", "mac_contention"))
    return results


def checked_plan(problem, solver):
    plan, _ = solver(problem)
    assert plan is not None, f"No plan from {solver.__name__}"
    valid, reason = plan.validate()
    assert valid, reason
    print(solver.__name__)
    print(plan.render("pt"))
    print("Validação: positiva")
    return {"cost": plan.cost, "actions": [a.name for a in plan.actions], "valid": valid}


def plan():
    problem = problem_from_diagnosis("mac_contention", "RM_A5", simulated=True)
    results = {solver.__name__: checked_plan(problem, solver)
               for solver in (plan_with_gps, plan_with_astar)}
    assert all(r["cost"] == 11 for r in results.values())
    return results


def multifault():
    problem = build_restoration_problem("RM_A5", ["mac-contention", "excess-path-loss"], simulated=True)
    result = checked_plan(problem, plan_with_astar)
    assert result["cost"] == 12
    assert result["actions"].count("stop_run(RM_A5)") == 1
    assert result["actions"].count("start_run(RM_A5)") == 1
    return result


def gps_counterexample():
    problem = Problem(
        name="abstract-local-versus-total-cost",
        operators=[
            Operator.build("prepare", add=["ready"], cost=10),
            Operator.build("correction_a", preconditions=["ready"], add=["done"], cost=1),
            Operator.build("correction_b", add=["done"], cost=3),
        ], initial=make_state([]), goal=make_state(["done"]),
    )
    results = {solver.__name__: checked_plan(problem, solver)
               for solver in (plan_with_gps, plan_with_astar)}
    assert results["plan_with_gps"]["cost"] == 11
    assert results["plan_with_astar"]["cost"] == 3
    return results


def checked_route(problem, result):
    assert result.found
    assert result.path[0] == problem.start and result.path[-1] == problem.goal
    assert not set(problem.avoid).intersection(result.path)
    assert math.isclose(problem.topology.path_cost(result.path), result.cost, abs_tol=1e-9)
    return {"path": result.path, "cost": result.cost, "expanded": result.expanded,
            "hops": result.length}


def route():
    problem = RoutingProblem(load_topology("simulated"), "LTE_ENB", "AP_B")
    results = {}
    for solver in (breadth_first, depth_first, uniform_cost, greedy_best_first, astar):
        result = solver(problem, problem.heuristic()) if solver in (astar, greedy_best_first) else solver(problem)
        results[result.algorithm] = checked_route(problem, result)
        print(result.describe("pt"))
    optimal = astar(problem, problem.heuristic())
    assert optimal.path == ["LTE_ENB", "LTE_CORE", "NOC", "AP_B"]
    assert round(optimal.cost, 2) == 70.51
    print(problem.explain_path(optimal.path, "pt"))
    return results


def reroute():
    topology = load_topology("simulated")
    topology.disable_link("LTE_ENB", "LTE_CORE")
    problem = RoutingProblem(topology, "LTE_ENB", "AP_B")
    result = astar(problem, problem.heuristic())
    checked = checked_route(problem, result)
    assert round(result.cost, 2) == 345.80
    print(result.describe("pt"))
    return checked


def benchmark():
    topology = load_topology("simulated")
    nodes = sorted(topology.nodes)
    # Independent dynamic-programming oracle; does not invoke the search module.
    distances = {u: {v: (0.0 if u == v else math.inf) for v in nodes} for u in nodes}
    for u in nodes:
        for v, cost in topology.successors(u):
            distances[u][v] = min(distances[u][v], cost)
    for k in nodes:
        for u in nodes:
            for v in nodes:
                distances[u][v] = min(distances[u][v], distances[u][k] + distances[k][v])
    pairs = informed_total = uniform_total = 0
    for source in nodes:
        for goal in nodes:
            if source == goal:
                continue
            problem = RoutingProblem(topology, source, goal)
            h = problem.heuristic()
            informed, uniform = astar(problem, h), uniform_cost(problem)
            checked_route(problem, informed)
            assert math.isclose(informed.cost, distances[source][goal], abs_tol=1e-9)
            assert math.isclose(uniform.cost, distances[source][goal], abs_tol=1e-9)
            for u in nodes:
                assert 0 <= h(u) <= distances[u][goal] + 1e-9
                for v, cost in topology.successors(u):
                    assert h(u) <= cost + h(v) + 1e-9
            pairs += 1
            informed_total += informed.expanded
            uniform_total += uniform.expanded
    assert (pairs, informed_total, uniform_total) == (870, 10310, 13920)
    result = {"ordered_pairs": pairs, "astar_expanded": informed_total,
              "uniform_expanded": uniform_total, "savings_pct": 100 * (1 - informed_total / uniform_total),
              "independent_oracle": "Floyd-Warshall", "cost_mismatches": 0,
              "heuristic_violations": 0}
    print(json.dumps(result, indent=2))
    return result


def integrated():
    diagnosis = diagnose_case("congestion").conclusions()["diagnosis"][0]
    assert diagnosis.value == "congestion"
    topology = load_topology("simulated")
    affected, source, target = "SAF_A1", "NOC", "FD_A"
    problem = problem_from_diagnosis(str(diagnosis.value), affected, topology=topology,
                                    reroute_target=target, simulated=True)
    assert f"run-active({affected})" in {str(p) for p in problem.initial}
    assert f"alternate-route({affected})" in {str(p) for p in problem.initial}
    plan_result = checked_plan(problem, plan_with_astar)
    assert f"reroute_traffic({affected})" in plan_result["actions"]
    routing = RoutingProblem(topology, source, target, avoid=(affected,))
    result = astar(routing, routing.heuristic())
    route_result = checked_route(routing, result)
    assert round(result.cost, 2) == 267.06
    print("Base: simulated; planejamento: simulated=True")
    print(f"Diagnóstico: {diagnosis.value}, CF {diagnosis.cf:+.3f}")
    print(result.describe("pt"))
    # Also exercise an impossible diversion with the same destination.
    for neighbor, _ in list(topology.neighbours(target)):
        topology.disable_link(target, neighbor)
    blocked = problem_from_diagnosis("congestion", affected, topology=topology,
                                    reroute_target=target, simulated=True)
    assert f"alternate-route({affected})" not in {str(p) for p in blocked.initial}
    blocked_plan, _ = plan_with_astar(blocked)
    assert blocked_plan is None
    return {"diagnosis_cf": diagnosis.cf, "plan": plan_result, "route": route_result,
            "isolated_destination_plan": None}


DEMOS = {"diagnose": diagnose, "plan": plan, "gps-counterexample": gps_counterexample,
         "multifault": multifault, "route": route, "reroute": reroute,
         "benchmark": benchmark, "integrated": integrated}


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("demo", choices=[*DEMOS, "all"])
    parser.add_argument("--json", type=Path, help="Optional evidence output file")
    args = parser.parse_args()
    selected = DEMOS if args.demo == "all" else {args.demo: DEMOS[args.demo]}
    results = {}
    for name, run in selected.items():
        print(f"\n=== {name} ===")
        results[name] = run()
    if args.json:
        args.json.write_text(json.dumps(results, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("\nVerificações das demonstrações concluídas.")


if __name__ == "__main__":
    main()
