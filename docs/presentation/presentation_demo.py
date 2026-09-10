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
    problem = problem_from_diagnosis("mac_contention", "ER_03", simulated=True)
    results = {solver.__name__: checked_plan(problem, solver)
               for solver in (plan_with_gps, plan_with_astar)}
    assert all(r["cost"] == 11 for r in results.values())
    return results


def multifault():
    problem = build_restoration_problem("ER_03", ["mac-contention", "excess-path-loss"], simulated=True)
    result = checked_plan(problem, plan_with_astar)
    assert result["cost"] == 12
    assert result["actions"].count("stop_run(ER_03)") == 1
    assert result["actions"].count("start_run(ER_03)") == 1
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
    problem = RoutingProblem(load_topology("dual"), "NOC", "ER_03")
    results = {}
    for solver in (breadth_first, depth_first, uniform_cost, greedy_best_first, astar):
        result = solver(problem, problem.heuristic()) if solver in (astar, greedy_best_first) else solver(problem)
        results[result.algorithm] = checked_route(problem, result)
        print(result.describe("pt"))
    optimal = astar(problem, problem.heuristic())
    assert optimal.path == ["NOC", "eNB_A", "RELAY_1", "RELAY_5", "CPE_03", "ER_03"]
    assert round(optimal.cost, 2) == 360.35
    # The point of this pair: the cheapest route has MORE hops than the
    # shortest one, because the short route drops onto the slow 900 MHz mesh.
    shortest = breadth_first(problem)
    assert len(shortest.path) < len(optimal.path)
    assert round(shortest.cost, 2) == 453.51
    print(problem.explain_path(optimal.path, "pt"))
    return results


def reroute():
    """
    Losing the pLTE side does not isolate the site: it fails over to the mesh.

    That is what dual homing buys, and it is visible in the cost. Disabling the
    fibre to eNB_A removes the whole private LTE path from the NOC, so the only
    remaining route to ER_03 is the 900 MHz store-and-forward chain.
    """
    topology = load_topology("dual")
    topology.disable_link("NOC", "eNB_A")
    problem = RoutingProblem(topology, "NOC", "ER_03")
    result = astar(problem, problem.heuristic())
    checked = checked_route(problem, result)
    assert result.path == ["NOC", "SAF_01", "SAF_02", "RM_03", "ER_03"]
    assert round(result.cost, 2) == 453.51
    print(result.describe("pt"))
    return checked


def benchmark():
    topology = load_topology("dual")
    nodes = sorted(topology.nodes)
    # Independent dynamic-programming oracle; does not invoke the search module.
    # It honours the same stub rule the search does: a grid site is customer
    # edge, so it may begin or end a route but never carry one. Floyd-Warshall
    # expresses that in one guard, because its middle loop IS the choice of
    # intermediate node. Without it the oracle finds cheaper routes across a
    # site and disagrees with every algorithm under test.
    distances = {u: {v: (0.0 if u == v else math.inf) for v in nodes} for u in nodes}
    for u in nodes:
        for v, cost in topology.successors(u):
            distances[u][v] = min(distances[u][v], cost)
    for k in nodes:
        if topology.node(k).stub:
            continue
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
    assert (pairs, informed_total, uniform_total) == (3540, 99963, 109740)
    result = {"ordered_pairs": pairs, "astar_expanded": informed_total,
              "uniform_expanded": uniform_total, "savings_pct": 100 * (1 - informed_total / uniform_total),
              "independent_oracle": "Floyd-Warshall", "cost_mismatches": 0,
              "heuristic_violations": 0}
    print(json.dumps(result, indent=2))
    return result


