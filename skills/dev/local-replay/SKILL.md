---
name: local-replay
description: Reproduce a single failing agent run locally and step through it, so a developer can debug one bad trajectory fast instead of guessing or re-running blind. Use when one specific run went wrong and you need to see why, when a user reports a bad interaction, or when iterating on a fix against a known failure.
---

# Local Replay

Debugging an agent by re-running it and hoping is slow and non-deterministic. This skill makes one failing run reproducible and inspectable on your machine — the fast inner loop for a *single* failure. It complements `trajectory-review` (which finds patterns across *many* traces); this is for the one run in front of you.

## When to use
- One specific run misbehaved and you need to see the exact cause.
- A user reports "the agent did X" and you have (or can get) the trace.
- Iterating on a fix and you want to re-test against the exact failing input.

## When NOT to use
- Diagnosing a *class* of failures across many runs — that's `trajectory-review`.
- No trace and no way to reconstruct the input — fix `agent-observability` first so runs are replayable.

## Procedure

1. **Capture the run as a replayable fixture.** From the trace (`agent-observability`), reconstruct the exact context window the model saw: system prompt version, inputs, retrieved memories/docs, tool results, and model+config. Save it as a fixture. If you can't rebuild the context window, the observability gap is the real bug — stop and fix that first.

2. **Freeze nondeterminism.** Pin the model version and config from the trace; where the stack allows, fix seed/temperature. Stub the tools to return the *recorded* results, so replay follows the original path instead of taking a new one. The goal is a run that reproduces the failure every time.

3. **Find the first divergence by stepping, not staring.** Replay turn by turn and locate the earliest point where behavior went wrong — wrong tool, misread result, missing fact, bad parameter (same first-divergence discipline as `trajectory-review`, applied to one run). Everything after the divergence is symptom.

4. **Form one hypothesis and change one thing.** At the divergence, change exactly one variable — a prompt line, a tool description, a retrieved doc, the model — and replay. One change per iteration keeps the signal attributable. Resist fixing three things and rerunning once.

5. **Confirm the fix on the fixture, then guard it.** The divergence must no longer occur (not merely a lucky pass). Then promote the fixture to a regression case in `eval-harness` so this exact failure can never silently return.

6. **Keep the loop tight.** Replay must be a single command against the fixture with no external calls (tools stubbed, network off). If a replay takes minutes or hits live services, the inner loop is broken — that's the thing to fix.

## Output contract
A saved replay fixture (reconstructed context + pinned model/config + stubbed tool results), the identified first divergence, the one-variable fix confirmed by re-replay, and a regression case added to `eval-harness`.

## Checklist
- [ ] Failing run reconstructed as a fixture that reproduces the failure every time.
- [ ] Model/config pinned; tools stubbed to recorded results; nondeterminism frozen.
- [ ] First divergence located by stepping, not guessing.
- [ ] Fix changed one variable at a time; divergence confirmed gone on replay.
- [ ] Fixture promoted to an `eval-harness` regression case.
- [ ] Replay runs in one command with no live/network calls.
