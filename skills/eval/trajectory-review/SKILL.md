---
name: trajectory-review
description: Analyze agent transcripts/traces to find where and why runs go wrong — failure taxonomy, first-divergence analysis, and ranked fixes. Use when an agent fails tasks and you need the cause, when eval scores drop, or when reviewing production traces for systematic failure modes.
---

# Trajectory Review

Evals tell you *that* the agent fails; trajectories tell you *where* and *why*. The discipline is finding the first divergence — the earliest step where the run left the successful path — because everything after it is noise.

## When to use
- Eval scores dropped or a class of tasks keeps failing.
- A production incident involved an agent doing something wrong (pairs with `agent-incident`).
- Periodic review of production traces to catch failure modes before users report them.

## When NOT to use
- You have no failing runs yet — build `eval-harness` first to generate comparable trajectories.
- Single interactive session going sideways — just read it; this skill is for *systematic* analysis.

## Procedure

1. **Assemble comparable runs.** Gather the failing trajectories plus 2–3 *successful* runs of the same/similar tasks. Without a success to diff against, you'll misjudge which oddities matter — successful runs are full of harmless weirdness.

2. **Find the first divergence in each failure.** Walk the failing run against a successful one, step by step, and mark the earliest point where they meaningfully differ: different tool chosen, different interpretation of a result, missing step, wrong parameter. Everything downstream is a symptom; the divergence is the finding.

3. **Classify each divergence** into the failure taxonomy:
   - **Context**: the needed fact wasn't in context (never retrieved, truncated, buried).
   - **Instruction**: fact present, but the prompt/skill didn't say what to do — or said it ambiguously.
   - **Tool**: right intent, but the tool's schema/description/error message misled (route to `tool-design`).
   - **Capability**: everything present and clear; the model still reasoned wrong.
   - **Environment**: flaky dependency, timeout, bad fixture — not the agent's fault.

4. **Aggregate before fixing.** Tally divergences by class and by prompt/tool involved. Fix the top cluster, not the most recent failure — one context-truncation bug often explains a dozen "random" failures. Capability failures are the only class where "try a better model" is the answer; teams over-diagnose it.

5. **Turn every confirmed failure into a regression task** in the eval harness before fixing it, so the fix is measurable and the failure can't silently return.

6. **Verify the fix on the trajectories**: rerun the originally failing tasks; confirm the first divergence no longer occurs (not merely that the task now passes — it can pass by luck).

## Output contract
A review report: runs analyzed, per-failure first-divergence with class, aggregate tally by class, ranked fixes with the cluster each addresses, regression tasks added, and rerun results confirming divergences closed.

## Checklist
- [ ] Failures diffed against successful runs, not read in isolation.
- [ ] Each failure annotated with its *first* divergence, not last symptom.
- [ ] Every divergence classified; capability used only when context+instruction+tool ruled out.
- [ ] Fixes target the largest cluster; each confirmed failure added to eval regressions.
- [ ] Rerun shows the divergence itself gone, not just a lucky pass.
