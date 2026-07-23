---
name: human-review-escalation
description: Format a high-signal escalation request when an agent must hand off to a human — context, what was tried, the exact blocker, and actionable options. Use when an agent is stuck in an unrecoverable error loop, faces an ambiguous choice with no clear policy, or reaches a high-risk action gate requiring explicit human approval (deletion, spend, irreversible change).
---

# Human Review Escalation

When an agent hits a dead end, faces ambiguity, or reaches a high-risk action gate, it must escalate to a human. A poor escalation ("I got stuck") forces the human to dig through traces. A good escalation is high-signal: it provides context, what was tried, the exact blocker, and actionable options.

## When to use
- An agent is stuck in an error loop it cannot recover from.
- The agent faces a decision with no clear policy (ambiguity).
- A task requires explicit human approval (e.g., high-risk action, spending limits).

## When NOT to use
- To ask for basic information that could be retrieved using existing tools.
- To avoid making a safe, reversible decision.

## Procedure

1. **State the exact blocker.** Open with a one-sentence summary of why the escalation is happening (e.g., "I am trapped in an API auth error loop" or "I need approval to drop this database table").
2. **Summarize the context (The 'What').** Briefly explain the original goal and the current state of the task. Do not dump the entire trace.
3. **List what was already tried.** Provide a bulleted list of the approaches or tools the agent just attempted, and why they failed. This prevents the human from suggesting things the agent already knows don't work.
4. **Provide options (The 'Now What').** Present 1-3 concrete options for the human to choose from. Options should be mutually exclusive and actionable (e.g., "Option A: Proceed with deletion. Option B: Abort and rollback. Option C: Provide a new API key").
5. **Include resumption instructions.** State exactly how the human should respond to resume the task (e.g., "Reply with A, B, or C").
6. **Pause execution.** Enter a wait state. Do not continue looping or hallucinating progress while waiting for the human.

## Output contract
A structured escalation message presented to the human, containing the blocker, context, attempted fixes, options, and resumption instructions.

## Anti-rationalization

| The agent will try to… | The correct response is… |
|---|---|
| Dump the last 50 lines of the error log. | Humans don't want raw logs first. Summarize the blocker and provide the logs only as an appendix or if asked. |
| Ask open-ended questions like "What should I do?" | Open-ended questions create cognitive load. Always propose concrete, actionable options. |
| Give up entirely and terminate the session. | Escalation is a pause, not a termination. Provide resumption instructions. |
| Guess and take a high-risk action to avoid bothering the human. | If it's a defined high-risk gate (e.g. data deletion), guessing is a critical failure. Ask. |

## Checklist
- [ ] Escalation starts with a clear, one-sentence statement of the blocker.
- [ ] Original goal and current state are summarized.
- [ ] Previously attempted fixes are listed to prevent redundant suggestions.
- [ ] 1-3 concrete options are presented for the human to choose from.
- [ ] Clear instructions on how to respond and resume are provided.
- [ ] Agent execution is paused pending human input.
