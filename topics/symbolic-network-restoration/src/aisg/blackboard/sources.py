"""
Knowledge sources: the experts that contribute to the blackboard.

PT-BR: ``KnowledgeSource`` corresponde ao ``AbstractEspecialista`` do exemplo da
       disciplina: ``is_activated`` e o ``eh_ativado``, ``contribute`` e o
       ``contribui`` e ``expertise`` descreve a competencia. A diferenca e que a
       condicao de ativacao nao e escrita a mao para cada especialista: um
       especialista e ativado quando algum nivel que ele le mudou desde a sua
       ultima contribuicao.

       Os especialistas baseados em regras NAO tem regras proprias. Cada um recebe
       um subconjunto das 41 regras da base simulada, com os mesmos identificadores,
       e roda sobre o mesmo motor de inferencia. Separar a base por competencia e
       o que torna o sistema multiespecialista; reescrever as regras apagaria a
       rastreabilidade ate o trabalho anterior.

EN:    ``KnowledgeSource`` corresponds to the course example's
       ``AbstractEspecialista``: ``is_activated`` is ``eh_ativado``, ``contribute``
       is ``contribui`` and ``expertise`` describes the competence. The difference
       is that the activation condition is not hand-written per expert: an expert
       is activated when some level it reads has changed since it last contributed.

       The rule-based experts have NO rules of their own. Each receives a subset of
       the simulated base's 41 rules, with the same ids, and runs on the same
       inference engine. Splitting the base by competence is what makes the system
       multi-expert; rewriting the rules would erase traceability back to the
       earlier work.
"""

from __future__ import annotations

from dataclasses import replace
from typing import Dict, List, Optional, Sequence, Set, Tuple

from aisg.blackboard.board import Blackboard, Entry, Level
from aisg.expert_system import (
    InferenceEngine,
    KnowledgeBase,
    build_simulated_knowledge_base,
)


class KnowledgeSource:
    """
    Base class for every expert.

    Subclasses declare ``reads`` and ``writes`` and implement ``_contribute``.
    """

    name: str = ""
    label_pt: str = ""
    label_en: str = ""
    expertise_pt: str = ""
    expertise_en: str = ""
    reads: Tuple[Level, ...] = ()
    writes: Tuple[Level, ...] = ()
    #: lower runs first when several experts are activated in the same cycle
    priority: int = 100

    def __init__(self) -> None:
        #: level -> the version this expert saw after its last contribution
        self._seen: Dict[Level, int] = {}

    def label(self, lang: str = "pt") -> str:
        return self.label_pt if lang == "pt" else self.label_en

    def expertise(self, lang: str = "pt") -> str:
        return self.expertise_pt if lang == "pt" else self.expertise_en

    def is_activated(self, board: Blackboard) -> bool:
        """
        PT-BR: Ativado quando ha algo novo nos niveis que le. Na primeira vez, exige
               tambem que exista alguma entrada para ler.
        EN:    Activated when there is something new on the levels it reads. The
               first time, it also requires some entry to exist.
        """
        changed = any(board.version(level) > self._seen.get(level, -1) for level in self.reads)
        if not self._seen:
            return changed and any(board.entries(level) for level in self.reads)
        return changed

    def contribute(self, board: Blackboard) -> Tuple[int, int]:
        """Contribute, then remember what was read. Returns ``(added, removed)``."""
        result = self._contribute(board)
        # Recorded AFTER contributing: an expert that writes to a level it also
        # reads must not be woken up by its own entries.
        self._seen = {level: board.version(level) for level in self.reads}
        return result

    def _contribute(self, board: Blackboard) -> Tuple[int, int]:
        raise NotImplementedError


#: Where each variable of the simulated base lives on the board.
VARIABLE_LEVEL: Dict[str, Level] = {
    "signal_quality": Level.SYMPTOM,
    "link_symptom": Level.SYMPTOM,
    "diagnosis": Level.HYPOTHESIS,
    "recommended_action": Level.HYPOTHESIS,
    "authorization_required": Level.HYPOTHESIS,
}


def variable_level(variable: str) -> Level:
    return VARIABLE_LEVEL.get(variable, Level.OBSERVATION)


