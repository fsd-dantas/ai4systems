"""
Rule-based inference engine with certainty factors.

PT-BR: Motor de inferencia com encadeamento para frente (dirigido por dados) e para
       tras (dirigido por objetivo), fatores de certeza no estilo MYCIN, estrategias
       de resolucao de conflito e explicacao 'por que' / 'como'.

EN:    Inference engine with forward (data-driven) and backward (goal-driven)
       chaining, MYCIN-style certainty factors, conflict-resolution strategies, and
       'why' / 'how' explanation.

Certainty factors / Fatores de certeza
--------------------------------------
A certainty factor (CF) lies in [-1, +1]: +1 is confirmed, -1 is refuted, 0 is no
evidence. Following Shortliffe & Buchanan's MYCIN:

* the CF of a premise is the *minimum* CF among its conditions (the weakest link);
* the CF a rule contributes is ``premise_cf * rule_cf``;
* a rule only fires when its premise CF exceeds :data:`FIRING_THRESHOLD`, so weak
  evidence does not cascade;
* two independent conclusions about the same fact are combined with the MYCIN
  combination function (see :func:`combine_cf`).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Dict, FrozenSet, List, Optional, Sequence, Tuple, Union

Number = Union[int, float]

#: MYCIN's classic threshold: a premise weaker than this does not fire a rule.
FIRING_THRESHOLD = 0.2


def combine_cf(cf1: float, cf2: float) -> float:
    """
    Combine two certainty factors for the same conclusion (MYCIN).

    PT-BR: Evidencias que se reforcam aproximam-se de 1 sem nunca ultrapassar;
           evidencias contraditorias cancelam-se parcialmente.
    EN:    Reinforcing evidence approaches 1 without exceeding it; contradictory
           evidence partially cancels out.
    """
    if cf1 >= 0 and cf2 >= 0:
        return cf1 + cf2 * (1 - cf1)
    if cf1 <= 0 and cf2 <= 0:
        return cf1 + cf2 * (1 + cf1)
    denominator = 1 - min(abs(cf1), abs(cf2))
    if denominator == 0:
        return 0.0
    return (cf1 + cf2) / denominator


class VariableKind(Enum):
    NUMERIC = "numeric"
    CATEGORICAL = "categorical"
    BOOLEAN = "boolean"


@dataclass(frozen=True)
class Variable:
    """
    An attribute the system can know about the world.

    ``askable`` variables may be requested from the user during a consultation;
    variables that are only ever concluded by rules are not askable.
    """

    name: str
    kind: VariableKind
    label_pt: str
    label_en: str
    #: allowed labels for categorical/boolean variables
    labels: Tuple[str, ...] = ()
    #: inclusive numeric range
    bounds: Optional[Tuple[Number, Number]] = None
    unit: str = ""
    askable: bool = True
    prompt_pt: str = ""
    prompt_en: str = ""

    def label(self, lang: str = "pt") -> str:
        return self.label_pt if lang == "pt" else self.label_en

    def prompt(self, lang: str = "pt") -> str:
        text = self.prompt_pt if lang == "pt" else self.prompt_en
        return text or self.label(lang)

    def validate_value(self, value: object) -> None:
        if self.kind is VariableKind.NUMERIC:
            if not isinstance(value, (int, float)):
                raise ValueError(f"{self.name} expects a number, got {value!r}")
            if self.bounds and not (self.bounds[0] <= value <= self.bounds[1]):
                raise ValueError(
                    f"{self.name}={value} is outside the declared range {self.bounds}"
                )
        else:
            if not isinstance(value, str):
                raise ValueError(f"{self.name} expects a label, got {value!r}")
            if self.labels and value not in self.labels:
                raise ValueError(
                    f"{self.name}={value!r} is not one of {', '.join(self.labels)}"
                )


class Operator(Enum):
    EQ = "="
    NE = "!="
    GT = ">"
    LT = "<"
    GE = ">="
    LE = "<="


@dataclass(frozen=True)
class Condition:
    """One antecedent test, e.g. ``snr_db < 8``."""

    variable: str
    operator: Operator
    value: object

    def __str__(self) -> str:
        return f"{self.variable} {self.operator.value} {self.value}"

    def render(self, kb: "KnowledgeBase", lang: str = "pt") -> str:
        var = kb.variables.get(self.variable)
        label = var.label(lang) if var else self.variable
        return f"{label} {self.operator.value} {self.value}"


@dataclass(frozen=True)
class Conclusion:
    """The consequent of a rule: it asserts ``variable = value``."""

    variable: str
    value: object

    def __str__(self) -> str:
        return f"{self.variable} = {self.value}"

    def render(self, kb: "KnowledgeBase", lang: str = "pt") -> str:
        var = kb.variables.get(self.variable)
        label = var.label(lang) if var else self.variable
        return f"{label} = {self.value}"


@dataclass(frozen=True)
class Rule:
    """
    A production rule: IF <antecedents> THEN <conclusion> WITH <cf>.

    ``cf`` is the rule's own strength: how much the expert believes the conclusion
    when the premise is fully certain.
    """

    id: str
    antecedents: Tuple[Condition, ...]
    conclusion: Conclusion
    cf: float = 1.0
    rationale_pt: str = ""
    rationale_en: str = ""

    def __post_init__(self) -> None:
        if not -1.0 <= self.cf <= 1.0:
            raise ValueError(f"rule {self.id}: cf must be in [-1, 1], got {self.cf}")
        if not self.antecedents:
            raise ValueError(f"rule {self.id}: a rule needs at least one antecedent")

    @property
    def specificity(self) -> int:
        """Number of conditions — used by the specificity conflict-resolution policy."""
        return len(self.antecedents)

    @property
    def referenced_variables(self) -> FrozenSet[str]:
        return frozenset(c.variable for c in self.antecedents)

    def rationale(self, lang: str = "pt") -> str:
        return self.rationale_pt if lang == "pt" else self.rationale_en

    def render(self, kb: "KnowledgeBase", lang: str = "pt") -> str:
        conj = " E " if lang == "pt" else " AND "
        premise = conj.join(c.render(kb, lang) for c in self.antecedents)
        if lang == "pt":
            return f"{self.id}: SE {premise} ENTAO {self.conclusion.render(kb, lang)} (CF {self.cf:+.2f})"
        return f"{self.id}: IF {premise} THEN {self.conclusion.render(kb, lang)} (CF {self.cf:+.2f})"


@dataclass
class Fact:
    """A believed value for a variable, with its certainty and where it came from."""

    variable: str
    value: object
    cf: float
    #: 'user', 'given', or a rule id
    source: str
    #: monotonically increasing stamp, used by the recency policy
    stamp: int = 0

    def render(self, kb: "KnowledgeBase", lang: str = "pt") -> str:
        var = kb.variables.get(self.variable)
        label = var.label(lang) if var else self.variable
        unit = f" {var.unit}" if var and var.unit else ""
        return f"{label} = {self.value}{unit} (CF {self.cf:+.2f}, {self.source})"


class ConflictResolution(Enum):
    """
    How the engine picks one rule when several are ready to fire.

    PT-BR: FIRST_MATCH segue a ordem da base; SPECIFICITY prefere a regra mais
           especifica (mais condicoes); RECENCY prefere a regra que usa os fatos
           adicionados mais recentemente.
    EN:    FIRST_MATCH follows base order; SPECIFICITY prefers the most specific rule
           (most conditions); RECENCY prefers the rule using the most recently added
           facts.
    """

    FIRST_MATCH = "first-match"
    SPECIFICITY = "specificity"
    RECENCY = "recency"


@dataclass
class KnowledgeBase:
    """A named set of variables and rules, plus the goals it can conclude."""

    name_pt: str
    name_en: str
    variables: Dict[str, Variable] = field(default_factory=dict)
    rules: List[Rule] = field(default_factory=list)
    goal_variables: Tuple[str, ...] = ()
    #: declared, calibratable numeric thresholds used by the rules
    thresholds: Dict[str, Number] = field(default_factory=dict)
    #: statement of what the base may and may not be used for
    validity_note_pt: str = ""
    validity_note_en: str = ""

    def name(self, lang: str = "pt") -> str:
        return self.name_pt if lang == "pt" else self.name_en

    def validity_note(self, lang: str = "pt") -> str:
        return self.validity_note_pt if lang == "pt" else self.validity_note_en

    def add_variable(self, variable: Variable) -> Variable:
        if variable.name in self.variables:
            raise ValueError(f"duplicate variable: {variable.name}")
        self.variables[variable.name] = variable
        return variable

    def add_rule(self, rule: Rule) -> Rule:
        if any(r.id == rule.id for r in self.rules):
            raise ValueError(f"duplicate rule id: {rule.id}")
        self.rules.append(rule)
        return rule

    def rules_concluding(self, variable: str) -> List[Rule]:
        return [r for r in self.rules if r.conclusion.variable == variable]

    def validate(self) -> List[str]:
        """
        Static check of the knowledge base.

        PT-BR: Detecta variaveis nao declaradas, valores fora do dominio e variaveis
               que nao sao perguntaveis nem concluiveis (becos sem saida).
        EN:    Detects undeclared variables, out-of-domain values, and variables that
               are neither askable nor concludable (dead ends).
        """
        problems: List[str] = []
        concluded = {r.conclusion.variable for r in self.rules}

        for rule in self.rules:
            for condition in rule.antecedents:
                var = self.variables.get(condition.variable)
                if var is None:
                    problems.append(
                        f"{rule.id}: condition on undeclared variable "
                        f"'{condition.variable}'"
                    )
                    continue
                if var.kind is not VariableKind.NUMERIC and var.labels:
                    if condition.operator in (Operator.EQ, Operator.NE) and (
                        condition.value not in var.labels
                    ):
                        problems.append(
                            f"{rule.id}: '{condition.value}' is not a declared label "
                            f"of {var.name} ({', '.join(var.labels)})"
                        )
                if not var.askable and var.name not in concluded:
                    problems.append(
                        f"{rule.id}: '{var.name}' is neither askable nor concluded "
                        "by any rule"
                    )
            target = self.variables.get(rule.conclusion.variable)
            if target is None:
                problems.append(
                    f"{rule.id}: concludes undeclared variable "
                    f"'{rule.conclusion.variable}'"
                )
            elif target.labels and rule.conclusion.value not in target.labels:
                problems.append(
                    f"{rule.id}: concludes '{rule.conclusion.value}', not a declared "
                    f"label of {target.name}"
                )

        for goal in self.goal_variables:
            if goal not in self.variables:
                problems.append(f"goal variable '{goal}' is not declared")
            elif goal not in concluded:
                problems.append(f"goal variable '{goal}' is not concluded by any rule")

        return problems


@dataclass
class TraceEntry:
    """One line of the reasoning trace."""

    kind: str  # 'ask' | 'fire' | 'skip' | 'goal' | 'note'
    text: str
    depth: int = 0
    rule_id: Optional[str] = None

    def render(self) -> str:
        marker = {"ask": "?", "fire": "*", "skip": "-", "goal": ">", "note": " "}.get(
            self.kind, " "
        )
        return f"{'  ' * self.depth}{marker} {self.text}"


class WorkingMemory:
    """
    The set of currently believed facts.

    PT-BR: Cada variavel guarda um mapa valor -> fato. Isso permite que o sistema
           mantenha varias hipoteses concorrentes com certezas diferentes, como faz
           um diagnostico real.
    EN:    Each variable holds a value -> fact map, so the system can carry several
           competing hypotheses with different certainties, as a real diagnosis does.
    """

    def __init__(self) -> None:
        self._facts: Dict[str, Dict[object, Fact]] = {}
        self._clock = 0
        # (variable, value) -> {source: cf}. Contributions are kept apart so a
        # rule that fires again REPLACES its own earlier contribution instead of
        # being combined with it. Combining a rule with itself would count the
        # same evidence twice, which is the failure mode MYCIN's combination
        # function is least forgiving about.
        self._contributions: Dict[Tuple[str, object], Dict[str, float]] = {}

    def __contains__(self, variable: str) -> bool:
        return variable in self._facts

    @property
    def variables(self) -> List[str]:
        return list(self._facts)

    def assert_fact(self, variable: str, value: object, cf: float, source: str) -> Fact:
        """
        Record one source's support for ``variable = value`` and recombine.

        PT-BR: A cada chamada, a contribuicao DAQUELA fonte e substituida e o CF
               final e recalculado a partir de todas as contribuicoes. Assim, uma
               regra que dispara de novo com premissa mais forte corrige sua
               propria conclusao, em vez de somar-se a si mesma.
        EN:    Each call replaces THAT source's contribution and recomputes the
               final CF from all contributions. A rule that fires again on a
               stronger premise therefore corrects its own conclusion instead of
               compounding with itself.
        """
        self._clock += 1
        key = (variable, value)
        contributions = self._contributions.setdefault(key, {})
        contributions[source] = cf

        # Deterministic order, so the result does not depend on firing order.
        merged = 0.0
        for name in sorted(contributions):
            merged = combine_cf(merged, contributions[name])

        source_chain = "+".join(sorted(contributions))
        fact = Fact(variable, value, merged, source_chain, self._clock)
        self._facts.setdefault(variable, {})[value] = fact
        return fact

    def get(self, variable: str, value: object) -> Optional[Fact]:
        return self._facts.get(variable, {}).get(value)

    def best(self, variable: str) -> Optional[Fact]:
        """The most strongly believed value for a variable."""
        bucket = self._facts.get(variable)
        if not bucket:
            return None
        return max(bucket.values(), key=lambda f: f.cf)

    def ranked(self, variable: str, *, min_cf: float = 0.0) -> List[Fact]:
        bucket = self._facts.get(variable, {})
        facts = [f for f in bucket.values() if f.cf > min_cf]
        return sorted(facts, key=lambda f: f.cf, reverse=True)

    def all_facts(self) -> List[Fact]:
        return sorted(
            (f for bucket in self._facts.values() for f in bucket.values()),
            key=lambda f: f.stamp,
        )

    def last_stamp(self, variable: str) -> int:
        bucket = self._facts.get(variable)
        return max((f.stamp for f in bucket.values()), default=0) if bucket else 0


#: Callback used to obtain an unknown askable variable: (variable, why-stack) ->
#: (value, cf) or ``None`` when the user does not know.
AskFn = Callable[[Variable, Sequence[Rule]], Optional[Tuple[object, float]]]


@dataclass
class Consultation:
    """The outcome of a consultation: conclusions, trace, and provenance."""

    kb: KnowledgeBase
    memory: WorkingMemory
    strategy: str
    trace: List[TraceEntry] = field(default_factory=list)
    fired_rules: List[str] = field(default_factory=list)
    cycles: int = 0

    def conclusions(self, *, min_cf: float = FIRING_THRESHOLD) -> Dict[str, List[Fact]]:
        return {
            goal: self.memory.ranked(goal, min_cf=min_cf)
            for goal in self.kb.goal_variables
            if self.memory.ranked(goal, min_cf=min_cf)
        }

    def render_trace(self) -> str:
        return "\n".join(entry.render() for entry in self.trace)

    def how(self, variable: str, value: object, lang: str = "pt", depth: int = 0) -> str:
        """
        Explain HOW a conclusion was reached, recursively.

        PT-BR: Percorre as regras que sustentam o fato e, para cada condicao, explica
               de onde veio o fato usado.
        EN:    Walks the rules supporting the fact and, for each condition, explains
               where the fact it used came from.
        """
        pad = "  " * depth
        fact = self.memory.get(variable, value)
        if fact is None:
            return f"{pad}({variable} = {value}: " + (
                "sem registro)" if lang == "pt" else "no record)"
            )
        if fact.source in ("user", "given"):
            origin = (
                "informado pelo usuario" if fact.source == "user" else "fato inicial"
            ) if lang == "pt" else (
                "supplied by the user" if fact.source == "user" else "initial fact"
            )
            return f"{pad}{fact.render(self.kb, lang)} — {origin}"

        lines = [f"{pad}{fact.render(self.kb, lang)}"]
        for rule_id in fact.source.split("+"):
            rule = next((r for r in self.kb.rules if r.id == rule_id), None)
            if rule is None:
                continue
            lines.append(f"{pad}  <= {rule.render(self.kb, lang)}")
            if rule.rationale(lang):
                lines.append(f"{pad}     {rule.rationale(lang)}")
            for condition in rule.antecedents:
                supporting = self.memory.best(condition.variable)
                if supporting is not None:
                    lines.append(
                        self.how(condition.variable, supporting.value, lang, depth + 2)
                    )
        return "\n".join(lines)


class InferenceEngine:
    """Runs forward and backward chaining over a knowledge base."""

    def __init__(
        self,
        kb: KnowledgeBase,
        *,
        ask: Optional[AskFn] = None,
        strategy: ConflictResolution = ConflictResolution.SPECIFICITY,
        max_cycles: int = 500,
        sufficient_cf: float = 0.9,
    ) -> None:
        problems = kb.validate()
        if problems:
            raise ValueError(
                "knowledge base is inconsistent:\n  - " + "\n  - ".join(problems)
            )
        self.kb = kb
        self.ask = ask
        self.strategy = strategy
        self.max_cycles = max_cycles
        #: once a goal reaches this certainty, backward chaining stops looking for
        #: further support for it — the classic "sufficiency" cut-off
        self.sufficient_cf = sufficient_cf
        self.memory = WorkingMemory()
        self.trace: List[TraceEntry] = []
        self._fired: List[str] = []
        #: rule id -> the premise CF it last fired on
        self._fired_premise: Dict[str, float] = {}
        self._why_stack: List[Rule] = []
        self._pending: set = set()

    # -- setup -----------------------------------------------------------
    def reset(self) -> None:
        self.memory = WorkingMemory()
        self.trace = []
        self._fired = []
        self._fired_premise = {}
        self._why_stack = []
        self._pending = set()

    def given(self, variable: str, value: object, cf: float = 1.0) -> None:
        """Load a fact that is known up front (telemetry, a form, a test case)."""
        var = self.kb.variables.get(variable)
        if var is None:
            raise KeyError(f"unknown variable: {variable}")
        var.validate_value(value)
        self.memory.assert_fact(variable, value, cf, "given")

    def _log(self, kind: str, text: str, rule_id: Optional[str] = None) -> None:
        self.trace.append(
            TraceEntry(kind=kind, text=text, depth=len(self._why_stack), rule_id=rule_id)
        )

    # -- condition evaluation -------------------------------------------
    def evaluate(self, condition: Condition) -> Optional[float]:
        """
        Certainty that a condition holds, or ``None`` when the variable is unknown.

        PT-BR: Comparacoes numericas usam o valor medido (CF do proprio fato).
               Comparacoes categoricas usam o CF do valor correspondente.
        EN:    Numeric comparisons use the measured value (the fact's own CF).
               Categorical comparisons use the CF of the matching value.
        """
        var = self.kb.variables[condition.variable]

        if var.kind is VariableKind.NUMERIC:
            fact = self.memory.best(condition.variable)
            if fact is None:
                return None
            actual = float(fact.value)  # type: ignore[arg-type]
            target = float(condition.value)  # type: ignore[arg-type]
            holds = {
                Operator.EQ: actual == target,
                Operator.NE: actual != target,
                Operator.GT: actual > target,
                Operator.LT: actual < target,
                Operator.GE: actual >= target,
                Operator.LE: actual <= target,
            }[condition.operator]
            return fact.cf if holds else 0.0

        if condition.operator is Operator.EQ:
            if condition.variable not in self.memory:
                return None
            fact = self.memory.get(condition.variable, condition.value)
            return fact.cf if fact else 0.0

        if condition.operator is Operator.NE:
            if condition.variable not in self.memory:
                return None
            match = self.memory.get(condition.variable, condition.value)
            if match is None:
                best = self.memory.best(condition.variable)
                return best.cf if best else 0.0
            return -match.cf if match.cf > 0 else abs(match.cf)

        raise ValueError(
            f"operator {condition.operator.value} is not defined for the "
            f"{var.kind.value} variable {var.name}"
        )

    def premise_cf(self, rule: Rule) -> Optional[float]:
        """Minimum CF across the antecedents; ``None`` if any is still unknown."""
        cfs: List[float] = []
        for condition in rule.antecedents:
            cf = self.evaluate(condition)
            if cf is None:
                return None
            if cf <= 0:
                return cf  # a failed condition short-circuits the conjunction
            cfs.append(cf)
        return min(cfs) if cfs else 0.0

    # -- conflict resolution ---------------------------------------------
    def _order_conflict_set(self, candidates: List[Tuple[Rule, float]]) -> List[Tuple[Rule, float]]:
        if self.strategy is ConflictResolution.FIRST_MATCH:
            order = {rule.id: i for i, rule in enumerate(self.kb.rules)}
            return sorted(candidates, key=lambda pair: order[pair[0].id])
        if self.strategy is ConflictResolution.SPECIFICITY:
            return sorted(
                candidates,
                key=lambda pair: (-pair[0].specificity, -pair[1], pair[0].id),
            )
        # RECENCY: prefer the rule whose antecedents rest on the newest facts
        def newest(rule: Rule) -> int:
            return max(
                (self.memory.last_stamp(c.variable) for c in rule.antecedents),
                default=0,
            )

        return sorted(candidates, key=lambda pair: (-newest(pair[0]), pair[0].id))

    # -- forward chaining -------------------------------------------------
    def forward_chain(self) -> Consultation:
        """
        Data-driven inference: fire what the known facts support, until quiescence.

        PT-BR: Ciclo reconhecer-agir: monta o conjunto de conflito, resolve o conflito
               pela estrategia escolhida e dispara UMA regra por ciclo, o que torna a
               ordem de raciocinio visivel no trace.
        EN:    Recognise-act cycle: builds the conflict set, resolves it with the
               chosen policy, and fires ONE rule per cycle, which makes the reasoning
               order visible in the trace.
        """
        cycles = 0
        while cycles < self.max_cycles:
            candidates: List[Tuple[Rule, float]] = []
            for rule in self.kb.rules:
                cf = self.premise_cf(rule)
                if cf is None or cf <= FIRING_THRESHOLD:
                    continue
                previous = self._fired_premise.get(rule.id)
                # A rule fires once, and again only if its premise has since
                # STRENGTHENED. Without this, a conclusion drawn early from a
                # partial premise stays frozen while its own support keeps
                # growing - which made downstream certainties depend on the
                # conflict-resolution policy that happened to order the firings.
                # Premises are bounded above by 1 and must strictly increase, so
                # re-firing terminates.
                if previous is not None and cf <= previous + 1e-9:
                    continue
                candidates.append((rule, cf))

            if not candidates:
                break

            ordered = self._order_conflict_set(candidates)
            if len(ordered) > 1:
                competing = ", ".join(r.id for r, _ in ordered[1:])
                self._log(
                    "note",
                    f"conflict set: {ordered[0][0].id} chosen by "
                    f"{self.strategy.value} over {competing}",
                )
            rule, cf = ordered[0]
            self._fire(rule, cf)
            cycles += 1

        return Consultation(
            kb=self.kb,
            memory=self.memory,
            strategy=self.strategy.value,
            trace=list(self.trace),
            fired_rules=list(self._fired),
            cycles=cycles,
        )

    def _fire(self, rule: Rule, premise_cf: float) -> None:
        conclusion_cf = premise_cf * rule.cf
        fact = self.memory.assert_fact(
            rule.conclusion.variable, rule.conclusion.value, conclusion_cf, rule.id
        )
        if rule.id not in self._fired:
            self._fired.append(rule.id)
        self._fired_premise[rule.id] = premise_cf
        self._log(
            "fire",
            f"{rule.id}: premise CF {premise_cf:+.2f} x rule CF {rule.cf:+.2f} "
            f"=> {rule.conclusion} (CF {fact.cf:+.2f})",
            rule_id=rule.id,
        )

    # -- backward chaining ------------------------------------------------
    def backward_chain(self, goal_variable: str) -> Consultation:
        """
        Goal-driven inference: try to establish ``goal_variable``.

        PT-BR: Pergunta ao usuario apenas o que o objetivo exige. A pilha de regras em
               curso e o 'porque' de cada pergunta.
        EN:    Asks the user only what the goal requires. The stack of rules in
               progress is the 'why' behind each question.
        """
        if goal_variable not in self.kb.variables:
            raise KeyError(f"unknown variable: {goal_variable}")
        self._log("goal", f"establish {goal_variable}")
        self._establish(goal_variable)
        return Consultation(
            kb=self.kb,
            memory=self.memory,
            strategy=self.strategy.value,
            trace=list(self.trace),
            fired_rules=list(self._fired),
            cycles=len(self._fired),
        )

    def _establish(self, variable: str) -> None:
        if variable in self._pending:
            self._log("note", f"{variable} already under evaluation — cycle avoided")
            return
        self._pending.add(variable)
        try:
            supporting = self.kb.rules_concluding(variable)
            for rule in supporting:
                if rule.id in self._fired:
                    continue

                # Sufficiency cut-off: stop once the goal is established strongly
                # enough that further evidence cannot change the decision.
                established = self.memory.best(variable)
                if established is not None and established.cf >= self.sufficient_cf:
                    self._log(
                        "note",
                        f"{variable} = {established.value} already established "
                        f"(CF {established.cf:+.2f}) — no further questions needed",
                    )
                    break

                self._why_stack.append(rule)
                try:
                    self._log("note", f"trying {rule.id} for {variable}")
                    # Evaluate conditions one at a time and abandon the rule as soon
                    # as one of them is false. This is what keeps a goal-driven
                    # consultation short: the user is never asked about the rest of a
                    # premise that can no longer hold.
                    refuted = False
                    for condition in rule.antecedents:
                        if self.evaluate(condition) is None:
                            self._obtain(condition.variable)
                        cf = self.evaluate(condition)
                        if cf is not None and cf <= 0:
                            self._log(
                                "skip",
                                f"{rule.id}: {condition} is false — the remaining "
                                "conditions are not asked",
                            )
                            refuted = True
                            break
                    if refuted:
                        continue

                    cf = self.premise_cf(rule)
                    if cf is None:
                        self._log("skip", f"{rule.id}: premise still unknown")
                    elif cf > FIRING_THRESHOLD:
                        self._fire(rule, cf)
                    else:
                        self._log("skip", f"{rule.id}: premise CF {cf:+.2f} too weak")
                finally:
                    self._why_stack.pop()

            if not supporting and variable not in self.memory:
                self._obtain(variable)
        finally:
            self._pending.discard(variable)

    def _obtain(self, variable: str) -> None:
        """Get a variable's value: derive it from rules, or ask the user."""
        if variable in self.memory:
            return
        var = self.kb.variables[variable]
        if self.kb.rules_concluding(variable):
            self._establish(variable)
            if variable in self.memory:
                return
        if not var.askable or self.ask is None:
            return
        self._log("ask", f"asking the user for {variable}")
        answer = self.ask(var, tuple(self._why_stack))
        if answer is None:
            return
        value, cf = answer
        var.validate_value(value)
        self.memory.assert_fact(variable, value, cf, "user")

    # -- explanation ------------------------------------------------------
    def why(self, lang: str = "pt") -> str:
        """
        Explain WHY the current question is being asked.

        PT-BR: Mostra a cadeia de regras que levou o motor ate esta pergunta.
        EN:    Shows the chain of rules that led the engine to this question.
        """
        if not self._why_stack:
            return (
                "Pergunta inicial: nenhuma regra em curso."
                if lang == "pt"
                else "Opening question: no rule in progress."
            )
        lines = []
        for depth, rule in enumerate(self._why_stack):
            lines.append("  " * depth + rule.render(self.kb, lang))
        return "\n".join(lines)
