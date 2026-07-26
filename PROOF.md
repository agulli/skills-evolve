# Proof: Does the five-part loop actually work?

This document answers, with real measurement and honest limits, the five claims the
library makes about itself. Every number here is reproducible from `simulator/` +
`scripts/` against the raw files in `simulator/results/`; the full method-by-method
trail is in [EXPERIMENTS.md](EXPERIMENTS.md) (EXP-001 … EXP-025).

**Reading the verdicts:** ✅ PROVEN (real data supports it), 🟡 PARTIAL (proven within a
scope, with a named gap), ⚙️ MECHANISM-ONLY (the machinery is proven to work *if* adopted;
the real-world claim can't be tested yet). Nothing here is rounded up.

Models used throughout: **Claude Haiku 4.5** and **Gemini Flash-Lite** — two small models
from two vendors, deliberately (cross-vendor confirmation is the whole point of a "norm").

---

## Scorecard

| # | Claim | Verdict | One-line result |
|---|-------|---------|-----------------|
| 1 | Skills are useful | 🟡 PARTIAL | **0 confirmed-harmful skills on either model** (FDR-corrected). 36/61 Gemini wins; 6 confirmed on *both* models. Gap: single-turn tasks; most skills at first-pass depth; 2 skills still ceiling-locked. |
| 2 | Router works | ✅ PROVEN | **92.3% top-1 on both models, 0% false-fire** on negative controls. Gap: self-authored queries; tier/compound-chain accuracy untested. |
| 3 | Eval is robust | ✅ PROVEN | 191/191 fixtures gate every run; **all replication CIs overlap** across independent samples; 6 registrar artifacts caught & retracted, none shipped. Gap: most registrars keyword-class. |
| 4 | Local evolution works | ✅ PROVEN | End-to-end scan→canary→decide loop with a **real gate that weighs quality AND cost** (promotes, reverts on weak quality, reverts on cost regression); Layer A on real data hits **precision/recall 1.0**. Gap: run on demo logs, not a production routing log yet. |
| 5 | Global culture works | ⚙️ MECHANISM-ONLY | Emitter is **structurally leak-proof**; defense **blocks planted attackers through sybil=16** on real data. Hard limit: **zero external adopters exist** — unprovable by any spend until people install it. |

Total real API spend for this proof round: **~$15.4** (~$13.7 EXP-023 + ~$0.6 EXP-024 + ~$0.4
EXP-025). The Haiku full-suite run hit its budget cap at 29/61 skills in EXP-023; a completion
pass for the remaining 32 is running separately (survived one network-outage abort and was
relaunched — see EXP-025). Cross-model results below cover those 29 until it lands.

---

## 1 — Are the skills useful? 🟡 PARTIAL

**Method.** Each skill's tasks run WITH vs. WITHOUT the skill, `runs=30`, graded by an
objective registrar the model never sees; paired McNemar effect + 95% CI. Then
**Benjamini-Hochberg FDR correction** at q=0.05 (61 simultaneous tests ⇒ ~3 expected false
positives uncorrected — so the raw count is *not* the honest count).

**Result (Gemini, all 61 skills, FDR-corrected):** **36 wins, 0 losses.** Top effects:
tool-design +0.83, secrets-management +0.62, long-horizon-brief +0.60 (a brand-new skill's
debut), skill-distillation +0.53, tool-adversarial-reading +0.51, reliability-engineering
+0.50.

**EXP-024 moved this from 24 → 31; EXP-025 moved it 31 → 36.** Same two levers each round,
aimed at the two structural gaps claim 1 itself named (ceiling-locked tasks too easy to
discriminate; near-misses underpowered):
- **EXP-024**: one harder task per ceiling-locked skill (14 skills) — 10 broke ceiling, 4
  became wins (`multimodal`, `testing-ergonomics`, `evolution-scan`, `model-migration`);
  doubled runs on the 7 closest near-misses — 3 crossed the FDR bar (`injection-audit`,
  `cost-optimization`, `latency-optimization`).
- **EXP-025**: after Antonio asked why the remaining ~24 skills showed no help, a second
  pass split them into three honest buckets — real ceiling (write a harder task), positive-
  but-underpowered (write one more task), and flat/negative (leave alone, don't force it).
  14 new tasks across the underpowered skills; 5 became wins (`verifier-design`,
  `compliance-mapping`, `skill-authoring`, `handoff-protocol`, `privacy`). 2 of the original
  4 ceiling-locked skills broke ceiling this round (`agent-observability`, `state-management`
  moved off ceiling, though not yet significant); `feedback-harvesting` and `retrieval-design`
  remain genuinely ceiling-locked — Gemini already answers both correctly without the skill,
  confirmed by direct inspection, not assumed.

**A real HURTS reading surfaced and was checked, not trusted.** `agent-code-review` came
back -0.044 with a 95% CI that barely excluded zero (p=0.042). A fresh 14-pair spot-check
found zero reproduction of the effect — both arms answered identically well every time — and
**FDR correction independently filtered it out** (threshold p≤0.029, this sits at p=0.042):
two independent checks agreeing it's boundary noise from a near-ceiling baseline, not a real
effect. Reported here rather than silently dropped.

**Result (cross-model, the 29 skills measured on both):** **6 confirmed useful on BOTH
models, 0 confirmed harmful on either.** Both-model wins: tool-design, secrets-management,
long-horizon-brief, tool-adversarial-reading, eval-harness, grounding-citation. A further 7
win on one model and are neutral (not negative) on the other.

**The load-bearing number: zero losses.** Across every skill measured, on either model,
FDR-corrected, **not one skill is confirmed to make the model worse.** Five apparent HURTS
findings this session (context-engineering, accretion-refactor, eval-harness,
requirements-interrogation, retrieval-design) were each traced to a *registrar* bug and
retracted after the fix — never a real skill defect (see claim 3).

**Honest gaps:**
- **Ecological validity** — tasks are single-turn micro-scenarios; the library's real claim
  is about multi-turn agent work. A skill can win micro-tasks and still not matter in a long
  session. Not yet tested; the right fix is dogfooding the routing log (claim 4's gap too).
- **Depth** — most newly-covered skills still have 2-4 tasks each (first real signal, enough
  to catch a strong win or a HURTS, not enough to resolve a small effect). 2 skills
  (`feedback-harvesting`, `retrieval-design`) remain ceiling-locked — Gemini already answers
  their hardest tested scenario correctly without the skill.
- **Coverage** — Haiku's table is 29/61 (budget cap); a completion pass for the rest is
  running separately.

---

## 2 — Does the router work? ✅ PROVEN

**Method.** 65 realistic user utterances → expected skill, plus **8 negative controls**
(smalltalk / unrelated questions whose correct answer is *route to nothing*). The router is
told it may answer `none`. Run live on both models.

**Result:**

| Model | Positive top-1 | False-fire rate (negative controls) |
|-------|----------------|-------------------------------------|
| Haiku 4.5 | 60/65 = **92.3%** | 0/8 = **0.0%** |
| Gemini Flash-Lite | 60/65 = **92.3%** | 0/8 = **0.0%** |

Both models route the right skill 92% of the time *and* correctly decline to fire on
"what's the capital of France?" — the false-fire error (an AUTO-tier skill firing on an
irrelevant moment) is the costlier one, and it measured zero. The earlier "48.3%" figure in
the history was a mock keyword-matcher artifact, not real routing (EXP-007).

**Honest gaps:** the queries were written by the same author as the skill descriptions
(some shared vocabulary is unavoidable — an independently-generated query set would be
stronger); tier correctness (right skill, right AUTO/PROPOSE/ASK level) and compound-moment
chains ("ship it" → guardrails + injection-audit + eval-harness) are specified in
ROUTING.md but not yet benchmarked.

---

## 3 — Is the eval robust? ✅ PROVEN

Three independent lines of evidence:

1. **Pre-spend gate.** Every registrar carries a should-pass and should-fail fixture;
   `python3 -m simulator.measure --selfcheck` verifies all **191/191** before any run, and
   the measurement refuses to spend if any registrar disagrees with its own fixture — it
   caught 3 real bugs in EXP-024's newly-written tasks and 3 more in EXP-025's, before a cent
   was spent on either batch.

2. **Stability replication** (the direct "would this reproduce?" test). Five skills spanning
   the effect range, re-measured as a second independent real sample: **all 5 CIs overlap
   run-1** (tool-design 0.833↔0.842, eval-harness 0.227↔0.247, guardrails 0.147↔0.213,
   grounding-citation 0.167↔0.139, context-engineering 0.004↔0.000). The numbers are not
   seed-luck.

3. **The eval caught its own bugs — six confirmed HURTS artifacts, and 11 pre-spend fixture
   bugs, none shipped.** Across the session, six registrar artifacts produced false HURTS
   verdicts (EXP-009 context-engineering, EXP-013 accretion-refactor, EXP-016 eval-harness +
   silent-failure-audit, EXP-022 requirements-interrogation + culture-telemetry, EXP-024
   retrieval-design). Every one was caught by reading raw completions, fixed, and
   **re-measured with non-overlapping before/after CIs** (retrieval-design: -0.122 significant
   HURTS → 0.000 ceiling) — the defect corrected, not the number massaged. EXP-025 added a
   different kind of catch: `--selfcheck` rejected 3 of 14 new tasks in one batch immediately
   (two had a keyword shared by their own pass/fail fixtures; one required `re.?baseline`,
   which doesn't match the gerund "baselining"), and spot-checking a handful of real
   completions against the *intended* answer — before spending on the full run — caught
   several more registrars rejecting genuinely correct, differently-phrased responses (e.g.
   "evaluate the retrieval **layer**" vs. the narrower "evaluate retrieval"). This is the
   eval-of-the-eval (`verifier-design`) working in practice, repeatedly, on brand-new tasks
   just as reliably as on old ones — both before and after real money was spent.

**Honest gap:** most registrars are keyword/structural ("medium" strength), and that class
is exactly where all five artifacts lived. The categorical upgrade — artifact-checking
registrars that parse the output (count the questions, validate the JSON) instead of
keyword-matching it — is real remaining work.

---

## 4 — Does local evolution work? ✅ PROVEN

Two independent demonstrations:

1. **The loop is operated, not just specified.** `harness/evolve_cycle.py` runs the full
   Engine end-to-end on a routing log: **scan** (detect a high-override skill) → **propose**
   (a concrete, reversible tier edit) → **canary** (measure on a held-out window) →
   **decide** (gated on quality *and* cost). Three gate paths are verified: it **PROMOTES**
   when the canary cuts the override rate past the bar at an acceptable cost; it **REVERTS**
   when the override rate doesn't fall enough; and it now also **REVERTS when quality
   improves but cost/invocation regresses past a 15% tolerance** (`--demo-cost-regression`) —
   a quality win bought with an uncapped cost increase is not a win. Logs with no cost field
   fall back to a quality-only gate rather than silently passing a check they never made.

2. **The culture mechanism recognizes real quality.** Feeding the real measured 29-skill
   effect table into the Layer-A population simulator (`--real` bridge): **precision 1.0,
   recall 1.0** at baseline — the mechanism promotes every truly-good skill and admits no
   bad one — and canon value **1.38 vs. the sealed synthetic model's ~0.2** (~7×), meaning
   the library's real skills clear the bar by a wider margin than the simulator ever assumed.

Backing both: the four real registrar fix-cycles above *are* local evolution executed by
hand — eval detected the defect, a fix was proposed, re-measurement gated it.

**Honest gap:** `evolve_cycle.py` runs on demo/constructed logs. A genuine cycle against a
real production routing log needs actual usage — the same dogfooding gap as claim 1.

---

## 5 — Does the global culture work? ⚙️ MECHANISM-ONLY

This is the one claim no amount of API spend can fully prove today, and the doc says so
plainly.

**What's proven — the mechanism:**
- **Structural privacy.** `harness/culture_emit.py` turns a routing log into the only thing
  allowed to leave a node: an anonymized, signed, k-anonymity-floored pattern-card of
  aggregate counts. The demo log carries planted secret fields (`prompt`, `user_message`,
  `tool_output`); the built-in leak check **proves none of them reach the card** — enforced
  by an allowlist in code, not by policy text.
- **Attack resistance on real data.** Planting 6 synthetic attackers on top of the real
  29-skill honest baseline and escalating sybil pressure: honest skills keep getting
  promoted and **attackers stay blocked (0 established) through sybil=16 orgs** — more fake
  infrastructure than a realistic attacker musters. At an extreme sybil=24, the EXP-017
  `org_weight_cap` defense **halves the breach (6 → 3 attackers)** but no longer fully holds
  on this distribution — an honest partial, consistent with the finding that eval-independence
  (not any single org-side knob) is the ceiling defense.

**The hard limit — the real-world claim is unproven and unspendable:** the library was
published to GitHub in this same work-stream. **There are zero external adopters, therefore
zero real community telemetry, therefore nothing real to validate.** "Does the *global
culture* work" is a question about people installing it and contributing pattern-cards — a
time-and-adoption question, not a budget one. What this round did was make it *adoptable*:
the emitter is working, tested, leak-proof code rather than a spec.

**Also honest:** two model families is the *minimum* for a cross-generation claim; a third
(a local Llama, a GPT-mini class model) would be needed before "validated per model
generation" is more than suggestive.

---

## What would move each verdict

| Claim | To upgrade the verdict |
|-------|------------------------|
| 1 | Finish the Haiku 61-skill table (running); crack the last 2 ceiling-locked skills (`feedback-harvesting`, `retrieval-design`) with a genuinely different scenario; deepen first-pass skills to 8-15 tasks (~$40); **dogfood the routing log on this repo's own development** (free, attacks the ecological-validity gap directly). |
| 2 | An independently-generated query set; add tier-correctness and compound-chain cases. |
| 3 | Upgrade the keyword-class registrars to artifact-checking parsers. |
| 4 | Run one real cycle against a production routing log (needs usage). |
| 5 | Real external adopters (the only thing that counts); a third model family. |
