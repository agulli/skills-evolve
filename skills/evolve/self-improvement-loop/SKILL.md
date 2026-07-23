---
name: self-improvement-loop
description: Design a bounded self-improvement loop where an agent proposes changes to its own prompts, skills, or memory, gated by evals and review. Use when building a self-evolving or always-on agent, or when an agent should learn from its failures without a human rewriting it each time.
---

# Self-Improvement Loop

A self-evolving agent is an ordinary agent plus a *bounded* loop: observe failures → propose a change → evaluate → gate → apply → monitor. The engineering is entirely in the bounds — an ungated loop optimizes for passing its own gate, not for being good.

**This skill defines the *design and bounds* of that loop** — the mutable/immutable surface, the gate, the risk tiers, the pathology monitors. The **operational pipeline that runs it on a schedule** is the `evolution-*` skills: `evolution-scan` detects when to evolve and dispatches, `evolution-canary` monitors each applied change, `evolution-propagate` spreads survivors. Think of this skill as the physics; the `evolution-*` skills are the machine that operates within it. When a scan dispatches a failure-cluster "to `self-improvement-loop`," it means the propose→gate→apply steps below.

## When to use
- **Designing** the bounds of a self-improving agent: what may change, the gate, the approval tiers, the stop conditions.
- Standing up the "agent improves its own skills" layer on top of an existing system.
- Proposing and gating a specific change for one failure cluster (the step `evolution-scan` dispatches here).

## When NOT to use
- **Scheduling or orchestrating** the loop — detecting *when* to evolve and dispatching — that's `evolution-scan` (the operational orchestrator). This skill owns the *bounds*, not the cadence.
- Tuning the routing table specifically — that's `routing-tuner`; tuning the mechanism's own thresholds — that's `evolution-meta`.
- The agent has no eval harness — build `eval-harness` first; without it, "improvement" is unmeasurable drift.
- The failures are harness/tool bugs (fix directly via `tool-design`/`guardrails`); the loop is for *behavioral* knowledge.

## Procedure

1. **Fix what may evolve — and what may never.** Mutable surface: skill bodies, prompt *procedure* sections, memory contents, few-shot examples. Immutable surface: constraints/safety layers, tool permissions, guardrail config, the eval gate itself, and this loop's own rules. The immutable list is enforced by the harness (file permissions, protected paths, review requirements), not by asking nicely.

2. **Feed the loop from evidence, not introspection.** Inputs are `trajectory-review` first-divergence findings and `feedback-harvesting` output — clustered, recurring failures. One-off failures don't trigger proposals; a cluster of ≥3 with a shared divergence does.

3. **Propose as diffs, not rewrites.** Each iteration produces the *smallest* change addressing one cluster: a new step in one skill, a clarified instruction, a new memory entry, a new few-shot example. One change per iteration — simultaneous changes make the eval signal unattributable.

4. **Gate on the full harness, not the triggering cases.** The proposal must (a) fix the cluster's regression tasks, and (b) not drop the overall eval score beyond the release gate. Run the change in shadow first if the eval set is thin. Improvement that only helps the cases it was derived from is overfitting with confidence.

5. **Apply with provenance, gated by risk tier.** Every applied change is committed with: the failure cluster it addresses, eval scores before/after, and the loop iteration ID. The risk tier determines who approves:

   | Surface modified | Risk | Auto-apply? |
   |---|---|---|
   | Memory contents, few-shot examples | Low | ✅ After eval-harness passes |
   | Trigger description, "When NOT to use" | Low | ✅ After routing eval passes |
   | Procedure step: add warning/pre-check | Medium | ✅ After full eval-harness (once trust earned) |
   | Procedure step: change action order | Medium | ⚠️ Shadow-run first (once trust earned) |
   | New skill creation | High | ❌ Human reviews and merges |
   | Safety/guardrail skill, X/$ behaviors | Critical | ❌ Always human; CI blocks |

   **Trust is earned, not default.** Medium-risk auto-apply starts locked. After 10 consecutive changes that pass the eval gate AND survive the canary period (see step 5b), Medium-risk auto-apply unlocks. One canary regression resets the counter to zero.

5b. **Enter the canary period on every auto-apply.** Every auto-applied change (Low or Medium risk) enters a canary period managed by `evolution-canary`: 7 days or 20 invocations (whichever comes first). During the canary, if override rate increases by >10pp or eval scores drop below the release gate, the change is auto-reverted. Only changes that survive the canary are promoted to permanent and become eligible for propagation via `evolution-propagate`.

6. **Monitor for loop pathologies** and stop conditions: eval-score plateau with rising change count (thrash), prompt/skill length growing monotonically (accretion — require the loop to also propose deletions), score gain on the harness with human-satisfaction drop (gate gaming — refresh the eval set), same file changed 3 iterations running (oscillation — freeze and escalate). Any pathology pauses the loop and pings the owner.

## Output contract
A loop spec + implementation: mutable/immutable surface lists with enforcement mechanism, trigger threshold, diff-proposal format, gate definition, approval matrix, provenance format, and the pathology monitors with stop conditions.

## Anti-rationalization

| The agent will try to… | The correct response is… |
|---|---|
| "This improvement is obvious, skip the eval gate" | "Obvious" improvements are the ones that introduce the subtlest regressions. The gate exists for these. |
| Apply multiple changes at once to "save time" | Simultaneous changes make the eval signal unattributable. One diff per iteration, always. |
| Edit the eval harness to make the change pass | The immutable surface exists precisely to prevent this. The loop cannot edit its own gate. |
| "One failure is enough to justify a change" | One failure is noise. The threshold is ≥3 failures with a shared divergence — a cluster, not an anecdote. |
| Skip the canary because "the eval passed" | Evals test canned tasks. The canary tests real usage. Both must pass. |

## Checklist
- [ ] Immutable surface enforced by the harness; loop cannot edit its own gate or guardrails.
- [ ] Proposals triggered only by evidence clusters (≥3 shared-divergence failures).
- [ ] One diff per iteration; gated on full harness, not just triggering cases.
- [ ] Every change committed with cluster, before/after scores, iteration ID.
- [ ] Risk-tier matrix enforced; Medium auto-apply locked until 10 consecutive canary-surviving wins.
- [ ] Every auto-applied change enters `evolution-canary`; reverted on regression.
- [ ] Thrash/accretion/gaming/oscillation monitors live, with pause-and-escalate.

