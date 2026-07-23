---
name: evolution-meta
description: Tune the evolution mechanism's own thresholds — override-rate trigger, failure-cluster minimum, canary duration, trust-earning count — based on evidence from past evolution cycles. Use after every 20 evolution cycles, when the evolution loop shows pathology, or when reviewing whether the mechanism's parameters are well-calibrated.
---

# Evolution Meta

The evolution mechanism has tunable parameters (30% override threshold, ≥3 cluster minimum, 7-day canary, 10-win trust). These are starting points, not ground truth. If the override threshold is too low, the loop thrashes on noise; too high, it misses real problems. This skill turns the evolution loop's own history into evidence for adjusting its parameters — meta-evolution. It is the only skill whose subject is the evolution mechanism itself.

## When to use
- After every 20 evolution cycles (triggered by `evolution-scan` counting its iterations).
- The evolution loop shows pathology (thrash, accretion, high revert rate) and the root cause may be a miscalibrated parameter.
- Scheduled review of whether the mechanism's parameters are earning their values.

## When NOT to use
- Tuning skill *routing* decisions — that's `routing-tuner`.
- Tuning a single skill's *procedure* — that's `self-improvement-loop`.
- Fewer than 20 evolution cycles have run — insufficient evidence to tune from.

## Procedure

1. **Pull the evolution attempt log.** Collect all records from `evolution-scan`, `evolution-canary`, and `evolution-conflict`: `{trigger_condition, trigger_threshold_at_time, draft, gate_result (pass/fail), apply_or_discard, canary_outcome (promoted/reverted/extended/escalated)}`.

2. **Compute per-parameter effectiveness.** For each tunable parameter:

   | Parameter | Default | Evidence to compute |
   |---|---|---|
   | Override-rate trigger threshold | 30% | Of changes triggered at this threshold: what % survived canary (promoted) vs. got reverted? |
   | Failure-cluster minimum (N) | 3 | Of clusters at size N that triggered changes: false-positive rate (reverted) vs. false-negative rate (estimated from manual invocations that should have been auto-triggered) |
   | Canary duration | 7 days / 20 invocations | Time-to-regression distribution: do reverts happen in day 1–3 (canary too long), or after promotion (canary too short)? |
   | Trust-earning threshold | 10 consecutive wins | Regression rate after auto-apply was unlocked: did 10 wins reliably predict continued success? |

3. **Identify miscalibration.** A parameter is miscalibrated if:
   - **Too aggressive** (threshold too low): high revert rate (>25% of triggered changes get reverted during canary).
   - **Too conservative** (threshold too high): humans are manually invoking evolution actions that the scan should have caught (detectable from `user_response: explicitly_invoked` in the routing log for evolve skills).

4. **Propose adjusted thresholds.** For each miscalibrated parameter, propose a new value within the adjustable range:
   - Override-rate trigger: 15%–50%
   - Failure-cluster minimum: 2–5
   - Canary duration: 3–14 days / 10–50 invocations
   - Trust-earning threshold: 5–20 consecutive wins

   Each proposal includes: the current value, proposed value, the evidence (revert rate, false-positive/negative rates), and the expected effect.

5. **Never auto-apply.** Meta-parameter changes are **Critical risk tier** — always. Present the proposals to the human with full evidence. The human decides. This boundary is permanent: the evolution mechanism does not autonomously change its own control parameters.

6. **Log the meta-review.** Record: `{cycle_count, parameters_reviewed, miscalibrations_found, proposals_made, human_decisions}`. The log feeds the next meta-review.

## Output contract
A meta-evolution report: the evolution cycle window reviewed, per-parameter effectiveness stats (revert rate, false-positive/negative rates), any proposed threshold adjustments with evidence, and the human's decision on each.

## Checklist
- [ ] ≥20 evolution cycles in the log before running.
- [ ] Per-parameter effectiveness computed from canary outcomes.
- [ ] Miscalibration identified by revert rate (too aggressive) or manual-invocation rate (too conservative).
- [ ] Proposals within adjustable ranges, with evidence and expected effect.
- [ ] Proposals presented to human — never auto-applied.
- [ ] Meta-review logged for the next cycle.
