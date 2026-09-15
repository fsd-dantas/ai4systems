"""
Blocks World as an eco-problem: the classic example.

PT-BR: Cada bloco e um agente cujo objetivo e estar sobre um lugar: uma mesa ou
       outro bloco. Um bloco so esta satisfeito se estiver sobre o seu objetivo E
       se o objetivo, quando for um bloco, tambem estiver satisfeito - essa e a
       relacao de dependencia. Impede a satisfacao quem esta em cima do bloco ou
       em cima do lugar de destino. Uma mesa comporta uma pilha.

       ``COURSE_EXAMPLE`` e o exemplo dos slides: C sobre B sobre A sobre T2; o
       objetivo e B sobre T3, C sobre B e A sobre C.

EN:    Every block is an agent whose goal is to be on a place: a table or another
       block. A block is satisfied only when it is on its goal AND the goal, if a
       block, is satisfied too - that is the dependency relation. Satisfaction is
       prevented by whatever sits on the block or on the destination. A table
       holds one stack.

       ``COURSE_EXAMPLE`` is the slides' example: C on B on A on T2; the goal is
       B on T3, C on B and A on C.
"""

from __future__ import annotations

from itertools import permutations, product
from typing import Dict, FrozenSet, Hashable, List, Mapping, Optional, Sequence, Tuple

from aisg.eco.engine import EcoAgent, EcoWorld, Ecosystem, Move

#: (tables, initial "block -> support", goal "block -> support")
COURSE_EXAMPLE: Tuple[Tuple[str, ...], Dict[str, str], Dict[str, str]] = (
    ("T1", "T2", "T3"),
    {"A": "T2", "B": "A", "C": "B"},
    {"B": "T3", "C": "B", "A": "C"},
)


class BlocksWorld(EcoWorld):
    def __init__(self, tables: Sequence[str], on: Mapping[str, str]) -> None:
        self.tables: Tuple[str, ...] = tuple(tables)
        self.on: Dict[str, str] = dict(on)
        self.blocks: Tuple[str, ...] = tuple(sorted(self.on))
        places = set(self.tables) | set(self.blocks)
        if set(self.tables) & set(self.blocks):
            raise ValueError("a name cannot be both a table and a block")
        for block, support in self.on.items():
            if support not in places or support == block:
                raise ValueError(f"{block} rests on an unknown place {support!r}")
        supports = list(self.on.values())
        if len(supports) != len(set(supports)):
            raise ValueError("two blocks rest on the same place")
        for block in self.blocks:
            self._base(block)  # raises on a cycle

    def _base(self, block: str) -> str:
        seen = set()
        place = block
        while place in self.on:
            if place in seen:
                raise ValueError(f"cycle of supports through {place}")
            seen.add(place)
            place = self.on[place]
        return place

    # -- queries ---------------------------------------------------------------
    def top_of(self, place: str) -> Optional[str]:
        return next((b for b, s in self.on.items() if s == place), None)

    def is_clear(self, place: str) -> bool:
        return self.top_of(place) is None

    def above(self, block: str) -> List[str]:
        chain = []
        top = self.top_of(block)
        while top is not None:
            chain.append(top)
            top = self.top_of(top)
        return chain

    def stacks(self) -> Dict[str, List[str]]:
        result = {}
        for table in self.tables:
            stack = []
            top = self.top_of(table)
            while top is not None:
                stack.append(top)
                top = self.top_of(top)
            result[table] = stack
        return result

    def render(self) -> str:
        return "  ".join(
            f"{table}:[{' '.join(stack) or '-'}]" for table, stack in self.stacks().items()
        )

    # -- EcoWorld ----------------------------------------------------------------
    def snapshot(self) -> Hashable:
        return tuple(sorted(self.on.items()))

    def apply(self, move: Move) -> None:
        block, place = move.agent, move.place
        if block not in self.on:
            raise ValueError(f"{block} is not a block")
        if place not in self.tables and place not in self.on:
            raise ValueError(f"{place} is not a place")
        if place == block:
            raise ValueError(f"{block} cannot rest on itself")
        if not self.is_clear(block):
            raise ValueError(f"{block} is not clear")
        if not self.is_clear(place):
            raise ValueError(f"{place} is not clear")
        self.on[block] = place


