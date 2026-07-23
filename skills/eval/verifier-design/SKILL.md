---
name: verifier-design
description: Design and stress-test the pass/fail check (registrar, deterministic assertion, or grader) behind an eval — not the tasks, the check itself. Use when writing any programmatic success criterion, when an eval shows a surprising or dramatic effect size, or before trusting a result that will change a shipping decision.
---

# Verifier Design

An eval is only as trustworthy as its verifier. A verifier that rewards the wrong thing — exact phrasing, keyword counts, citation frequency, tool-call counts — produces a confident, replicable number that is confidently wrong. Replication is not correctness: a broken verifier reproduces its own bug just as reliably as a real effect reproduces itself.

## When to use
- Writing any programmatic/deterministic pass-fail check for an eval task.
- An eval result shows a large or surprising effect — before trusting it enough to act on it.
- A verifier's pass rate looks suspiciously high or low, or diverges sharply between two similar conditions.

## When NOT to use
- Designing the task set itself (use `eval-harness`).
- The check requires subjective/semantic judgment, not deterministic matching (use `llm-judge`).
- Debugging a specific failed run after the fact (use `trajectory-review`).

## Procedure

1. **Name the actual capability before writing the check.** Write one sentence: "Pass iff [the independently observable outcome that constitutes success]." If the sentence names a literal string, keyword, or count instead of an outcome, that's the first sign of trouble — ask whether the literal thing IS the capability (e.g., valid JSON syntax) or just a proxy for it (e.g., "mentions the word 'secure'").

2. **Never reward what you didn't intend to test.** Don't score on response length, keyword counts, citation frequency, exact phrasing, or tool-call counts unless one of those literally constitutes the capability under test. A skill that instructs paraphrase, compaction, or reformatting will be punished by any check that requires verbatim text — the check needs to tolerate the transformation the skill is supposed to produce.

3. **Match evidence to outcome type.** Objective facts (file exists, test passes, valid schema, code executes) get deterministic checks. Semantic claims (is this supported by the source, is this a good summary) get an LLM judge (see `llm-judge`) — never a keyword-overlap proxy standing in for semantic judgment. For extraction/compaction tasks, check that the load-bearing content (numbers, IDs, dates — the actual checkable trace) survives, not that the surrounding prose matches verbatim.

4. **Write one should-pass and one should-fail fixture before running anything for real.** Construct a plausible completion a competent agent would produce (expect PASS) and a plausible-but-wrong one (expect FAIL — dropped fact, wrong number, unresolved contradiction, missing citation). Run the checker against both. If either gives the wrong verdict, fix the check — don't expand the task matrix first, and don't spend real API budget against an unverified check.

5. **Don't trust the target's self-report as its own proof.** Never accept "I called the tool" or "the file was created" as ground truth — check the actual execution trace, file state, or tool-call log. This is the same failure mode `silent-failure-audit` targets in production; catch it in the verifier at design time instead.

6. **When a result surprises you, read the raw completions before believing the number.** A large or unexpected effect — especially one that replicates across models, days, or samples — is exactly when it's tempting to trust the aggregate and skip inspection. Pull 5–10 real WITH/WITHOUT completions and read them. A verifier bug replicates its bug just as reliably as a real effect replicates; only reading actual output tells them apart.

7. **Re-check after every fix.** Any edit to a verifier invalidates every result it ever produced. Re-run the fixtures, then re-measure for real before updating any downstream decision — a routing tier, a ship gate, a "this doesn't work" conclusion.

## Output contract
A verifier with: (1) the one-sentence pass condition, (2) a should-pass and a should-fail fixture committed alongside it, (3) a note on which evidence type it checks (deterministic fact vs. judged semantic) — and, once wired into a harness, a self-check gate that runs the fixtures before any real measurement spend.

## Anti-rationalization

| The agent will try to… | The correct response is… |
|---|---|
| "The effect size is huge, it must be a real defect" | A huge, surprising effect is the strongest reason to suspect the verifier, not the weakest. Read raw completions before acting on it. |
| "It replicated across two models/days, so it's confirmed" | Replication proves the measurement is consistent, not that it's correct. A broken verifier replicates its own bug with the same reliability as a real effect. |
| "Exact phrase match is the simplest way to check the fact survived" | Exact match can't tell paraphrase from information loss. If the skill's job is to compact/reword, the check must tolerate that transformation. |
| "I'll add more tasks to see if the signal holds up" | Expanding the task matrix on a broken verifier just produces more of the same wrong answer, faster. Fix the verifier first. |
| "The agent said it passed, that's good enough" | Self-report is not ground truth. Check the actual execution trace / file state / registrar output. |

## Checklist
- [ ] One-sentence pass condition names an outcome, not a proxy (keyword/length/exact phrase), unless the proxy IS the capability.
- [ ] Should-pass and should-fail fixtures written and checked before any real measurement.
- [ ] Deterministic checks used for objective facts; LLM judge only for semantic claims.
- [ ] Verifier tolerates whatever transformation the skill under test is supposed to produce (paraphrase, compaction, reformatting).
- [ ] Any surprising/large effect size triggers a raw-completion read before it's trusted.
- [ ] Every verifier edit triggers a re-check of fixtures + a re-measurement before downstream decisions change.
