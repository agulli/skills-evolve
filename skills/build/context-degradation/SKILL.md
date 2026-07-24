---
name: context-degradation
description: Diagnose which context failure mode is degrading a long-running agent — lost-in-middle, poisoning, distraction, confusion, or clash — before reaching for a fix. Use when output quality decays as context grows, when the agent ignores instructions that are demonstrably in context, when a hallucination persists after correction, or when the agent applies constraints from the wrong task.
---

# Context Degradation Diagnosis

Long-context failures are not one disease. An agent that "gets worse as the conversation grows" may be suffering any of five distinct failure modes, and each has a different fix. Treating them all with "compact more aggressively" (the `context-engineering` reflex) can make the wrong one worse — compaction *spreads* poisoning by baking a hallucination into the summary. Diagnose first; then route to the right treatment.

This skill is the diagnostic sibling of `context-engineering` (which manages the window) — the same relationship `trajectory-review` has to general agent failures.

## When to use
- Output quality decays as context grows, and you don't yet know why.
- The agent ignores an instruction that is verifiably present in context.
- A hallucination or wrong fact persists across turns despite corrections.
- The agent applies constraints or calls tools from a *different* task in the same window.

## When NOT to use
- You already know the mode and need the window managed — that's `context-engineering`.
- The failure isn't context-length-related (fails on short runs too) — that's `trajectory-review`.
- The static prompt itself is contradictory — that's `prompt-architecture`.

## The five failure modes

| Mode | Signature | Wrong fix that makes it worse |
|---|---|---|
| **Lost-in-middle** | Instruction/fact present in mid-context is ignored; same content at the start or end works | Adding *more* context |
| **Poisoning** | A wrong "fact" (from a tool output, retrieval, or earlier hallucination) is repeated and built upon; survives correction | Compacting — bakes the poison into the summary |
| **Distraction** | Quality drops after loading documents/results that are irrelevant to the task, even if correct | Loading more "just in case" context |
| **Confusion** | Constraints or tool choices from task A applied to task B sharing the window | Merging more tasks into one session |
| **Clash** | Two individually-correct but contradictory sources (versions, perspectives); agent oscillates or picks arbitrarily | Adding a third source |

## Procedure

1. **Confirm it's context-dependent.** Re-run the failing request in a fresh, minimal context. If it still fails, this is not degradation — use `trajectory-review`. If it succeeds clean, you have a context failure mode; continue.

2. **Locate the failure against position.** Find where the ignored instruction / wrong fact sits in the window. Mid-context placement with correct behavior when the same content is moved to the start or end confirms **lost-in-middle**. Fix: move load-bearing content to the edges (attention follows a U-curve), add structural headers as anchors, or pin it (see `context-engineering` tiers).

3. **Trace wrong facts to their entry point.** For a persistent wrong claim, walk backward to the turn where it first appeared. If it entered via a tool output, retrieved document, or the agent's own earlier answer and has been *referenced since* — that's **poisoning**. Fix: truncate to before the entry point and rebuild with verified content only; do not layer corrections on top (the poisoned version usually wins), and do not compact across the poisoned span.

4. **Audit relevance of what's loaded.** List what's in the window vs. what the current task actually needs. A large irrelevant share (even correct content) with quality dropping after it loaded is **distraction**. Fix: filter before loading, retrieve on demand via tool calls instead of preloading, and trim at the source (`context-engineering` step 2).

5. **Check for task bleed.** If the window hosts multiple tasks, look for constraints applied across task boundaries — that's **confusion**. Fix: one task per context; segment into separate sessions or sub-agents with isolated windows (`agent-architecture` / `handoff-protocol`).

6. **Check for contradictory sources.** If two sources disagree and both are individually plausible (two API versions, two policies), the oscillation is **clash**. Fix: establish source precedence *before* loading (newest-wins, authority ranking), version-filter, and annotate the conflict explicitly in context rather than leaving both unmarked.

7. **Establish the degradation threshold empirically.** Long-context performance holds flat and then drops sharply — the cliff is model- and task-specific. Find yours by testing the same task at increasing fill levels rather than trusting published context-window sizes; then set `context-engineering` compaction triggers safely below that cliff (a 70% utilization trigger is a reasonable starting default; move it based on measurement).

## Output contract
A diagnosis: the identified failure mode(s) with the evidence that discriminates them (fresh-context result, position test, poison entry turn, relevance audit, task/source inventory), the routed fix per mode, and — if measured — the empirical degradation threshold to feed back into `context-engineering`'s budgets.

## Anti-rationalization

| The agent will try to… | The correct response is… |
|---|---|
| "Context is degraded — compact it" | Compacting poisoned context bakes the hallucination into the summary. Diagnose the mode first. |
| "Just add the instruction again, louder" | If the mode is lost-in-middle, re-adding mid-context repeats the failure. Move it to an edge or pin it. |
| "More context can't hurt — it's all accurate" | Distraction degrades output with *correct but irrelevant* content. Relevance, not accuracy, is the bar. |
| "The model keeps making the same mistake — it's a model problem" | A wrong fact that survives correction is usually poisoning. Find the entry turn; truncate before it. |
| "We'll handle the contradiction in the prompt" | Clash needs source precedence decided before loading, not adjudicated by the model per-turn. |

## Checklist
- [ ] Fresh-minimal-context re-run performed; failure confirmed context-dependent.
- [ ] Failure mode identified from the five, with discriminating evidence — not assumed.
- [ ] Poisoning: entry turn found; rebuilt from before it; no compaction across the poisoned span.
- [ ] Lost-in-middle: load-bearing content moved to window edges or pinned.
- [ ] Distraction/confusion: relevance audit done; one task per context.
- [ ] Clash: source precedence rule established before content loads.
- [ ] Degradation cliff measured for this model/task; compaction triggers set below it.
