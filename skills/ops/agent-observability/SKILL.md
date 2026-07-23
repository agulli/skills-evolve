---
name: agent-observability
description: Instrument a production agent — trace structure, the metrics that matter, cost/token accounting, and alerts. Use when an agent ships to production, when debugging requires re-running instead of reading traces, or when nobody can say what the agent did yesterday.
---

# Agent Observability

If you can't replay what the agent saw and did, every production bug becomes archaeology. Instrument three layers: traces (what happened), metrics (how it's trending), and alerts (when to look).

## When to use
- An agent is going to production, or is already there uninstrumented.
- Debugging currently means "try to reproduce it" instead of "read the trace".
- Cost, latency, or quality is drifting and nobody noticed for a week.

## When NOT to use
- Choosing what to log for *security* audit specifically (that's the `guardrails` audit trail; align formats, different purpose).
- One-off local debugging — read the session transcript directly.

## Procedure

1. **Structure traces around the run, not the request.** One trace per agent task; one span per turn; child spans per tool call. Every span carries: model + version, input/output token counts, latency, cost, and tool name/params/result-size. Propagate a `run_id` through every downstream call — including subagents, whose traces link to the parent.

2. **Capture enough to replay.** Store the full prompt assembly (system prompt version, injected context, retrieved memories) and raw tool results — sampled if volume forces it, but 100% for failed runs. A trace you can't reconstruct the context window from can't answer "why did it do that". Redact secrets/PII at write time, not read time.

3. **Emit the metric set that catches agent-specific rot:**
   - **Outcome**: task success rate (from `eval-harness` criteria where possible), human-override/edit rate.
   - **Efficiency**: turns per task, tokens per task, cost per task, p50/p95 latency.
   - **Behavior canaries**: tool-error rate per tool, retry-loop count, truncation events, refusal rate.
   All sliced by task type and model version — aggregate averages hide everything interesting.

4. **Version everything that shapes behavior**: prompt hash, skill versions, toolset hash, model ID on every trace. When a metric moves, the first question is "what changed?" — the trace must answer it.

5. **Alert on drift and cliffs, not single failures**: success rate drops >X points day-over-day, cost per task up >Y%, any tool's error rate >Z%, retry-loop spike. Route to a human who owns the agent; every alert links to sample traces.

6. **Verify by debugging blind**: take yesterday's worst run, and using only the observability stack (no logs-diving, no rerun), reconstruct what the agent saw and where it went wrong. If you can't, instrumentation isn't done.

## Output contract
Instrumentation code in the repo plus a one-page runbook: trace schema, metric definitions with slice dimensions, alert thresholds and owners, dashboard link, and the blind-debug verification note.

## Checklist
- [ ] One trace per run; spans carry model, tokens, cost, latency; `run_id` spans subagents.
- [ ] Context window reconstructable for any failed run; secrets redacted at write.
- [ ] Outcome, efficiency, and canary metrics emitted, sliced by task type and model.
- [ ] Prompt/skill/toolset/model versions stamped on every trace.
- [ ] Drift alerts wired to an owner; blind-debug test passed on a real failed run.
