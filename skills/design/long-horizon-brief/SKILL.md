---
name: long-horizon-brief
description: Write the task brief for an autonomous long-running agent — an exact success predicate over the artifact, an explicit list of near-misses that don't count, enumerated failure modes, and a return condition — so hours of unsupervised work can't end in an answer-shaped artifact that solves nothing. Use before launching any multi-hour/overnight autonomous run, when delegating open-ended work to parallel workers, or after an autonomous run returned something plausible that didn't actually solve the problem.
---

# Long-Horizon Task Brief

Everything that makes a long autonomous run productive — persistence, autonomy, parallelism — also raises the cost of a weak specification. An agent under persistence pressure with a vague brief produces an **answer-shaped artifact**: something formatted like a solution that doesn't solve the problem, discovered only after the compute is spent. The brief is the contract that makes "done" checkable before the run starts, not negotiable after it ends.

This sits between `requirements-interrogation` (extracting requirements from a human) and `prompt-architecture` (the static system prompt): it specifies *one autonomous work item*. The failure it prevents is the one `silent-failure-audit` catches after the fact — prevention beats detection by hours of compute.

## When to use
- Launching an agent on multi-hour or overnight autonomous work.
- Delegating open-ended work to parallel workers (pair with `handoff-protocol` for the mechanics).
- A previous autonomous run returned a plausible-looking artifact that didn't actually solve the problem.

## When NOT to use
- Interactive, short-leash tasks where you review every few steps — the overhead isn't warranted.
- Requirements are still unknown — that's `requirements-interrogation`, first.
- The success criterion is already a machine-checkable test — just use it (`eval-harness`); a brief adds nothing.

## Procedure

1. **Define every load-bearing term, including degenerate cases.** Any term the success judgment depends on gets a definition, and the definition names its edge cases explicitly — the loopholes an artifact could technically satisfy while missing the point. Undefined terms become whatever interpretation is cheapest under pressure.

2. **Write ONE exact success predicate — over the artifact, not the effort.** A single statement, quantifiers and scope explicit, that an adversarial reader could apply to the returned artifact and answer yes/no without asking you. Never a predicate over confidence ("agent is satisfied"), effort ("spent 4 hours"), or narrative ("made significant progress").

3. **Enumerate what does NOT count.** List the plausible near-misses explicitly: partial progress, a solution to a narrowed version of the problem, a reduction to a different unproven claim, verification of a few easy cases presented as the general result. Every near-miss not on this list is one the agent can legitimately return. This list is to the brief what negative-constraint tests are to `eval-harness`.

4. **Enumerate domain-specific failure modes.** The ways a candidate can *look* right while being wrong in this particular domain — circular reasoning presented as proof, benchmark contamination, a fix that only works on the demo input. This is the auditor's checklist; without it, review defaults to "seems plausible."

5. **Specify the return condition and effort floor.** When the agent should stop and return: predicate satisfied, a listed failure mode conclusively hit, or budget exhausted — with a minimum effort floor so it doesn't return "couldn't do it" after one shallow attempt. Pair every persistence instruction with a verification gate: "keep trying" without "and re-verify each attempt against the predicate" is how success signals get gamed.

6. **For parallel workers, force structural diversity.** Keep early workers blind to your favored approach; group attempts by underlying idea (not surface wording) in an explicit registry; mark dead routes as requiring a *materially new mechanism* to reopen; defer cross-pollination until independent attempts have exposed real strengths. Otherwise N workers converge on one approach and you've paid N times for it.

7. **Adversarially review the brief before launch.** Check: Can an adversarial reader unambiguously apply the success predicate to an artifact? Is every plausible near-miss explicitly non-counting? Does the auditor have the failure-mode list? Is the return condition a predicate over the artifact? Any "no" is a defect in the brief — cheaper to fix now than after the run (`adversarial-review` on the brief itself for high-stakes runs).

## Output contract
The brief document: definitions with degenerate cases, the single success predicate, the non-counting list, the failure-mode checklist, return condition + effort floor, and (for parallel runs) the diversity policy — plus the pre-launch adversarial review's answers.

## Anti-rationalization

| The agent will try to… | The correct response is… |
|---|---|
| "The task is clear enough from the one-line description" | Clear-to-you is not checkable-by-an-adversary. Hours of autonomous compute against an ambiguous target produces an answer-shaped artifact. |
| "I made substantial progress" (returned as success) | Progress is not the predicate. If partial progress should count, it belongs in the brief explicitly — otherwise it's a listed non-counting outcome. |
| "All parallel workers agree, so it's right" | Unanimous agreement among workers seeded the same way is correlation, not confirmation — same lesson as correlated eval blind spots (EXP-001). |
| "The brief is too strict; loosening it mid-run" | Mid-run loosening under persistence pressure is exactly how gaming happens. Change the brief only between runs, deliberately. |
| "It passes the examples given" | Verifying listed cases is a listed non-counting outcome unless the predicate says otherwise. The predicate covers the scope, not the samples. |

## Checklist
- [ ] Every load-bearing term defined, degenerate cases named.
- [ ] One success predicate, applicable by an adversarial reader to the artifact alone.
- [ ] Non-counting near-misses enumerated explicitly.
- [ ] Domain-specific failure-mode checklist written for the auditor.
- [ ] Return condition is a predicate over the artifact; effort floor set; persistence paired with verification.
- [ ] Parallel runs: diversity policy set (blind starts, idea-level registry, dead-route marking).
- [ ] Brief itself adversarially reviewed before launch.
