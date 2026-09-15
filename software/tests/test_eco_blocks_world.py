"""
Tests for the eco-resolution engine on Blocks World.

PT-BR: A propriedade central nao e "resolve o exemplo" - e a CONVERGENCIA. O
       motor nao planeja, entao nada garante por construcao que os agentes
       cheguem a satisfacao. Os testes rodam o motor a partir de TODAS as
       configuracoes iniciais contra TODOS os objetivos com 3 blocos e 3 mesas,
       e reexecutam cada sequencia de acoes num verificador que nao compartilha
       codigo com o motor nem com o dominio.
EN:    The central property is not "solves the example" - it is CONVERGENCE. The
       engine does not plan, so nothing guarantees by construction that the
       agents reach satisfaction. The tests run the engine from EVERY initial
       configuration against EVERY goal with 3 blocks and 3 tables, and replay
       each action sequence in a checker that shares no code with the engine or
       the domain.
"""

from __future__ import annotations

import pytest

from aisg.eco import (
    COURSE_EXAMPLE,
    AgentState,
    BlocksWorld,
    Move,
    blocks_ecosystem,
    enumerate_configurations,
)


def replay(tables, initial, moves):
    """
    Independent checker: plain dictionaries, no engine, no BlocksWorld.
    Returns the final configuration, or raises AssertionError on an illegal move.
    """
    on = dict(initial)
    for move in moves:
        block, place = move.agent, move.place
        assert block in on, f"{block} is not a block"
        assert place in tables or place in on, f"{place} is not a place"
        assert place != block
        assert block not in on.values(), f"{move}: {block} is not clear"
        assert place not in on.values(), f"{move}: {place} is not clear"
        on[block] = place
    return on


def test_the_course_example_converges_to_its_goal():
    tables, initial, goal = COURSE_EXAMPLE
    result = blocks_ecosystem(tables, initial, goal).solve()
    assert result.converged, result.reason
    assert replay(tables, initial, result.moves) == goal


def test_the_course_example_uses_satisfaction_aggression_and_flight():
    tables, initial, goal = COURSE_EXAMPLE
    events = {entry.event for entry in blocks_ecosystem(tables, initial, goal).solve().trace}
    assert {"attack", "attacked", "flee", "satisfy"} <= events


def test_an_agent_waits_until_its_dependency_is_satisfied():
    """
    Ordered top-down, C and A act before the block they must rest on is in
    place, so they wait; the resolution still converges.
    """
    from aisg.eco import Ecosystem

    tables, initial, goal = COURSE_EXAMPLE
    bottom_up = blocks_ecosystem(tables, initial, goal)
    top_down = Ecosystem(bottom_up.world, list(reversed(bottom_up.order)))
    result = top_down.solve()
    waits = [e for e in result.trace if e.event == "wait"]
    assert waits and all(e.state is AgentState.WAITING for e in waits)
    assert {e.agent for e in waits} <= {"A", "C"}
    assert result.converged
    assert replay(tables, initial, result.moves) == goal


def test_an_attacked_block_never_flees_onto_its_attacker_or_the_attackers_goal():
    tables, initial, goal = COURSE_EXAMPLE
    result = blocks_ecosystem(tables, initial, goal).solve()
    trace = result.trace
    for i, entry in enumerate(trace):
        if entry.event != "attacked":
            continue
        forbidden = {part for part in entry.detail.replace("must avoid ", "").split("~") if part}
        flight = next((e for e in trace[i + 1:] if e.agent == entry.agent and e.event == "flee"), None)
        if flight is not None:
            destination = flight.detail.split(" -> ")[1]
            assert destination not in forbidden, f"{entry.agent} fled onto {destination}"


CONFIGURATIONS = enumerate_configurations(("A", "B", "C"), ("T1", "T2", "T3"))


def test_the_enumeration_covers_every_arrangement():
    # 3 blocks on 3 labelled tables, one stack per table: 60 arrangements
    assert len(CONFIGURATIONS) == 60
    for on in CONFIGURATIONS:
        BlocksWorld(("T1", "T2", "T3"), on)


