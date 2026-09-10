# Reassessment of commit 6a1c129

**Result for the clarified indoor scope: 78.0 points earned out of 95 assessable
points; 5 oral-defense points pending.**

Reviewed on 2026-09-10 using [assessment protocol v1.0](assessment-protocol.md).
This is an AI-assisted academic review using a graduate-student review standard,
not an instructor grade or an observed oral defense. No instructor endorsement
of the rubric has been recorded. The author confirmed the three assignment
requirements and the approved 90-minute presentation format.

**Scope clarification:** the author intends the indoor bench to be the primary
scenario for **all three assignments**. The earlier 82.5/95 assessment treated
the submitted indoor diagnosis and retained backhaul planning/routing together.
This amendment evaluates the completeness of their transition to the indoor
scenario. Weather and rain-fade inputs are outside that scenario; their absence
is correct and incurs no deduction. The illustrative nature of the examples also
incurs no deduction for missing field measurements.

The submission was clean at the start of review:
`6a1c1295b7d1597387dca0a06e519eabbccb6eef`. Environment: Windows, Python 3.13.12,
using the repository's existing virtual environment. This report was added after
reviewing that commit; application code, tests and slides were not edited.

## Score by the published criteria

Factors follow the protocol's 0 / 0.25 / 0.50 / 0.75 / 1.00 scale.

| Criterion | Maximum | Factor | Earned | Evidence / reason |
|---|---:|---:|---:|---|
| Expert system: rules, variables and knowledge traceability | 8 | 1.00 | 8 | Two explicit knowledge bases, each with 18 variables and 43 rules; nominal thresholds and rule rationales |
| Expert system: chaining and certainty propagation | 12 | 0.75 | 9 | Main demonstrations work; order-dependent certainty persists in both bases (F1) |
| Expert system: explanation, cases and unknown inputs | 10 | 0.75 | 7.5 | Cases and partial records execute; non-finite telemetry can become certain evidence (F3) |
| Planning: states, conditions, effects and assumptions | 10 | 0.75 | 7.5 | Per-fault repair model is sound, but the two replacement indoor diagnoses lack corresponding modeled repairs (F0) |
| Planning: executable plans, goals and constraints | 12 | 1.00 | 12 | Existing suite and 512 additional solver outcomes; no outstanding modeled faults on successful plans |
| Planning: diagnosis/route integration and failure handling | 8 | 0.50 | 4 | Pipeline remains bound to the backhaul knowledge base (F0); destination mismatch also persists (F2) |
| A*: path, cost and failure handling | 12 | 1.00 | 12 | Independent reference now in tests; all 1,142 directed paths and costs rechecked |
| A*: heuristic and optimality conditions | 8 | 1.00 | 8 | Valid model-specific bounds and exhaustive checks on the bundled graphs |
| A*: comparison and interpretation | 5 | 0.75 | 3.75 | Expansion totals still described too broadly; scaling claim exceeds two examples (F5) |
| Documentation: installation, execution and reproduction | 5 | 0.75 | 3.75 | Suite and notebook execute; default telemetry query templates are malformed (F4) |
| Oral defense: clarity, understanding and timing | 5 | Pending | Pending | Duration approved; actual defense not observed |
| Documentation: code/slide/source consistency and limitations | 5 | 0.50 | 2.5 | Stale repair representation and incorrect failure-route result remain in the actual deck (F6) |

| Area | Earned / assessed maximum |
|---|---:|
| Expert system | 24.5 / 30 |
| Planning | 23.5 / 30 |
| A* | 23.75 / 25 |
| Documentation, excluding oral defense | 6.25 / 10 |
| **Assessed total** | **78.0 / 95** |

No final score out of 100 is extrapolated. The earlier 85/100 used a less detailed
preliminary assessment and did not separate unobserved oral-defense points. It is
not directly comparable to this total. The multiple-fault correction and independent
reference tests are substantive improvements; remaining and newly introduced defects
prevent treating this as a fully corrected submission.

Relative to the 82.5/95 mixed-scenario assessment, the indoor-scope amendment
changes only two criteria: planning representation loses 2.5 points for missing
indoor repair semantics; integration loses 2 points for the pipeline selecting the
wrong knowledge base. These are distinct issues: adding repair operators alone
would not switch the pipeline, and switching the pipeline alone would not make
the new diagnoses plannable. Algorithm correctness credit is retained. This is
a correction of assessment scope, not a claim that the code regressed after review.

Deductions have separate primary causes: F0 affects indoor modeling and selection,
F1 affects propagation, F2 integration,
F3 unknown-input handling, F4 execution, F5 interpretation and F6 consistency of
published material. Optional real-world deployment and research novelty are not
additional course requirements. No deduction is made merely for lacking field data.

## Changes that earned credit

- **Multiple-fault restoration corrected.** `verify_link` now requires a repair
  predicate for every supplied fault. The original interference + power failure
  counterexample no longer closes the work order prematurely.
