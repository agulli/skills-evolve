---
name: model-card
description: Document an agent's capabilities, limitations, intended use, and evaluated performance in a standard card — so users, reviewers, and future maintainers know what it can and can't do without reverse-engineering it. Use when an agent reaches a milestone/release, before handing it to another team, or when nobody can state what the agent is actually good at.
---

# Agent Model Card

An agent without a capability disclosure gets used outside what it's good at, reviewed without context, and inherited by people who must reverse-engineer its limits. A model card is the honest, evidenced statement of what the agent does, for whom, how well, and where it fails. It consumes `eval-harness` results and turns them into a disclosure others can trust.

## When to use
- An agent hits a release or milestone, or goes to real users.
- Handing the agent to another team, or publishing it internally/externally.
- Nobody can concisely state what the agent is and isn't good at.

## When NOT to use
- A throwaway prototype nobody else will touch.
- Building the evals themselves — that's `eval-harness`; this documents their results.

## Procedure

1. **State intended use and out-of-scope use.** What the agent is *for*, who should use it, and — just as important — what it should *not* be used for. Most agent harm comes from off-label use; naming the boundary is the highest-value line in the card. Be specific enough that a reader can tell whether their use case is in scope.

2. **Document capabilities with evidence, not adjectives.** For each thing the agent does well, cite the eval that shows it and the score (`eval-harness`). "Good at summarization" is marketing; "82% task-success on the summarization eval set, N=50" is a capability disclosure. Claims without numbers don't belong in a card.

3. **Document limitations and known failure modes honestly.** Where does it fail, degrade, or need supervision? What inputs break it? What did `trajectory-review` and `feedback-harvesting` reveal? An honest limitations section builds more trust than an inflated capabilities one — and prevents the incidents that come from surprise limits.

4. **Record the operating envelope.** The model generation it runs on, cost and latency profile, the guardrails/permissions in place (`guardrails`), data handling (`privacy`), and any human-in-the-loop requirement. This is what a reviewer or adopter needs to decide if it fits their constraints.

5. **Attach the evaluation context.** What was evaluated, on what data, when — so a reader can judge whether the numbers apply to their situation and how stale they are. Evals on a clean test set that doesn't match production is a caveat the card must state, not hide.

6. **Version and date the card; tie it to model generation.** A card is true for a model generation and a config; both churn. Stamp the date and versions, and re-issue on material change (`model-migration` triggers a re-card). A stale card asserting last-generation capabilities is worse than none.

## Output contract
A model card: intended and out-of-scope use, evidenced capabilities (with eval scores + N), honest limitations and failure modes, the operating envelope (model gen, cost/latency, guardrails, data handling, HITL), the evaluation context, and version/date tied to model generation. Lives with the agent and is re-issued on material change.

## Checklist
- [ ] Intended use and explicit out-of-scope use stated specifically.
- [ ] Each capability claim backed by an eval score and sample size.
- [ ] Limitations and known failure modes documented honestly.
- [ ] Operating envelope recorded (model gen, cost/latency, guardrails, data, HITL).
- [ ] Evaluation context (what/when/on-what-data) attached with staleness noted.
- [ ] Card versioned, dated, tied to model generation; re-issue trigger defined.
