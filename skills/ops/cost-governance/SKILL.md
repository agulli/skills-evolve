---
name: cost-governance
description: Control agent spend at the org/fleet level — budgets, per-tenant quotas, spend caps, attribution, and anomaly alerts — so many agents and users don't add up to a surprise bill or a runaway. Use when multiple agents/users/tenants share a budget, when spend needs attribution or limits, or after an unexpected cost spike.
---

# Cost Governance

`cost-optimization` makes one agent cheaper; cost governance keeps a *fleet* of agents and users from adding up to a surprise. At scale the risk isn't an inefficient prompt — it's a runaway loop, an abusive user, or a hundred agents with no budget attribution producing a bill nobody can explain. This skill puts spend under control and attribution. It's the org-level counterpart to per-agent `cost-optimization`.

## When to use
- Multiple agents, users, or tenants draw on a shared LLM budget.
- Spend needs to be attributed, capped, or quota'd per team/user/tenant.
- An unexpected cost spike happened and nobody could say why or stop it fast.

## When NOT to use
- A single agent whose efficiency is the concern — that's `cost-optimization`.
- No real budget pressure and no multi-tenant fan-out.

## Procedure

1. **Attribute every dollar.** Tag spend by agent, tenant, user, and task type at the point of the call (`agent-observability` carries the tags). Without attribution you can't set fair budgets, find the expensive path, or catch the abuser — you only see one aggregate number rising. Attribution is the prerequisite for everything else here.

2. **Set budgets and quotas with enforcement.** Define spend budgets per team/tenant and per-user quotas, and *enforce* them in the harness — not as a dashboard nobody watches. A budget with no enforcement is a post-mortem line item. Decide the action at the limit: throttle, downgrade the model (`model-routing`), queue, or block.

3. **Cap the runaway before it runs.** Per-task and per-day spend caps stop the failure that actually blows budgets: a retry loop, a stuck agent, an adversarial input driving unbounded calls. The cap fires in the harness regardless of model judgment (pairs with the retry-loop canary in `agent-observability` and `reliability-engineering`). This is the single highest-value control.

4. **Alert on anomalies, not just totals.** Watch for the *shape* of a problem: a tenant's spend jumping day-over-day, cost-per-task climbing, one user or agent dominating, a spike in a specific model. Route alerts to an owner with the attribution attached so "why did cost jump?" is answerable in minutes, not a week (`agent-incident` if it's live harm).

5. **Forecast before scaling.** Before a 10x in users or a new high-volume agent, project the spend from per-task cost × expected volume and check it against budget. A rollout that's fine per-task and ruinous at scale is a governance failure that a five-minute forecast catches.

6. **Give owners visibility and levers.** Each budget owner sees their attributed spend and has a lever (quota, model tier, rate limit) they control. Governance that only central finance can see or act on doesn't change behavior; the team generating the cost needs the number and the knob.

## Output contract
A cost-governance setup: spend attribution by agent/tenant/user/task, enforced budgets/quotas with defined limit-actions, per-task and per-day runaway caps, anomaly alerts routed to owners with attribution, a pre-scale forecast, and per-owner visibility + levers. Caps and quotas land as enforced config.

## Checklist
- [ ] Spend attributed by agent, tenant, user, and task type at call time.
- [ ] Budgets/quotas defined and enforced in the harness, with a limit-action.
- [ ] Per-task and per-day runaway caps fire regardless of model judgment.
- [ ] Anomaly alerts (shape, not just total) routed to owners with attribution.
- [ ] Spend forecast checked before any large scale-up.
- [ ] Each budget owner has visibility and a control lever.
