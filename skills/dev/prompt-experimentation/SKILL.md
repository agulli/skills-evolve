---
name: prompt-experimentation
description: Run a disciplined prompt/config experiment — variants, a fixed task set, one metric, and a kept winner — so prompt changes are decisions with evidence instead of vibes. Use when trying prompt or config variants, when "this wording feels better," or when tuning effort/model/temperature against a real task set.
---

# Prompt Experimentation

Most prompt iteration is one-shot guessing: change wording, run once, keep it because the single output looked good. This skill makes prompt changes small controlled experiments so you keep what actually wins. It's the fast experimentation loop; `prompt-architecture` designs the prompt's *structure*, `eval-harness` is the release gate this borrows from.

## When to use
- Trying two or more prompt/config variants and deciding which to keep.
- "This phrasing feels better" — before shipping the feeling.
- Tuning effort, model, or temperature against real tasks.

## When NOT to use
- Restructuring a prompt's sections/budget — that's `prompt-architecture`.
- The change is a bug fix with a known-correct answer — just `local-replay` it.

## Procedure

1. **Fix the task set before touching the prompt.** Pull 5–20 representative tasks (from real usage, via `feedback-harvesting` or logs). Freeze them. Choosing tasks *after* seeing variant outputs is how you fool yourself — you'll pick tasks the variant you already like happens to win.

2. **Pre-register one metric and the decision rule.** State what "better" means (a programmatic check, an `llm-judge` rubric, or human rating) and the bar to switch ("variant wins if it beats baseline on the metric with no regression on any task"). One primary metric — multiple metrics let you cherry-pick a winner after the fact.

3. **Change one variable per variant.** Each variant differs from baseline in exactly one thing — one instruction, one example, one config value. If a variant changes three things and wins, you've learned nothing about which one mattered.

4. **Run with honesty about noise.** N≥3 runs per (variant × task) because outputs are stochastic; keep temperature/config fixed except the variable under test; report the metric with variance, not the single best output. A one-run win is noise wearing a result's clothes.

5. **Prefer pairwise where you're judging quality.** For subjective quality, an A/B pairwise judgment (this vs. baseline, positions randomized) is far more reliable than absolute scores — see `llm-judge`. Blind the variant labels so brand/length bias doesn't leak in.

6. **Keep the winner and the receipt.** Commit the winning variant *with* the experiment record — task set, metric, per-variant scores with variance, and the decision. When someone later asks "why is the prompt worded this way," the receipt answers. Promote the task set toward `eval-harness` so the win is protected from future regressions.

## Output contract
An experiment record: the frozen task set, the pre-registered metric + decision rule, the variants (each one-variable), per-variant scores with variance over N≥3 runs, and the kept winner committed with its receipt.

## Checklist
- [ ] Task set frozen before variants were written; drawn from real usage.
- [ ] One primary metric + switch rule pre-registered before running.
- [ ] Each variant differs from baseline by exactly one variable.
- [ ] N≥3 runs per variant×task; variance reported, not the best single output.
- [ ] Quality judgments done pairwise with randomized positions and blinded labels.
- [ ] Winner committed with the experiment receipt; task set fed toward `eval-harness`.
