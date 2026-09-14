"""
The control component: who contributes next.

PT-BR: Corresponde ao ``Controlador`` do exemplo da disciplina, com um laco e um
       limite. A diferenca: a cada ciclo o controlador monta a AGENDA (todos os
       especialistas ativados), escolhe UM pela prioridade declarada e registra
       quem ficou de fora. Um especialista por ciclo torna a ordem de raciocinio
       visivel, como o motor de regras faz com o conjunto de conflito. O laco para
       por QUIESCENCIA - nenhum especialista tem nada novo a ler - ou pelo limite,
       e o resultado diz qual dos dois aconteceu.

EN:    Corresponds to the course example's ``Controlador``, with a loop and a limit.
       The difference: each cycle the controller builds the AGENDA (every activated
       expert), picks ONE by declared priority, and records who was left out. One
       expert per cycle makes the reasoning order visible, as the rule engine does
       with its conflict set. The loop stops at QUIESCENCE - no expert has anything
       new to read - or at the limit, and the result says which one happened.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Sequence, Tuple

from aisg.blackboard.board import Blackboard
from aisg.blackboard.sources import KnowledgeSource


@dataclass
class CycleRecord:
    cycle: int
    source: str
    #: every activated expert, in the order the controller ranked them
    agenda: Tuple[str, ...]
    added: int
    removed: int


@dataclass
class Run:
    board: Blackboard
    records: List[CycleRecord] = field(default_factory=list)
    #: True when the loop ended because no expert was activated
    quiescent: bool = False

    @property
    def cycles(self) -> int:
        return len(self.records)


class Controller:
    def __init__(
        self,
        board: Blackboard,
        sources: Sequence[KnowledgeSource],
        *,
        limit: int = 100,
    ) -> None:
        names = [s.name for s in sources]
        if len(set(names)) != len(names):
            raise ValueError(f"expert names must be unique: {names}")
        self.board = board
        self.sources = list(sources)
        self.limit = limit

    def agenda(self) -> List[KnowledgeSource]:
        activated = [s for s in self.sources if s.is_activated(self.board)]
        return sorted(activated, key=lambda s: (s.priority, s.name))

    def step(self) -> Optional[CycleRecord]:
        agenda = self.agenda()
        if not agenda:
            return None
        chosen = agenda[0]
        self.board.cycle += 1
        added, removed = chosen.contribute(self.board)
        return CycleRecord(
            cycle=self.board.cycle,
            source=chosen.name,
            agenda=tuple(s.name for s in agenda),
            added=added,
            removed=removed,
        )

    def loop(self) -> Run:
        run = Run(board=self.board)
        while run.cycles < self.limit:
            record = self.step()
            if record is None:
                run.quiescent = True
                break
            run.records.append(record)
        return run
