---
name: secrets-management
description: Handle credentials an agent uses — where API keys and tokens live, scoping, rotation, injection at egress, and keeping secrets out of prompts, logs, and traces. Use when an agent authenticates to any service, before adding a tool that needs a credential, or when reviewing where secrets currently live.
---

# Secrets Management

Credentials are the highest-value thing an agent touches and the easiest to leak — into a prompt, a log line, a trace, a tool result, or a model that memorizes them. This skill governs where secrets live and how they reach the point of use without ever entering the model's context. It's distinct from `guardrails` (gates *actions*) and `privacy` (governs *personal data*); this governs *credentials*.

## When to use
- An agent authenticates to any external service (APIs, databases, cloud, SaaS).
- Adding a tool or MCP server that needs a key/token.
- Reviewing where an existing agent's secrets currently live.

## When NOT to use
- No credentials involved at all.
- Personal-data handling — that's `privacy` (though the redaction disciplines overlap).

## Procedure

1. **Inventory every secret and its blast radius.** List each credential the agent can reach, what it unlocks, and its scope. A single over-broad key (full-admin where read-only would do) turns any agent mistake or injection into a maximal breach. You can't protect secrets you haven't enumerated.

2. **Keep secrets out of the model's context — always.** The credential must never appear in a prompt, a tool *input* the model constructs, a tool result it reads, memory, or telemetry. The model should reference a secret by name/handle; the actual value is substituted downstream, at egress, by code the model can't see. A secret in context is a secret one paraphrase away from the output.

3. **Store in a real secret store, injected at use.** Secrets live in a vault / secret manager / scoped environment, never in code, config committed to git, prompts, or the sandbox image. They're injected into the outbound request at the boundary (egress-time substitution) or held host-side and used by a trusted tool the agent calls — the agent orchestrates, the credential stays out of reach.

4. **Scope to least privilege and short TTL.** Each credential grants the minimum the task needs and expires. Per-user/per-task scoped, short-lived tokens beat one long-lived god-key: they cap blast radius and make rotation cheap. Gate the use of any high-privilege credential like an X/$ action (`guardrails`).

5. **Scrub secrets from every sink at write time.** Logs, traces, error messages, and telemetry are where secrets leak by accident. Redact at write time, not read time (same discipline as `privacy`) — a secret written to a log raw has already leaked, even if masked on display. Pattern-scan outputs for credential shapes as a backstop.

6. **Design rotation and revocation before you need them.** Every secret has a rotation path and a revocation path; assume any secret can be compromised and make replacing it routine, not an incident. Verify by rotating a real credential and confirming the agent picks up the new one with no code change and no downtime.

## Output contract
A secrets design: the credential inventory (what each unlocks + scope), the store and egress-injection mechanism, the least-privilege/TTL policy, write-time scrubbing across logs/traces/telemetry, and a tested rotation + revocation path. Storage and injection land as config, not prose.

## Checklist
- [ ] Every credential inventoried with what it unlocks and its scope.
- [ ] No secret ever enters a prompt, model-built tool input, tool result, memory, or telemetry.
- [ ] Secrets in a real store; injected at egress or used host-side; never in code/git/image.
- [ ] Least-privilege scope + short TTL; high-privilege use gated.
- [ ] Redaction at write time across logs/traces/errors/telemetry; credential-shape backstop scan.
- [ ] Rotation and revocation paths exist and were tested on a real credential.
