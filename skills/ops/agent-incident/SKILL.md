---
name: agent-incident
description: Respond to a live agent misbehaving in production — contain blast radius, diagnose from traces, remediate, and turn the incident into regressions. Use when an agent is doing something wrong right now, sent something it shouldn't have, or is burning money in a loop.
---

# Agent Incident Response

Agent incidents differ from service outages: the system is *acting*, not just failing. Containment comes before diagnosis — stop the actions first, understand them second.

## When to use
- An agent is taking wrong actions now (bad messages sent, wrong data written, runaway spend).
- A user reports the agent did something nobody asked for.
- An alert fired: retry-loop spike, cost cliff, success-rate collapse.

## When NOT to use
- Systematic quality decline with no active harm — that's `trajectory-review` on your own schedule.

## Procedure

1. **Contain (minutes).** Pick the smallest step that stops harm, in order of preference: revoke the specific dangerous capability (disable one tool, drop one permission) → pause the affected task type → kill the agent entirely. Snapshot before killing: running trajectories, queue state, recent traces — the evidence dies with the process. Note containment time.

2. **Scope the blast radius.** From the audit trail (`guardrails`) and traces (`agent-observability`): which runs took externally visible (X/$) actions in the incident window? List every send/write/spend with target and reversibility. Externally visible harm (wrong emails, public posts, customer data) triggers the human comms step *now*, not after diagnosis.

3. **Diagnose from traces, not vibes.** Take 3–5 affected runs; find the first divergence (`trajectory-review` method). Check the usual suspects in order:
   - **What changed?** — model version, prompt/skill deploy, tool/API change, data-source change in the last window. Most agent incidents are a deploy someone didn't think was a deploy.
   - **Injection?** — untrusted content in context just before the bad action (route to `injection-audit` if yes).
   - **Environment?** — upstream API returning garbage the agent dutifully acted on.

4. **Remediate at the right layer.** Rolled-back deploy, patched tool contract, new guardrail gate, or injection mitigation — matched to the diagnosis. Resist the reflex to just add prompt text saying "don't do that"; if the harness allowed the harmful action, the harness is the bug (see `guardrails` step 5).

5. **Recover deliberately**: re-enable in stages (shadow/dry-run mode → limited cohort → full), watching the specific metric that would have caught this incident earlier.

6. **Close the loop (The "Never Again" List)**: every incident must be added to the Adversarial Regression Set. Anonymize the failing trace and append it to `eval-harness` as an immutable regression task. Also ensure an alert or canary is created that would fire earlier next time, and write a postmortem noting time-to-contain and whether guardrails behaved as designed.

## Output contract
An incident report: timeline (detect → contain → diagnose → recover), blast-radius list with reversibility, first-divergence diagnosis, remediation layer and rationale, staged-recovery results, and the regression task + new alert added.

## Checklist
- [ ] Contained before diagnosed; evidence snapshotted before any kill.
- [ ] Every X/$ action in the window enumerated; external harm escalated to humans immediately.
- [ ] Diagnosis names a first divergence and a cause class (deploy/injection/environment/capability).
- [ ] Fix landed in the harness/tools, not only in prompt wording.
- [ ] Staged recovery watched the metric that should have caught it.
- [ ] Regression task and earlier-firing alert both added.
