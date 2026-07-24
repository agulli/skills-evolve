---
name: llm-judge
description: Design and calibrate an LLM-as-judge grader — rubric, prompt, bias controls, and validation against human labels. Use when eval outcomes can't be checked programmatically, when judge scores disagree with human judgment, or when setting up pairwise model comparisons.
---

# LLM Judge Design

A judge is a measurement instrument: it needs a rubric, calibration against ground truth, and known error bars. An uncalibrated judge is a random number generator with confident formatting.

## When to use
- Eval tasks whose success can't be checked programmatically (writing quality, helpfulness, reasoning soundness).
- Judge scores don't match what humans think (calibration drift).
- Comparing two models/prompts pairwise at scale.

## When NOT to use
- The outcome IS programmatically checkable (tests pass, JSON valid, state correct) — code beats judges; use it and skip this skill.

## Procedure

1. **Write the rubric before the prompt.** Decompose "good" into 3–6 named, independently checkable criteria, each with a concrete description of what earns each score. Binary or 3-point scales per criterion — 1–10 scales produce noise centered on 7.

2. **Choose the judgment mode:**
   - **Criterion scoring** — absolute quality tracking over time.
   - **Pairwise A/B** — comparing two systems; far more reliable than absolute scores, use whenever you have two candidates.
   - **Rubric + reference answer** — tasks with a gold answer needing semantic (not exact) match.

3. **Build the judge prompt**: the rubric verbatim, 2–3 scored examples spanning quality range (including one deceptive case — plausible-looking but wrong), instruction to justify *before* scoring, and a structured output schema (per-criterion score + one-line evidence).

4. **Control the known biases**: for pairwise, don't just randomize positions — **run each comparison twice with positions swapped**; if the two passes disagree, the item is a TIE at low confidence, full stop (a per-item consistency check catches what dataset-level randomization only averages away). Cap length's influence by rubric criterion (verbosity bias); judge model ≠ judged model where possible (self-preference); scrub model/system names from transcripts (brand bias); and require the judge to cite specific evidence from the response, not just justify — confident, authoritative tone otherwise inflates scores (authority bias).

5. **Calibrate against humans.** Label 30–50 items yourself (or with the domain owner). Measure judge-human agreement with the metric that fits the scale: Cohen's κ or plain agreement % for binary/categorical; **Spearman's ρ or Kendall's τ for ordinal scales** (a 4-vs-5 disagreement is not the same failure as 1-vs-5, and κ can't tell them apart). Ship at κ ≥ 0.6 / agreement ≥ 80%; below that, fix the *rubric* first — disagreement is usually a vague criterion, not a weak judge model. Look for *systematic* disagreement patterns (the judge always harsher on one category), not just the aggregate rate. Report every eval score with this agreement number attached.

6. **Monitor drift**: re-run the calibration set whenever the judge model version changes, and quarterly regardless. For high-stakes gates, use 3-judge majority or escalate low-confidence/split verdicts to a human queue.

## Output contract
A judge package in the repo: rubric doc, judge prompt with examples, bias controls noted, the human-labeled calibration set, agreement stats (κ / %), and the drift re-check schedule. Wired into `eval-harness` as a grader.

## Checklist
- [ ] Rubric has ≤6 independent criteria on binary/3-point scales.
- [ ] Pairwise used where two candidates exist; each comparison run twice with positions swapped, disagreement → TIE.
- [ ] Judge cites specific evidence from the response, not just a justification (authority-bias control).
- [ ] Judge justifies before scoring; output is structured and parseable.
- [ ] Calibrated on ≥30 human-labeled items; κ ≥ 0.6 or agreement ≥ 80%.
- [ ] Scores always reported with the agreement number; drift re-check scheduled.