class BlockAgent(EcoAgent):
    def __init__(self, name: str, goal: str, tables: Sequence[str]) -> None:
        super().__init__(name)
        self.goal = goal
        self._tables = tuple(tables)

    def dependencies(self, world: EcoWorld) -> Tuple[str, ...]:
        return () if self.goal in self._tables else (self.goal,)

    def is_satisfied(self, world: EcoWorld, ecosystem: Ecosystem) -> bool:
        assert isinstance(world, BlocksWorld)
        if world.on[self.name] != self.goal:
            return False
        return self.goal in self._tables or ecosystem.satisfied(self.goal)

    def satisfaction_move(self, world: EcoWorld) -> Optional[Move]:
        return Move(self.name, self.goal)

    def blockers(self, world: EcoWorld, move: Move) -> List[str]:
        assert isinstance(world, BlocksWorld)
        found = []
        on_me = world.top_of(self.name)
        if on_me is not None:
            found.append(on_me)
        on_destination = world.top_of(move.place)
        if on_destination is not None and on_destination != self.name:
            found.append(on_destination)
        return list(dict.fromkeys(found))

    def flight_moves(self, world: EcoWorld, constraints: FrozenSet[str]) -> List[Move]:
        assert isinstance(world, BlocksWorld)
        excluded = set(constraints) | {self.name, world.on[self.name]} | set(world.above(self.name))
        # Tables first: a block on a table blocks nobody's satisfaction but the
        # table's own goal, which keeps flights from creating new conflicts.
        places = [t for t in world.tables if t not in excluded]
        places += [b for b in world.blocks if b not in excluded]
        return [Move(self.name, place) for place in places]

    def goal_places(self, world: EcoWorld) -> FrozenSet[str]:
        return frozenset({self.goal})

    def position(self, world: EcoWorld) -> Hashable:
        assert isinstance(world, BlocksWorld)
        return world.on[self.name]


def blocks_ecosystem(
    tables: Sequence[str],
    initial: Mapping[str, str],
    goal: Mapping[str, str],
    **kwargs,
) -> Ecosystem:
    """
    PT-BR: Agentes ordenados de baixo para cima no objetivo, como no exemplo da
           aula: quem vai para a mesa age primeiro.
    EN:    Agents ordered bottom-up in the goal, as in the course example: those
           bound for a table act first.
    """
    if set(initial) != set(goal):
        raise ValueError("initial and goal must name the same blocks")
    world = BlocksWorld(tables, initial)
    BlocksWorld(tables, goal)  # the goal must itself be a legal configuration

    def depth(block: str) -> int:
        d = 0
        while goal[block] not in tables:
            block = goal[block]
            d += 1
        return d

    order = sorted(goal, key=lambda b: (depth(b), b))
    return Ecosystem(world, [BlockAgent(b, goal[b], tables) for b in order], **kwargs)


def enumerate_configurations(
    blocks: Sequence[str], tables: Sequence[str]
) -> List[Dict[str, str]]:
    """Every legal arrangement of ``blocks`` in stacks on ``tables``."""
    configurations = []
    seen = set()
    for assignment in product(tables, repeat=len(blocks)):
        per_table: Dict[str, List[str]] = {t: [] for t in tables}
        for block, table in zip(blocks, assignment):
            per_table[table].append(block)
        for orders in product(*(permutations(per_table[t]) for t in tables)):
            on = {}
            for table, order in zip(tables, orders):
                below = table
                for block in order:
                    on[block] = below
                    below = block
            key = tuple(sorted(on.items()))
            if key not in seen:
                seen.add(key)
                configurations.append(on)
    return configurations
