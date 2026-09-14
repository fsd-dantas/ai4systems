"""
The blackboard: the shared space the experts read from and write to.

PT-BR: O quadro-negro e o UNICO meio de comunicacao entre os especialistas. Nenhum
       especialista chama outro: cada um le alguns niveis do quadro, contribui com
       entradas em outro nivel e assina o que escreveu. Corresponde ao
       ``QuadroNegro`` do exemplo da disciplina, com duas diferencas deliberadas:
       as entradas ficam organizadas em NIVEIS de abstracao, como no Hearsay-II, e
       cada entrada carrega certeza, autoria e suporte. E isso que permite
       reconstruir, depois, quem concluiu o que e a partir de que.

EN:    The blackboard is the ONLY channel between experts. No expert calls another:
       each one reads some levels of the board, contributes entries to another
       level, and signs what it wrote. It corresponds to the course example's
       ``QuadroNegro``, with two deliberate differences: entries are organised in
       LEVELS of abstraction, as in Hearsay-II, and every entry carries certainty,
       authorship and support. That is what lets us reconstruct, afterwards, who
       concluded what from what.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

from aisg.expert_system.engine import combine_cf


class Level(IntEnum):
    """
    Levels of abstraction, from raw evidence to the restoration plan.

    PT-BR: Cada especialista le niveis mais baixos e escreve num nivel igual ou
           mais alto. A solucao sobe pelo quadro.
    EN:    Each expert reads lower levels and writes to the same or a higher one.
           The solution climbs the board.
    """

    OBSERVATION = 0
    SYMPTOM = 1
    HYPOTHESIS = 2
    INCIDENT = 3
    ACCESS = 4
    PLAN = 5


LEVEL_LABELS: Dict[Level, Tuple[str, str]] = {
    Level.OBSERVATION: ("observacoes", "observations"),
    Level.SYMPTOM: ("sintomas", "symptoms"),
    Level.HYPOTHESIS: ("hipoteses", "hypotheses"),
    Level.INCIDENT: ("incidentes", "incidents"),
    Level.ACCESS: ("acesso multi-RAT", "multi-RAT access"),
    Level.PLAN: ("planos", "plans"),
}


def level_label(level: Level, lang: str = "pt") -> str:
    pt, en = LEVEL_LABELS[level]
    return pt if lang == "pt" else en


#: Author name used for evidence placed on the board from outside the experts.
TASK_GENERATOR = "task-generator"


@dataclass
class Entry:
    """
    One signed contribution on the board.

    ``support`` names what the entry rests on: rule ids for a rule expert, other
    subjects for the correlator, blocking nodes for the router. ``id`` and
    ``cycle`` record when it was posted and take no part in equality, so an expert
    that re-derives exactly what it already said changes nothing.
    """

    level: Level
    subject: str
    key: str
    value: Any
    cf: float
    author: str
    support: Tuple[str, ...] = ()
    data: Dict[str, Any] = field(default_factory=dict)
    rationale_pt: str = ""
    rationale_en: str = ""
    id: int = field(default=0, compare=False)
    cycle: int = field(default=0, compare=False)

    def rationale(self, lang: str = "pt") -> str:
        return self.rationale_pt if lang == "pt" else self.rationale_en

    def render(self) -> str:
        return (
            f"L{int(self.level)} {self.subject:<9} {self.key}={self.value} "
            f"(CF {self.cf:+.2f}, {self.author})"
        )


class Blackboard:
    """
    Shared state of one problem-solving session.

    PT-BR: Guarda um contador de versao por nivel. O controlador usa esses
           contadores para saber quais especialistas tem algo novo para ler.
    EN:    Keeps one version counter per level. The controller uses those counters
           to tell which experts have something new to read.
    """

    def __init__(self) -> None:
        self._entries: List[Entry] = []
        self._next_id = 1
        self._versions: Dict[Level, int] = {level: 0 for level in Level}
        #: the controller cycle currently running, stamped on new entries
        self.cycle = 0
        #: (cycle, "add" | "remove", entry) in the order it happened
        self.history: List[Tuple[int, str, Entry]] = []

    # -- writing -----------------------------------------------------------
    def publish(
        self,
        author: str,
        entries: Iterable[Entry],
        *,
        levels: Sequence[Level],
        subjects: Optional[Iterable[str]] = None,
    ) -> Tuple[int, int]:
        """
        Replace what ``author`` has on ``levels`` with ``entries``.

        PT-BR: Um especialista sempre republica TUDO o que conclui sobre o seu
               escopo. Entradas identicas permanecem; as novas entram; as que ele
               nao sustenta mais saem. Assim uma conclusao tirada de evidencia
               parcial nunca fica congelada no quadro.
        EN:    An expert always republishes EVERYTHING it concludes about its scope.
               Identical entries stay, new ones go in, and the ones it no longer
               supports come out. A conclusion drawn from partial evidence therefore
               never stays frozen on the board.

        Returns ``(added, removed)``. Versions only move when something changed,
        which is what lets the controller reach quiescence.
        """
        scope_levels = set(levels)
        scope_subjects = set(subjects) if subjects is not None else None
        new = list(entries)
        for entry in new:
            if entry.author != author:
                raise ValueError(f"{author} cannot publish an entry signed by {entry.author}")
            if entry.level not in scope_levels:
                raise ValueError(f"{author} did not declare level {entry.level.name}")
            if scope_subjects is not None and entry.subject not in scope_subjects:
                raise ValueError(f"{author}: subject {entry.subject} is outside the scope")

        old = [
            e for e in self._entries
            if e.author == author
            and e.level in scope_levels
            and (scope_subjects is None or e.subject in scope_subjects)
        ]
        unmatched = list(old)
        added: List[Entry] = []
        for entry in new:
            match = next((o for o in unmatched if o == entry), None)
            if match is None:
                added.append(entry)
            else:
                unmatched.remove(match)

        if unmatched:
            gone = {id(e) for e in unmatched}
            self._entries = [e for e in self._entries if id(e) not in gone]
            for entry in unmatched:
                self._versions[entry.level] += 1
                self.history.append((self.cycle, "remove", entry))
        for entry in added:
            entry.id = self._next_id
            entry.cycle = self.cycle
            self._next_id += 1
            self._entries.append(entry)
            self._versions[entry.level] += 1
            self.history.append((self.cycle, "add", entry))
        return len(added), len(unmatched)

    # -- reading -----------------------------------------------------------
    def version(self, level: Level) -> int:
        return self._versions[level]

    def entries(
        self,
        level: Optional[Level] = None,
        *,
        subject: Optional[str] = None,
        key: Optional[str] = None,
        author: Optional[str] = None,
    ) -> List[Entry]:
        return [
            e for e in self._entries
            if (level is None or e.level == level)
            and (subject is None or e.subject == subject)
            and (key is None or e.key == key)
            and (author is None or e.author == author)
        ]

    def subjects(self, level: Level) -> List[str]:
        return sorted({e.subject for e in self._entries if e.level == level})

    def belief(self, level: Level, subject: str, key: str) -> Dict[Any, float]:
        """
        Combined certainty per value, across every author that posted it.

        PT-BR: Contribuicoes de autores diferentes para o mesmo valor combinam-se
               pela funcao do MYCIN, em ordem deterministica de autor.
        EN:    Contributions from different authors to the same value combine with
               MYCIN's function, in a deterministic author order.
        """
        per_value: Dict[Any, List[Tuple[str, float]]] = {}
        for entry in self.entries(level, subject=subject, key=key):
            per_value.setdefault(entry.value, []).append((entry.author, entry.cf))
        combined: Dict[Any, float] = {}
        for value, contributions in per_value.items():
            cf = 0.0
            for _author, contribution in sorted(contributions):
                cf = combine_cf(cf, contribution)
            combined[value] = cf
        return combined

    def ranked(
        self, level: Level, subject: str, key: str, *, min_cf: float = 0.0
    ) -> List[Tuple[Any, float]]:
        believed = self.belief(level, subject, key)
        pairs = [(value, cf) for value, cf in believed.items() if cf > min_cf]
        return sorted(pairs, key=lambda pair: (-pair[1], str(pair[0])))

    def best(self, level: Level, subject: str, key: str) -> Optional[Tuple[Any, float]]:
        ranked = self.ranked(level, subject, key, min_cf=-1.0)
        return ranked[0] if ranked else None

    def __len__(self) -> int:
        return len(self._entries)
