---
name: agent-code-review
description: Review a change to agent code for the failure modes generic code review misses — prompt/tool edits, context and cost impact, non-determinism, and safety-surface changes. Use when reviewing a PR that touches prompts, tools, agent config, or skills, or before merging any change to an agent's behavior.
---

# Agent Code Review

A diff to an agent isn't like a diff to ordinary code: a one-line prompt edit can change behavior across every task, a new tool can open an exfiltration path, and "it passed once" proves nothing. Generic code review checks the code; this checks the *agent-specific* surface. It runs on the diff; `eval-harness` is the numeric gate this insists on.

## When to use
- Reviewing a PR that touches prompts, tool definitions, agent config, or skills.
- Before merging any change to how an agent behaves.

## When NOT to use
- Pure non-agent code in the repo (build scripts, unrelated services) — normal review applies.
- Reviewing the *design* rather than a diff — that's `agent-architecture` / `prompt-architecture`.

## Procedure

1. **Demand evidence, not assertion.** The PR must show the change ran against the eval harness with before/after scores — not "tested locally, looks good." A behavior change with no eval delta is unreviewable; send it back for the number (`eval-harness`, `prompt-experimentation`).

2. **Read prompt edits for blast radius.** A changed instruction affects *every* task, not just the one that motivated it. Check: does it contradict an existing instruction (the model averages contradictions)? Is it duplicated elsewhere now? Does aggressive phrasing ("ALWAYS", "you MUST") risk over-triggering? One-instruction-one-place, per `prompt-architecture`.

3. **Read tool/capability changes for the safety surface.** Any new or widened tool is a `guardrails` question: what's its blast-radius class (R/W/X/$)? Does it take untrusted input (`injection-audit`)? Does it handle secrets or PII (`secrets-management`, `privacy`)? A new `send_`/`delete_`/`deploy_` tool never merges without that check.

4. **Check the context and cost impact.** Does the change grow the prompt, add a large tool result, or increase turns? Estimate the token/cost delta (`cost-optimization`, `context-engineering`). A helpful-looking addition that adds 2k tokens to every call is a cost regression hiding as a feature.

5. **Check determinism and error handling.** New tool calls need actionable error contracts and retryable/non-retryable handling (`tool-design`, `reliability-engineering`). Any code that parses tool output must use a real parser, not string-matching. Flag anything that assumes the model returns exactly one shape.

6. **Confirm the regression net moved.** If the PR fixes a failure, a regression case for it must be *in the diff*. A fix with no test is a fix that will silently revert.

## Output contract
Review comments organized by the axes above (evidence, prompt blast-radius, safety surface, cost/context, determinism, regression coverage), each tied to a specific line, with a clear merge/block verdict and what's needed to unblock.

## Checklist
- [ ] Before/after eval numbers present; no eval delta → blocked.
- [ ] Prompt edits checked for contradiction, duplication, over-triggering.
- [ ] New/widened tools classified R/W/X/$ and checked for injection/secrets/PII surface.
- [ ] Token/cost/turn delta estimated; regressions flagged.
- [ ] Tool-output parsing is real parsing; error contracts actionable.
- [ ] Any fix ships with its regression case in the same diff.