- **Meaningful regression tests added.** The suite checks incomplete repairs,
  unavailable remedies, unknown faults, and both planners. All 155 tests pass,
  compared with 108 in the previous review.
- **Independent A* reference retained in the project.** The new Floyd–Warshall
  comparison checks every ordered pair, avoiding reliance solely on `astar(h=0)`
  as an oracle for A*.
- **Bench-specific knowledge separated from the field model.** The conducted-bench
  base replaces weather-related concepts with commanded attenuation and cabling
  faults while reusing the engine. This improves the relevance of the model to a
  controlled experiment.
- **Observation records support replay and explicit gaps.** The provided JSON loads
  six of thirteen observable variables and leaves the other seven unknown. The CLI
  produces an interference conclusion with CF 0.595 from that example.
- **Assessment scope and status are documented.** The rubric remains a proposal;
  the deck contains 54 main slides plus two hidden assessment appendices.

## Outstanding findings

### F0 — High: indoor diagnosis has not been carried through planning and routing

The intended replacements in [kb_bench.py](../src/aisg/expert_system/kb_bench.py)
are appropriate for the declared indoor scenario:

| Retained outdoor concept | Indoor replacement |
|---|---|
| `weather` | `attenuation_db` |
| `rain_fade` | `excess_attenuation` |
| `path_obstruction` | `cabling_fault` |

Inspection confirms that the bench base has no `weather` variable and no
`rain_fade` diagnosis. However:

- `cmd_pipeline` still calls `build_knowledge_base()` and uses the outdoor `CASES`.
  The `--kb bench` selector exists for `diagnose`, not for the pipeline.
- `problem_from_diagnosis("excess_attenuation", "N1")` and
  `problem_from_diagnosis("cabling_fault", "N1")` both raise `ValueError`.
  The planner's mapping retains the outdoor diagnoses instead of the replacements.
- The two bundled routing graphs and their presentation remain backhaul scenarios.
  No mapping from those simulated nodes, link types and costs to the intended
  conducted bench was supplied. Their successful A* checks prove correctness on
  those graphs, not completion of the indoor demonstration.

**Correction:** select the bench consistently throughout the demonstration;
provide indoor repair operators for the new diagnoses; and supply either a bench
topology or an explicit emulation mapping for the existing synthetic graph and
cost model. Reuse the general search and planning engines. Replacing rain-fade
with excess attenuation is not merely a label change: the indoor repair must
restore the intended path budget rather than wait for weather to clear.
Update the script, notebook and slides to describe the same scenario.

### F1 — High: inference remains dependent on rule ordering

In the indoor `excess_attenuation` case, diagnosis CF remains 0.924, but the
recommended-action CF changes from **0.7854** under first-match/specificity to
**0.5100** under recency. Therefore, testing only the winning diagnosis does not
establish invariant reasoning results. This finding does not depend on weather
or a rain-fade case from the retained outdoor base.

The engine skips already-fired rules permanently, even when their premises later
gain or lose support. See [engine.py](../src/aisg/expert_system/engine.py),
`forward_chain`, and the fixed-point claim in [expert-system documentation](01-expert-system.md).

**Correction:** settle dependencies before firing downstream rules, or track and
recompute individual rule contributions without double counting. Add regression
checks for the complete diagnosis/action CF results across policies. If approximate
order-dependent semantics are intentional, state their limits explicitly instead
of claiming a common fixed point.

### F2 — High: the reroute precondition does not use the requested destination

```bash
aisg --lang en pipeline --case congestion --node AP_A --target SUB_S1
```

Still produces a validated five-action restoration plan, followed by
`There is no path between NOC and SUB_S1.`

[cli.py](../src/aisg/cli.py), `cmd_pipeline`, constructs the planning problem
before resolving `args.target`. The domain checks an internally selected field
device. Per-fault repair predicates do not address this separate defect.

**Correction:** resolve source, destination and exclusions once, then use them for
planning feasibility and final routing. Require the unreachable-destination example
to fail before a restoration plan is reported as valid.

### F3 — High: a NaN reading becomes certain total packet loss

Using a simulated valid Prometheus vector response with value `"NaN"`, the
`success_ratio_to_loss_pct` converter returns **100.0**. The resulting observation
contains `packet_loss_pct=(100.0, 1.0)`, has no unavailable entry, and passes
knowledge-base validation. Thus an undefined numeric reading becomes a strong
measurement rather than an explicit gap.

See [prometheus.py](../src/aisg/prometheus.py), `success_ratio_to_loss_pct` and
`PrometheusClient.scalar`.

**Correction:** reject non-finite values before conversion, record them as
unavailable, and reject invalid success ratios rather than silently saturating
them. Check NaN and both infinities across converters. This finding is reproducible
without contacting a real telemetry endpoint.

### F4 — High for the telemetry extension: default queries contain double braces

Rendering the first default spec for subject `L1` produces:

```text
min_over_time(radio_rssi_dbm{{link="L1"}}[5m])
```

