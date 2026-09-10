"""
Tests for the search algorithms and the routing problem.

PT-BR: Os testes mais importantes aqui nao sao 'o A* encontra um caminho', e sim
       'o caminho e OTIMO' e 'a heuristica e admissivel e consistente' — as duas
       propriedades das quais a otimalidade depende.

EN:    The most important tests here are not 'A* finds a path' but 'the path is
       OPTIMAL' and 'the heuristic is admissible and consistent' — the two properties
       optimality rests on.
"""

from __future__ import annotations

import itertools
import math

import pytest

from aisg.domain import (
    BUNDLED_TOPOLOGIES,
    MAX_SPEED_M_PER_MS,
    load_default_topology,
    load_topology,
)
from aisg.search import (
    RoutingProblem,
    astar,
    breadth_first,
    depth_first,
    greedy_best_first,
    iterative_deepening,
    shortest_route,
    uniform_cost,
)


@pytest.fixture
def topology():
    """The 17-node working scenario."""
    return load_default_topology()


@pytest.fixture(params=sorted(BUNDLED_TOPOLOGIES))
def any_topology(request):
    """
    Every bundled scenario.

    PT-BR: As propriedades do A* — admissibilidade, consistencia e otimalidade — nao
           podem depender do cenario. Por isso sao verificadas em todos eles.
    EN:    A*'s properties — admissibility, consistency, optimality — must not depend
           on the scenario, so they are checked against every one of them.
    """
    return load_topology(request.param)


# --- topology integrity ----------------------------------------------------
def test_every_bundled_scenario_is_connected(any_topology):
    start = next(iter(any_topology.nodes))
    reached = {start}
    frontier = [start]
    while frontier:
        for neighbour, _link in any_topology.neighbours(frontier.pop()):
            if neighbour not in reached:
                reached.add(neighbour)
                frontier.append(neighbour)
    assert reached == set(any_topology.nodes), "every node must be reachable"


def test_bundled_scenarios_have_the_expected_size():
    assert len(load_topology("base").nodes) == 17
    assert len(load_topology("scale").nodes) == 30


def test_link_costs_are_positive(any_topology):
    for link in any_topology.active_links():
        assert any_topology.link_cost(link) > 0


def test_unknown_topology_name_is_rejected():
    with pytest.raises(KeyError, match="unknown topology"):
        load_topology("nonexistent-scenario")


# --- heuristic properties: the heart of A* ---------------------------------
def test_heuristic_is_admissible_for_every_source_goal_pair(any_topology):
    """h(n) must never exceed the true optimal cost from n to the goal."""
    for goal in any_topology.nodes:
        h = any_topology.heuristic(goal)
        for source in any_topology.nodes:
            problem = RoutingProblem(any_topology, source, goal)
            optimal = uniform_cost(problem)  # ground truth, no heuristic involved
            assert optimal.found
            assert h(source) <= optimal.cost + 1e-9, (
                f"h({source}) = {h(source):.3f} overestimates the true cost "
                f"{optimal.cost:.3f} to {goal}"
            )


def test_heuristic_is_consistent(any_topology):
    """h(u) <= cost(u, v) + h(v) for every edge and every goal."""
    for goal in any_topology.nodes:
        h = any_topology.heuristic(goal)
        for u in any_topology.nodes:
            for v, step_cost in any_topology.successors(u):
                assert h(u) <= step_cost + h(v) + 1e-9, (
                    f"consistency violated on {u} -> {v} towards {goal}"
                )


def test_heuristic_is_zero_at_the_goal(topology):
    h = topology.heuristic("RECLOSER_7")
    assert h("RECLOSER_7") == pytest.approx(0.0)


def test_heuristic_equals_straight_line_over_max_speed(topology):
    h = topology.heuristic("SUB_S1")
    expected = topology.distance("NOC", "SUB_S1") / MAX_SPEED_M_PER_MS
    assert h("NOC") == pytest.approx(expected)


# --- optimality ------------------------------------------------------------
def test_astar_matches_uniform_cost_on_every_pair(any_topology):
    """A* with an admissible heuristic must return an optimal-cost path."""
    for source, goal in itertools.combinations(sorted(any_topology.nodes), 2):
        problem = RoutingProblem(any_topology, source, goal)
        optimal = uniform_cost(problem)
        informed = astar(problem, problem.heuristic())
        assert informed.found == optimal.found
        assert informed.cost == pytest.approx(optimal.cost)


