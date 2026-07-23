---
name: sandbox-policy
description: Choose and configure the execution sandbox for agent-run code — isolation level, filesystem/network policy, resource limits, and escape review. Use when an agent will execute generated code or shell commands, or when reviewing an existing agent's isolation.
---

# Sandbox Policy

Agent-generated code is untrusted code with your credentials nearby. The sandbox decision is: what isolation level, what the code can reach, and what happens on the first escape attempt.

## When to use
- An agent will run generated code, shell commands, or third-party tools.
- Choosing between local execution, containers, microVMs, or hosted sandboxes (E2B, Modal, etc.).
- Reviewing an existing agent whose "sandbox" is a working directory and good intentions.

## When NOT to use
- The agent only calls typed APIs and never executes arbitrary code — `guardrails` covers that surface.

## Procedure

1. **Classify the workload:**
   - Who authors the code the agent runs? (operator-reviewed / agent from trusted input / agent from *untrusted* input)
   - What must it legitimately reach? (files, network hosts, secrets)
   - Multi-tenant? (one user's agent output near another user's data)

2. **Pick the isolation rung** — lowest rung consistent with the worst-case author:

   | Rung | Mechanism | Fits |
   |------|-----------|------|
   | 1 | OS sandbox on dev machine (seatbelt/landlock, restricted FS+net) | Interactive dev tools, operator watching |
   | 2 | Container, non-root, no shared mounts | Server-side, trusted-input code, single-tenant |
   | 3 | MicroVM / hosted sandbox per session | Untrusted-input code, multi-tenant, anything internet-facing |

   Untrusted input anywhere upstream (see `injection-audit`) means the code author is effectively the attacker → rung 3.

3. **Write the reach policy, deny-by-default:**
   - Filesystem: explicit allowlist of readable/writable paths; workspace is writable, host homedir is not.
   - Network: explicit host allowlist (package registries, required APIs); no wildcard egress — open egress turns any injection into exfiltration.
   - Secrets: injected per-task with minimum scope and TTL; never in the sandbox image or a mounted env file.

4. **Set resource limits**: CPU time, memory, disk, wall-clock per execution, and max concurrent sandboxes. Agents in retry loops will find your missing limit.

5. **Decide teardown**: default to ephemeral (fresh sandbox per task); persistent sandboxes need a stated reason, an owner, and a max age.

6. **Verify the walls** from inside the sandbox with a canary script: read a host path outside the allowlist, call a non-allowlisted host, exceed the memory cap, exceed wall-clock. All four must fail, and the failures must appear in your logs/alerts.

## Output contract
A sandbox policy doc plus the enforcing config (container spec, sandbox profile, or provider settings): workload classification, chosen rung with rationale, FS/network/secrets allowlists, resource limits, teardown policy, and canary verification output.

## Checklist
- [ ] Isolation rung matches worst-case code author, not the happy path.
- [ ] FS and network are deny-by-default with written allowlists; no wildcard egress.
- [ ] Secrets scoped per task with TTL; none baked into image or mounts.
- [ ] CPU/memory/disk/wall-clock/concurrency limits all set.
- [ ] Canary verified all four walls from inside; escapes alert somewhere a human looks.
