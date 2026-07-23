---
name: memory-design
description: Design an agent's memory system — what to remember, storage tiers, retrieval, and forgetting policy. Use when an agent needs to persist knowledge across sessions, when memory grows unbounded, or when retrieved memories are stale or irrelevant.
---

# Agent Memory Design

Memory is a write policy, a storage layout, a retrieval path, and a forgetting policy. Most teams design only storage — then drown in stale, unranked facts.

## When to use
- An agent needs knowledge to persist across sessions (preferences, decisions, project state).
- Memory exists but retrieval surfaces stale or irrelevant entries, or the store grows without bound.
- Choosing between context stuffing, RAG, and structured memory for a new agent.

## When NOT to use
- Within-session state only → that's context management, keep it in the conversation/scratchpad.
- The knowledge is static and versionable → put it in the repo (CLAUDE.md, docs), not memory.

## Procedure

1. **Write the write policy first.** Define what earns a memory: facts that are (a) not derivable from the codebase/history, (b) likely needed in a *future* session, and (c) stable for weeks+. Everything else is noise. Define it as rules the agent can apply, with 3 positive and 3 negative examples.

2. **Choose the storage tier per memory type** — most systems need two, not five:

   | Type | Tier | Retrieval |
   |------|------|-----------|
   | Identity/preferences (small, always relevant) | Flat file loaded every session | None — always in context |
   | Episodic facts, decisions | One file per fact + index | Index scan or keyword |
   | Large corpus (docs, history) | Vector/hybrid search store | Semantic retrieval |
   | Entity relationships at scale | Graph store | Traversal — only if queries genuinely need multi-hop |

3. **Design retrieval for precision over recall.** A wrong memory in context is worse than a missing one — the agent trusts it. Rank by relevance × recency; cap injected memories per turn (3–5); always label provenance and date so the agent can discount stale entries.

4. **Design forgetting on day one.** Every memory carries created/last-confirmed timestamps. Policy needs: decay or archive after N days unconfirmed, contradiction resolution (new fact supersedes and deletes the old — never keep both), and a size cap that forces review.

5. **Make memories inspectable.** Human-readable format (markdown files beat DB rows for agent memory), user-editable, with the write policy documented next to the store. If the user can't read and fix memory, trust erodes on the first bad recall.

6. **Verify with a cross-session test**: session A writes memories from a realistic task; session B (fresh context) must use them correctly on a related task, and must *not* surface irrelevant ones. Measure: recall of needed facts, zero stale/irrelevant injections.

## Output contract
A memory design doc: write policy with examples, tier choice per memory type with rationale, retrieval ranking and per-turn cap, forgetting policy with timestamps/caps, plus the cross-session test results.

## Checklist
- [ ] Write policy stated as rules with 3 positive / 3 negative examples.
- [ ] Tiers justified by type; no vector store where a file index suffices.
- [ ] Retrieval capped per turn; memories carry provenance + dates.
- [ ] Forgetting policy exists: decay, contradiction supersedes, size cap.
- [ ] Store is human-readable and user-editable.
- [ ] Cross-session test passed: needed facts recalled, zero stale injections.
