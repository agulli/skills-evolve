---
name: handoff-protocol
description: Design the mechanics of multi-agent coordination — handoff conventions, shared vs. isolated state, message contracts between agents, and result-return — once you've chosen a multi-agent architecture. Use when building agent-to-agent handoffs, when a coordinator delegates to sub-agents, or when multi-agent runs lose context or duplicate work at the seams.
---

# Handoff Protocol

`agent-architecture` decides *whether* to go multi-agent; this skill designs *how the agents actually coordinate*. Multi-agent systems fail at the seams — the handoff that drops context, the sub-agent that re-derives what the caller already knew, the results that come back in an unusable shape. This is the rules-of-engagement layer (Culture Engineering would call it a protocol-class pattern).

## When to use
- Building handoffs between agents, or a coordinator delegating to sub-agents.
- Multi-agent runs lose context, duplicate work, or produce inconsistent results.
- Designing agent-to-agent (A2A) communication.

## When NOT to use
- Choosing whether to be multi-agent at all — that's `agent-architecture` (do it first; most "multi-agent" should be one agent).
- A single agent with tools — no handoff exists.

## Procedure

1. **Define the handoff contract explicitly.** Each handoff is an interface: what the calling agent passes (task, context, constraints, success criteria) and what the called agent returns (result, status, what it couldn't do). Write it down. Implicit handoffs — "the sub-agent will figure out what I meant" — are where context drops and work duplicates.

2. **Decide shared vs. isolated context per agent, deliberately.** Sub-agents can share the caller's context (coherent but expensive and leaky) or run isolated with only a briefing (cheap, focused, but must be told everything they need). Isolation is usually right — it's what makes sub-agents a context *saving* — but then the briefing must be complete. Choose per role; don't default.

3. **Make the briefing carry intent, not just the task.** A sub-agent performs better when it knows *why* — the larger goal and how its output will be used — so it connects its work to the right context instead of guessing. A bare task with no intent produces technically-correct-but-useless handoffs.

4. **Design the return contract for the caller's use.** Results come back in a shape the coordinator can act on — structured, with status (done / partial / failed / needs-input) and provenance — not a wall of prose the caller must re-parse. Tool-input-style structure beats free text at a handoff boundary (`tool-design` discipline applies).

5. **Handle async, long-lived, and failing sub-agents.** For sub-agents that run long or communicate over time, define the messaging contract and how the coordinator stays unblocked (async, not spawn-and-wait) — and what happens when a sub-agent fails, times out, or goes off-track (`reliability-engineering`, `state-management` for durable coordination). Long-lived sub-agents that keep context outperform re-spawning.

6. **Trace across the handoff.** Propagate a run id through every agent and sub-agent so the whole multi-agent trajectory is one reconstructable trace, not disconnected fragments (`agent-observability`). Multi-agent debugging is impossible without this — a failure in a sub-agent must be findable from the top-level run.

## Output contract
A handoff-protocol design: the per-handoff pass/return contracts, the shared-vs-isolated context decision per role with briefing requirements, intent propagation, the structured return + status contract, async/failure handling, and cross-agent tracing via a propagated run id.

## Checklist
- [ ] Every handoff has an explicit pass contract (task+context+constraints+success) and return contract.
- [ ] Shared-vs-isolated context chosen per role; isolated sub-agents get complete briefings.
- [ ] Briefings carry intent (the why), not just the task.
- [ ] Results return structured, with status and provenance, in the caller's usable shape.
- [ ] Async/long-lived/failing sub-agents handled; coordinator stays unblocked.
- [ ] Run id propagated across all agents for one reconstructable trace.
