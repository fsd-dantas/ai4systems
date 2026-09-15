"""
Eco-resolution engine: satisfaction, aggression, flight and dependency.

PT-BR: O comportamento padrao de cada agente, como na disciplina:

       * objetivo satisfeito            -> nao fazer nada;
       * objetivo nao satisfeito        -> tentar satisfaze-lo;
       * alguem impede a satisfacao     -> agredi-lo;
       * agredido                       -> fugir para um lugar diferente do
                                           objetivo do agressor;
       * alguem impede a fuga           -> agredir o bloqueador.

       A agressao carrega RESTRICOES (como ``~B~T3`` no exemplo dos slides): o
       agredido nao pode fugir para o agressor nem para o objetivo dele, e quem
       foge repassa as proprias restricoes a quem bloqueia sua fuga. A relacao de
       DEPENDENCIA (Sohier, Denis e Lesage, projeto CASPER) define a ordem: um
       agente espera ate que aqueles de quem depende estejam satisfeitos.

       Estados, com os nomes da maquina de estados da aula entre parenteses:
       WAITING (espera por dependencia), SEEKING_SATISFACTION
       (BuscandoSatisfacao), SATISFIED (Satisfacao), SEEKING_FLIGHT
       (BuscandoFuga), FLED (Fuga).

       O motor NAO planeja: nao olha adiante nem compara alternativas. Ele so
       executa o comportamento local de cada agente e registra o que acontece.
       Por isso a convergencia nao e garantida por construcao e precisa ser
       verificada: o resultado declara se convergiu e, se nao, por que parou.

EN:    Each agent's default behaviour, as in the course:

       * goal satisfied                 -> do nothing;
       * goal not satisfied             -> try to satisfy it;
       * someone prevents satisfaction  -> attack them;
       * attacked                       -> flee somewhere other than the
                                           attacker's goal;
       * someone prevents the flight    -> attack the blocker.

       Aggression carries CONSTRAINTS (like ``~B~T3`` in the slides' example):
       the attacked agent may not flee onto the attacker or the attacker's goal,
       and an agent fleeing passes its own constraints to whoever blocks its
       flight. The DEPENDENCY relation (Sohier, Denis and Lesage, CASPER project)
       sets the order: an agent waits until those it depends on are satisfied.

       States, with the course state machine's names in brackets: WAITING
       (waiting for dependencies), SEEKING_SATISFACTION (BuscandoSatisfacao),
       SATISFIED (Satisfacao), SEEKING_FLIGHT (BuscandoFuga), FLED (Fuga).

       The engine does NOT plan: it neither looks ahead nor compares
       alternatives. It only runs each agent's local behaviour and records what
       happens. Convergence is therefore not guaranteed by construction and must
       be checked: the result states whether it converged and, if not, why it
       stopped.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, FrozenSet, Hashable, List, Optional, Sequence, Tuple


class AgentState(Enum):
    WAITING = "waiting"
    SEEKING_SATISFACTION = "seeking-satisfaction"
    SATISFIED = "satisfied"
    SEEKING_FLIGHT = "seeking-flight"
    FLED = "fled"


#: The course state machine's names, for rendering.
STATE_NAMES_PT: Dict[AgentState, str] = {
    AgentState.WAITING: "Esperando",
    AgentState.SEEKING_SATISFACTION: "BuscandoSatisfacao",
    AgentState.SATISFIED: "Satisfacao",
    AgentState.SEEKING_FLIGHT: "BuscandoFuga",
    AgentState.FLED: "Fuga",
}


@dataclass(frozen=True)
class Move:
    agent: str
    place: str

    def __str__(self) -> str:
        return f"{self.agent} -> {self.place}"


@dataclass(frozen=True)
class TraceEntry:
    """One event of a resolution: who did what, in which state, and why."""

    index: int
    agent: str
    #: wait | attack | attacked | flee | satisfy | blocked | give-up
    event: str
    state: AgentState
    detail: str

    def render(self, lang: str = "pt") -> str:
        state = STATE_NAMES_PT[self.state] if lang == "pt" else self.state.value
        return f"{self.index:>4}  {self.agent:<10} {self.event:<9} [{state}] {self.detail}"


class EcoWorld:
    """The environment the agents share. Domains subclass it."""

    def snapshot(self) -> Hashable:
        raise NotImplementedError

    def apply(self, move: Move) -> None:
        """Carry out a move; raise ``ValueError`` when it is illegal."""
        raise NotImplementedError


class EcoAgent:
    """
    An eco-agent. Domains implement the five hooks; the engine supplies the
    behaviour.
    """

    def __init__(self, name: str) -> None:
        self.name = name

    def dependencies(self, world: EcoWorld) -> Tuple[str, ...]:
        """Agents that must be satisfied before this one acts."""
        return ()

    def is_satisfied(self, world: EcoWorld, ecosystem: "Ecosystem") -> bool:
        raise NotImplementedError

    def satisfaction_move(self, world: EcoWorld) -> Optional[Move]:
        """The move that satisfies the goal, or ``None`` when there is none."""
        raise NotImplementedError

    def blockers(self, world: EcoWorld, move: Move) -> List[str]:
        """Agents that prevent ``move`` right now, nearest first."""
        raise NotImplementedError

    def flight_moves(self, world: EcoWorld, constraints: FrozenSet[str]) -> List[Move]:
        """Places this agent may flee to, respecting ``constraints``, preferred first."""
        raise NotImplementedError

    def goal_places(self, world: EcoWorld) -> FrozenSet[str]:
        """What an attacked agent must avoid on this agent's behalf."""
        raise NotImplementedError

    def position(self, world: EcoWorld) -> Hashable:
        """Where the agent is now; lets the engine notice a flight made deeper in a chain."""
        raise NotImplementedError


