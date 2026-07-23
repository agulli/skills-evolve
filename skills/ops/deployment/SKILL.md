---
name: deployment
description: Ship an agent change safely — shadow, canary, staged rollout, and fast rollback gated on live metrics — so a bad prompt/tool/model change is caught on a fraction of traffic instead of all of it. Use when releasing a change to a production agent, when a deploy caused a regression, or when there's no safe way to roll a change out.
---

# Agent Deployment

A prompt edit is a production deploy: it changes behavior for every user at once, and unlike code it can't be spotted by reading the diff. This skill ships agent changes the way risky changes should ship — to a fraction of traffic first, watched by metrics, reversible fast. It's the proactive complement to `agent-incident` (the reactive path) and it leans on `eval-harness` (offline gate) and `agent-observability` (live signal).

## When to use
- Releasing any behavior change (prompt, tool, model, config) to a production agent.
- A previous deploy caused a regression nobody caught before full rollout.
- There's no defined way to roll a change out or back.

## When NOT to use
- Pre-production changes with no live traffic — the `eval-harness` gate is enough there.
- An active production incident — that's `agent-incident`.

## Procedure

1. **Gate on evals before any traffic.** No change reaches production without passing the offline `eval-harness` gate (no regression on the suite, regression cases green). The eval gate is the cheap filter; everything below is for what evals can't catch — real-traffic distribution, live cost, emergent behavior.

2. **Shadow first for risky changes.** Run the new version alongside the old on real traffic *without serving its output* — compare responses, cost, latency, and tool usage against production. Shadow catches "passed evals, breaks on real inputs" before a single user sees it. Use it for model swaps and large prompt changes.

3. **Canary to a small cohort, watched by metrics.** Serve the new version to a small, representative slice (or internal users first). Pre-define the metrics that decide promotion — success rate, override/edit rate, cost per task, latency, refusal rate (`agent-observability`) — and the abort thresholds. A canary nobody is watching against thresholds is just a slow full rollout.

4. **Stage the rollout.** Expand in steps (e.g. 5% → 25% → 100%), holding at each stage long enough for the metrics to move, with the abort thresholds live at every stage. A model upgrade that gains overall but fails one regression cohort shows up here, on a fraction of users.

5. **Make rollback instant and boring.** Reverting is one action, faster than diagnosing — flip back to the known-good version, then investigate. Because prompts/config are versioned (`agent-scaffolding`), rollback is a version pointer change, not a redeploy. Practice it; a rollback path that's never been exercised isn't one.

6. **Version and log every deploy.** Each release stamps the prompt/tool/model/skill versions onto traces (`agent-observability`) so "what changed?" is always answerable — the first question of every incident. Record what shipped, when, to what cohort, and the metric outcome.

## Output contract
A deployment plan and record: the eval gate, shadow/canary/staged strategy with pre-defined promotion metrics and abort thresholds, the one-action rollback path (tested), and per-deploy version stamping. Rollout automation lands as config/pipeline, not a manual checklist someone forgets.

## Anti-rationalization

| The agent will try to… | The correct response is… |
|---|---|
| "This change is low-risk, we can skip canary" | Every change that broke production was "low-risk" until it wasn't. Canary is for exactly these changes. |
| "The evals passed, so it's safe to go to 100%" | Evals test a fixed set. Production has distribution, volume, and edge cases evals can't cover. |
| "Rollback is easy, we'll just revert if something goes wrong" | Have you *tested* the rollback? An untested rollback path is not a rollback path. |
| Ship on a Friday / before a holiday | The deploy window matters. Ship when someone is watching and can respond. |
| "We'll add version stamping later" | Without version stamps, the first question of every incident — "what changed?" — has no answer. |

## Checklist
- [ ] Offline eval gate passed before any production traffic.
- [ ] Risky changes shadowed on real traffic before serving.
- [ ] Canary to a small cohort with pre-defined promotion metrics + abort thresholds.
- [ ] Rollout staged; thresholds live at every stage.
- [ ] Rollback is one action, version-pointer based, and has been exercised.
- [ ] Every deploy stamps versions onto traces and records cohort + metric outcome.

