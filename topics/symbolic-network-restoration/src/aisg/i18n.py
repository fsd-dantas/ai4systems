"""
Minimal bilingual message catalogue (pt-BR / en).

PT-BR: Nao usamos gettext para manter o projeto sem dependencias e com os textos
       visiveis no proprio codigo, o que facilita a leitura durante a apresentacao.
EN:    We avoid gettext to keep the project dependency-free and the strings visible
       in the source, which helps when walking through the code in a presentation.
"""

from __future__ import annotations

from typing import Dict, Iterable

LANGUAGES = ("pt", "en")
DEFAULT_LANGUAGE = "pt"

# key -> {lang: text}
CATALOGUE: Dict[str, Dict[str, str]] = {
    # --- generic ---------------------------------------------------------
    "yes": {"pt": "sim", "en": "yes"},
    "no": {"pt": "nao", "en": "no"},
    "unknown": {"pt": "desconhecido", "en": "unknown"},
    "value_unknown_hint": {
        "pt": "(Enter = nao sei)",
        "en": "(Enter = I don't know)",
    },
    "invalid_option": {
        "pt": "Opcao invalida. Tente novamente.",
        "en": "Invalid option. Please try again.",
    },
    "certainty": {"pt": "certeza", "en": "certainty"},
    "cost": {"pt": "custo", "en": "cost"},
    "path": {"pt": "caminho", "en": "path"},
    "plan": {"pt": "plano", "en": "plan"},
    "goal": {"pt": "objetivo", "en": "goal"},
    "step": {"pt": "passo", "en": "step"},
    "none_found": {"pt": "nenhuma solucao encontrada", "en": "no solution found"},
    # --- expert system ---------------------------------------------------
    "es_title": {
        "pt": "Sistema Especialista — Diagnostico de Enlace de Backhaul",
        "en": "Expert System — Backhaul Link Diagnosis",
    },
    "es_ask_numeric": {
        "pt": "Qual o valor de '{label}' [{lo}, {hi}]?",
        "en": "What is the value of '{label}' [{lo}, {hi}]?",
    },
    "es_ask_categorical": {
        "pt": "Qual o valor de '{label}'?",
        "en": "What is the value of '{label}'?",
    },
    "es_conclusion": {"pt": "CONCLUSAO", "en": "CONCLUSION"},
    "es_no_conclusion": {
        "pt": "Nenhuma conclusao pode ser derivada com os fatos disponiveis.",
        "en": "No conclusion can be derived from the available facts.",
    },
    "es_why": {
        "pt": "Por que esta pergunta esta sendo feita:",
        "en": "Why this question is being asked:",
    },
    "es_how": {"pt": "Como esta conclusao foi obtida:", "en": "How this conclusion was reached:"},
    "es_fired_rules": {"pt": "Regras disparadas", "en": "Fired rules"},
    "es_known_facts": {"pt": "Fatos conhecidos", "en": "Known facts"},
    "es_forward": {"pt": "encadeamento para frente", "en": "forward chaining"},
    "es_backward": {"pt": "encadeamento para tras", "en": "backward chaining"},
    # --- planning --------------------------------------------------------
    "pl_title": {
        "pt": "Gerador Automatico de Planos de Acao (STRIPS / GPS)",
        "en": "Automated Action-Plan Generator (STRIPS / GPS)",
    },
    "pl_initial_state": {"pt": "Estado inicial", "en": "Initial state"},
    "pl_goal_state": {"pt": "Estado objetivo", "en": "Goal state"},
    "pl_plan_found": {"pt": "Plano encontrado com {n} acoes", "en": "Plan found with {n} actions"},
    "pl_no_plan": {"pt": "Nenhum plano encontrado.", "en": "No plan found."},
    "pl_validation_ok": {
        "pt": "Validacao: o plano e executavel e atinge o objetivo.",
        "en": "Validation: the plan is executable and reaches the goal.",
    },
    "pl_validation_fail": {
        "pt": "Validacao FALHOU: {reason}",
        "en": "Validation FAILED: {reason}",
    },
    # --- search ----------------------------------------------------------
    "se_title": {
        "pt": "Busca A* — Roteamento no Backhaul de Comunicacao",
        "en": "A* Search — Routing over the Communication Backhaul",
    },
    "se_expanded": {"pt": "nos expandidos", "en": "nodes expanded"},
    "se_generated": {"pt": "nos gerados", "en": "nodes generated"},
    "se_frontier_peak": {"pt": "pico da fronteira", "en": "peak frontier size"},
    "se_no_path": {
        "pt": "Nao existe caminho entre {start} e {goal}.",
        "en": "There is no path between {start} and {goal}.",
    },
}


def t(key: str, lang: str = DEFAULT_LANGUAGE, **kwargs: object) -> str:
    """Translate ``key`` into ``lang``, formatting any keyword arguments."""
    lang = lang if lang in LANGUAGES else DEFAULT_LANGUAGE
    entry = CATALOGUE.get(key)
    if entry is None:
        return key
    text = entry.get(lang, entry.get(DEFAULT_LANGUAGE, key))
    return text.format(**kwargs) if kwargs else text


def bilingual(key: str, sep: str = " / ") -> str:
    """Return the pt-BR and English forms joined, for headers and figure labels."""
    entry = CATALOGUE.get(key)
    if entry is None:
        return key
    return sep.join(entry[lang] for lang in LANGUAGES if lang in entry)


def known_keys() -> Iterable[str]:
    return CATALOGUE.keys()
