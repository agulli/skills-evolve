---
name: latency-optimization
description: Reduce an agent's user-perceived latency — streaming, parallel tool calls, speculative/prefetch work, model-for-latency, and turn reduction — without losing quality. Use when an agent feels slow, when p95 latency is user-facing, or when time-to-first-token or total turn time hurts the experience.
---

# Latency Optimization

Latency and cost are different problems with different fixes, and users feel latency directly. An agent can be cheap and still feel sluggish — long time-to-first-token, serialized tool calls, too many turns. This skill attacks *perceived* speed. It shares measurement discipline with `cost-optimization` but optimizes a different axis; a change here is kept only if quality holds (`eval-harness`).

## When to use
- An agent feels slow, or p95 latency is user-facing and hurts the experience.
- Time-to-first-token or total turn time is the complaint.
- Before scaling an interactive agent where responsiveness matters.

## When NOT to use
- Latency-insensitive batch/offline work — optimize cost instead (`cost-optimization`), or batch it.
- The bill, not the clock, is the problem — that's `cost-optimization`.

## Procedure

1. **Measure where the time goes.** From traces (`agent-observability`), break latency down: time-to-first-token, per-tool-call latency, number of serialized model round-trips, and tail (p95/p99) vs. median. Optimize the biggest contributor — usually serialized round-trips or a slow tool, rarely the thing you assumed. Tail latency matters more than mean for user experience.

2. **Stream to cut perceived latency for free.** For any user-facing response, stream tokens so the user sees progress immediately instead of waiting for the full generation. Time-to-first-token, not total time, is what "feels slow." Streaming is the highest-ROI latency win and costs nothing in quality.

3. **Parallelize independent work.** Tool calls with no dependency between them should run concurrently, not in sequence — and the harness must return them as one batch so the model keeps making parallel calls. Serialized independent calls are the most common self-inflicted latency. Fan out where the work allows.

4. **Do speculative and prefetch work.** Where you can predict the next step, start it early — prefetch the likely-needed data during the model's think time, warm the prompt cache before the request lands (`cost-optimization`). Overlap waiting with useful work instead of doing everything strictly in order.

5. **Match model and effort to the latency need.** A smaller/faster model or lower effort on latency-critical steps (classification, routing, simple extraction) can cut time with no quality loss — reserve the slow frontier model for steps that need it (`model-routing`). Test the quality trade explicitly; don't downgrade blind.

6. **Reduce turns.** Fewer model round-trips is often the biggest structural win: give the model what it needs up front so it doesn't round-trip to discover it, consolidate multi-step tool sequences, and cut unnecessary reflection. Gate every change on quality — report Δlatency with Δeval-score so a speed win never silently costs correctness.

## Output contract
A before/after latency report: the latency breakdown (TTFT, per-tool, round-trips, p95/p99), changes applied in leverage order, and per-change Δlatency with Δeval-score. Streaming and parallelization left in place.

## Checklist
- [ ] Latency broken down (TTFT, per-tool, round-trips, tail vs. median); biggest contributor targeted.
- [ ] User-facing responses stream; TTFT measured.
- [ ] Independent tool calls parallelized and returned as one batch.
- [ ] Speculative/prefetch/cache-warm work overlaps model think time.
- [ ] Model/effort matched to latency need on non-critical steps, quality-tested.
- [ ] Turn count reduced where possible; every change reports Δlatency with Δeval-score.
