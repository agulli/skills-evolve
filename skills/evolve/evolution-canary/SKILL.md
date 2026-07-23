---
name: evolution-canary
description: Monitor a recently auto-applied skill change during its canary period — track override rate and eval scores post-apply, auto-revert on regression, promote to permanent on stability. Use after an evolution change is auto-applied, when checking active canaries, or when a canary needs manual resolution.
---

# Evolution Canary

Every auto-applied skill change is a hypothesis: "this diff improves the skill." The canary period tests that hypothesis on live usage before the change becomes permanent. Without it, auto-apply is irreversible optimism; with it, auto-apply is a safe experiment with a built-in undo.

## When to use
- After `self-improvement-loop` auto-applies a change (Low or Medium risk tier).
- When `evolution-scan` checks the status of active canaries.
- A canary is approaching its window limit and needs resolution.

## When NOT to use
- The change requires human review (High/Critical risk) — it doesn't enter canary; it enters a PR.
- Monitoring a production *deployment* (traffic routing, model swap) — that's `deployment`.

## Procedure

1. **Register the canary.** On auto-apply, create a canary record in the canary registry (`evolution-canaries.json` in the skills directory): `{change_hash, skill_name, diff_summary, apply_date, baseline_override_rate, baseline_eval_score, invocation_count: 0, status: "canary", extension_count: 0}`.

2. **Collect post-apply signal.** On each check (triggered by `evolution-scan`), pull routing log entries for the modified skill since `apply_date`. Update `invocation_count`. Compute post-apply override rate and eval scores from the entries.

3. **Evaluate against regression thresholds:**
   - **Override rate increased by >10 percentage points** vs. baseline → regression.
   - **Eval score dropped below the release gate** → regression.
   - Neither → stable so far.

4. **Decide the canary outcome:**

   | Condition | Action |
   |---|---|
   | Regression detected | **Auto-revert**: `git revert` the change commit. Log: `{change_hash, revert_reason, pre/post metrics, revert_date}`. Update status to `"reverted"`. If this was a Medium-risk auto-apply, decrement the trust counter. |
   | Stable AND (≥7 days elapsed OR ≥20 invocations) | **Promote**: update status to `"permanent"`. The change is now eligible for propagation via `evolution-propagate`. |
   | Stable but under both thresholds | **Continue**: no action, check again next scan. |
   | Inconclusive after 14 days (one extension) | **Escalate**: notify human with the evidence collected so far. Update status to `"escalated"`. |

5. **On first check only: extend if empty.** If 7 days have passed but invocation count is <5 (the skill rarely fires), extend the canary window once (+7 days, increment `extension_count`). Do not extend more than once — a skill that fires <5 times in 14 days may not warrant the change.

6. **Commit provenance on every outcome.** Every revert, promotion, or escalation is committed with: the original change hash, the trigger that caused the change, before/after metrics, and the canary decision rationale.

## Output contract
Per canary: the current status (`canary` / `promoted` / `reverted` / `escalated`), the evidence window (invocations, override rate, eval scores vs. baseline), and the action taken. The canary registry is the persistent state.

## Checklist
- [ ] Canary registered on auto-apply with baseline metrics.
- [ ] Post-apply override rate and eval scores collected on each scan.
- [ ] Regression thresholds checked: override +10pp or eval below gate.
- [ ] Auto-revert executed on regression with full provenance committed.
- [ ] Promotion at ≥7 days or ≥20 invocations if stable; extension if too few invocations.
- [ ] Escalation to human if inconclusive after one extension.