def _floyd_warshall(topology):
    """
    All-pairs shortest costs, computed WITHOUT any of the package's search code.

    PT-BR: `uniform_cost` e literalmente `astar` com h=0 — comparar os dois nao e
           uma verificacao independente: um defeito no laco principal, na fila de
           prioridade ou na reconstrucao do caminho corromperia os dois de forma
           identica e o teste passaria. Floyd-Warshall e um algoritmo diferente,
           escrito aqui, e por isso serve de referencia externa.
    EN:    `uniform_cost` is literally `astar` with h=0, so comparing them is not
           an independent check: a defect in the main loop, the priority queue or
           path reconstruction would corrupt both identically and the test would
           still pass. Floyd-Warshall is a different algorithm, written here, and
           therefore an outside reference.
    """
    nodes = sorted(topology.nodes)
    index = {n: i for i, n in enumerate(nodes)}
    size = len(nodes)
    dist = [[math.inf] * size for _ in range(size)]
    for i in range(size):
        dist[i][i] = 0.0
    for node in nodes:
        for neighbour, step in topology.successors(node):
            i, j = index[node], index[neighbour]
            dist[i][j] = min(dist[i][j], step)

    for k in range(size):
        dk = dist[k]
        for i in range(size):
            via = dist[i][k]
            if via == math.inf:
                continue
            row = dist[i]
            for j in range(size):
                candidate = via + dk[j]
                if candidate < row[j]:
                    row[j] = candidate
    return nodes, index, dist


def test_astar_matches_an_independent_reference_on_every_ordered_pair(any_topology):
    """A* costs must match Floyd-Warshall, which shares no code with the package."""
    nodes, index, dist = _floyd_warshall(any_topology)
    checked = 0
    for source in nodes:
        for goal in nodes:
            if source == goal:
                continue
            problem = RoutingProblem(any_topology, source, goal)
            result = astar(problem, problem.heuristic())
            reference = dist[index[source]][index[goal]]
            assert result.found == (reference < math.inf)
            if result.found:
                assert result.cost == pytest.approx(reference), (
                    f"{source} -> {goal}: A* says {result.cost:.4f}, "
                    f"Floyd-Warshall says {reference:.4f}"
                )
            checked += 1
    assert checked == len(nodes) * (len(nodes) - 1)  # ordered pairs


def test_astar_never_expands_more_nodes_than_uniform_cost(any_topology):
    """A consistent heuristic can only help. Totalled to avoid per-pair noise."""
    astar_total = ucs_total = 0
    for source, goal in itertools.combinations(sorted(any_topology.nodes), 2):
        problem = RoutingProblem(any_topology, source, goal)
        astar_total += astar(problem, problem.heuristic()).expanded
        ucs_total += uniform_cost(problem).expanded
    assert astar_total <= ucs_total


def test_the_heuristic_saves_more_work_as_the_graph_grows():
    """
    PT-BR: A vantagem da heuristica cresce com o grafo — o argumento pratico a favor
           do A* em cenarios maiores.
    EN:    The heuristic's advantage grows with the graph — the practical argument for
           A* on larger scenarios.
    """
    savings = {}
    for name in ("base", "scale"):
        topology = load_topology(name)
        astar_total = ucs_total = 0
        for source, goal in itertools.combinations(sorted(topology.nodes), 2):
            problem = RoutingProblem(topology, source, goal)
            astar_total += astar(problem, problem.heuristic()).expanded
            ucs_total += uniform_cost(problem).expanded
        savings[name] = 1.0 - astar_total / ucs_total

    assert savings["scale"] > savings["base"]


def test_reported_cost_equals_the_recomputed_path_cost(topology):
    problem = RoutingProblem(topology, "NOC", "RECLOSER_7")
    result = astar(problem, problem.heuristic())
    assert result.cost == pytest.approx(topology.path_cost(result.path))


def test_path_starts_at_the_source_and_ends_at_the_goal(topology):
    problem = RoutingProblem(topology, "AP_B", "SUB_S1")
    result = astar(problem, problem.heuristic())
    assert result.path[0] == "AP_B"
    assert result.path[-1] == "SUB_S1"


