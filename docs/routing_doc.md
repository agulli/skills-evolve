# Skill Routing

> **Source of truth:** the operational router — the actual table the agent loads on every turn — is [`skills/ROUTING.md`](../skills/ROUTING.md). That file is authoritative and is what the installer wires in. This document is a conceptual companion; **when the two differ, `skills/ROUTING.md` wins.**

This document explains the routing mechanism (The "When"). 

## The Core Concept
The library is designed to be **model-routed, not human-remembered**. Three layers make that reliable, each catching what the previous one misses:

1. **Trigger contracts** — every skill's `description` states what it does *and the behavioral moment that should trigger it*, in the vocabulary users actually type. The harness matches on this automatically once a skill is installed.
2. **The router** — `skills/ROUTING.md` is a compact, always-loaded table mapping observable user behavior to a skill.
3. **Deterministic hooks** — for gates that must never depend on model judgment (e.g., eval gate before prompt commits), these are enforced by your project's harness/CI.

## Autonomy Tiers
The router operates on three tiers to determine how much friction to introduce before acting. Humans stay in the loop by tier, not by being asked constantly:

- **AUTO** — invoke immediately; announce in one line ("running trajectory-review on this trace"). Used for read-only or diagnostic skills.
- **PROPOSE** — name the moment and the skill, state what it produces, and proceed unless the user redirects. Used for skills that create work products or change scope.
- **ASK** — explicit confirmation required. Used for skills that gate, block, or restructure things the user owns.

Explicit human invocation (e.g., typing `/skill-name`) or refusal always overrides the router.

## Why Log Decisions?
Every routing decision (accept/override/skip) is logged as data locally. Overrides and misses are not failures — they are the training signal that the `routing-tuner` skill uses to tighten this table over time. Autonomy without this log cannot improve; it only repeats.

*For the actual routing rules payload injected into your agent's system prompt, see [skills/ROUTING.md](../skills/ROUTING.md).*
