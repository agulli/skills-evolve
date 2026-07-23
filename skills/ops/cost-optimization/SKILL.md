---
name: cost-optimization
description: Reduce an agent's cost and latency without dropping quality — measurement, prompt-cache hygiene, model routing, context diet, and batching. Use when the LLM bill spikes, when cost per task must come down, or before scaling an agent 10x.
---

# Agent Cost Optimization

Optimize in order of leverage: measure → cache → shrink context → route models → batch. Never cut cost blind — every change ships with an eval score next to the savings number.

## When to use
- Cost per task or the monthly bill needs to come down, or usage is about to scale 10x.
- Latency is user-visible and prompt-bound.
- Choosing a cheaper model and needing to know what it breaks.

## When NOT to use
- No evals exist yet — build `eval-harness` first; cost work without a quality gate is just quality reduction with extra steps.

## Procedure

1. **Measure before touching anything.** From observability data get: cost per task by task type, token breakdown (system prompt vs context vs history vs output), cache hit rate, and turns per task. The biggest line item gets attacked first — it's usually re-sent context, not output.

2. **Fix prompt-cache hygiene** — highest ROI, zero quality risk:
   - Stable content first (system prompt, tools, skills), volatile content last; cached reads are ~10x cheaper.
   - Kill cache-busters: timestamps, random IDs, or reordered tool definitions in the stable prefix invalidate everything after them.
   - Verify with the API's cache-read token counts, not intuition. Target: >80% of input tokens cached on multi-turn tasks.

3. **Put the context on a diet:**
   - Truncate/summarize tool results at the source (`tool-design` limits); the model rarely needs 400 rows to answer.
   - Compact old turns: after N turns, replace verbose history with a structured summary.
   - Audit the system prompt for dead weight (`prompt-architecture` inventory) — every line is paid on every call.

4. **Route models by task difficulty.** Slice eval scores by model: tasks where the small model matches the big one within the gate get routed down. Classification, extraction, and formatting steps almost never need the frontier model; keep it for planning and hard reasoning turns. Route by *task type* first (simple, static); dynamic per-request routing only if the static split leaves real money on the table.

5. **Batch and cap:** anything latency-insensitive (evals, backfills, digests) goes to the batch API at ~50% price. Set per-task and per-day spend caps in the harness — retry loops burn budgets fastest (pair with the retry-loop canary in `agent-observability`).

6. **Gate every change on the eval harness**: report Δcost, Δlatency, and Δpass@1 together. A 40% saving with a 3-point quality drop is a decision for the owner, not a silent deploy.

## Output contract
A before/after report: baseline breakdown, changes applied in leverage order, and per-change Δcost / Δlatency / Δeval-score. Spend caps and cache-hit monitoring left in place.

## Checklist
- [ ] Token/cost breakdown measured before any change; biggest item attacked first.
- [ ] Cache hit rate verified via API counts; stable-prefix violations fixed.
- [ ] Tool results and history bounded; system prompt dead weight removed.
- [ ] Model routing backed by per-model eval slices, not vibes.
- [ ] Batch API used for offline work; spend caps set.
- [ ] Every change reports Δcost with Δeval-score; no silent quality drops.
