---
name: prompt-architecture
description: Design or refactor an agent's system prompt as a structured, budgeted artifact — sections, context layers, and degradation order. Use when writing a new agent's system prompt, when a prompt has grown past ~500 lines, or when the agent ignores instructions.
---

# Prompt Architecture

Treat the system prompt as an engineered artifact with sections, a token budget, and an owner per section — not a text file that accretes.

## When to use
- Writing the system prompt for a new agent.
- An agent inconsistently follows instructions (often a structure problem, not a wording problem).
- The prompt exceeds ~500 lines or nobody can say what a given paragraph is for.

## When NOT to use
- Choosing between agent patterns (use `agent-architecture` first).
- Task-level prompts inside a fixed workflow step — those are templates, keep them local.

## Procedure

1. **Inventory** the current prompt (if one exists). Tag every paragraph with one of: identity, capability, constraint, procedure, format, example, dead (nobody knows why it's there). Delete dead paragraphs — they cost tokens and attention every call.

2. **Structure into the standard layer order.** Stable content first (maximizes prompt-cache hits), volatile content last:
   1. Identity & role — one short paragraph
   2. Environment & capabilities — what tools exist, what the harness does
   3. Hard constraints — safety rules, permissions, things that override everything
   4. Procedures — how to do the recurring tasks, numbered
   5. Output format — schemas, examples
   6. Dynamic context — retrieved docs, memory, session state (injected, not authored)

3. **Budget each layer** in tokens. Rule of thumb for a production agent: identity+environment ≤ 10%, constraints ≤ 15%, procedures ≤ 40%, format+examples ≤ 20%, leaving ≥ 15% headroom. Record the numbers.

4. **Apply the instruction-strength rules:**
   - One instruction, one place. Duplicated rules drift; the model averages contradictions.
   - Positive over negative: "respond in JSON" beats "don't use prose". Reserve "never" for the constraints layer.
   - Examples beat rules for format; rules beat examples for behavior.
   - If an instruction is violated in testing, first try *moving it* (later = more salient) before rewording it.

5. **Define the degradation order**: which layers get truncated/summarized when dynamic context overflows. Constraints are never truncated; examples go first.

6. **Verify**: run the agent's 3 most common tasks and 1 known-hard task; confirm instructions in each layer are honored. A prompt refactor with no test run is not done.

## Output contract
The restructured prompt file plus a header comment (or sidecar doc) listing: layer boundaries, token budget per layer, degradation order, and the date/results of the verification run.

## Checklist
- [ ] Every paragraph tagged with a layer; zero dead paragraphs.
- [ ] Stable→volatile order (cache-friendly).
- [ ] No instruction appears twice; no contradictions.
- [ ] Token budget written down and met, with ≥15% headroom.
- [ ] Degradation order defined; constraints never degrade.
- [ ] Verified on 3 common + 1 hard task after the change.
