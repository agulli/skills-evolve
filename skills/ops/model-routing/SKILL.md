---
name: model-routing
description: Route each request or step to the right model by difficulty, cost, latency, and a quality floor — with fallback when the chosen model fails or refuses. Use when an agent spans cheap and frontier models, when one model for everything is over- or under-powered, or when you need provider failover.
---

# Model Routing

Using one model for every step is either overpaying (frontier model on trivial classification) or under-delivering (small model on hard reasoning). Routing sends each unit of work to the cheapest model that clears a quality floor, and fails over when a model is down or refuses. It's a standalone concern that `cost-optimization` and `latency-optimization` both lean on, distinct from `model-migration` (a one-time generational move).

## When to use
- An agent uses steps of varying difficulty and you're paying frontier prices for all of them.
- A single model choice is over-powered for easy work or under-powered for hard work.
- You need failover across models/providers for reliability.

## When NOT to use
- A single-step agent where one model is clearly right — routing is overhead.
- Moving the *whole* agent to a new generation — that's `model-migration`.

## Procedure

1. **Slice work by difficulty, backed by evals.** Identify the classes of step the agent performs (classify, extract, format, plan, hard-reason) and measure each model's quality on each class with `eval-harness`. Routing decisions come from those per-class numbers, not intuition — "the small model is fine for extraction" is a claim to verify, not assume.

2. **Set a quality floor per class and route down to it.** For each class, route to the cheapest/fastest model that still clears the floor. Classification, extraction, and formatting rarely need the frontier model; planning and hard reasoning usually do. The floor is the guardrail that keeps cost/latency routing from quietly degrading quality.

3. **Prefer static routing by task type; add dynamic only if it pays.** Route by *step type* first — it's simple, cacheable, and debuggable. Only add per-request difficulty classification (a cheap model deciding the route) if the static split leaves real money or latency on the table; it adds a call and a failure mode.

4. **Design fallback and failover.** When the chosen model times out, rate-limits, errors, or refuses (`reliability-engineering`), route to an alternate — a different model or provider — rather than failing the step. Define the fallback order per class. Provider failover is often the real reason to route at all.

5. **Watch the cache and context cost of switching.** Prompt caches are per-model and switching models mid-conversation invalidates them; a route that saves on model price but forces cold cache-writes every turn can cost more (`cost-optimization`). Route at boundaries, or spawn a sub-agent on the cheaper model rather than swapping mid-loop.

6. **Monitor routing quality and re-tune.** Track per-route quality, cost, and latency, and the fallback rate (`agent-observability`). Model releases shift the right routing table — re-run the per-class eval when a model changes (ties to `model-migration`). A routing table set once and never revisited drifts out of optimal.

## Output contract
A routing policy: the step-class taxonomy with per-model per-class eval scores, the quality floor and chosen model per class, static-vs-dynamic decision, the fallback/failover order, cache-aware switching rules, and monitored per-route quality/cost/latency with a re-tune trigger.

## Checklist
- [ ] Step classes defined; per-model per-class quality measured via evals.
- [ ] Quality floor set per class; cheapest model that clears it is chosen.
- [ ] Static-by-task-type routing preferred; dynamic added only where it pays.
- [ ] Fallback/failover order defined per class for timeout/limit/error/refusal.
- [ ] Cache/context cost of model switching accounted for; route at boundaries.
- [ ] Per-route quality/cost/latency and fallback rate monitored; re-tune on model change.
