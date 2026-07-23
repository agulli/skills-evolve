---
name: adversarial-review
description: Subject a non-trivial agent design decision to a fresh-context adversarial review before it stands — spawn a reviewer biased to disprove, not approve. Use when making architectural decisions under uncertainty, when asserting safety/correctness properties, when the blast radius of being wrong is high (production, irreversible, security-sensitive), or any time a confident output would be cheaper to verify now than to debug later.
---

# Adversarial Review

A confident design decision is not a correct one. Long sessions accumulate context that quietly turns assumptions into "facts." This skill materializes a reviewer — biased to **disprove**, not approve — before any non-trivial agent decision stands. It is the *in-flight* complement to `trajectory-review` (which reviews *after* the run) and `eval-harness` (which tests *against canned cases*).

## When to use
- About to choose an agent architecture, tool set, or safety boundary under uncertainty.
- About to claim a non-obvious property: "this is safe," "this scales," "this won't leak PII."
- The decision's blast radius is high: production, security, cost, irreversible side effects.
- Working on a skill, prompt, or guardrail you don't fully understand yet.

## When NOT to use
- Trivial changes: renaming, formatting, config tweaks with no behavioral impact.
- Following a clear, unambiguous user instruction with low risk.
- The decision has already been reviewed and approved by a human.
- Speed is explicitly prioritized over verification by the stakeholder.

## Procedure

1. **CLAIM — Name what stands.** Write the decision in 2–3 lines, plus why it matters (what breaks if it's wrong).

   ```
   CLAIM: "The new guardrail catches prompt injection by checking the
           last 3 messages, not just the current one."
   WHY IT MATTERS: If wrong, an attacker splits their injection across
                   messages and bypasses the guard entirely.
   ```

2. **EXTRACT — Isolate the artifact.** Pull out the concrete thing to review (the code, the prompt section, the architecture diagram, the skill procedure) and the contract it must satisfy (the invariants, the threat model, the success criteria). Strip your reasoning — the reviewer should see *what* you built, not *why* you think it's right.

3. **DOUBT — Invoke a fresh-context review.** Present the artifact + contract to a reviewer (another agent, a subagent, or a human) with this adversarial prompt:

   > "Here is [artifact]. It must satisfy [contract]. Your job is to find ways it fails, not to confirm it works. List concrete failure scenarios with reproduction steps. If you find none, say so — but try hard first."

   The reviewer must NOT see your reasoning from steps 1–2. They review the artifact cold. That's the point — your reasoning is what might be wrong.

4. **RECONCILE — Classify every finding.** For each issue the reviewer raises:

   | Classification | Meaning | Action |
   |---|---|---|
   | **Valid — breaks contract** | The artifact fails an invariant | Fix before proceeding |
   | **Valid — edge case uncovered** | The contract was incomplete | Add the invariant, then fix |
   | **Invalid — reviewer error** | The reviewer misread the artifact | Note and dismiss (but verify your dismissal) |
   | **Uncertain** | Can't tell without testing | Write a test case or experiment |

5. **STOP — Check the stop condition.** Stop the doubt cycle when:
   - All findings are trivial or invalid (the artifact is clean).
   - You've run 3 doubt cycles (diminishing returns).
   - The stakeholder explicitly overrides ("ship it, we'll iterate").
   
   If still finding valid issues after 3 cycles, escalate — the artifact needs more than review.

## Anti-rationalization

| The agent will try to… | The correct response is… |
|---|---|
| "I'm confident this is correct" | Confidence is not evidence. Run the doubt cycle — confident mistakes are the most expensive. |
| "This is too simple to review" | Simple claims are the cheapest to verify. If it's truly simple, the cycle takes 30 seconds. |
| "I already considered this" | You considered it in the context that produced it. A fresh-context reviewer catches what you've normalized. |
| "The user is waiting, no time for review" | A 2-minute review now saves a 2-hour debug later. The user is more upset by a broken agent than a short wait. |
| Skip the EXTRACT step and show reasoning | The point of fresh-context review is to strip your reasoning. Showing it defeats the purpose. |
| Accept all findings without thinking | Reconciliation means *classifying* findings, not accepting them blindly. Invalid findings exist. |

## Output contract
A review record per decision: the claim, the artifact reviewed, the reviewer's findings, the classification of each finding (valid/invalid/uncertain), the fixes applied, and the stop condition met. This record is committed as provenance alongside the decision.

## Checklist
- [ ] Non-trivial decision identified; claim + why-it-matters written.
- [ ] Artifact extracted and presented cold (without reasoning) to a reviewer.
- [ ] Reviewer prompted adversarially (find failures, not confirmations).
- [ ] Every finding classified: valid-breaks-contract / valid-edge-case / invalid / uncertain.
- [ ] Valid findings fixed before proceeding; uncertain ones tested.
- [ ] Stop condition met (trivial findings only, 3 cycles, or stakeholder override).
