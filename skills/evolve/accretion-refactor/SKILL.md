---
name: accretion-refactor
description: Consolidate and shrink a bloated system prompt or skill by removing dead instructions, resolving contradictory constraints, and pruning rules added in panic. Use periodically to combat prompt drift, or when an agent starts ignoring instructions because the context window is overwhelmed with "NEVER do X" rules.
---

# Accretion Refactor

Over months of debugging, teams add "NEVER do X" or "ALWAYS remember Y" to system prompts after every incident. The prompt balloons, instructions contradict each other, and the model starts dropping context (the "accretion" problem). This skill forces a procedural review of a bloated text artifact to consolidate rules, delete redundant constraints, and shrink the token count.

## When to use
- An agent's system prompt has grown by >30% since the last review.
- The agent starts "forgetting" or ignoring explicit instructions.
- After an incident, you discover the agent violated a rule that contradicts another rule in the prompt.
- Scheduled prompt hygiene (e.g., once a quarter).

## When NOT to use
- Diagnosing a single, specific run failure (use `trajectory-review`).
- Making a surgical, one-line fix to a prompt.

## Procedure

1. **Snapshot the Baseline.** Before touching the text, record the current length (token or word count) and the baseline eval score. You cannot refactor a prompt without a running eval harness to prove you didn't break it.
2. **Cluster by Intent.** Group all instructions and constraints in the prompt by their underlying intent (e.g., Tone, Formatting, Safety/Guardrails, API rules).
3. **Hunt for Contradictions.** Look for rules that conflict. (e.g., "Always be concise" vs. "Explain every step of your reasoning"). Resolve them by prioritizing the stricter or safer constraint and deleting the other.
4. **Prune the Dead Wood.** 
   - Remove instructions addressing tools or systems that no longer exist.
   - Remove "panic rules" (highly specific instructions added after a one-off bug that the model wouldn't normally do anyway).
5. **Consolidate.** Combine multiple similar negative constraints into a single, cohesive principle. Push formatting constraints out of the prompt and into the tool schemas (e.g., change "Always format dates as YYYY-MM-DD" in the prompt to a strict regex pattern in the JSON schema).
6. **Evaluate the Refactor.** Run the `eval-harness` against the shortened prompt. 
   - If the score drops on regression tasks, you pruned a load-bearing rule. Restore it.
   - If the score is stable, commit the shorter prompt.

## Anti-rationalization

| The agent will try to… | The correct response is… |
|---|---|
| Refuse to delete a rule because "it was put there for a reason." | Rules added in a panic are often bandaids for underlying tool design flaws. If the tool is fixed, the rule is dead wood. Delete it and let the eval prove it. |
| Reorganize the prompt without actually making it shorter. | The goal is token compression and clarity. If the length hasn't dropped, you haven't refactored. |
| Skip the eval run. | Refactoring without an eval is just rewriting. You must prove the agent still performs. |

## Output contract
A before-and-after diff of the prompt or skill file, the token count reduction achieved, a list of contradictory or dead rules removed, and the passing eval score confirming no regressions.

## Checklist
- [ ] Baseline token count and eval score recorded before starting.
- [ ] Instructions clustered by intent; contradictions resolved.
- [ ] Dead, outdated, or "panic" rules removed.
- [ ] Formatting constraints pushed to schemas where possible.
- [ ] Post-refactor eval score confirms stability.
- [ ] Final token count is lower than the baseline.