def test_every_initial_state_converges_to_every_goal():
    """
    60 x 60 = 3600 problems. Every one must converge, and every action sequence
    must be legal and end exactly in the goal.
    """
    tables = ("T1", "T2", "T3")
    failures = []
    longest = 0
    for initial in CONFIGURATIONS:
        for goal in CONFIGURATIONS:
            result = blocks_ecosystem(tables, initial, goal).solve()
            refused = [e for e in result.trace if e.event == "refused"]
            if refused or not result.converged or replay(tables, initial, result.moves) != goal:
                failures.append((initial, goal, result.reason))
            longest = max(longest, result.steps)
    assert not failures, f"{len(failures)} problems did not converge, e.g. {failures[0]}"
    # Not optimal: the agents do not plan. Pinned so a regression is visible.
    assert longest <= 20, f"a problem needed {longest} moves"


TOWER_OF_FOUR = {"A": "T4", "B": "A", "C": "B", "D": "C"}


def test_every_arrangement_of_four_blocks_builds_the_tower_with_four_tables():
    tables = ("T1", "T2", "T3", "T4")
    for initial in enumerate_configurations(("A", "B", "C", "D"), tables):
        result = blocks_ecosystem(tables, initial, TOWER_OF_FOUR).solve()
        assert result.converged, (initial, result.reason)
        assert replay(tables, initial, result.moves) == TOWER_OF_FOUR


def test_with_scarce_tables_convergence_is_not_guaranteed_but_always_reported():
    """
    Four blocks on three tables leave little free space, and the agents can
    keep displacing each other. The engine must then stop with an explicit
    reason, never with an illegal move, and every run it calls converged must
    really reach the goal.
    """
    tables = ("T1", "T2", "T3")
    goal = {"A": "T3", "B": "A", "C": "B", "D": "C"}
    outcomes = {"converged": 0, "stopped": 0}
    for initial in enumerate_configurations(("A", "B", "C", "D"), tables):
        result = blocks_ecosystem(tables, initial, goal).solve()
        final = replay(tables, initial, result.moves)
        if result.converged:
            assert final == goal
            outcomes["converged"] += 1
        else:
            assert result.reason in (
                "world state repeated: cycle",
                "no progress in a whole round",
                "move limit reached",
            )
            assert result.unsatisfied
            outcomes["stopped"] += 1
    assert outcomes["converged"] + outcomes["stopped"] == 360
    assert outcomes["converged"] >= 300


def test_a_satisfied_ecosystem_does_nothing():
    tables, _initial, goal = COURSE_EXAMPLE
    result = blocks_ecosystem(tables, goal, goal).solve()
    assert result.converged and result.moves == [] and result.rounds == 0


def test_illegal_moves_are_refused_by_the_world():
    tables, initial, _goal = COURSE_EXAMPLE
    world = BlocksWorld(tables, initial)
    with pytest.raises(ValueError):
        world.apply(Move("A", "T1"))  # A is under B
    with pytest.raises(ValueError):
        world.apply(Move("C", "A"))  # A is not clear


def test_the_move_limit_stops_the_resolution_honestly():
    tables, initial, goal = COURSE_EXAMPLE
    result = blocks_ecosystem(tables, initial, goal, max_moves=1).solve()
    assert not result.converged
    assert result.reason == "move limit reached"
    assert result.unsatisfied


def test_states_follow_the_course_state_machine():
    tables, initial, goal = COURSE_EXAMPLE
    states = {
        entry.event: entry.state
        for entry in blocks_ecosystem(tables, initial, goal).solve().trace
    }
    assert states["attacked"] is AgentState.SEEKING_FLIGHT
    assert states["flee"] is AgentState.FLED
    assert states["satisfy"] is AgentState.SATISFIED
    assert states["attack"] in (AgentState.SEEKING_SATISFACTION, AgentState.SEEKING_FLIGHT)