def integrated():
    diagnosis = diagnose_case("congestion").conclusions()["diagnosis"][0]
    assert diagnosis.value == "congestion"
    topology = load_topology("dual")
    affected, source, target = "SAF_02", "NOC", "ER_06"
    problem = problem_from_diagnosis(str(diagnosis.value), affected, topology=topology,
                                    reroute_target=target, simulated=True)
    assert f"run-active({affected})" in {str(p) for p in problem.initial}
    assert f"alternate-route({affected})" in {str(p) for p in problem.initial}
    plan_result = checked_plan(problem, plan_with_astar)
    assert f"reroute_traffic({affected})" in plan_result["actions"]
    routing = RoutingProblem(topology, source, target, avoid=(affected,))
    result = astar(routing, routing.heuristic())
    route_result = checked_route(routing, result)
    # Normally ER_06 is served by the 900 MHz mesh through SAF_02. Diverting
    # around the congested relay moves the site onto pLTE, and the cost rises.
    assert result.path == ["NOC", "eNB_A", "RELAY_1", "RELAY_5", "CPE_06", "ER_06"]
    assert round(result.cost, 2) == 509.55
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


def planning_graph():
    """
    Interrogate the STRIPS domain through its planning graph.

    Two domains are analysed: the restoration domain as it ships, and a minimal
    reconstruction of the shape it had before the multi-fault fix, where a single
    shared fault-cleared literal was satisfied by ANY repair. The second must
    reproduce the reported defect, and name its cause.
    """
    from aisg.planning.planning_graph import analyse
    from aisg.planning.strips import Operator, Problem, Predicate, make_state

    def two_fault(shared):
        cleared = (lambda f: "fault-cleared(?n)") if shared else (lambda f: f"cleared-{f}(?n)")
        ops = [
            Operator.build("fix_a", parameters=("?n",), preconditions=("fault-a(?n)",),
                           add=(cleared("fault-a"),), delete=("fault-a(?n)",)),
            Operator.build("fix_b", parameters=("?n",), preconditions=("fault-b(?n)",),
                           add=(cleared("fault-b"),), delete=("fault-b(?n)",)),
            Operator.build("verify", parameters=("?n",),
                           preconditions=tuple({cleared("fault-a"), cleared("fault-b")}),
                           add=("service-restored(?n)",)),
        ]
        return Problem(name=f"dois-defeitos(compartilhado={shared})", operators=ops,
                       initial=make_state(["fault-a(N)", "fault-b(N)"]),
                       goal=make_state(["service-restored(N)"]),
                       objects={"node": ["N"]}, parameter_types={"?n": "node"})

    success = Predicate("service-restored", ("N",))
    faults = [Predicate("fault-a", ("N",)), Predicate("fault-b", ("N",))]
    out = {}
    for shared in (True, False):
        result = analyse(two_fault(shared), success=success, fault_literals=faults)
        print(result.render("pt"))
        print()
        out["antes" if shared else "depois"] = {
            "choice_points": {k: list(v) for k, v in result.choice_points.items()},
            "violations": list(result.success_invariant_violations)}

    # the shipped domain: no choice points, no violations, crew operators dead
    live = build_restoration_problem("ER_03", ["mac-contention", "node-stopped"], simulated=True)
    shipped = analyse(live, success=Predicate("service-restored", ("ER_03",)),
                      fault_literals=[Predicate("mac-contention", ("ER_03",)),
                                      Predicate("node-stopped", ("ER_03",))])
    assert shipped.choice_points == {}
    assert shipped.success_invariant_violations == ()
    assert {"dispatch_crew", "realign_antenna"} <= set(shipped.dead_operators)
    assert out["antes"]["violations"] and not out["depois"]["violations"]
    assert out["antes"]["choice_points"] == {"fault-cleared(N)": ["fix_a", "fix_b"]}
    print(shipped.render("pt"))
    out["dominio_atual"] = {"dead_operators": list(shipped.dead_operators),
                            "choice_points": shipped.choice_points,
                            "violations": list(shipped.success_invariant_violations)}
    return out


DEMOS = {"diagnose": diagnose, "planning-graph": planning_graph, "plan": plan, "gps-counterexample": gps_counterexample,
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