class RuleExpert(KnowledgeSource):
    """
    An expert defined by a subset of the simulated knowledge base.

    PT-BR: As variaveis que este especialista le, mas que outro especialista
           conclui, tornam-se ENTRADAS: vem do quadro, e nao de regras suas.
    EN:    Variables this expert reads but another expert concludes become INPUTS:
           they come from the board, not from its own rules.
    """

    def __init__(
        self,
        name: str,
        label_pt: str,
        label_en: str,
        expertise_pt: str,
        expertise_en: str,
        rule_ids: Sequence[str],
        *,
        priority: int,
        full_kb: Optional[KnowledgeBase] = None,
    ) -> None:
        super().__init__()
        full = full_kb or build_simulated_knowledge_base()
        wanted = set(rule_ids)
        rules = [rule for rule in full.rules if rule.id in wanted]
        missing = wanted - {rule.id for rule in rules}
        if missing:
            raise ValueError(f"{name}: unknown rule ids {', '.join(sorted(missing))}")

        concluded = {rule.conclusion.variable for rule in rules}
        referenced = {c.variable for rule in rules for c in rule.antecedents}
        variables = {
            var_name: (
                var if var.askable or var_name in concluded else replace(var, askable=True)
            )
            for var_name, var in full.variables.items()
        }

        self.name = name
        self.label_pt, self.label_en = label_pt, label_en
        self.expertise_pt, self.expertise_en = expertise_pt, expertise_en
        self.priority = priority
        self.rule_ids: Tuple[str, ...] = tuple(rule.id for rule in rules)
        self.inputs: Tuple[str, ...] = tuple(sorted(referenced - concluded))
        self.outputs: Tuple[str, ...] = tuple(sorted(concluded))
        self.reads = tuple(sorted({variable_level(v) for v in self.inputs}))
        self.writes = tuple(sorted({variable_level(v) for v in self.outputs}))
        self.kb = KnowledgeBase(
            name_pt=label_pt,
            name_en=label_en,
            variables=variables,
            rules=rules,
            goal_variables=self.outputs,
            thresholds=dict(full.thresholds),
            validity_note_pt=full.validity_note_pt,
            validity_note_en=full.validity_note_en,
        )
        # Fails fast if the subset is not a consistent base on its own.
        InferenceEngine(self.kb)

    def _contribute(self, board: Blackboard) -> Tuple[int, int]:
        subjects: Set[str] = set()
        for level in self.reads:
            subjects.update(
                e.subject for e in board.entries(level) if e.key in self.inputs
            )

        new: List[Entry] = []
        for subject in sorted(subjects):
            engine = InferenceEngine(self.kb)
            for variable in self.inputs:
                level = variable_level(variable)
                for value, cf in sorted(
                    board.belief(level, subject, variable).items(), key=lambda p: str(p[0])
                ):
                    if level is Level.OBSERVATION:
                        engine.given(variable, value, cf)
                    else:
                        engine.memory.assert_fact(variable, value, cf, "board")
            consultation = engine.forward_chain()

            for fact in sorted(
                (f for f in engine.memory.all_facts() if f.variable in self.outputs),
                key=lambda f: (f.variable, str(f.value)),
            ):
                new.append(Entry(
                    level=variable_level(fact.variable),
                    subject=subject,
                    key=fact.variable,
                    value=fact.value,
                    cf=fact.cf,
                    author=self.name,
                    support=tuple(fact.source.split("+")),
                    rationale_pt=consultation.how(fact.variable, fact.value, "pt"),
                    rationale_en=consultation.how(fact.variable, fact.value, "en"),
                ))
        return board.publish(self.name, new, levels=self.writes)


#: The rule experts. Every rule of the simulated base belongs to exactly one.
#: (name, label pt, label en, expertise pt, expertise en, rule ids, priority)
EXPERT_SPECS: Tuple[Tuple[str, str, str, str, str, Tuple[str, ...], int], ...] = (
    (
        "symptom", "Especialista em sintomas", "Symptom expert",
        "Qualifica o sinal e o sintoma do enlace; reconhece a linha de base.",
        "Grades the signal and the link symptom; recognises the baseline.",
        ("S01", "S02", "S03", "S04", "S05", "S06", "S07", "S08", "S22"), 10,
    ),
    (
        "rf", "Especialista em RF e propagacao", "RF and propagation expert",
        "Interferencia co-canal e perda de percurso excedente.",
        "Co-channel interference and excess path loss.",
        ("S10", "S11", "S12", "S13", "S23", "S24"), 20,
    ),
    (
        "mac", "Especialista em acesso ao meio", "Medium-access expert",
        "Contencao de CSMA-CA com sinal saudavel.",
        "CSMA-CA contention with a healthy signal.",
        ("S14", "S15", "S25"), 20,
    ),
    (
        "availability", "Especialista em disponibilidade", "Availability expert",
        "No parado e queda do repetidor a montante.",
        "Stopped nodes and upstream relay loss.",
        ("S16", "S17", "S18", "S26"), 20,
    ),
    (
        "routing", "Especialista em encaminhamento", "Forwarding expert",
        "No que responde sem rota para o destino.",
        "A responding node with no route to the destination.",
        ("S19",), 20,
    ),
    (
        "traffic", "Especialista em trafego", "Traffic expert",
        "Congestionamento: fila sob carga alta com RF saudavel.",
        "Congestion: queueing under high load with healthy RF.",
        ("S20", "S21"), 20,
    ),
    (
        "action", "Especialista em acao e autorizacao", "Action and authorisation expert",
        "Acao recomendada por hipotese e a exigencia de janela autorizada.",
        "The action each hypothesis recommends, and whether it needs an authorised window.",
        tuple(f"S{n}" for n in range(27, 43)), 30,
    ),
)


def build_rule_experts(full_kb: Optional[KnowledgeBase] = None) -> List[RuleExpert]:
    full = full_kb or build_simulated_knowledge_base()
    return [
        RuleExpert(name, lpt, len_, ept, een, rule_ids, priority=priority, full_kb=full)
        for name, lpt, len_, ept, een, rule_ids, priority in EXPERT_SPECS
    ]
