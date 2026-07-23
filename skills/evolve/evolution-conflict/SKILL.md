---
name: evolution-conflict
description: Resolve conflicts when multiple evolution triggers fire on the same skill simultaneously — prioritize by severity, sequence changes, detect contradictions, and escalate when two proposed fixes oppose each other. Use when evolution-scan detects multiple pending changes targeting one skill file.
---

# Evolution Conflict

When the evolution loop runs at scale, multiple triggers will inevitably target the same skill in the same cycle — an override cluster AND a failure cluster, or a model shift AND a procedure fix. Applying changes without conflict resolution produces silent overwrites, contradictory edits, or eval regressions from interacting diffs. This skill serializes concurrent evolution.

## When to use
- `evolution-scan` detects ≥2 pending triggers targeting the same skill file.
- A proposed diff would modify a section already modified by another pending diff.
- Two failure clusters suggest opposite changes to the same procedure step.

## When NOT to use
- Only one trigger targets the skill — no conflict to resolve; dispatch directly.
- The conflict is between two *different* skills (e.g., overlapping triggers) — that's `skill-maintenance`.

## Procedure

1. **List all pending triggers for the target skill.** Gather: `{trigger_type, evidence, proposed_diff (if already drafted), risk_tier}` for each. If diffs haven't been drafted yet, note that — priority determines draft order.

2. **Assign priority.** Rank triggers by severity — higher priority gets applied first:

   | Priority | Trigger type | Rationale |
   |---|---|---|
   | 1 (highest) | Safety / compliance gap | Blocking: the skill may be unsafe |
   | 2 | Failure cluster (§1B) | Users are actively failing |
   | 3 | Override cluster (§1A) | Users are annoyed but not failing |
   | 4 (lowest) | Model staleness (§1C) | Scheduled, not urgent |

3. **Take an advisory lock.** Create a lock file (`<skill-name>.evolution-lock`) to signal that this skill is undergoing evolution. Other evolution dispatches targeting this skill should wait or queue. The lock is advisory — it prevents concurrent drafting, not concurrent reading.

4. **Apply the highest-priority diff first.** Draft (if not yet drafted) and gate the highest-priority change through `eval-harness`. If it passes, apply it (per the risk tier's auto-apply rules).

5. **Re-evaluate remaining triggers.** After the first change lands, re-run the detection for lower-priority triggers on the *updated* skill. The first fix often resolves other triggers (e.g., a procedure fix that reduces failure clusters also reduces overrides). Drop any trigger that no longer fires.

6. **Detect contradictions.** If two triggers propose changes to the **same procedure step** that are **directionally opposite** (e.g., "do X before Y" vs. "do Y before X", or "add check C" vs. "remove check C"):
   - Do NOT auto-apply either.
   - Log both diffs side by side with their source evidence (trajectory IDs, override counts).
   - Escalate to human with a contradiction report: the two diffs, their evidence, and which one has stronger support (more trials, higher severity).
   - The human's decision is recorded as a new routing eval case.

7. **Release the lock and log.** Remove the lock file. Log the resolution: `{skill, triggers_received, priority_order, diffs_applied, triggers_dropped_after_first_fix, contradictions_escalated}`.

## Output contract
A conflict resolution report per skill: the triggers received, their priority ordering, diffs applied in sequence with gate results, triggers that resolved after the first fix, and any contradictions escalated to human review.

## Checklist
- [ ] All pending triggers for the skill listed with type and evidence.
- [ ] Priority assigned by severity; highest-priority drafted and gated first.
- [ ] Advisory lock taken before drafting; released after resolution.
- [ ] Lower-priority triggers re-evaluated after first fix; dropped if no longer firing.
- [ ] Contradictory diffs detected and escalated — never auto-applied.
- [ ] Resolution logged with full trigger→outcome chain.
