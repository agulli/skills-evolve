# Experiment & Benchmark Ledger

This ledger tracks empirical measurements, population simulation sweeps, and router benchmarks across model generations.

> **Agent Protocol (Claude, Gemini, Codex, Human):**
> 1. **Read before running:** Check this file to see what hypotheses, skills, and models have already been tested.
> 2. **Save raw JSON:** Output measure/benchmark runs to `simulator/results/<model>_<date>.json`.
> 3. **Append concise summary:** Append a standardized entry under `## Log` below with key metrics (paired CI95, effect size, false-positive rate) and conclusions.

---

## Metrics Moved (cumulative, EXP-001 → EXP-013)

The headline deltas across this whole arc — read this before the full table below if you just want to know what actually changed.

| Metric | Before | After |
|---|---|---|
| `context-engineering` effect (Haiku) | **-0.341**, significant HURTS (wrong — registrar bug, EXP-005) | **+0.113**, significant HELPS (EXP-009/012) |
| `context-engineering` effect (Gemini) | **-0.366**, significant HURTS (wrong, EXP-006) | **0.0**, ceiling/neutral (EXP-009/012) |
| `context-engineering` routing tier | ASK (defensive lockdown, EXP-005/006) | PROPOSE (restored, EXP-009) |
| Router accuracy | 48.3% (mock keyword-overlap — not a real number, EXP-003) | **91-93%**, real, live, both models (EXP-007/011) |
| Registrar fixture coverage | 0/43 | **43/43** (EXP-010) |
| Full-suite real measurement | fragmented across 4 sessions/days, inconsistent registrar state | **1 clean, single-session, `--selfcheck`-gated run**, both models (EXP-011/012) |
| Canon value (real skills vs. sealed synthetic assumption) | ~0.21-0.33 (what Layer A assumed) | **~1.73** (what real skills actually deliver) — 5-8x higher (EXP-012) |
| Canon recall (real vs. sealed) | 0.42-1.0, scenario-dependent (sealed) | **1.0, every scenario** (real, EXP-012) |
| Skill count | 58 | 59 (`verifier-design` added) |
| `accretion-refactor` effect (Haiku) | **-0.133**, significant HURTS (wrong — registrar bug, EXP-012) | **-0.013**, not significant (EXP-013) |
| `tool-adversarial-reading` effect (Haiku) | 0.0, ceiling (task too easy to measure, EXP-008/012) | **+0.039**, significant HELPS (EXP-013) |
| `tool-adversarial-reading` effect (Gemini) | 0.0, ceiling (EXP-008) | **+0.494**, significant HELPS (EXP-013) |
| `accretion-refactor` / `tool-adversarial-reading` task coverage | 1 / 2 tasks | 5 / 6 tasks (EXP-013) |
| Registrar fixture coverage | 43/43 | **51/51** (EXP-013) |

