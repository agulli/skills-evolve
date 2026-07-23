# Skill-Culture Simulator

A **self-contained** validator for this repo's core claims — that the skills do something good, that their evaluation is trustworthy, and that their evolution-as-culture is valid. Pure Python **stdlib, no dependencies, deterministic per seed, no network in Layer A**. Nothing here imports from or points at any other repo.

It answers three questions, each with the right tool:

| | Hypothesis | How it's tested |
|---|---|---|
| **H1** | Do these 54 skills actually make a small-model agent *better*? | Layer B measures real WITH-vs-WITHOUT effect sizes on held-out tasks |
| **H2** | Is the evaluation *good* — does "passed the eval" mean genuinely better? | Layer B measures the eval's false-positive rate; Layer A sweeps how eval quality changes the outcome |
| **H3** | Is the evolution-as-culture *valid* — does the Canon promote good and reject bad? | Layer A runs 100 adopters against **sealed ground truth** and scores promotions |

## The design: measure → calibrate → simulate

Splitting by cost is the whole trick. LLMs are needed only to learn *what the skills actually do*; the population dynamics don't need them.

- **Layer B — measure (real LLMs, small n).** `measure.py` runs Haiku and Gemini-3.5-flash-lite on a held-out task suite, **with vs without** each skill, graded by an **independent registrar** (a programmatic check the agent never sees). Out come two numbers per skill per model: the **effect size** (H1) and the **eval false-positive rate** (H2).
- **Layer A — simulate (deterministic, 100+ nodes, free).** `run.py` runs the adopter population against a **sealed ground-truth world**. Feed Layer B's measured effect sizes in as the world's true effects and the population dynamics run on reality instead of synthetic numbers.

Reality calibrates the parameters; the cheap sim scales the population. You spend tokens only where reality is actually required.

## Run it

```bash
# Layer A — the mechanism, against sealed ground truth (no keys, ~8s)
python3 -m simulator.run --scenario all          # baseline, adversarial, churn, hard, + H2 sweep
python3 -m simulator.run --scenario eval-sweep   # H2 on its own
python3 -m simulator.run --scenario adversarial --seed 42 --nodes 100 --rounds 80 --json

# Layer B — measure real skill efficacy + eval-validity
python3 -m simulator.measure --model mock  --runs 8              # no keys, synthetic signal
python3 -m simulator.measure --model haiku --runs 5 --out haiku.json   # needs ANTHROPIC_API_KEY
python3 -m simulator.measure --model gemini --runs 5 --limit 6         # needs GEMINI_API_KEY

# model ids are env-overridable (Gemini's flash-lite string changes across releases):
HAIKU_MODEL=claude-haiku-4-5 GEMINI_MODEL=gemini-2.5-flash-lite python3 -m simulator.measure --model gemini
```

The Haiku and Gemini adapters are wired (Anthropic + google-genai SDKs). A call that fails (no key, transient error) warns and returns empty rather than killing the run. `--limit N` caps tasks for a cheap smoke test; `--out` saves the JSON so its `skill_effects` can feed `World.build`.

## What the numbers mean

