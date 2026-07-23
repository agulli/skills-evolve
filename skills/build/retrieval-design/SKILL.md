---
name: retrieval-design
description: Design the retrieval layer for a knowledge agent — chunking, indexing, query construction, ranking, and how much retrieved content reaches the context — so answers are grounded in the right evidence at acceptable cost. Use when building RAG or a knowledge agent, when retrieved context is irrelevant or bloated, or when the agent answers from the wrong source.
---

# Retrieval Design

RAG fails on retrieval quality far more than on the model. If the wrong chunks come back, the best model answers confidently from bad evidence. This skill designs retrieval as a measurable component — chunking, query, ranking, and budget — distinct from `memory-design` (agent's own memory) and `context-engineering` (the window it lands in). Grounding on the returned evidence is `grounding-citation`.

## When to use
- Building a RAG pipeline or any agent that answers from a document/knowledge corpus.
- Retrieved context is irrelevant, redundant, or floods the window.
- The agent answers from the wrong source, or misses content that's in the corpus.

## When NOT to use
- The knowledge fits in the prompt/context — just include it; retrieval adds failure modes for nothing.
- The agent's *own* cross-session memory — that's `memory-design`.

## Procedure

1. **Chunk for retrievability, not for tidiness.** Chunk size and boundaries determine what can be found. Too large → diluted embeddings and wasted tokens; too small → lost context. Chunk on semantic boundaries (sections, not fixed byte counts), keep enough surrounding context to be self-contained, and attach metadata (source, section, date) for filtering and citation.

2. **Design the query, not just the store.** The user's raw question is often a poor query. Consider query rewriting, decomposition of multi-part questions, and metadata filters (date, source, permission) before the vector search. The best index answers the wrong query wrongly.

3. **Choose retrieval method by the failure you're avoiding.** Semantic (embeddings) for meaning, keyword/BM25 for exact terms and identifiers, hybrid for both. Names, codes, and IDs are where pure-semantic silently fails — hybrid or keyword catches them. Justify the choice against your corpus, don't default to "vector search."

4. **Rank and cut for precision.** Retrieve broadly, then re-rank and keep only the top few — a wrong chunk in context is worse than a missing one because the model trusts it (mirror of `memory-design`'s precision stance). Cap how much retrieved content reaches the window; dedupe near-identical chunks; trim each to what's relevant (`context-engineering`).

5. **Carry provenance through to the answer.** Every retrieved chunk keeps its source + location so the agent can cite it and a human can verify. Retrieval that returns text without provenance makes grounding and debugging impossible (hands off to `grounding-citation`).

6. **Evaluate retrieval on its own.** Build a small labeled set of query → correct-chunks and measure retrieval precision/recall *before* blaming the model. When answers are wrong, this tells you whether the fault is retrieval or generation — the single most useful RAG debugging signal (feeds `eval-harness`).

## Output contract
A retrieval design: chunking strategy + metadata, query construction (rewrite/decompose/filter), retrieval method with rationale, ranking + budget policy, provenance carried to the answer, and a retrieval-only eval set with precision/recall numbers.

## Checklist
- [ ] Chunks are semantic, self-contained, and carry source/section/date metadata.
- [ ] Query construction handles rewriting/decomposition/filters, not just raw text.
- [ ] Retrieval method justified against the corpus (identifiers/exact-match considered).
- [ ] Retrieve-broad-then-rerank; top-k capped; near-duplicates removed; chunks trimmed.
- [ ] Provenance carried through to enable citation and verification.
- [ ] Retrieval evaluated in isolation (precision/recall) before blaming generation.
