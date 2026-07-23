---
name: agent-identity
description: Design who an agent acts as and what it's authorized to do — delegated identity, per-user permission boundaries, OAuth scope minimization, and the confused-deputy problem. Use when an agent acts on behalf of users, accesses per-user data, or holds broader permissions than any single user should wield.
---

# Agent Identity & Authorization

An agent that acts "on behalf of users" is a confused deputy waiting to happen: it holds credentials and permissions, and if it doesn't track *whose* authority it's using for *which* action, it will use one user's access to serve another's request. This skill designs identity and authorization boundaries. It's distinct from `secrets-management` (where the credential lives) and `guardrails` (what actions are gated) — this governs *whose authority* an action runs under.

## When to use
- An agent acts on behalf of users (reads their data, takes actions as them).
- One agent serves multiple users/tenants with different permissions.
- The agent holds broader access than any single user should have.

## When NOT to use
- A single-user, single-identity agent with no delegation — the boundary is trivial.
- The concern is credential storage/rotation — that's `secrets-management`.

## Procedure

1. **Separate the agent's identity from the user's authority.** Name three things explicitly: what the *agent* is (a service principal), what the *user* authorized it to do, and what authority *this action* runs under. Actions on a user's behalf must use that user's scoped authority — not the agent's ambient permissions. Conflating them is the confused-deputy bug.

2. **Propagate identity through every hop.** The acting user's identity must travel through tool calls, sub-agents, and downstream services — not get lost at the first boundary where the agent falls back to its own privileged credential. A request that enters as "user A" and hits the database as "the agent" has lost the boundary that authorization depends on.

3. **Enforce authorization at the resource, not just the prompt.** "Only show the user their own data" in the system prompt is not access control — it's a suggestion. The actual check must happen where the data lives (row-level security, per-user scoped tokens, resource ACLs), so that even a fully hijacked prompt (`injection-audit`) can't cross the boundary.

4. **Minimize scope at consent time.** When the agent obtains delegated access (OAuth, tokens), request the narrowest scopes the task needs, per user. Broad "read/write everything" grants mean any agent error or injection operates at full scope. Scope minimization caps blast radius before anything goes wrong.

5. **Handle the multi-tenant isolation boundary.** In a shared agent serving many tenants, prove one tenant's data/context can't leak into another's request — separate memory/retrieval scopes per tenant (`memory-design`, `retrieval-design`), no shared caches keyed loosely. Cross-tenant leakage is the highest-severity failure of a multi-user agent.

6. **Test with a hostile second user.** Attempt, as user B, to make the agent read or act on user A's data — directly, via injection, and via a chained request. Confirm the resource-level checks hold regardless of what the prompt was talked into. An identity design with no cross-user attack test is unverified.

## Output contract
An identity/authz design: the agent-vs-user authority separation, how identity propagates through hops, where authorization is enforced at the resource layer, the scope-minimization policy, the multi-tenant isolation boundaries, and cross-user attack test results.

## Checklist
- [ ] Agent identity, user authorization, and per-action authority are distinct and documented.
- [ ] Acting-user identity propagates through tools, sub-agents, and downstream calls.
- [ ] Authorization enforced at the resource (not just the prompt) — holds under a hijacked prompt.
- [ ] Delegated scopes minimized per user; no broad ambient grants.
- [ ] Multi-tenant memory/retrieval/cache scopes isolated per tenant.
- [ ] Cross-user attack test (direct + injection + chained) passed.
