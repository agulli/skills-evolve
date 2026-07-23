---
name: reliability-engineering
description: Make an agent survive the failures of everything it depends on — model timeouts/rate limits, tool errors, provider outages — with retries, fallbacks, circuit breakers, and graceful degradation. Use when an agent runs in production, when a dependency's failure takes the whole agent down, or when transient errors surface to users.
---

# Reliability Engineering

An agent is a distributed system whose dependencies — the model, tools, providers — all fail routinely: timeouts, rate limits, 5xxs, outages. Without deliberate handling, one flaky dependency takes the whole run down or surfaces raw errors to users. This skill makes failure survivable. It's distinct from `agent-incident` (responding when something's wrong now) — this is the design that prevents most incidents.

## When to use
- An agent runs in production against models, tools, or external services.
- A single dependency's hiccup takes the whole agent down or reaches the user raw.
- Transient errors (rate limits, timeouts) are a recurring pain.

## When NOT to use
- A local, dependency-free, best-effort script where failure is fine.
- Responding to an active incident — that's `agent-incident`.

## Procedure

1. **Enumerate dependencies and their failure modes.** List everything the agent calls — model, each tool, each external service — and how each fails: timeout, rate limit (429), transient 5xx, hard error, slow-but-succeeds, wrong-but-succeeds. You can't make failures survivable that you haven't named.

2. **Classify retryable vs. terminal, and retry only the former.** Transient failures (timeout, 429, 5xx) get retried with exponential backoff and jitter; deterministic failures (bad input, auth, 4xx) do not — retrying them just wastes time and money. Cap retries and total wall-clock so a stuck dependency can't loop forever (`tool-design` error contracts feed this).

3. **Add fallbacks for critical paths.** For a dependency whose failure would break the task, define the fallback: an alternate model/provider (`model-routing`), a cached or stale result, a degraded-but-useful answer, or a clean "can't do this right now." A critical dependency with no fallback is a single point of failure by omission.

4. **Break circuits on repeated failure.** When a dependency is failing persistently, stop hammering it — trip a circuit breaker so calls fail fast to the fallback instead of piling up timeouts and burning budget/latency. Half-open retry to detect recovery. This protects both the agent and the struggling dependency.

5. **Degrade gracefully, don't collapse.** Partial capability beats total failure: if one tool is down, can the agent still do the rest and tell the user what it couldn't? Design the reduced-function mode explicitly rather than letting one error abort everything. Pair with durable state (`state-management`) so a mid-run failure resumes rather than restarts.

6. **Test with injected failures.** Reliability that isn't tested against real failure is a hypothesis. Inject timeouts, 429s, outages, and slow responses (fault injection) and confirm the agent retries correctly, falls back, breaks circuits, degrades, and never surfaces a raw stack trace. Track a dependency-failure-survival metric (`agent-observability`).

## Output contract
A reliability design: the dependency × failure-mode map, the retryable/terminal classification with backoff/caps, fallbacks for critical paths, circuit-breaker thresholds, the graceful-degradation modes, and fault-injection test results. Enforcement lands as code/config.

## Checklist
- [ ] Every dependency's failure modes enumerated.
- [ ] Retryable vs. terminal classified; backoff+jitter, retry and wall-clock caps set.
- [ ] Critical-path dependencies have a defined fallback.
- [ ] Circuit breakers trip on persistent failure and probe for recovery.
- [ ] Graceful-degradation mode defined; mid-run failures resume via durable state.
- [ ] Fault injection confirms survival; no raw errors reach users; survival metric tracked.
