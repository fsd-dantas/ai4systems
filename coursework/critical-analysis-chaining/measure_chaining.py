"""
Measure forward and backward chaining on the same knowledge base.

PT-BR: Evidencia para a analise critica. Os 8 casos da base simulada sao
       resolvidos pelos dois encadeamentos sobre as mesmas 41 regras. No
       progressivo, todos os 13 fatos observaveis sao fornecidos de antemao; no
       regressivo, o motor pergunta so o que o objetivo exige, e as respostas vem
       do mesmo caso.
EN:    Evidence for the critical analysis. The simulated base's 8 cases are solved
       by both chainings over the same 41 rules. Forward chaining is given all 13
       observable facts up front; backward chaining asks only what the goal
       needs, answered from the same case.

    PYTHONPATH=software python coursework/critical-analysis-chaining/measure_chaining.py
"""

from __future__ import annotations

from aisg.expert_system import SIM_CASES, InferenceEngine, build_simulated_knowledge_base


def measure():
    kb = build_simulated_knowledge_base()
    rows = []
    for case, facts in SIM_CASES.items():
        forward = InferenceEngine(kb)
        for variable, value in facts.items():
            forward.given(variable, value)
        f = forward.forward_chain()

        asked = []

        def ask(variable, _why, facts=facts, asked=asked):
            asked.append(variable.name)
            return (facts[variable.name], 1.0) if variable.name in facts else None

        backward = InferenceEngine(kb, ask=ask)
        b = backward.backward_chain("diagnosis")

        for mode, consultation, n_asked, external in (
            ("forward", f, len(facts), "given"),
            ("backward", b, len(asked), "user"),
        ):
            best = consultation.memory.best("diagnosis")
            derived = [x for x in consultation.memory.all_facts() if x.source not in (external, "given")]
            rows.append({
                "case": case,
                "mode": mode,
                "asked": n_asked,
                "fired": len(consultation.fired_rules),
                "derived": len(derived),
                "diagnosis": best.value if best else None,
                "cf": best.cf if best else None,
            })
    return kb, rows


def main() -> None:
    kb, rows = measure()
    askable = sum(1 for v in kb.variables.values() if v.askable)
    print(f"{len(kb.rules)} rules, {askable} askable variables, {len(SIM_CASES)} cases\n")
    print("| case | mode | asked | rules fired | facts derived | diagnosis (CF) |")
    print("|---|---|---|---|---|---|")
    for r in rows:
        print(f"| {r['case']} | {r['mode']} | {r['asked']} | {r['fired']} | {r['derived']} "
              f"| {r['diagnosis']} ({r['cf']:+.2f}) |")
    n = len(SIM_CASES)
    for mode in ("forward", "backward"):
        mine = [r for r in rows if r["mode"] == mode]
        print(f"\n{mode}: mean asked {sum(r['asked'] for r in mine) / n:.2f}, "
              f"mean fired {sum(r['fired'] for r in mine) / n:.2f}, "
              f"mean derived {sum(r['derived'] for r in mine) / n:.2f}")
    agree = sum(
        1 for case in SIM_CASES
        if len({r["diagnosis"] for r in rows if r["case"] == case}) == 1
    )
    print(f"same best diagnosis: {agree}/{n}")


if __name__ == "__main__":
    main()