All seven default specs retain double selector braces. `MetricSpec.render` uses
string replacement, which does not unescape the doubled braces in the templates.
PromQL uses a single pair around label matchers, so the expected expression is
`min_over_time(radio_rssi_dbm{link="L1"}[5m])`.
See [official Prometheus selector syntax](https://prometheus.io/docs/prometheus/latest/querying/basics/#instant-vector-selectors).

Existing injected fetchers accept the query string without parsing it, so their
success does not validate PromQL. The syntax defect is established from the
rendered output and official grammar; no live server was contacted during review.

**Correction:** use literal single selector braces with the existing placeholder
replacement, escape subject values appropriately, and check every rendered default
query against a parser or a controlled Prometheus instance. Keep unavailable-metric
handling separate from detecting a broken query template.

### F5 — Medium: correctness validation improved, but performance claims did not

The new ordered-pair oracle is an improvement in correctness coverage. The older
expansion experiment still uses `itertools.combinations`: one direction per
unordered pair. Its published totals (1,382 / 1,519 and 5,571 / 7,657) reproduce
that experiment, not an experiment over both directions.

Across all directed pairs, this review reproduced:

| Scenario | Directed pairs | A* expansions | UCS expansions | Reduction |
|---|---:|---:|---:|---:|
| Base | 272 | 2,342 | 2,584 | 9.37% |
| Scale | 870 | 10,310 | 13,920 | 25.93% |

Report which pair definition is used. Describe the larger reduction as a result
for these two topologies, not a general law that larger graphs necessarily benefit
more. See [A* discussion](03-astar.md) and [search tests](../tests/test_search.py).

### F6 — Medium: presentation material has not followed the implementation

The actual PPTX, not just its source, still contains:

- Slide 26: the shared `fault-cleared(?n)` effect instead of the per-fault repair
  predicate now used by the operator.
- Slide 30: a GPS explanation based on that obsolete shared predicate.
- Slide 47: approximately **357 ms** after disabling `LTE_ENB-RM_A5`. Its command
  actually returns **312.44 ms** via
  `NOC -> LTE_CORE -> LTE_ENB -> RM_B3 -> SAF_A2 -> RECLOSER_7`.
  Disabling this one link does not remove the entire LTE overlay.

The old predicate also remains in the planning document, script and diagram source.
The test-count and slide-count corrections are credited, but do not resolve these
substantive mismatches.

**Correction:** synchronize operator examples, traces and diagrams with the model;
generate route results from the exact command and rebuild the deck.

## Validation record and boundaries

| Check executed | Result |
|---|---|
| Full suite: `python -m pytest -p no:cacheprovider` | 155 passed |
| Notebook code cells executed sequentially in memory, Agg plotting backend | 25 executed successfully; not a live Jupyter UI check |
| All 128 subsets of seven known faults × two alternate-route settings × two planners | 512 outcomes matched solvability; every successful plan validated and left no known fault literal |
| Independent routing cost/path and heuristic audit | 1,142 directed pairs passed; no cost/path or heuristic violations |
| Bench demonstration: `diagnose --kb bench --case excess_attenuation` | Executes and explains the selected diagnosis |
| Partial JSON observation demonstration | Executes; six supplied variables and seven missing variables reported |
| Previous ordering and destination counterexamples | Still reproduced |
| Default query rendering and injected NaN response | New defects reproduced as described above |
| Actual PPTX text and notes inspection | 56 slides; appendices 55–56 hidden; substantive stale content remains |

The fault-subset audit covers the built-in deterministic operators and builder
inputs; it is not a proof for arbitrary future operators, extra initial facts or
physical equipment. The A* audit covers the bundled graphs under the stated cost
model. No fresh package installation, live Prometheus query, real bench experiment
or oral-defense observation was performed in this review.

**Provenance clarification from the author:** the bench cases and observation JSON
are illustrative examples, not records of actual bench or Prometheus measurements.
This resolves the provenance question. The JSON's `source: prometheus`, timestamp
and query fields demonstrate the record format; they do not establish actual
collection. Present these examples explicitly as illustrative in demonstrations.

The examples establish software behavior and an experiment design, not measured
diagnostic accuracy. An induction recipe and a commanded setting should be
distinguished from verified realization of the fault; collect baseline,
intervention confirmation, timestamps and repeated observations before presenting
causal labels as experimentally established. This provenance clarification alone
did not change the prior 82.5/95: no real-measurement credit had been assumed,
and field data are not an additional requirement of the course assignment.
The subsequent clarification that all three assignments should use the indoor
scenario produces the **78.0/95** assessment above, with five oral-defense points
pending, because the transition is incomplete outside the diagnosis module.

**Confidence:** high for the reproduced software results and source-based findings.
The scoring factors remain academic judgments. No numerical claim of greater than
99% confidence is made for the grade. The rubric's endorsement and the remaining
oral-defense criterion require actual instructor/defense evidence.

Recommended order before reassessment: complete the indoor transition (F0),
repair F1–F4; synchronize the deck and
qualify the experimental claims; rerun the evidence matrix on a new identified
commit. Additional features are less valuable at this point than completing these
corrections.
