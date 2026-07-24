---
name: eval-harness
description: Build an evaluation harness for an agent — task set, graders, baselines, and a runnable pass/fail gate. Use when an agent has no evals, before a model/prompt change ships, or when "it seems better" needs to become a number.
---

# Agent Eval Harness

An agent without evals is tuned by anecdote. The harness turns "seems better" into a number you can gate releases on: tasks × graders × baseline.

## When to use
- An agent is heading to production with no eval suite.
- Before changing model, prompt, or tools on an agent that already works.
- Someone says "the new version feels better" and money depends on it.

## When NOT to use
- Diagnosing *why* a specific run failed (use `trajectory-review`).
- Designing the grader model itself in depth (use `llm-judge`).

## Procedure

1. **Collect tasks from reality, not imagination.** Pull 20–50 tasks from real usage: logs, support tickets, the team's own prompts. Split: ~60% common cases, ~25% known-hard cases, ~15% regression cases (every past incident becomes a task forever). Synthetic tasks only to fill coverage gaps, and label them as synthetic.

2. **Define per-task success criteria before running anything.** Each task gets: input, any required fixtures/state, and an explicit outcome check. Prefer checks in this order — exact/programmatic (file exists, test passes, API state correct) → rubric-scored by LLM judge → human review. If you can't state the success criterion, the task isn't ready. And when both kinds apply, deterministic checks are **gates, not score components**: a schema-invalid or structurally-broken artifact fails outright and never reaches the judge — otherwise an invalid output gets laundered by a favorable LLM score into a passing composite.

3. **Grade outcomes, not transcripts.** For agents, assert on end state (did the ticket get the right label? does the code pass the hidden tests?), not on whether the agent took your favorite path. Add trajectory assertions only for hard constraints (never called tool X, stayed under N turns, under $Y cost).

4. **Define Negative Constraints (The "Do Not Do X" Test).** In addition to success criteria, define explicit negative tests to prevent catastrophic success (e.g., solved the bug by deleting the database). Every task must assert that boundaries were not violated.

5. **Run with statistical honesty:** N≥3 runs per task (agents are nondeterministic); report pass@1 and variance, not the best run; fix temperature/seed where the stack allows; pin model versions in results. **When comparing two conditions on the SAME task set** (skill vs. no-skill, prompt v1 vs. v2, model A vs. B), use a **paired** test on the per-task outcome pairs — never diff two independent pass rates. For binary pass/fail, that means McNemar's test: only the discordant pairs (A passed/B failed, or vice versa) carry signal, so compute the effect and its CI from those, not from the raw pass-rate delta. Treating paired arms as independent samples silently loses power at low N and can report "not significant" on a real effect, or the reverse.

6. **Baseline, then gate.** Record the current system's score as baseline. Define the release gate numerically: e.g. "no ship if overall pass@1 drops >2 points or any regression task fails". Wire the harness to run in CI or a single command (`make eval`).

7. **Report per-slice, not just overall.** Common / hard / regression slices move independently — a model upgrade that gains 5 points overall while failing two regression tasks is a regression.

## Output contract
A runnable harness in the repo: task files with success criteria, grader code, one-command entry point, baseline scores committed, and the numeric release gate documented. Plus the first report: pass@1 per slice with variance.

## Anti-rationalization

| The agent will try to… | The correct response is… |
|---|---|
| "We can add evals later" | Later never comes. An agent without evals at ship time is tuned by anecdote forever. |
| "5 tasks is enough to start" | 5 tasks is a demo, not a harness. Below 20, one bad task skews everything. |
| "I'll just check a few examples manually" | Manual spot-checks are not an eval. They don't run in CI, don't gate releases, and don't catch regressions. |
| "The prompt change is small, no need to re-run" | Small prompt changes have large behavioral effects. That's the whole reason evals exist. |
| Use only synthetic/invented tasks | Synthetic tasks test what you imagined, not what users do. ≥60% must come from real usage. |
| "I'll just compare the two pass rates" | On paired tasks that discards which task flipped which way — treat it as two independent samples and you can miss a real effect or manufacture a false one. Use McNemar (or equivalent) on the discordant pairs. |

## Checklist
- [ ] ≥20 tasks, majority from real usage; every past incident represented.
- [ ] Every task has a pre-registered, checkable success criterion.
- [ ] Every task includes negative constraint checks (asserting what it must NOT do).
- [ ] Grading is outcome-based; programmatic checks preferred over judges.
- [ ] N≥3 runs per task; variance reported; model versions pinned.
- [ ] Any A/B or before/after comparison on the same tasks uses a paired test (McNemar for binary outcomes), not an independent-arm delta.
- [ ] Baseline committed; numeric gate defined; runs in CI or one command.