- **H3 (culture validity)** — per scenario: **precision** (of promoted skills, how many are truly good), **recall**, **`malicious_established`** (planted-harmful skills that reached the Canon — must be **0**), and the **canon-value curve** (the true uplift a fresh adopter gets from today's Canon, per model tier). The weak tier's lower uplift *is* the small-model ceiling.
- **H2 (eval validity)** — the eval-sweep holds everything fixed and varies only the eval. The headline result: a **`weak`** eval (poor specificity) is largely *survivable* because independent errors average out across nodes, but a **`blindspotted`** eval — even with *better* raw specificity — drops precision and lets malicious skills through, because its errors are **correlated** across the population. **It is error *correlation*, not error *rate*, that breaks the culture.** That is the single most important thing this simulator has to say about "is the eval good enough."
- **H1 (skills help)** — in Layer A it's the world's effect sizes; the canon-value curve is the realized "skills help" outcome. Layer B replaces the synthetic effects with measured ones.

## Files

| File | Role |
|---|---|
| `world.py` | Sealed ground truth — skills × task-classes × model-tiers → true effects; malicious/null; generation churn. The oracle. |
| `stats.py` | Paired A/B trial; Beta-posterior promotion tail (regularized incomplete beta). |
| `evalgate.py` | The eval-harness modeled as a noisy classifier with an independent + **correlated** error split (the H2 lever). |
| `nodes.py` | The 100 adopters — honest / optimist (pub-bias) / gamer / sybil, split across two model tiers and six task-classes. |
| `commons.py` | Append-only ledger; shared→proposed→Canon promotion with cross-org + cross-class thresholds, org-jackknife, and a human block/remove backstop. |
| `run.py` | Round loop, scenarios, metrics, CLI. Seeds from the real 54 skill names. |
| `tasks.py` | Held-out tasks with **objective registrars** (planted-element pattern) — the anchor that makes H1/H2 non-circular. |
| `measure.py` | Layer B — real-LLM effect + eval measurement; mock mode + Haiku/Gemini adapter stubs. |

## How many tasks? (one is not enough)

A single task can't answer "does this skill help": LLM outcomes are noisy, and the effect swings by task (some tasks the model already nails → null; some are perfectly suited → large). You're estimating the *mean* effect per `(skill × class × model)`, so you need a spread.

`measure.py` reports a **paired (McNemar) 95% CI on each skill's effect and a `significant` flag** (CI excludes zero). Significance responds to sample size exactly as it should — in mock runs, **1/7 skills are significant at 2 runs, 3/7 at 8 runs**, and the well-covered skills (`secrets-management`, `context-engineering` at n≈40–64) reach significance while the thin ones (`eval-harness`, `injection-audit` at n=10) stay "not yet." That flag *is* the "not enough data" signal, made mechanical.

The suite ships with **36 varied tasks** (secrets 8, context 8, prompt-arch 6, grounding 6, tool-design 4, eval 2, injection 2). **Target: ~8–15 tasks per skill, 3–5 paired runs each (~30–50 paired observations/skill)** — enough to detect a ~10pp effect. Across ~10 high-traffic skills that's ~100–150 tasks; trivial on Haiku/flash-lite. Grow `tasks.py` toward that (keep tasks *structurally varied*, not clones — variety across tasks is what makes the mean effect real).

## Methodology guards (why this isn't circular)

1. **Ground truth is sealed.** The pipeline never reads `world.py`'s effects; only noisy trials sample from it, and metrics compare against it afterward. This is the only way to say "the culture was right/wrong."
2. **The registrar is independent.** In Layer B, success is decided by a programmatic check the agent never sees — not by the agent judging itself. That anchor is what lets us *validate the evaluator* (H2) rather than trust it.
3. **Contamination is a null result, not a bug.** If a model already does a task without the skill, that skill's measured effect is ~0 — correctly reported as "no help here."
4. **Two vendors on purpose.** Haiku and Gemini are two independent tiers; a norm confirmed by one that holds on the other is the real "culture, not folklore" test, and it exercises correlated-blind-spot risk across models.

## Status & next steps

Layer A is complete and validated. Layer B is wired end to end: **36-task objective suite**, **real Haiku + Gemini adapters** (Anthropic + google-genai), paired-CI significance, and mock mode for keyless runs. Remaining to get real numbers:

1. **Set keys** (`ANTHROPIC_API_KEY`, `GEMINI_API_KEY`) and confirm `GEMINI_MODEL` is the exact current flash-lite id.
2. **Measure with both models** — `--model haiku` and `--model gemini` — and grow `tasks.py` until the high-traffic skills read `significant: true`.
3. **Feed `skill_effects` into `World.build`** and re-run the population scenarios on real effect sizes; check whether the eval false-positive rate *repeats across both models* — a cross-model blind spot is the H2 failure the population sim then propagates.
