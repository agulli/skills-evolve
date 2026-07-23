---
name: model-migration
description: Move an agent to a new model generation without regressing — re-baseline evals, re-tune prompts for the new model's behavior, re-check breaking API changes and cost/latency, and roll out safely. Use when upgrading the model behind an agent, when a provider deprecates a model, or when a new model promises gains you want to capture.
---

# Model Migration

Swapping the model behind an agent is not a config change — a new generation follows instructions differently, calibrates length and tool use differently, may drop parameters, and re-tokenizes text so budgets shift. A prompt tuned for the old model can regress on the new one. This skill migrates deliberately. It's pointed for a self-evolving library: Culture Engineering's law is that knowledge decays each model generation, so migration is a recurring event, not a one-off.

## When to use
- Upgrading the model behind an agent to a newer generation.
- A provider deprecates or retires the model you're on.
- A new model promises quality/cost/latency gains worth capturing.

## When NOT to use
- Routing *between* models at runtime by task — that's `model-routing`.
- No model change — obviously.

## Procedure

1. **Re-baseline evals on the new model first.** Before changing anything else, run the existing `eval-harness` on the new model as-is. This is the migration's ground truth: it shows what regressed and what improved from the raw swap, separating model change from prompt change. Migrating without a re-baseline is flying blind.

2. **Check breaking API changes.** New generations remove or change parameters (thinking/effort config, sampling params, prefill support, tool versions), change defaults, and re-tokenize (so `max_tokens` and context budgets shift). Read the provider's migration notes; fix what now errors *and* what silently changed behavior. Never guess model IDs — use the exact current strings.

3. **Re-tune the prompt for the new model's behavior, not the old one's.** New models are often more literal, calibrate verbosity to task, reach for tools differently, and may need less aggressive instruction. Prompt scaffolding written to overcome the old model's quirks can now over- or under-trigger. Treat prompt changes as `prompt-experimentation` against the re-baseline, one variable at a time — and don't assume old "be concise"/"always use the tool" lines still help.

4. **Re-measure cost and latency.** Per-token pricing, tokenization, and speed all change; a migration can shift the cost/latency profile even at equal quality. Re-baseline both (`cost-optimization`, `latency-optimization`) rather than assuming — and re-tune effort/config for the new model's curve.

5. **Handle thinking/reasoning and context-window changes.** If the new model changes how reasoning is configured or returned, or offers a different context window, adjust `context-engineering` budgets and any code that reads reasoning output. These are common silent regressions in a migration.

6. **Roll out via deployment, not a flip.** Migrate behind `deployment` — shadow the new model against the old on real traffic, canary, watch the promotion metrics, keep rollback to the old model one action away. A model swap is exactly the high-risk change shadow/canary exists for.

## Output contract
A migration record: the raw re-baseline (regressions/improvements from the swap), the breaking-change fixes, the prompt re-tuning experiments with before/after, the re-measured cost/latency, thinking/context adjustments, and the shadow/canary rollout outcome with rollback ready.

## Checklist
- [ ] Evals re-baselined on the new model before other changes.
- [ ] Breaking API/parameter/tokenizer changes checked and fixed (exact model IDs used).
- [ ] Prompt re-tuned for the new model via one-variable experiments against the re-baseline.
- [ ] Cost and latency re-measured, not assumed; effort/config re-tuned.
- [ ] Thinking/reasoning and context-window changes handled.
- [ ] Rolled out via shadow/canary with one-action rollback to the old model.
