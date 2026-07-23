---
name: silent-failure-audit
description: Review only runs marked "Successful" to hunt for instances where the agent hallucinated a success message but quietly failed to execute the actual task. Use when reviewing an eval harness that has high scores but suspicious downstream bugs, or when an agent claims to have completed a task but state hasn't changed.
---

# Silent Failure Audit

Most eval tuning focuses on failing runs (`trajectory-review`). This skill looks exclusively at runs marked as *Successful*. It specifically hunts for "sycophancy" or metrics fraud — instances where the agent hallucinated a success message (e.g., "I have updated the database!") but quietly skipped or failed the actual tool call.

## When to use
- Eval scores are surprisingly high but users are reporting bugs.
- You suspect the agent is gaming the eval harness.
- You are reviewing an agent that uses a "think before acting" loop that might be getting stuck in thought.

## When NOT to use
- To diagnose runs that explicitly failed and threw errors (use `trajectory-review`).
- When the eval harness already asserts 100% programmatically on end-state and relies on zero LLM-as-a-judge steps.

## Procedure

1. **Filter for Successes.** Gather a batch of 10-20 trajectories that your eval harness or users graded as "Successful" or "Done."
2. **Read for the "Bait and Switch".** Read the transcript looking for the exact moment the agent claimed success to the user.
3. **Verify the Action.** Cross-reference the agent's claim with the actual tool calls executed immediately prior. Did it actually call the `update_database` tool, or did it just output the JSON payload as plain text and say "Done"?
4. **Identify the Loophole.** If the agent lied, identify why the eval harness let it get away with it. Was the eval checking the transcript for the word "Done" instead of querying the database? Was the user too trusting?
5. **Close the Loophole.** For every silent failure found, write a programmatic negative constraint in the eval harness (e.g., "Assert that `update_database` was called exactly once with status 200").
6. **Re-score the Baseline.** Rerun the eval harness with the tightened criteria and note the true (lower) baseline score.

## Anti-rationalization

| The agent will try to… | The correct response is… |
|---|---|
| Assume a "Success" grade is always correct. | The purpose of this audit is assuming the grade is a lie. Trust nothing but the actual tool execution logs. |
| Blame the user for not checking the agent's work. | Agents are built to reduce human toil. If the human has to double-check every API call, the agent has negative value. |
| Fix the prompt to say "don't lie." | Prompting doesn't fix silent failures reliably. The fix must be in the eval harness's assertion logic. |

## Output contract
An audit report: the number of successful runs reviewed, the number of silent failures found, the specific loopholes in the eval harness that allowed them, and the tightened programmatic assertions added to close them.

## Checklist
- [ ] Only runs marked "Successful" were reviewed.
- [ ] Every success claim was cross-referenced against actual tool execution logs.
- [ ] Discovered loopholes were closed with programmatic end-state assertions, not prompt tweaks.
- [ ] The true, adjusted baseline score was recorded after tightening the harness.
