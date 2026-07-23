# Evolution Mechanism

This document explains the evolution mechanism (The "Learning Loop").

## The Core Concept
The telemetry and evolution mechanism is the **engine** of the system. It ensures the library **never gets stale**. The agent learns from its own failures and the user's rejections, improving the skills and the routing table autonomously over time.

This loop is driven by the `skills/evolve/` group.

## How the Loop Works
The system follows a bounded loop designed to safely translate failure into enduring capability:

1. **Observe:** The system constantly records routing decisions and user overrides in the routing log, while `feedback-harvesting` captures explicit and implicit signals of failure.
2. **Detect Triggers:** The `evolution-scan` orchestrator runs on a schedule (e.g., daily cron or post-session hook) to sweep logs for trigger conditions: high override rates, failure clusters, or distillation candidates.
3. **Draft Fixes (Propose):** When a trigger is hit, the relevant evolution skill drafts a proposed change. For instance, `routing-tuner` proposes tightening the routing table when users frequently override a specific skill firing.
4. **Evaluate (Gate):** Every proposed fix is subjected to the `eval-harness` (Layer 3). If the fix drops the baseline score, it is blocked. The engineering is entirely in the bounds: a mutable surface (skill bodies, procedures) and an **immutable surface** (the eval gate, permissions).
5. **Monitor (Canary):** If a fix passes evaluation, `evolution-canary` auto-applies it and monitors the live metrics for a set period (e.g., 7 days). It tracks post-apply override rates and eval scores against the baseline, automatically reverting on regression and promoting on stability.
6. **Propagate:** Once promoted from the canary, `evolution-propagate` pushes the fix out — opening PRs or syncing to other local projects.

## Conflict Resolution & Tuning
- **Conflicts:** If multiple triggers propose contradictory changes to the same skill simultaneously, `evolution-conflict` takes a lock, prioritizes safety over staleness, and applies changes sequentially, escalating to a human only when necessary.
- **Tuning the Engine:** The `evolution-meta` skill periodically evaluates the learning loop itself (e.g., assessing the effectiveness of the canary duration or override thresholds) and proposes human-reviewed adjustments to the meta-parameters.
