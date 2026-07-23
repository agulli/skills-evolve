---
name: evolution-scan
description: Run a periodic evolution sweep — scan the routing log and telemetry for trigger conditions (high override rates, failure clusters, model shifts, distillation candidates), classify each by type and risk, and dispatch to the appropriate skill. Use on a daily schedule, after a session batch, or when manually reviewing the evolution backlog.
---

# Evolution Scan

The orchestrator of the self-improvement mechanism. No individual evolve skill knows when to run — they fire at moments. This skill *creates* those moments by scanning the routing log on a cadence, detecting trigger conditions, and dispatching to the right skill. Without it, evolution is reactive and human-initiated; with it, evolution is scheduled and autonomous.

## When to use
- On a daily schedule (cron, post-session hook, or CI trigger) to sweep for evolution opportunities.
- After a batch of sessions, to process accumulated routing evidence.
- Manually, to review what the evolution backlog looks like.

## When NOT to use
- To tune a single routing decision — that's `routing-tuner`.
- To diagnose a specific failure — that's `trajectory-review`.
- The routing log doesn't exist yet — stand it up first (step 0 of `routing-tuner`).

## Procedure

1. **Verify the scheduler is installed.** Check that this skill is triggered on a cadence (cron job, post-session hook, or CI trigger). If no scheduler exists, install one per the environment's hook mechanism. The scheduler's only job is to invoke the agent with: "Run `evolution-scan`." Without a scheduler, this skill runs only when a human remembers — which is the problem it solves.

2. **Read the routing decision log since the last scan.** Pull all records since the last `evolution-scan` timestamp. Each record has: `{timestamp, moment_signal, skill_fired, tier, user_response, run_id}`. If no records exist, log "empty window" and stop.

3. **Detect override-rate triggers.** Compute per-skill override rate over a sliding window (minimum N≥10 invocations). For each skill exceeding the threshold (default 30%), create a pending trigger: `{type: override_cluster, skill, rate, evidence_run_ids}`. Dispatch to `routing-tuner`.

4. **Detect failure-cluster triggers.** Pull `trajectory-review` findings (or run it if stale). For each cluster of ≥3 failures sharing the same first-divergence in a task class where a skill was active, create a pending trigger: `{type: failure_cluster, skill, cluster_id, evidence}`. Dispatch to `self-improvement-loop`.

5. **Detect model-shift triggers.** Check the `model_generation` bucket against the last-scanned generation. If shifted, create a pending trigger for every skill: `{type: model_shift, generation_old, generation_new}`. Dispatch to `model-migration`.

6. **Detect distillation candidates.** Scan for task classes solved ≥3 times without a dedicated skill, with high effort (>10 turns or backtracking). Create a pending trigger: `{type: distillation_candidate, task_class, trajectory_ids}`. Dispatch to `skill-distillation`.

7. **Check for conflicts.** If multiple triggers target the same skill, dispatch to `evolution-conflict` before any individual resolution proceeds.

8. **Check active canaries.** Read the canary registry. For each active canary, dispatch to `evolution-canary` for status check.

9. **Log the scan.** Write a scan record: `{timestamp, window, triggers_found, dispatches, canaries_checked}`. Update the last-scan timestamp.

## Output contract
A scan report: the window covered, triggers detected per type, dispatches made (skill × target × evidence), canary statuses, and any scheduler installation or repair performed.

## Checklist
- [ ] Scheduler verified or installed; next scan will fire without human action.
- [ ] Routing log read; window since last scan stated.
- [ ] Override-rate, failure-cluster, model-shift, and distillation triggers detected and dispatched.
- [ ] Conflicts detected and routed to `evolution-conflict` before resolution.
- [ ] Active canaries checked via `evolution-canary`.
- [ ] Scan record logged with timestamp, triggers, and dispatches.
