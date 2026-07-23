# Judge Rubric Template & Worked Example

Copy this structure; replace the worked example (support-reply quality) with your domain. Keep ≤6 criteria, binary or 3-point scales only.

## Rubric structure

```markdown
# Rubric: <what is being judged>
Task context given to the judge: <1–2 sentences — what the system was asked to do>

## Criteria

### C1. <name> (binary)
PASS: <concrete, observable condition>
FAIL: <concrete, observable condition>

### C2. <name> (3-point)
2: <fully meets — observable>
1: <partially — observable, name the typical shortfall>
0: <misses — observable>
```

Rules that make criteria gradeable:
- Each criterion must be checkable **independently** — if grading C3 requires knowing C1's score, merge or split them.
- Describe **observable properties of the output**, never intent ("the answer cites the order ID" ✅, "the answer is helpful" ❌).
- Include one deceptive boundary per criterion in the examples: an output that *looks* passing but fails.

## Worked example — support-reply quality

### C1. Factual grounding (binary)
PASS: every factual claim about the customer's account/order appears in the provided context.
FAIL: any claim not present in context (invented dates, amounts, policies).

### C2. Resolves the actual question (3-point)
2: directly answers what was asked; nothing essential missing.
1: answers a related-but-different question, or answers partially.
0: doesn't address the question.

### C3. Actionability (binary)
PASS: the customer knows exactly what happens next (who acts, by when) or what they must do.
FAIL: ends without a next step when one is needed.

### C4. Tone within policy (binary)
PASS: no blame, no over-promising (no "guarantee", no compensation offers unless context authorizes).
FAIL: any of the above.

## Judge prompt skeleton

```text
You are grading a <domain> output against a rubric. You will see: the task,
the context the system had, and the output.

<rubric verbatim>

<2–3 scored examples spanning the range, including one deceptive case>

For each criterion: quote the evidence from the output FIRST, then assign
the score. Do not average across criteria. Output JSON:
{"C1": {"evidence": "...", "score": 0|1},
 "C2": {"evidence": "...", "score": 0|1|2}, ...}
```

## Calibration sheet format

One row per human-labeled item; compute agreement per criterion, not just overall — a vague criterion shows up as one bad column.

| item_id | C1 human | C1 judge | C2 human | C2 judge | … | notes |
|---|---|---|---|---|---|---|

Ship gate: κ ≥ 0.6 (or ≥80% agreement) on **every** criterion. A single criterion below the gate → rewrite that criterion, don't swap the judge model.
