"""
STRIPS representation: predicates, operators, states, and problems.

PT-BR: STRIPS (Fikes & Nilsson, 1971) representa uma acao por tres conjuntos:
       precondicoes (o que precisa ser verdade), lista de adicao (o que passa a ser
       verdade) e lista de remocao (o que deixa de ser verdade). O estado do mundo e
       o conjunto de literais positivos verdadeiros; tudo o que nao esta no conjunto
       e considerado falso (hipotese do mundo fechado).

EN:    STRIPS (Fikes & Nilsson, 1971) represents an action by three sets:
       preconditions (what must hold), an add list (what becomes true), and a delete
       list (what stops being true). A world state is the set of true positive
       literals; anything absent is taken to be false (closed-world assumption).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import (
    Callable,
    Dict,
    FrozenSet,
    Iterable,
    Iterator,
    List,
    Optional,
    Sequence,
    Tuple,
)

_ATOM_RE = re.compile(r"^\s*([A-Za-z_][\w-]*)\s*\(([^()]*)\)\s*$")


@dataclass(frozen=True, order=True)
class Predicate:
    """
    A ground or lifted atom, e.g. ``link-down(RM_A5)`` or ``at(?tech, ?site)``.

    Arguments beginning with ``?`` are variables; everything else is a constant.
    """

    name: str
    args: Tuple[str, ...] = ()

    @classmethod
    def parse(cls, text: str) -> "Predicate":
        """Parse ``name(arg1, arg2)`` or a bare ``name``."""
        text = text.strip()
        match = _ATOM_RE.match(text)
        if match:
            name, raw_args = match.group(1), match.group(2).strip()
            args = tuple(a.strip() for a in raw_args.split(",") if a.strip())
            return cls(name, args)
        if re.fullmatch(r"[A-Za-z_][\w-]*", text):
            return cls(text, ())
        raise ValueError(f"malformed predicate: {text!r}")

    @property
    def variables(self) -> Tuple[str, ...]:
        return tuple(a for a in self.args if a.startswith("?"))

    @property
    def is_ground(self) -> bool:
        return not self.variables

    def substitute(self, binding: Dict[str, str]) -> "Predicate":
        return Predicate(self.name, tuple(binding.get(a, a) for a in self.args))

    def __str__(self) -> str:
        return f"{self.name}({', '.join(self.args)})" if self.args else self.name


State = FrozenSet[Predicate]


def make_state(atoms: Iterable[object]) -> State:
    """Build a state from predicates or from strings like ``'link-down(RM_A5)'``."""
    parsed = []
    for atom in atoms:
        if isinstance(atom, Predicate):
            parsed.append(atom)
        elif isinstance(atom, str):
            parsed.append(Predicate.parse(atom))
        else:
            raise TypeError(f"cannot read {atom!r} as a predicate")
    for predicate in parsed:
        if not predicate.is_ground:
            raise ValueError(f"a state may only contain ground atoms, got {predicate}")
    return frozenset(parsed)


def format_state(state: State, *, indent: str = "  ") -> str:
    return "\n".join(f"{indent}{p}" for p in sorted(state, key=str)) or f"{indent}(vazio / empty)"


@dataclass(frozen=True)
class Operator:
    """
    A STRIPS action schema.

    PT-BR: ``cost`` permite planejar por custo (horas de equipe, risco, janela de
           manutencao) e nao apenas por numero de acoes.
    EN:    ``cost`` allows planning by cost (crew hours, risk, maintenance window)
           rather than merely by number of actions.
    """

    name: str
    parameters: Tuple[str, ...] = ()
    preconditions: FrozenSet[Predicate] = frozenset()
    add_list: FrozenSet[Predicate] = frozenset()
    delete_list: FrozenSet[Predicate] = frozenset()
    cost: float = 1.0
    description_pt: str = ""
    description_en: str = ""

    @classmethod
    def build(
        cls,
        name: str,
        *,
        parameters: Sequence[str] = (),
        preconditions: Sequence[str] = (),
        add: Sequence[str] = (),
        delete: Sequence[str] = (),
        cost: float = 1.0,
        description_pt: str = "",
        description_en: str = "",
    ) -> "Operator":
        """Ergonomic constructor taking predicate strings."""
        op = cls(
            name=name,
            parameters=tuple(parameters),
            preconditions=frozenset(Predicate.parse(p) for p in preconditions),
            add_list=frozenset(Predicate.parse(p) for p in add),
            delete_list=frozenset(Predicate.parse(p) for p in delete),
            cost=cost,
            description_pt=description_pt,
            description_en=description_en,
        )
        op.validate()
        return op

    def validate(self) -> None:
        declared = set(self.parameters)
        used = {
            var
            for group in (self.preconditions, self.add_list, self.delete_list)
            for predicate in group
            for var in predicate.variables
        }
        undeclared = used - declared
        if undeclared:
            raise ValueError(
                f"operator {self.name}: variables used but not declared as "
                f"parameters: {', '.join(sorted(undeclared))}"
            )
        overlap = self.add_list & self.delete_list
        if overlap:
            raise ValueError(
                f"operator {self.name}: {', '.join(str(p) for p in overlap)} "
                "appears in both the add and the delete list"
            )

    def describe(self, lang: str = "pt") -> str:
        text = self.description_pt if lang == "pt" else self.description_en
        return text or self.name

    def ground(self, binding: Dict[str, str]) -> "Action":
        missing = [p for p in self.parameters if p not in binding]
        if missing:
            raise ValueError(
                f"operator {self.name}: unbound parameter(s) {', '.join(missing)}"
            )
        return Action(
            operator=self,
            binding=dict(binding),
            preconditions=frozenset(p.substitute(binding) for p in self.preconditions),
            add_list=frozenset(p.substitute(binding) for p in self.add_list),
            delete_list=frozenset(p.substitute(binding) for p in self.delete_list),
        )


@dataclass(frozen=True)
class Action:
    """A fully ground operator, ready to apply to a state."""

    operator: Operator
    binding: Dict[str, str] = field(hash=False, compare=False, default_factory=dict)
    preconditions: FrozenSet[Predicate] = frozenset()
    add_list: FrozenSet[Predicate] = frozenset()
    delete_list: FrozenSet[Predicate] = frozenset()

    @property
    def name(self) -> str:
        args = ", ".join(self.binding[p] for p in self.operator.parameters)
        return f"{self.operator.name}({args})" if args else self.operator.name

    @property
    def cost(self) -> float:
        return self.operator.cost

    def applicable(self, state: State) -> bool:
        return self.preconditions <= state

    def unmet_preconditions(self, state: State) -> FrozenSet[Predicate]:
        return frozenset(self.preconditions - state)

    def apply(self, state: State) -> State:
        if not self.applicable(state):
            missing = ", ".join(str(p) for p in sorted(self.unmet_preconditions(state), key=str))
            raise ValueError(f"{self.name} is not applicable; missing: {missing}")
        return frozenset((state - self.delete_list) | self.add_list)

    def describe(self, lang: str = "pt") -> str:
        template = self.operator.describe(lang)
        for param, value in self.binding.items():
            template = template.replace(param, value)
        return template

    def __str__(self) -> str:
        return self.name

    def __hash__(self) -> int:
        return hash((self.operator.name, tuple(sorted(self.binding.items()))))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Action):
            return NotImplemented
        return self.operator.name == other.operator.name and self.binding == other.binding


@dataclass
class Problem:
    """A STRIPS planning problem: operators, objects, initial state, and goal."""

    name: str
    operators: List[Operator]
    initial: State
    goal: State
    #: type name -> objects of that type, used to ground the operators
    objects: Dict[str, List[str]] = field(default_factory=dict)
    #: operator parameter -> type name
    parameter_types: Dict[str, str] = field(default_factory=dict)
    #: optional guard rejecting degenerate bindings, e.g. travelling from a place
    #: to itself: ``(operator_name, binding) -> keep?``
    binding_filter: Optional[Callable[[str, Dict[str, str]], bool]] = None

    def __post_init__(self) -> None:
        for predicate in self.goal:
            if not predicate.is_ground:
                raise ValueError(f"goal must be ground, got {predicate}")

    def candidate_values(self, parameter: str) -> List[str]:
        type_name = self.parameter_types.get(parameter)
        if type_name is None:
            return sorted({obj for values in self.objects.values() for obj in values})
        return list(self.objects.get(type_name, []))

    def ground_actions(self) -> List[Action]:
        """Instantiate every operator over the declared objects."""
        actions: List[Action] = []
        for operator in self.operators:
            for binding in self._bindings(operator):
                if self.binding_filter and not self.binding_filter(operator.name, binding):
                    continue
                actions.append(operator.ground(binding))
        # A stable order keeps search runs reproducible.
        actions.sort(key=lambda a: a.name)
        return actions

    def _bindings(self, operator: Operator) -> Iterator[Dict[str, str]]:
        params = list(operator.parameters)
        if not params:
            yield {}
            return

        def walk(index: int, partial: Dict[str, str]) -> Iterator[Dict[str, str]]:
            if index == len(params):
                yield dict(partial)
                return
            param = params[index]
            for value in self.candidate_values(param):
                partial[param] = value
                yield from walk(index + 1, partial)
            partial.pop(param, None)

        yield from walk(0, {})

    def is_goal(self, state: State) -> bool:
        return self.goal <= state

    def unmet_goals(self, state: State) -> FrozenSet[Predicate]:
        return frozenset(self.goal - state)


@dataclass
class Plan:
    """An ordered sequence of ground actions, with validation support."""

    problem: Problem
    actions: List[Action] = field(default_factory=list)
    #: the state after each action, parallel to ``actions``
    trajectory: List[State] = field(default_factory=list)
    strategy: str = ""
    #: search instrumentation, when the planner reports it
    stats: Dict[str, float] = field(default_factory=dict)

    @property
    def cost(self) -> float:
        return sum(a.cost for a in self.actions)

    @property
    def length(self) -> int:
        return len(self.actions)

    def validate(self) -> Tuple[bool, Optional[str]]:
        """
        Re-execute the plan from the initial state.

        PT-BR: Um plano so vale se for executavel passo a passo E atingir o objetivo.
        EN:    A plan is only valid if it is executable step by step AND reaches the goal.
        """
        state = self.problem.initial
        for step, action in enumerate(self.actions, start=1):
            if not action.applicable(state):
                missing = ", ".join(
                    str(p) for p in sorted(action.unmet_preconditions(state), key=str)
                )
                return False, (
                    f"step {step} ({action.name}) is not applicable; missing: {missing}"
                )
            state = action.apply(state)
        if not self.problem.is_goal(state):
            missing = ", ".join(str(p) for p in sorted(self.problem.unmet_goals(state), key=str))
            return False, f"the final state does not satisfy the goal; missing: {missing}"
        return True, None

    def render(self, lang: str = "pt", *, show_effects: bool = False) -> str:
        if not self.actions:
            return "(plano vazio / empty plan)"
        lines = []
        for step, action in enumerate(self.actions, start=1):
            lines.append(f"{step:>2}. {action.name}   [{action.cost:g}]")
            detail = action.describe(lang)
            if detail and detail != action.name:
                lines.append(f"     {detail}")
            if show_effects:
                added = ", ".join(str(p) for p in sorted(action.add_list, key=str))
                deleted = ", ".join(str(p) for p in sorted(action.delete_list, key=str))
                if added:
                    lines.append(f"     + {added}")
                if deleted:
                    lines.append(f"     - {deleted}")
        total = "custo total" if lang == "pt" else "total cost"
        lines.append(f"    {total}: {self.cost:g}")
        return "\n".join(lines)
