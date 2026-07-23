---
name: grounding-citation
description: Make an agent ground its claims in retrieved evidence and cite sources — verify quotes, attribute statements, and refuse or flag when unsupported — so answers are checkable and hallucinations are caught. Use when an agent answers from documents/search, when it states facts without sources, or when hallucination is a real risk.
---

# Grounding & Citation

An agent that retrieves the right evidence can still hallucinate — inventing facts, misattributing sources, or asserting beyond what the evidence supports. Grounding closes the gap between "had the evidence" and "used only the evidence." It sits on top of `retrieval-design` (which gets the evidence) and turns provenance into verifiable, cited answers.

## When to use
- An agent answers from retrieved documents, search results, or a knowledge base.
- The agent states facts without attributing them, or attributes them wrongly.
- Hallucination has real cost (compliance, medical/legal/financial, user trust).

## When NOT to use
- Creative or open-ended generation where grounding isn't the goal.
- Retrieval quality itself is the problem — fix `retrieval-design` first; you can't cite evidence you didn't retrieve.

## Procedure

1. **Require claims to trace to evidence.** Instruct the agent to answer *from the provided evidence*, attaching the source for each factual claim, and to say "not supported by the available sources" rather than fill gaps from parametric memory. The refusal path is the point — an agent that never says "I don't know from these sources" is guessing.

2. **Carry provenance in, citations out.** Retrieved chunks arrive with source + location (`retrieval-design`). The answer carries them back as citations the user can follow. A cited answer is a checkable answer; an uncited one is a claim on faith.

3. **Verify quotes and attributions, don't trust them.** Models paraphrase-as-quote and cite the wrong chunk. Where stakes are high, verify programmatically that quoted text actually appears in the cited source and that the citation maps to a real retrieved chunk — not just that a citation is present. A fabricated citation is worse than none.

4. **Separate grounded claims from reasoning.** Distinguish what the evidence says from the agent's inference on top of it. Both are legitimate; conflating them ("the document says X" when X is the agent's deduction) is a subtle, high-trust failure. Mark inference as inference.

5. **Handle insufficient and conflicting evidence explicitly.** Define behavior when sources are missing (refuse/flag), thin (hedge with the gap stated), or contradictory (surface the conflict rather than silently picking one). Silent resolution of conflicting sources is where grounded-looking answers go most wrong.

6. **Measure the grounding failure modes.** Add eval cases for: unsupported claims presented as fact, fabricated/mismatched citations, and questions whose answer *isn't* in the corpus (the agent should decline, not invent). Track a hallucination rate, not just task success (`eval-harness`, `llm-judge` for the rubric).

## Output contract
A grounding design: the answer-from-evidence + refusal instruction, the citation format carrying provenance, the quote/attribution verification step, the inference-vs-evidence separation, the insufficient/conflicting-evidence policy, and eval cases measuring hallucination and citation-fidelity rates.

## Checklist
- [ ] Agent instructed to answer from evidence and to decline when unsupported.
- [ ] Every factual claim carries a followable citation to a real retrieved chunk.
- [ ] Quotes/attributions verified against source, not assumed correct.
- [ ] Evidence-based claims separated from the agent's own inference.
- [ ] Missing/thin/conflicting-evidence behavior defined and enforced.
- [ ] Eval cases for unsupported claims, bad citations, and out-of-corpus questions; hallucination rate tracked.
