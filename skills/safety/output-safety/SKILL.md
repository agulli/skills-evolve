---
name: output-safety
description: Screen and constrain what an agent says or generates — harmful/toxic content, unsafe advice, off-policy claims, and brand/compliance violations — before it reaches a user. Use when an agent produces user-facing content, when outputs could be harmful or off-policy, or when a generated response caused a complaint.
---

# Output Safety

Guardrails govern what an agent *does*; output safety governs what it *says*. A user-facing agent can produce toxic content, dangerous advice, confident falsehoods, or off-brand/off-policy claims — none of which its tool-permission gates catch, because no tool was called. This skill screens generated content before it reaches a person. It complements `guardrails` (actions) and `grounding-citation` (factual support).

## When to use
- An agent produces content a user reads (chat, emails, summaries, generated docs).
- Outputs could be harmful, toxic, unsafe advice, or off-policy.
- A generated response drew a complaint or a policy violation.

## When NOT to use
- Purely internal outputs with no human or downstream consumer at risk.
- Factual grounding of claims specifically — that's `grounding-citation`.

## Procedure

1. **Define the output policy concretely.** "Be safe" is unenforceable. Enumerate the categories that are out of bounds for *this* agent — harmful/dangerous instructions, harassment/toxicity, medical/legal/financial advice beyond scope, off-brand tone, disallowed claims (guarantees, competitor mentions) — with examples of allowed vs. disallowed. The policy is the spec the screen enforces.

2. **Screen outputs, not just inputs.** Input filtering doesn't catch an agent that generates something bad from a benign prompt. Put a check *between generation and the user*: policy classification, banned-content patterns, or a safety judge (`llm-judge`) for nuanced categories. The screen runs on every user-facing output, in the harness, not the prompt.

3. **Decide the failure action per category.** For each violation type: block and regenerate, block and return a safe fallback, redact the offending part, or escalate to a human (`hitl-escalation`). A screen with no defined action just logs harm as it ships. High-harm categories block; borderline ones may soften or flag.

4. **Handle refusals as a designed behavior.** When the agent should decline (out-of-scope, unsafe request), the refusal itself should be helpful and on-tone, not a curt block — and consistent, so users can't reword their way past it. Test that legitimate requests aren't over-refused (the other failure mode).

5. **Keep the prompt layer and the enforcement layer both.** Instruct the model on the policy (it prevents most violations cheaply) *and* enforce with the output screen (it catches what the model misses, including under injection). Prompt-only safety fails adversarially; screen-only wastes tokens generating content that gets thrown away — use both.

6. **Red-team the outputs and track a violation rate.** Attempt to elicit each disallowed category — directly and via injection (`injection-audit`). Add eval cases for both under-blocking (harm slips through) and over-blocking (safe content refused), and track a violation rate over time (`eval-harness`, `feedback-harvesting` for real complaints).

## Output contract
An output-safety design: the concrete output policy with examples, the between-generation-and-user screen, the per-category failure action, the refusal behavior, the prompt+screen dual layer, and red-team results with under/over-block eval cases and a tracked violation rate.

## Checklist
- [ ] Output policy enumerates disallowed categories with allowed/disallowed examples.
- [ ] Every user-facing output passes a screen in the harness, not just the prompt.
- [ ] Each violation category has a defined action (block/fallback/redact/escalate).
- [ ] Refusals are helpful, on-tone, consistent; over-refusal tested.
- [ ] Both prompt-layer instruction and enforcement-layer screen present.
- [ ] Red-teamed (direct + injection); under/over-block eval cases; violation rate tracked.
