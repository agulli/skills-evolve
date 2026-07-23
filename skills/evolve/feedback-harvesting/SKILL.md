---
name: feedback-harvesting
description: Systematically collect and structure feedback signals about an agent — explicit corrections, implicit signals (edits, overrides, abandonment), and outcomes — into a ranked improvement queue. Use when feedback arrives ad hoc and evaporates, or to build the signal-collection layer of a self-evolving agent.
---

# Feedback Harvesting

Users tell you what's wrong with your agent constantly — mostly not in words. Harvesting turns corrections, edits, overrides, and rage-quits into a structured queue that `self-improvement-loop` and humans can act on.

## When to use
- Feedback about the agent lives in Slack threads and memory, arriving ad hoc and evaporating.
- Building the input layer for a `self-improvement-loop`.
- Deciding what to improve next and wanting evidence instead of the loudest anecdote.

## When NOT to use
- Diagnosing *why* a flagged run failed — that's `trajectory-review`; harvesting decides *which* runs deserve that analysis.

## Procedure

1. **Instrument the implicit channels** — they carry most of the signal:
   - **Edit distance**: user substantially rewrote the agent's output before using it.
   - **Override**: user re-did the task manually or repeated the request with added constraints ("no, actually...").
   - **Abandonment**: task cancelled mid-run, output ignored, session dropped after a response.
   - **Interruption**: user stopped the agent mid-action (strongest negative signal — they saw where it was going).
   Log each with `run_id` so the trajectory is retrievable.

2. **Capture explicit feedback at near-zero cost**: thumbs/flag on outputs where a UI exists; a lightweight correction convention in chat-based agents (detect "no/wrong/don't" turns and tag the run); a standing channel where teammates drop agent complaints that a daily job ingests.

3. **Normalize into feedback records**: `{run_id, task_type, signal_type, severity (annoyance | wrong-output | harmful-action), verbatim evidence, date}`. Keep the user's words — summaries at this stage destroy the detail that later diagnosis needs.

4. **Cluster by failure, not by phrasing.** Group records that point at the same behavior (same task type + same signal pattern, or same first-divergence once reviewed). Rank clusters by frequency × severity × cost-of-failure. This ranked queue *is* the product of this skill.

5. **Route each top cluster**: harmful-action → `agent-incident` now; wrong-output cluster → `trajectory-review` for diagnosis, then `self-improvement-loop` or a human fix; annoyance cluster → batch for prompt/UX review. Every routed cluster gets an owner and lands as a regression task once confirmed.

6. **Close the loop visibly and measure the funnel**: when a cluster is fixed, note it where the feedback came from ("the X issue is fixed") — feedback dries up when it disappears into a void. Track weekly: records harvested → clustered → routed → fixed, and the implicit-signal rates (edit/override/abandonment) as the agent's real satisfaction metrics.

## Output contract
The harvesting pipeline (signal instrumentation + ingestion job) plus a living ranked queue: clusters with frequency/severity/evidence, routing decision and owner per cluster, and the weekly funnel + implicit-signal-rate report.

## Checklist
- [ ] All four implicit signals instrumented and tied to `run_id`.
- [ ] Explicit channel exists with near-zero friction; verbatim words preserved.
- [ ] Records clustered by underlying failure; ranked by frequency × severity × cost.
- [ ] Every top cluster routed with an owner; harmful-action goes to incident response immediately.
- [ ] Fixes announced back at the source; funnel and implicit rates reported weekly.