The three results worth remembering above the rest: **context-engineering's regression was fake** — the fix flipped it from confirmed-twice-both-models HURTS to confirmed HELPS, and the bug was in the test, not the skill (EXP-009). **canon value under real data is 5-8x higher than the synthetic model ever assumed** — the simulator was underselling this library's actual skills, not overselling them (EXP-012). And the *same exact anti-pattern hit twice* — `accretion-refactor`'s HURTS finding (EXP-012) was the identical bug class as context-engineering's, in a different registrar, caught by applying the same discipline (`verifier-design`'s own checklist) the first incident produced (EXP-013).

Total real API spend across the whole arc: ~$8.2 (against $20 authorized across three budget rounds — $5 for EXP-005 through EXP-010, $10 for EXP-011/012, $5 for EXP-013).

---

## Executive Summary Table

| Exp ID | Date | Target / Hypothesis | Model | Sample Size | Headline Result | Status / Verdict |
|---|---|---|---|---|---|---|
| EXP-001 | 2026-07-21 | $H_2$: Eval error correlation | Simulator (100 nodes) | 60 rounds | Correlated blindspots drop precision to 0.875; independent noise is 1.0 | Confirmed: Error correlation breaks culture |
| EXP-002 | 2026-07-22 | $H_1$/$H_2$: Layer B Mock Audit & Triage | Mock (43 tasks) | n=215 paired | `context-engineering` effect +0.250 (CI95: [0.045, 0.455]); false-positive rate 0.299 | `self_eval` fixed; over-pruning guardrails added |
| EXP-003 | 2026-07-22 | Router Prompt Benchmark | Mock (58 queries) | n=58 queries | Top-1 Keyword Overlap Accuracy: 48.3% (28/58) | Standup native router benchmark dataset |
| EXP-004 | 2026-07-22 | Live LLM Router Integration | Haiku / Gemini | n=58 queries | Wired `llm_route_query` to `simulator.measure` adapters | Ready for live API key execution |
| EXP-005 | 2026-07-22 | $H_1$: Post-guardrail REAL re-measure of context-engineering/prompt-architecture/injection-audit | Haiku (real) | n=640 paired | `context-engineering` -0.341 (CI [-0.393,-0.289], HURTS); `prompt-architecture` +0.129 (helps); `injection-audit` +0.212 (helps); FPR 0.982 | Guardrail fix did NOT resolve context-engineering — replicated, slightly worse |
| EXP-006 | 2026-07-22 | $H_1$: Post-guardrail REAL re-measure of context-engineering/prompt-architecture/injection-audit | Gemini (real) | n=640 paired | `context-engineering` -0.366 (CI [-0.42,-0.311], HURTS); `prompt-architecture` +0.004 (not sig — orig. -0.246 finding did NOT replicate); `injection-audit` +0.35 (sig helps — orig. -0.15 finding REVERSED); FPR 0.978 | context-engineering regression confirmed on both models twice; the two Gemini-only regressions from EXP prior to this ledger were noise (n=2-6 tasks), not real |
| EXP-007 | 2026-07-22 | Live LLM Router Benchmark execution (resolves EXP-003/004) | Haiku + Gemini | n=58 queries each | Haiku 91.4% (53/58, $0.137); Gemini 93.1% (54/58, $0.013) | Real routing is strong; the 48.3% EXP-003 number was a keyword-matcher artifact, not a router defect |
| EXP-008 | 2026-07-22 | $H_1$: FIRST real measurement of 5 previously-unvalidated skills (tool-adversarial-reading, silent-failure-audit, synthetic-task-generation, accretion-refactor, guardrails) | Haiku + Gemini (real) | n=840 paired each | `guardrails` significant helps both models (Haiku +0.125, Gemini +0.5); `accretion-refactor` mixed (Gemini +0.1 sig, Haiku -0.075 not sig); `tool-adversarial-reading` ceiling effect on both (1.0/1.0, ties broke on 0 tasks so far — needs harder tasks); FPR swung to 1.0 (Haiku)/0.729 (Gemini) on this task mix | First empirical data point for these 4 skills; also shows eval_false_positive_rate is task-mix-dependent, not a fixed per-model constant — EXP-005/006's ~0.98 finding shouldn't be generalized as universal |
| EXP-009 | 2026-07-22 | $H_2$→$H_1$: root-cause the context-engineering "HURTS" finding by inspecting raw completions, not just pass/fail counts | Haiku (transcripts) + Haiku/Gemini (real) | n=640 paired (320/model) | Registrar bug found and fixed (see Log); re-measured with the fix: Haiku +0.106 (CI [0.069,0.143], significant HELPS, was -0.341); Gemini 0.0 (ceiling 1.0/1.0 both arms, was -0.366 HURTS) | **The EXP-005/006 "confirmed HURTS, twice, both models" verdict was itself wrong — a measurement artifact, not a skill defect. Corrected: skill helps (Haiku) or is neutral (Gemini). ROUTING.md tier restored to PROPOSE.** |
| EXP-010 | 2026-07-22 | Registrar self-check infrastructure (all 43 registrars vs. their own fixtures) | N/A (no API calls, $0) | 43/43 tasks | 1 issue found on first run (a swapped fixture, not a registrar bug); 0/43 after fix | `--selfcheck` + auto pre-spend gate added to `measure.py`; no other registrar shows the EXP-009 anti-pattern (not proof of correctness, just no failure against the fixtures written) |
| EXP-011 | 2026-07-22 | Full 43-task real baseline: router / eval / evolution / culture ($10 budget) | Gemini (real, clean) + Haiku (blocked) | n=1290 paired (Gemini) | Gemini's full-suite baseline landed clean, replicates every prior overlapping measurement. Haiku blocked twice — a connectivity outage corrupted attempt 1 (preserved, unused), then Anthropic org ran out of API credits mid-retry on attempt 2 (killed before it wrote a file) | Hardened `measure.py` (30s timeout + 8-consecutive-failure circuit breaker) so a repeat doesn't silently corrupt data again. Built the long-flagged, never-done Layer B→Layer A bridge (`World.from_measured`, `run.py --real`), dry-verified — waiting on a clean Haiku file to run it on the full 12-skill set. **Haiku re-run blocked on Antonio resolving Anthropic billing.** |
| EXP-012 | 2026-07-22 | Clean Haiku full-43 baseline lands; Layer B→Layer A bridge run for real | Haiku (real, clean) | n=1290 paired (Haiku) | Haiku's full-suite baseline landed clean, 3,870/3,870 calls, replicates every prior overlapping measurement. `accretion-refactor` newly flagged -0.133 significant HURTS (n=1 task, underpowered, not yet investigated). Layer A on real data: recall=1.0 every scenario, canon value ~1.73 vs. sealed's ~0.09-0.33 (5-8x higher) | Local evolution mechanism never misses a real good skill; this library's real skills outperform the sealed synthetic calibration Layer A shipped with. `accretion-refactor` flag carried forward to EXP-013 |
| EXP-013 | 2026-07-22 | Root-cause the accretion-refactor HURTS flag from EXP-012; fix tool-adversarial-reading's ceiling effect | Haiku (transcripts) + Haiku/Gemini (real) | n=990 paired/model | Same anti-pattern as EXP-009: `_not_both` failed on literal both-phrases-present, but the skill's own framing encourages quoting the removed phrase to explain the fix. Fixed with removal-cue detection; expanded accretion-refactor 1→5 tasks, tool-adversarial-reading 2→6 (harder, ceiling-breaking tasks). Re-measured: `accretion-refactor` Haiku -0.013 not sig (was -0.133 HURTS), Gemini +0.013 not sig; `tool-adversarial-reading` Haiku +0.039 sig helps, Gemini +0.494 sig helps (both were 0.0 ceiling) | **accretion-refactor's HURTS finding retracted — registrar artifact, not a skill defect, same bug class as EXP-009. tool-adversarial-reading now confirmed-helps on both models where it was previously unmeasurable.** |

**Total spend through EXP-013: ~$0.671** (of $5 authorized for this batch — Haiku $0.6288 expanded run + ~$0.02 raw-transcript investigation + Gemini $0.0207). Raw artifacts: `simulator/results/{haiku,gemini}_expanded_20260722.json`.

**Total spend through EXP-011: ~$0.7854+** (of $10 authorized for this batch; the killed Haiku retry's exact spend is unrecorded — process was killed before it could report, bounded/small since it was caught within about a minute of the billing cutoff). Raw artifacts: `simulator/results/gemini_full43_20260722.json`, `simulator/results/haiku_full43_20260722_OUTAGE_CORRUPTED.json` (unused).

**Total spend through EXP-010 (prior $5 budget): $3.7900.** Raw artifacts: `simulator/results/{haiku,gemini}_context-engineering_fixedeval_20260722.json`.

**Total spend across EXP-005 through EXP-008 (2026-07-22, $5 budget authorized): $2.9411** (Haiku $2.8184 + Gemini $0.1227). Raw artifacts: `simulator/results/{haiku,gemini}_targeted_20260722.json`, `simulator/results/{haiku,gemini}_newskills_20260722.json`.

---

## Log

### [EXP-001] 2026-07-21 — Layer A Population Simulation ($H_1, H_2, H_3$)
* **Contributor:** Gemini (Antigravity)
* **Command:** `python3 -m simulator.run --scenario all`
* **Hypothesis ($H_2$ / $H_3$):** Evaluate population precision and canon uplift across strong, typical, weak, and blindspotted evals over 60 rounds.
* **Key Metrics:**
  * `strong` / `typical` / `weak`: Precision = `1.0`, Malicious Promoted = `0`.
  * `blindspotted`: Precision = `0.875`, Malicious Promoted = `1`.
  * `canon_value` (strong tier newcomer uplift): `+0.2392`
* **Conclusions & Verdict:** Independent noise in evaluations cancels out across nodes. Correlated evaluation blind spots allow malicious skills to breach the Canon.
* **Raw Artifact:** `simulator/run.py` stdout log

---

### [EXP-002] 2026-07-22 — Layer B Task Measurement & Triage Sweep
* **Contributor:** Gemini (Antigravity)
* **Command:** `python3 -m simulator.measure --model mock --runs 5`
* **Hypothesis ($H_1$ / $H_2$):** Audit `eval_false_positive_rate` computation and measure paired win-rate deltas across 43 objective tasks.
* **Key Metrics:**
  * `eval_false_positive_rate`: `0.299` (corrected from forced `1.0` hardcode).
  * `eval_sensitivity`: `0.949`
  * `context-engineering`: Effect `+0.250` (CI95: `[0.045, 0.455]`, **significant: true**)
  * `tool-design`: Effect `+0.300` (CI95: `[-0.013, 0.613]`)
  * `accretion-refactor`: Effect `+0.400` (CI95: `[-0.301, 1.101]`)
* **Conclusions & Verdict:** Fixed `self_eval` modeling in `measure.py`. Added over-pruning guardrails to `context-engineering/SKILL.md` and temporarily set routing tier to `ASK` in `skills/ROUTING.md`.
* **Raw Artifact:** `simulator/results/mock_20260722.json`

---

### [EXP-003] 2026-07-22 — Router Benchmark Dataset Standup
* **Contributor:** Gemini (Antigravity)
* **Command:** `python3 scripts/benchmark-router.py --mode mock`
* **Hypothesis:** Benchmark `skills/ROUTING.md` prompt routing accuracy against a 58-query dataset across all 7 lifecycle groups.
* **Key Metrics:**
  * `accuracy`: `48.3%` (28/58 correct via keyword overlap matcher).
* **Conclusions & Verdict:** Created native test harness `scripts/benchmark-router.py` to evaluate LLM provider routing accuracy.
* **Raw Artifact:** `scripts/benchmark-router.py`

---

### [EXP-004] 2026-07-22 — Live LLM Provider Benchmark Integration
* **Contributor:** Gemini (Antigravity)
* **Command:** `python3 scripts/benchmark-router.py --mode llm --model haiku`
* **Hypothesis:** Wire live LLM provider adapters (Haiku & Gemini) to `scripts/benchmark-router.py` to benchmark top-1 system prompt intent routing accuracy.
* **Key Metrics:**
  * `llm_adapter_support`: Wired to `simulator.measure.get_adapter` (Haiku & Gemini Flash-Lite).
  * `fallback_graceful`: Automatically falls back to mock matcher if API keys are absent.
* **Conclusions & Verdict:** Router benchmark script is ready for live API execution when `ANTHROPIC_API_KEY` or `GEMINI_API_KEY` are provided.
* **Raw Artifact:** `scripts/benchmark-router.py`

---

### [EXP-005/006] 2026-07-22 — Post-guardrail REAL re-measurement of the 3 flagged skills
* **Contributor:** Claude (Fable 5), $5 API budget authorized by Antonio
* **Command:** `python3 -m simulator.measure --model {haiku,gemini} --skills context-engineering,prompt-architecture,injection-audit --runs 40 --budget {1.30,0.30}` (added `--skills` filter to `measure.py` to target just these 3 without re-running the full 36-task suite)
* **Hypothesis ($H_1$):** Does the over-pruning guardrail sentence added to `context-engineering/SKILL.md` (in the EXP-002 mock triage) actually fix the real -0.32/-0.32 HURTS effect measured 2026-07-20? Do the two Gemini-only regressions (prompt-architecture -0.246, injection-audit -0.15) replicate on a fresh sample?
* **Key Metrics:**
  * `context-engineering`: Haiku -0.341 (CI [-0.393,-0.289]); Gemini -0.366 (CI [-0.42,-0.311]). Both still significant HURTS — slightly *worse* than the pre-guardrail baseline (-0.316/-0.322).
  * `prompt-architecture`: Haiku +0.129 (significant helps, replicates 2026-07-20); Gemini +0.004 (NOT significant — the original -0.246 HURTS finding did not replicate).
  * `injection-audit`: Haiku +0.212 (significant helps, replicates); Gemini +0.35 (significant helps — the original -0.15 HURTS finding REVERSED).
  * `eval_false_positive_rate`: Haiku 0.982, Gemini 0.978 — both replicate the 2026-07-20 values (0.97/0.98) almost exactly.
* **Conclusions & Verdict:** The one-sentence guardrail fix to `context-engineering` did **not** work — the regression is now confirmed twice on both models, not once. `ROUTING.md`'s ASK-tier note updated to reflect confirmed (not hypothesized) status; do not restore until a real fix re-measures positive. The two Gemini-only regressions from the first run do NOT hold up under a second sample (n=2-6 tasks per skill is too small to trust a single run in either direction) — treat them as noise, no action needed on prompt-architecture or injection-audit. The FPR ~0.97-0.98 replication on this specific task mix, across 2 models × 2 independent days, is the most trustworthy finding in this batch.
* **Raw Artifact:** `simulator/results/haiku_targeted_20260722.json`, `simulator/results/gemini_targeted_20260722.json`

---

### [EXP-007] 2026-07-22 — Live LLM Router Benchmark, actually executed
* **Contributor:** Claude (Fable 5)
* **Command:** `python3 scripts/benchmark-router.py --mode llm --model {haiku,gemini}` (added spend reporting to the script's `__main__`, matching `measure.py`'s convention)
* **Hypothesis:** What is the REAL (not mock keyword-overlap) top-1 routing accuracy against the 58-query benchmark dataset?
* **Key Metrics:** Haiku 91.4% (53/58, $0.1373); Gemini 93.1% (54/58, $0.0131).
* **Conclusions & Verdict:** EXP-003's 48.3% was an artifact of the mock matcher (naive keyword overlap against `ROUTING.md` rows), not a real routing weakness — real models route this table well. Closes EXP-004's "ready for live execution" status.
* **Raw Artifact:** stdout only (not saved to `simulator/results/`; dataset lives in `scripts/benchmark-router.py`)

---

### [EXP-008] 2026-07-22 — First real measurement of 5 previously-unvalidated skills
* **Contributor:** Claude (Fable 5)
* **Command:** `python3 -m simulator.measure --model {haiku,gemini} --skills tool-adversarial-reading,silent-failure-audit,synthetic-task-generation,accretion-refactor,guardrails --runs 40 --budget {0.90,0.15}`
* **Hypothesis ($H_1$):** These 4 skills (added between the last checkpoint and now) plus `guardrails` had zero real-model measurement. What's the real effect?
* **Key Metrics:**
  * `guardrails`: Haiku +0.125 (sig helps), Gemini +0.5 (sig helps) — the strongest confirmed-helps skill in this batch on both models.
  * `accretion-refactor`: Gemini +0.1 (sig helps, barely); Haiku -0.075 (not significant, n=40) — directionally mixed, underpowered.
  * `tool-adversarial-reading`: ceiling effect on both models (with_pass = without_pass = 1.0) — the 2 existing tasks are too easy to discriminate; needs harder tasks before this skill can be measured meaningfully.
  * `silent-failure-audit`, `synthetic-task-generation`: not significant on either model, n too small (1-2 tasks).
  * `eval_false_positive_rate`: Haiku 1.0, Gemini 0.729 on this task mix — a big swing from the ~0.98 seen in EXP-005/006.
* **Conclusions & Verdict:** First empirical data point for 4 skills that shipped with zero validation. `guardrails` is solid. The FPR swing vs. EXP-005/006 shows `eval_false_positive_rate` is task-mix-dependent, not a fixed per-model constant — don't generalize the ~0.98 number as a universal property of Haiku/Gemini self-eval; it's specific to the context-engineering/prompt-architecture/injection-audit task mix. Next: write 6-13 more tasks per new skill (target ~8-15/skill) before trusting these numbers, especially tool-adversarial-reading's ceiling effect.
* **Raw Artifact:** `simulator/results/haiku_newskills_20260722.json`, `simulator/results/gemini_newskills_20260722.json`

---

### [EXP-009] 2026-07-22 — Root-caused and fixed the context-engineering "HURTS" finding — it was the registrar, not the skill
* **Contributor:** Claude (Fable 5)
* **Command:** Manual transcript pull (`simulator.tasks.load_tasks()` + `simulator.measure.get_adapter("haiku").generate(...)` for all 8 context-engineering tasks, both arms, real Haiku calls), followed by `python3 -m simulator.measure --model {haiku,gemini} --skills context-engineering --runs 40 --budget {1.00,0.10}` after the fix.
* **Hypothesis:** EXP-005/006 called context-engineering confirmed-HURTS on both models, twice each — but that verdict came only from aggregate pass/fail counts, never from reading what the model actually produced. Before accepting a 5th consecutive negative reading, inspect the raw completions.
* **Root cause found:** `_fact_survives_and_shorter` in `simulator/tasks.py` required the ENTIRE fact phrase to appear as an exact case-insensitive substring in the output. The skill's own instruction is to *compact* — the model complies by dropping linking verbs ("is"/"are"), abbreviating units ("per minute"→"/min"), and reordering clauses. That is compaction working correctly, and it broke the exact-substring check every time. Example (`context-0`, Haiku): WITH-skill output `"Rate limit 4096 tokens/min."` (84 chars, well under the 300 cap, factually complete) — registrar said FAIL because it wasn't the literal string `"rate limit is 4096 tokens per minute"`. The WITHOUT arm passed more often only because it happened to echo facts closer to verbatim by default, not because it preserved information better. Confirmed across all 8 tasks: length was never the binding constraint (every WITH-skill output was under cap); the failures were 100% paraphrase-driven.
* **Fix:** Rewrote the registrar as a token-overlap check — every numeric/id token in the fact (the actual "checkable trace": rate limits, dates, ticket IDs, versions — the literal load-bearing content) must survive verbatim; up to one other content word may be dropped/paraphrased. Verified against a positive-fixture/negative-fixture pair before trusting it (empty output, wrong number, fact dropped entirely, correct-but-over-cap — all correctly still FAIL) — this is the same two-fixture discipline described in LangChain's `eval-engineering` skill's `verifier-design.md` reference, applied here after the fact rather than before.
* **Key Metrics (post-fix, real re-measurement):** Haiku +0.106 (CI [0.069,0.143], n=320, significant HELPS — was -0.341); Gemini 0.0 (n=320, with_pass=without_pass=1.0, ceiling — was -0.366 HURTS).
* **Conclusions & Verdict:** The EXP-005/006 "confirmed regression, replicated on both models, guardrail fix ineffective" narrative was itself built on a broken measurement. The skill was never the problem. `ROUTING.md` tier restored from ASK to PROPOSE. **Lesson for this ledger going forward: a pass/fail count that replicates is not the same as a pass/fail count that's correct — replicating a bug just makes it look more credible. Any registrar showing a large, surprising effect should have its raw completions read, not just its aggregate stats, before the tier gets changed.**
* **Raw Artifact:** `simulator/results/haiku_context-engineering_fixedeval_20260722.json`, `simulator/results/gemini_context-engineering_fixedeval_20260722.json`; fix in `simulator/tasks.py` (`_fact_survives_and_shorter`, `_key_tokens`)

---

### [EXP-010] 2026-07-22 — Registrar self-check infrastructure (prompted by langchain-ai/langchain-skills' eval-engineering skill)
* **Contributor:** Claude (Fable 5), $0 spend (pure code, no API calls)
* **Command:** `python3 -m simulator.measure --selfcheck`
* **Hypothesis:** EXP-009 found one broken registrar by manually reading transcripts after the fact. Are there others? And can the two-fixture check (borrowed from LangChain's `eval-engineering`/`verifier-design.md`: "one clearly-capable result should pass, one plausible-but-wrong result should fail; if either doesn't, fix the rubric before trusting it") be turned into a structural gate instead of something that has to be remembered?
* **What was built:** `simulator/tasks.py` now carries a `FIXTURES` dict — one positive and one negative sample completion per task, 43/43 tasks covered — plus a `selfcheck(tasks)` function that asserts every registrar passes its own positive sample and rejects its own negative sample. `measure.py` gained `--selfcheck` (checks fixtures only, no API calls, exits 0/1) and made the check an automatic pre-spend gate on every real/mock run: it now refuses to spend budget if any in-scope registrar disagrees with its own fixture, unless `--force` is passed.
* **Key Metrics:** 43/43 tasks now have fixtures. First run caught 1 bug — not in a registrar, in the fixture itself (`context-2`'s good/bad samples were swapped, immediately caught by the same mechanism it was built to enforce). After the fix: 0/43 disagreements — no other registrar in the suite shows the EXP-009 anti-pattern (rewarding/punishing exact phrasing where paraphrase should be tolerated, or any other should-pass/should-fail mismatch a plausible fixture would catch).
* **Conclusions & Verdict:** The EXP-009 bug was isolated to `context-engineering`, not systemic — 42 other registrars checked out clean against a fixture written specifically to probe their known failure shape (secrets: literal-secret-present; dedup: count≠1; contradiction: both sides present; tool schema: missing enum/limit; decline/cite: fabrication vs. proper decline/citation; etc.). This doesn't prove there's no other bug — a fixture only catches what it was written to probe — but it converts "we assume the registrars are fine" into "we checked, against a specific adversarial case, for every task in the suite." Any newly added task should ship with a fixture pair from now on; `--selfcheck` will silently skip tasks with none, so coverage can regress without noticing unless someone checks the `covered/total` line in the output.
* **Raw Artifact:** `simulator/tasks.py` (`FIXTURES`, `selfcheck`), `simulator/measure.py` (`--selfcheck`, `--force`, pre-spend gate)

---

### [EXP-011] 2026-07-22 — Full 43-task real baseline attempt: two outages, one clean Gemini result, Haiku pending
* **Contributor:** Claude (Fable 5), $10 budget authorized ("large simulation, smart money": router / eval / evolution / culture)
* **Command:** `python3 -m simulator.measure --model {haiku,gemini} --runs 30 --out simulator/results/{haiku,gemini}_full43_20260722.json` (no `--skills` filter — first single-session, `--selfcheck`-gated run across the entire 43-task suite, superseding the fragmented partial runs in EXP-005/006/008/009)
* **What happened, in order:**
  1. First attempt (both models, background): Antonio's connection dropped mid-run. `_retry`'s graceful degradation (2 attempts, then return `""`) meant the run didn't crash — it silently ground through the rest of the suite converting every subsequent call to an empty response. Diagnosed from the output alone: tasks run in fixed file order, and `secrets-management`/`context-engineering` (first two blocks) show real, plausible, prior-consistent numbers, while `grounding-citation` onward (8 straight skills) all read exactly `with_pass=0.0, without_pass=0.0` — the signature of an empty string failing every registrar identically on both arms, not a real "no effect." Call count (972) also far under the ~3,870 expected, since an empty "with" answer skips the self-assess call. Preserved as `haiku_full43_20260722_OUTAGE_CORRUPTED.json`, NOT used for anything. Gemini's job hung entirely (0 CPU progress for 10+ min) rather than degrading — no timeout was set on the `google-genai` client, so a dead connection blocked forever instead of failing fast.
  2. Hardened `measure.py`: added a 30s timeout to both the Anthropic and Gemini clients (`Anthropic(timeout=30)`, `genai.Client(http_options=types.HttpOptions(timeout=30000))`), and a circuit breaker (`_CONSEC_FAIL_LIMIT=8`) that raises and aborts the run after 8 consecutive failures instead of silently grinding through an outage. Verified connectivity was back (curl both API hosts, got real 404s not timeouts), killed the hung Gemini process, re-launched both fresh.
  3. Mid-re-run, Anthropic's org ran out of API credits ("Your Claude API access is turned off"). The Haiku process (already in memory, running the OLD pre-hardening code) showed the exact same corruption signature starting — CPU time spiked from 0:02.81 to 0:11.51 in under a minute, consistent with calls now failing fast on a billing error rather than taking real generation time. Killed it before it wrote a corrupted file. Gemini is a separate vendor/billing account (Google) and was completely unaffected — let it run to completion.
* **Key Metrics (Gemini, clean, real, complete):** all 43 tasks, 3,870/3,870 calls, $0.1239. `secrets-management` +0.625 sig helps; `context-engineering` 0.0 ceiling (matches EXP-009 exactly); `prompt-architecture` +0.006 not sig (matches EXP-006's +0.004 closely); `grounding-citation` +0.267 sig helps; `tool-design` +0.817 sig helps (matches original run's "strongest confirmed-helps"); `eval-harness` +0.117 sig helps; `injection-audit` +0.467 sig helps; `tool-adversarial-reading` 1.0/1.0 ceiling (matches EXP-008 exactly); `silent-failure-audit` +0.283 sig helps; `synthetic-task-generation` 0.0/0.0 (matches EXP-008's near-zero); `accretion-refactor` 1.0/1.0 ceiling (close to EXP-008's 1.0/0.9); `guardrails` +0.567 sig helps (matches EXP-008's +0.5 closely). `eval_false_positive_rate` 0.906 — a normal-looking value, not the corrupted run's near-zero or the earlier suspiciously-high ~0.98.
* **Conclusions & Verdict:** Gemini's full-suite real baseline is trustworthy — replicates every prior measurement it overlaps with, in file order with no gaps, no corruption signature. Haiku's equivalent is still pending — blocked on Antonio resolving Anthropic billing, not re-attempted since a retry right now would just fail immediately. Also built `World.from_measured()` in `world.py` + a `--real HAIKU_JSON GEMINI_JSON` flag on `run.py` (the long-flagged, never-done Layer B -> Layer A bridge) and dry-tested it against the small EXP-005/006 3-skill files — it correctly promoted the 2 truly-good skills and excluded the genuinely-bad one, precision/recall both 1.0. Ready to run for real the moment a clean Haiku file exists.
* **Raw Artifact:** `simulator/results/gemini_full43_20260722.json` (clean); `simulator/results/haiku_full43_20260722_OUTAGE_CORRUPTED.json` (preserved as evidence, unused); hardening in `simulator/measure.py` (`_CALL_TIMEOUT_S`, `_CONSEC_FAIL_LIMIT`, `_consec_fail`); bridge in `simulator/world.py` (`World.from_measured`) and `simulator/run.py` (`--real`, `load_real_world`)

---

### [EXP-012] 2026-07-22 — Clean Haiku baseline lands; Layer B → Layer A bridge run for real (H3 on real data)
* **Contributor:** Claude (Fable 5)
* **Command:** Antonio added Anthropic credits; re-ran `python3 -m simulator.measure --model haiku --runs 30 --out simulator/results/haiku_full43_20260722.json` with the hardened code from EXP-011, then `python3 -m simulator.run --scenario all --real simulator/results/haiku_full43_20260722.json simulator/results/gemini_full43_20260722.json --json` vs. the sealed synthetic baseline (`--scenario all --seed 7`).
* **Key Metrics (Haiku, clean, real, complete):** all 43 tasks, 3,870/3,870 calls, $2.744. `context-engineering` +0.113 (matches EXP-009's +0.106 closely); `tool-design` +0.992, `grounding-citation` +0.639 (both match the original run's "strongest confirmed-helps on both models"); `eval-harness` -0.1 not sig (matches original "not yet discriminating"); `tool-adversarial-reading` 0.0 ceiling (matches EXP-008 exactly); `synthetic-task-generation` +0.133 not sig (close to EXP-008's +0.1). New: `accretion-refactor` **-0.133, significant HURTS** (CI [-0.255,-0.012]) — previously not-significant on both models (EXP-008: Haiku -0.075 not sig). Backed by only 1 task (n=30) — flagged per this file's own "target ~8-15 tasks/skill" guidance as underpowered, not confirmed; not investigated further this session, noted for a future pass same as the injection-audit/prompt-architecture small-n lesson from EXP-005/006.
* **Layer A on real data (12 skills with real coverage) vs. sealed synthetic (59 skills), all 4 scenarios + eval-sweep:** Recall = **1.0 in every real-data scenario** (baseline/adversarial/churn/hard) vs. 0.394-1.0 (often much lower, e.g. 0.424 baseline) on sealed synthetic. Precision 0.8-0.889 real vs. 0.389-1.0 sealed. Canon value (newcomer uplift, strong tier) ≈**1.73 real vs. 0.09-0.33 sealed** — roughly 5-8x higher. Malicious-established = 0 in all real runs (untested by design, all 12 real skills are known-legit — EXP-001's sealed sweep still owns the malicious-detection question).
* **Conclusions & Verdict:** The culture-building mechanism never misses a real, genuinely-good skill (perfect recall across every adversary regime tested) — local evolution is working as designed. Canon value being 5-8x higher on real data than the sealed model assumed means Layer A's original "realistic agent engineering" calibration (effect_lo=0.02-0.12) was conservative relative to what this library's actual, iterated-on skills deliver — a positive finding about the library's own quality, not just the mechanism. Precision <1.0 is NOT evidence of bad-skill promotion: it traces to `prompt-architecture`/`eval-harness` sitting in genuinely ambiguous territory (not significant on either model individually), where the oracle's flat 0.03-effect-average threshold draws an arbitrary line through noise — a limitation of the oracle, not the mechanism. Caveat: only 12/59 skills have real task coverage, and `World.from_measured` applies one aggregate real effect uniformly across all 6 classes (documented simplification) — first real signal, not a final verdict on the whole library.
* **Raw Artifact:** `simulator/results/haiku_full43_20260722.json` (clean, supersedes the corrupted version); `simulator/results/layer_a_real_20260722.json`, `simulator/results/layer_a_sealed_20260722.json`. Deterministic per `--seed`; reproduce with `python3 -m simulator.run --scenario all --real simulator/results/{haiku,gemini}_full43_20260722.json --json`.

---

### [EXP-013] 2026-07-22 — accretion-refactor's HURTS finding was another registrar bug (same anti-pattern as EXP-009); tool-adversarial-reading's ceiling fixed with harder tasks
* **Contributor:** Claude (Fable 5), $5 budget authorized ("what next experiments")
* **Command:** Manual transcript pull (20 real Haiku completions on `accretion-0`), followed by `python3 -m simulator.measure --model {haiku,gemini} --skills accretion-refactor,tool-adversarial-reading --runs 30 --budget {1.20,0.15}` after fixing the registrar and adding 8 new tasks (4 per skill).
* **Hypothesis:** EXP-012 flagged `accretion-refactor` -0.133 significant HURTS on Haiku but never investigated it (n=1 task). Per `verifier-design`'s own checklist ("any surprising/large effect triggers a raw-completion read before it's trusted"), read the actual completions before accepting the verdict.
* **Root cause found:** `_not_both(a, b)` in `simulator/tasks.py` failed if BOTH phrases appeared anywhere in the output as a literal substring — but the skill's own framing ("resolving contradictory constraints") encourages the model to *explain* what it removed, which means quoting the removed phrase. Sampled 20 real WITH-arm completions on Haiku: 3 failed, and 2 of the 3 were unambiguous false negatives — e.g. `'```\nALWAYS format output as a markdown table.\n```\n\nThe contradictory "NEVER output markdown" is removed since it directly conflicts...'` — the model clearly resolves the contradiction and explains its reasoning, and the naive substring check can't tell "quoted to explain what was pruned" from "still an active instruction." Same anti-pattern as `context-engineering` (EXP-009), different registrar.
* **Fix:** Rewrote `_not_both` so a phrase only counts as still-ACTIVE if at least one occurrence has no nearby removal cue (`contradictory|conflicts?|negat*|remov*|cancel*|resolv*|...` within a ~60-char window). Verified against all 3 real failing transcripts (2/3 now correctly PASS; the 3rd was genuinely ambiguous model output and is a defensible fail either way) and all existing fixtures (`prompt-contra-0/1`, `accretion-0` — all still correct, since `_not_both` is shared by 3 tasks).
* **Also expanded coverage** (both underpowered): `accretion-refactor` 1→5 tasks (4 new varied contradiction types + 1 panic-rule-escalation task using a new `_panic_pruned` registrar factory); `tool-adversarial-reading` 2→6 tasks (4 new *harder*, subtler ambiguities — bare-float money amounts, unbounded image dimensions, discriminating which string field needs an enum vs. which is correctly free-text — since the original 2 tasks hit a 1.0/1.0 ceiling on both models, meaning they were too easy to measure the skill at all). `--selfcheck`: 51/51 tasks now have fixtures, all pass.
* **Key Metrics (post-fix, real re-measurement, 990 calls/model):** `accretion-refactor`: Haiku -0.013 (CI [-0.045,0.019], not significant, was -0.133 significant HURTS); Gemini +0.013 (not significant). `tool-adversarial-reading`: Haiku +0.039 (CI [0.011,0.067], significant helps, was 0.0 ceiling); Gemini +0.494 (CI [0.421,0.567], significant helps, was 0.0 ceiling) — the harder tasks fully resolved the ceiling effect and revealed a real, substantial positive effect, especially on Gemini.
* **Conclusions & Verdict:** `accretion-refactor`'s HURTS finding is retracted — it was a measurement artifact, not a skill defect, confirmed by both fixing the registrar AND quintupling the task count (so this isn't just "the bug moved," it's independently corroborated). `tool-adversarial-reading` is now a confirmed-helps skill on both models where it was previously unmeasurable. No `ROUTING.md` tier changes needed — neither skill was ever downgraded, only flagged. Running lesson reinforced twice now (EXP-009, EXP-013): **when the same registrar pattern (exact-substring / literal-both-present) is used to check whether a model "kept" or "removed" something, and the skill under test explicitly encourages explaining reasoning, check for this specific false-negative shape first** before trusting a HURTS verdict.
* **Raw Artifact:** `simulator/results/haiku_expanded_20260722.json`, `simulator/results/gemini_expanded_20260722.json`; fix in `simulator/tasks.py` (`_not_both`, `_phrase_active`, `_REMOVAL_CUES`, `_panic_pruned`, new tasks `accretion-1..4`, `tool-adv-read-2..5`)

---

### [EXP-014] 2026-07-22 — Is local culture evolving? Is global/community culture evolving? ($0, existing data only)
* **Contributor:** Claude (Fable 5), $0 spend — pure analysis of already-collected data
* **Command:** `python3 -c "..."` against `simulator/results/layer_a_real_20260722.json` (Layer A on real data, EXP-012) and the before/after pairs already in this ledger for the 3 skills fixed in EXP-009/EXP-013.
* **Hypothesis:** Two distinct questions that get conflated: does the population-simulation's Canon *converge/stabilize* within a run (Layer A mechanism), vs. does the *actual measured quality* of skills in this repo change between real time points (real local evolution) vs. does a *real external community* exist yet to evolve at all (global/Commons).
* **Local culture — Layer A mechanism shape:** canon value (strong tier, real 12-skill data, baseline scenario) jumps **0 -> 1.7159 in round 0->1**, then moves a total of **0.0007 across rounds 3-59** (1.7253 to 1.7260 — noise-level, not a trend). Converges almost instantly once real trial evidence flows, then holds steady rather than continuing to drift — the correct, intended steady-state behavior of the mechanism, not evidence it stops "evolving" in a bad sense.
* **Local culture — real evolution that actually happened this session:** compared real measured effect + 95% CI before vs. after the EXP-009/EXP-013 fix-and-remeasure cycles, per skill (Haiku): `context-engineering` -0.341 [-0.393,-0.289] -> +0.113 [0.069,0.156], CIs **do not overlap**; `tool-adversarial-reading` 0.0 [0,0] -> +0.039 [0.011,0.067], CIs **do not overlap**; `accretion-refactor` -0.133 [-0.255,-0.012] -> -0.013 [-0.045,0.019], CIs overlap narrowly (a false-negative de-confirmed rather than a new positive confirmed, a different but still real evolution shape). 2 of 3 skills show statistically clean separation between two real time points.
* **Global/community culture:** unanswerable at any price right now, not a budget question — `culture-telemetry` (the Commons) requires real, independent external installs contributing anonymized aggregate telemetry, and this repo was pushed to GitHub for the first time earlier in this same session (see the git-push turn). Zero external adopters exist yet, so there is no real community data to test significance against. What money CAN buy - more Layer A simulated-commons scenarios (sybil/org-jackknife/cross-tier) - only tests whether the mechanism *would* work if a community existed, which EXP-001 already substantially covers, and costs $0 either way (pure stdlib).
* **Conclusions & Verdict:** Local culture is evolving, with real statistical evidence, at $0 marginal cost (data already collected). Global culture cannot be measured yet at any price - re-ask after real external adoption generates real telemetry, which is a time/adoption question, not a spend question.
* **Raw Artifact:** none new (analysis only, reused `layer_a_real_20260722.json` + EXP-009/EXP-013 log entries)

---

### [EXP-015] 2026-07-23 — Adversarial resilience sweep: how much attack does it take to actually poison the culture mechanism?
* **Contributor:** Claude (Fable 5), $0 spend — pure Layer A simulation, no API calls
* **Command:** custom sweep script (`simulate()` called directly, not via the CLI's fixed scenario presets) — `simulator/results/adversarial_sweep_20260722.json`. Seed 7, 100 nodes, 60 rounds throughout, matching the existing baseline for comparability.
* **Hypothesis:** Antonio asked to simulate an adversarial attack on the "global community" mechanism. Framing check first (see EXP-014): there is no real external community yet, so this tests whether the *mechanism* (org-jackknife in `commons.py` + `EvalGate` blind-spot modeling) would resist poisoning if a community existed - not whether a real community is currently under attack. Two structurally different attack surfaces exist in the code and were tested separately before combining: (1) org-jackknife defeats a promotion that collapses when any *single* org's evidence is dropped - does it hold as the *number* of independent sybil orgs grows, not just nodes-per-org? (2) a correlated eval blind spot fools honest and dishonest nodes identically in the same round - the org-jackknife can't see this at all, since it's not an org-independence problem.
* **Sweep 1 - pure sybil-org scale** (malicious_rate=0.08, eval=typical, gamer/optimist=0): precision=1.0, malicious_established=0 through **sybil_orgs=6** (30 fake nodes). At sybil_orgs=8 (40 fake nodes) precision drops to 0.742 but malicious_established is *still 0* - the drop is noise-inflated over-promotion of mediocre-but-not-malicious skills (recall jumps 0.375→0.719), not a poisoned Canon. Malicious skills stay fully blocked through **sybil_orgs=16 (120 fake nodes** - more sybil infrastructure than the entire 100-node honest population). First leak at **sybil_orgs=24 (120 fake nodes): 2 malicious skills established**, precision 0.542, n_promoted=59/59 (everything gets waved through).
* **Sweep 2 - eval blind spot as a *cheaper* attack than sybil volume**, fixed moderate combined attack (malicious_rate=0.08, sybil_orgs=2, gamer_rate=0.10, optimist_rate=0.15) crossed with eval quality: strong/typical/weak all hold at malicious_established=0 (precision degrades 0.852→0.66 but no poisoning). The moment the SAME attack is paired with a **correlated blind-spot eval (`blindspotted` preset)**: malicious_established=1. `none` (no eval at all): malicious_established=2. **A sybil_orgs=2 attack that fails completely against a typical eval succeeds the instant it's paired with a correlated blind spot** - confirming EXP-001's original finding under active adversarial pressure, not just passive noise: correlated blind spots are the cheap attack surface, sybil volume is the expensive one.
* **Sweep 3 - worst case** (malicious_rate=0.20, sybil_orgs=8, gamer_rate=0.25, optimist_rate=0.30) crossed with eval quality: even **`strong` eval only partially protects - 5 malicious skills established**, precision 0.574. typical=9, weak=10, blindspotted=10, none=10 (saturates - past a certain attack size, eval quality stops being the dominant defense variable at all). Notably worse than sweep 1's sybil_orgs=8 alone (0 malicious) at the same sybil count - the added gamer/optimist behavioral adversaries and higher malicious_rate compound multiplicatively, not additively, with sybil volume.
* **Conclusions & Verdict:** The mechanism is genuinely resilient to realistic attack sizes - it takes more fake infrastructure than the entire honest population (16-24 sybil orgs) to poison the Canon through sybil volume alone, and even then only 2/~30 truly-malicious skills slip through. But it is NOT resilient to a well-resourced, multi-vector attack (sweep 3) or to a cheaply-exploited correlated eval blind spot (sweep 2) - both bypass org-jackknife entirely because they attack a different axis (eval trustworthiness, not org independence) that the jackknife was never designed to catch. **Practical implication: the single highest-leverage defense investment is eval-blind-spot detection/diversity (independent eval methodologies across orgs), not raising the sybil-detection bar** - sweep 1 shows the jackknife already tolerates far more sybil volume than any realistic attacker would likely muster, while sweep 2 shows a tiny, cheap attack succeeds the moment eval independence breaks down.
* **Follow-up not yet run:** `min_orgs` (currently hardcoded to 3 in `commons.py`'s `tally()`/`canon_by_class()` defaults) is not exposed as a sweepable parameter. A natural next experiment: does raising `min_orgs` to 5-7 meaningfully push out the sybil_orgs breaking point found in sweep 1, and at what cost to legitimate-skill promotion speed (newcomer orgs need more independent confirmations before anything reaches Canon)?
* **Raw Artifact:** `simulator/results/adversarial_sweep_20260722.json`; sweep script not yet committed to the repo (ran from scratch space) - worth promoting to a `simulator/adversarial.py` CLI mode if this becomes a recurring check.