@dataclass
class Resolution:
    converged: bool
    reason: str
    moves: List[Move] = field(default_factory=list)
    trace: List[TraceEntry] = field(default_factory=list)
    unsatisfied: List[str] = field(default_factory=list)
    rounds: int = 0

    @property
    def steps(self) -> int:
        return len(self.moves)


class Ecosystem:
    """
    A population of eco-agents in one world.

    PT-BR: ``solve`` percorre os agentes na ordem declarada, rodada apos rodada.
           Cada agente com dependencias satisfeitas tenta se satisfazer; as
           agressoes e fugas acontecem dentro dessa tentativa. Para quando todos
           estao satisfeitos, quando uma rodada inteira nao muda o mundo, quando
           um estado do mundo se repete ao fim de uma rodada, ou no limite de
           movimentos.
    EN:    ``solve`` goes through the agents in declared order, round after round.
           Each agent whose dependencies are satisfied tries to satisfy itself;
           attacks and flights happen inside that attempt. It stops when every
           agent is satisfied, when a whole round leaves the world unchanged,
           when a world state repeats at the end of a round, or at the move
           limit.
    """

    def __init__(
        self,
        world: EcoWorld,
        agents: Sequence[EcoAgent],
        *,
        max_moves: int = 500,
        max_depth: int = 40,
    ) -> None:
        names = [a.name for a in agents]
        if len(set(names)) != len(names):
            raise ValueError(f"agent names must be unique: {names}")
        self.world = world
        self.order: List[EcoAgent] = list(agents)
        self.agents: Dict[str, EcoAgent] = {a.name: a for a in agents}
        self.max_moves = max_moves
        self.max_depth = max_depth
        self._moves: List[Move] = []
        self._trace: List[TraceEntry] = []

    # -- queries -------------------------------------------------------------
    def satisfied(self, name: str) -> bool:
        return self.agents[name].is_satisfied(self.world, self)

    def unsatisfied(self) -> List[str]:
        return [a.name for a in self.order if not self.satisfied(a.name)]

    # -- resolution ----------------------------------------------------------
    def solve(self) -> Resolution:
        seen = {self.world.snapshot()}
        rounds = 0
        while True:
            if not self.unsatisfied():
                return self._result(True, "all agents satisfied", rounds)
            if len(self._moves) >= self.max_moves:
                return self._result(False, "move limit reached", rounds)
            before = self.world.snapshot()
            rounds += 1
            for agent in self.order:
                if self.satisfied(agent.name):
                    continue
                waiting = [d for d in agent.dependencies(self.world) if not self.satisfied(d)]
                if waiting:
                    self._log(agent.name, "wait", AgentState.WAITING,
                              f"depends on {', '.join(waiting)}")
                    continue
                self._satisfy(agent, depth=0, chain=frozenset())
                if len(self._moves) >= self.max_moves:
                    break
            after = self.world.snapshot()
            if after == before:
                return self._result(False, "no progress in a whole round", rounds)
            if after in seen:
                return self._result(False, "world state repeated: cycle", rounds)
            seen.add(after)

    def _result(self, converged: bool, reason: str, rounds: int) -> Resolution:
        return Resolution(
            converged=converged,
            reason=reason,
            moves=list(self._moves),
            trace=list(self._trace),
            unsatisfied=self.unsatisfied(),
            rounds=rounds,
        )

    def _log(self, agent: str, event: str, state: AgentState, detail: str) -> None:
        self._trace.append(TraceEntry(len(self._trace) + 1, agent, event, state, detail))

    def _apply(self, agent: EcoAgent, move: Move, event: str, state: AgentState) -> bool:
        """
        Carry out a move. A world that refuses it (a resource taken by an agent
        this one may not displace, for instance) leaves the agent blocked.
        """
        try:
            self.world.apply(move)
        except ValueError as exc:
            self._log(agent.name, "refused", state, f"{move}: {exc}")
            return False
        self._moves.append(move)
        self._log(agent.name, event, state, str(move))
        return True

    def _satisfy(self, agent: EcoAgent, depth: int, chain: FrozenSet[Tuple[str, FrozenSet[str]]]) -> bool:
        if self.satisfied(agent.name):
            return True
        move = agent.satisfaction_move(self.world)
        if move is None:
            self._log(agent.name, "give-up", AgentState.SEEKING_SATISFACTION,
                      "no move can satisfy the goal")
            return False
        for blocker in agent.blockers(self.world, move):
            if blocker not in agent.blockers(self.world, move):
                continue  # already cleared by an earlier flight in this loop
            constraints = agent.goal_places(self.world) | {agent.name}
            self._log(agent.name, "attack", AgentState.SEEKING_SATISFACTION,
                      f"{blocker} blocks {move}; {blocker} must avoid {_fmt(constraints)}")
            if not self._flee(self.agents[blocker], constraints, depth + 1, chain):
                self._log(agent.name, "blocked", AgentState.SEEKING_SATISFACTION,
                          f"{blocker} could not flee")
                return False
        if self.satisfied(agent.name):
            return True  # the chain of flights already put it in place
        if agent.blockers(self.world, move):
            self._log(agent.name, "blocked", AgentState.SEEKING_SATISFACTION,
                      f"{move} is still blocked")
            return False
        return self._apply(agent, move, "satisfy", AgentState.SATISFIED)

    def _flee(
        self,
        agent: EcoAgent,
        constraints: FrozenSet[str],
        depth: int,
        chain: FrozenSet[Tuple[str, FrozenSet[str]]],
    ) -> bool:
        self._log(agent.name, "attacked", AgentState.SEEKING_FLIGHT,
                  f"must avoid {_fmt(constraints)}")
        # An attacker may itself be attacked further down the chain - the block
        # sitting on its victim must move. Only the SAME agent attacked with the
        # SAME constraints again is a loop.
        key = (agent.name, constraints)
        if depth > self.max_depth or key in chain:
            self._log(agent.name, "give-up", AgentState.SEEKING_FLIGHT,
                      "aggression chain repeats itself or is too deep")
            return False
        chain = chain | {key}
        if len(self._moves) >= self.max_moves:
            return False
        start = agent.position(self.world)

        def fled_meanwhile() -> bool:
            # Attacked again deeper in the chain, the agent may already have
            # moved; if its new place respects these constraints, it has fled.
            now = agent.position(self.world)
            return now != start and now not in constraints
        candidates = agent.flight_moves(self.world, constraints)
        if not candidates:
            self._log(agent.name, "give-up", AgentState.SEEKING_FLIGHT,
                      "no place respects the constraints")
            return False
        for move in candidates:
            if not agent.blockers(self.world, move) and self._apply(
                agent, move, "flee", AgentState.FLED
            ):
                return True
        # Every flight is blocked: attack whoever blocks the preferred one.
        for move in candidates:
            cleared = True
            for blocker in agent.blockers(self.world, move):
                # As in the course rule, the blocker avoids only its direct
                # attacker and that attacker's goal - here, the flight's
                # destination. Inheriting the whole chain's constraints left the
                # last agent nowhere to go; loops are caught by the chain guard.
                inherited = frozenset({agent.name, move.place})
                self._log(agent.name, "attack", AgentState.SEEKING_FLIGHT,
                          f"{blocker} blocks the flight {move}; "
                          f"{blocker} must avoid {_fmt(inherited)}")
                if not self._flee(self.agents[blocker], inherited, depth + 1, chain):
                    cleared = False
                    break
                if fled_meanwhile():
                    return True
            if fled_meanwhile():
                return True
            if cleared and not agent.blockers(self.world, move) and self._apply(
                agent, move, "flee", AgentState.FLED
            ):
                return True
        self._log(agent.name, "give-up", AgentState.SEEKING_FLIGHT, "every flight stays blocked")
        return False


def _fmt(places: FrozenSet[str]) -> str:
    return "".join(f"~{p}" for p in sorted(places))