def test_every_consecutive_pair_in_the_path_is_a_real_link(topology):
    problem = RoutingProblem(topology, "RM_B2", "RM_A5")
    result = astar(problem, problem.heuristic())
    for u, v in zip(result.path, result.path[1:]):
        assert v in [n for n, _ in topology.neighbours(u)]


# --- comparative behaviour, as demonstrated in class -----------------------
def test_greedy_is_fast_but_can_be_suboptimal(topology):
    """The exact contrast the presentation makes: speed bought with optimality."""
    problem = RoutingProblem(topology, "NOC", "RECLOSER_7")
    greedy = greedy_best_first(problem, problem.heuristic())
    optimal = astar(problem, problem.heuristic())
    assert greedy.found
    assert greedy.expanded < optimal.expanded
    assert greedy.cost > optimal.cost


def test_breadth_first_minimises_hops_not_cost(topology):
    problem = RoutingProblem(topology, "NOC", "RECLOSER_7")
    bfs = breadth_first(problem)
    optimal = astar(problem, problem.heuristic())
    assert bfs.length <= optimal.length
    assert bfs.cost >= optimal.cost


def test_depth_first_finds_a_path_but_offers_no_guarantee(topology):
    problem = RoutingProblem(topology, "NOC", "RECLOSER_7")
    result = depth_first(problem)
    assert result.found
    assert result.cost >= astar(problem, problem.heuristic()).cost


def test_iterative_deepening_finds_the_shallowest_solution(topology):
    problem = RoutingProblem(topology, "NOC", "RECLOSER_7")
    assert iterative_deepening(problem).length == breadth_first(problem).length


# --- failures and re-routing ----------------------------------------------
def test_disabling_a_link_changes_the_optimal_route(topology):
    problem = RoutingProblem(topology, "NOC", "RECLOSER_7")
    before = astar(problem, problem.heuristic())

    topology.disable_link("LTE_ENB", "RM_A5")
    after_problem = RoutingProblem(topology, "NOC", "RECLOSER_7")
    after = astar(after_problem, after_problem.heuristic())

    assert after.found
    assert after.cost > before.cost
    assert after.path != before.path


def test_avoiding_a_node_excludes_it_from_the_path(topology):
    problem = RoutingProblem(topology, "NOC", "RECLOSER_7", avoid=("RM_A5",))
    result = astar(problem, problem.heuristic())
    assert result.found
    assert "RM_A5" not in result.path


def test_search_reports_failure_when_the_goal_is_isolated(topology):
    for neighbour, _link in list(topology.neighbours("RECLOSER_7")):
        topology.disable_link("RECLOSER_7", neighbour)
    problem = RoutingProblem(topology, "NOC", "RECLOSER_7")
    result = astar(problem, problem.heuristic())
    assert not result.found
    assert result.path == []


def test_shortest_route_helper_returns_none_when_unreachable(topology):
    for neighbour, _link in list(topology.neighbours("RECLOSER_7")):
        topology.disable_link("RECLOSER_7", neighbour)
    assert shortest_route(topology, "NOC", "RECLOSER_7") is None


def test_trivial_problem_where_source_is_the_goal(topology):
    problem = RoutingProblem(topology, "NOC", "NOC")
    result = astar(problem, problem.heuristic())
    assert result.found
    assert result.path == ["NOC"]
    assert result.cost == pytest.approx(0.0)


# --- input validation ------------------------------------------------------
def test_unknown_node_is_rejected(topology):
    with pytest.raises(KeyError):
        RoutingProblem(topology, "NOWHERE", "NOC")


def test_goal_in_the_avoid_set_is_rejected(topology):
    with pytest.raises(ValueError, match="goal node"):
        RoutingProblem(topology, "NOC", "RM_A5", avoid=("RM_A5",))


def test_negative_step_costs_are_refused():
    class Broken:
        def initial_state(self):
            return "a"

        def is_goal(self, state):
            return state == "b"

        def successors(self, state):
            yield ("go", "b", -1.0)

    with pytest.raises(ValueError, match="negative step cost"):
        astar(Broken())
