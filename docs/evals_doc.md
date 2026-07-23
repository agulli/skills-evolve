# Evaluation Mechanism

This document explains the evaluation mechanism (The "Gate").

## The Core Concept
The evaluation mechanism is the **truth layer** of the system. It answers the question, *"Did this actually make the agent better?"* Without this layer, an agent is just guessing and tuning by anecdote. Every change proposed by the system must pass through the numeric gate defined here before it can be trusted.

Evaluation is handled by the `skills/eval/` group, which builds both in-flight adversarial checks and post-hoc outcome-based test suites.

## How Eval is Made
The core of the evaluation system is built using the `eval-harness` skill. It enforces:

1. **Real Tasks:** An evaluation suite consisting of 20–50 tasks taken from *real usage* (logs, support tickets, failures), rather than synthetic scenarios. Every past incident must be included as a regression task.
2. **Deterministic Criteria:** Every task gets a pre-registered, checkable success criterion. Checks prefer programmatic assertions over LLM judges over human review.
3. **Outcome Grading:** The harness grades the end state (e.g., "was the ticket labeled correctly?"). It avoids asserting on the transcript or the agent's path, unless there are hard constraints (like cost).
4. **Statistical Honesty:** It runs every task multiple times to account for model nondeterminism, reports variance, and pins the baseline score.

## How Eval is Used
Once the harness is built, it serves as an automated, numeric gate:

- **Blocking Regressions:** The harness wires itself into CI or acts as a pre-commit hook. If a score drops or a single regression task fails, the change is blocked.
- **Gating the Loop:** When the `self-improvement-loop` proposes an automatic fix, it is subjected to the harness. If the fix improves the score, it advances; if the score drops, it is silently discarded.
- **Trace Debugging:** When eval scores drop, `trajectory-review` analyzes traces for the *first divergence* to find the root cause.
- **Model Disclosures:** `model-card` translates these numeric scores into an honest public disclosure of capability.
