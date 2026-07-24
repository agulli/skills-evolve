---
name: context-engineering
description: Engineer what occupies an agent's context window over a long run — token budgeting, compaction, summarization cadence, eviction policy, and result trimming — so it stays coherent and affordable across many turns. Use when an agent runs long-horizon, when context grows until it truncates or degrades, or when per-task token cost climbs with conversation length.
---

# Context Engineering

The context window is the agent's working memory, and it is scarce. Long-horizon agents don't fail because the model is weak — they fail because the *right* tokens got evicted and the *wrong* ones (stale tool dumps, dead turns) crowded them out. This skill manages what occupies the window over time; it is distinct from `memory-design` (cross-session storage) and `prompt-architecture` (the static prompt).

## When to use
- An agent runs many turns / tool calls and quality decays as the conversation grows.
- Context approaches the window limit and truncates, or per-task token cost rises with length.
- Tool results routinely flood the window (large JSON, file dumps, search results).

## When NOT to use
- Designing the static system prompt — that's `prompt-architecture`.
- Persisting knowledge across sessions — that's `memory-design`.
- Reducing cost by caching/routing without a length problem — that's `cost-optimization`.

## Procedure

1. **Budget the window as tiers.** Split the window into: **pinned** (system prompt, task goal, hard constraints — never evicted), **working** (recent turns and active tool results), and **compactible** (older history). Assign a token ceiling to each; the working+compactible ceiling is what triggers compaction. Write the numbers down — an unbudgeted window fills with whatever arrives last. Useful starting defaults until measured: compact at ~70% window utilization, compact *immediately* at ~80%, and treat tool outputs exceeding ~50% of the window as the first target. Placement matters too: attention follows a U-curve, so keep load-bearing content (goal, constraints) at the start or end of the window, never buried mid-context (see `context-degradation` for diagnosing this).

2. **Trim tool results at the source.** The largest recoverable waste is verbose tool output. Cap each tool's result (pagination, `limit`, summary mode — see `tool-design`), and post-process before it enters context: extract the fields the agent will actually use, drop the rest. The model rarely needs 400 rows to answer a question about 3.

3. **Mask old observations instead of holding or dropping them.** For tool outputs whose key finding is already extracted, replace the verbose body after ~3 turns with a compact reference — `[result #N elided; key finding: X; retrievable on demand]` — keeping the pointer and conclusion, not the payload. Never mask observations for the *current* task step or recent error output (you'll need the detail); mask duplicates and boilerplate immediately. This sits between holding everything (cost) and dropping everything (loses the trail).

4. **Compact, don't just truncate.** When the compactible tier exceeds budget, replace old turns with a **structured summary** (decisions made, state established, open threads, artifacts produced) rather than dropping them blind. Truncation loses the fact that mattered on turn 3; a good summary keeps it in a fraction of the tokens. **Crucial:** Never drop task-critical parameters, schema definitions, or active constraints during compaction — over-pruning instructions is the #1 cause of regression when this skill is applied. Compact on a cadence (every N turns or M tokens), not only at the cliff.

5. **Set an eviction policy for the working tier.** Decide what leaves first when space is tight: completed tool results before their conclusions, superseded intermediate results before final ones, verbose reasoning before decisions. Constraints, required input fields, and the task goal are pinned and never evicted (mirror the degradation order from `prompt-architecture`).

6. **Externalize instead of holding.** For state the agent revisits, write it to a scratchpad/file the agent can re-read on demand rather than carrying it in every turn's context. A pointer costs a few tokens; the full artifact costs them every turn it lingers. Pair with `memory-design` when the state must also survive the session. If a single task's context need exceeds ~60% of the window even after trimming and masking, stop optimizing within one window and **partition**: split across sub-agents with isolated contexts (`agent-architecture`/`handoff-protocol`) — but only when there are ≥3 separable subtasks, so the savings exceed the coordination overhead.

7. **Preserve cache-friendliness.** Compaction and eviction rewrite history — which invalidates prompt cache from the edit point forward. Compact in batches at stable boundaries (not every turn), keep the pinned prefix byte-stable, and append summaries rather than rewriting the whole transcript, so most of the prefix still cache-reads (see `cost-optimization`).

8. **Verify on a long run, against numeric targets.** Drive the agent through a run long enough to trigger compaction 2–3 times on a task with a fact planted early that's needed late. Confirm: the late step still has the early fact, quality doesn't step down after each compaction, and token-per-turn flattens instead of growing. Acceptance bars to aim for (measure, don't assume): compaction should reclaim ~50–70% of the compacted span's tokens at under ~5% quality cost on your eval set; masking should reclaim well over half of masked-observation tokens at negligible quality cost. If quality drops more than that, the compaction is over-pruning — see the step-4 warning.

## Output contract
A context plan: tier budgets (pinned/working/compactible with token ceilings), per-tool trimming rules, compaction trigger + summary schema, eviction order, externalization points, and the long-run verification result (early-fact recall, quality-across-compactions, token-per-turn curve).

## Checklist
- [ ] Window split into pinned / working / compactible with written token ceilings; load-bearing content at the window edges, not mid-context.
- [ ] Every high-volume tool result trimmed at the source before entering context.
- [ ] Old observations masked to pointer + key finding after use; current-task and error output never masked.
- [ ] Old history compacted to a structured summary on a cadence, not truncated at the cliff.
- [ ] Eviction order defined; goal and constraints pinned and never evicted.
- [ ] Revisited state externalized to a re-readable scratchpad, not held every turn.
- [ ] Compaction preserves a byte-stable cached prefix.
- [ ] Long-run test: early fact survives to late step; quality flat across compactions; token/turn flattens.
