---
name: state-management
description: Design durable state for long-running or resumable agents — checkpointing, resume-after-failure, idempotency, and human-in-the-loop pause/resume — so a multi-step run survives crashes, restarts, and waits without losing or duplicating work. Use when an agent runs long or across sessions, must survive interruptions and restarts, or pauses for human input.
---

# State Management

A long-running agent is a distributed workflow: it will crash, get restarted, hit a rate limit, or wait on a human halfway through. If its state lives only in the process, every interruption loses work or — worse — repeats side effects. This skill designs durable, resumable state. It is distinct from `memory-design` (knowledge to recall) and `context-engineering` (the window) — this is *execution* state.

## When to use
- An agent runs long enough to be interrupted (minutes to hours), or spans sessions.
- The run pauses for human approval/input and must resume later (`hitl` moments).
- Steps have side effects that must not double-execute on retry.

## When NOT to use
- Short single-turn tasks that complete in one call — durable state is overhead.
- Recalling facts across sessions — that's `memory-design`.

## Procedure

1. **Model the run as steps with explicit state transitions.** Identify the durable checkpoints — points where progress is worth saving. Between checkpoints is retryable work; at each checkpoint the run's state (what's done, what's next, accumulated results) is persisted so a restart resumes there, not from zero.

2. **Make every side-effecting step idempotent.** A crash after a side effect but before its checkpoint means the step reruns. Design so rerunning is safe: idempotency keys on external calls, "create-or-get" instead of "create", check-before-act. Non-idempotent side effects are how resumable agents send the same email twice or double-charge.

3. **Persist state outside the process.** Execution state goes to durable storage (db, workflow engine, or the harness's own state store), not in-memory. Persist enough to reconstruct the run: current step, inputs, completed results, and the context needed to continue. Redact secrets/PII in persisted state (`privacy`, `secrets-management`).

4. **Design pause/resume as a first-class state.** For human-in-the-loop waits, "waiting for approval" is a durable state the run can sit in for hours or days, then resume from — not a blocked thread. Capture what's being asked and what to do with each answer (`hitl-escalation` if present; otherwise define it here).

5. **Handle the retry/restart contract.** Define what happens on resume: verify the last checkpoint is consistent, skip completed idempotent steps, and cap retries so a poison step doesn't loop forever (`reliability-engineering`). A resume that blindly re-runs from the checkpoint without verifying state is a corruption source.

6. **Test by killing it mid-run.** Interrupt the agent at several points — before/after a side effect, during a tool call, while paused for input — and confirm resume completes correctly exactly once with no duplicated effects. A durable-state design with no kill-test is unverified.

## Output contract
A state design: the step/checkpoint model, the idempotency strategy per side-effecting step, the durable store and what's persisted (with secrets/PII redacted), the pause/resume states, the retry/restart contract, and kill-test results at multiple interruption points.

## Checklist
- [ ] Run modeled as steps with explicit durable checkpoints.
- [ ] Every side-effecting step is idempotent (keys / create-or-get / check-before-act).
- [ ] State persisted outside the process; enough to fully reconstruct; secrets/PII redacted.
- [ ] Human-wait modeled as a durable pause/resume state, not a blocked thread.
- [ ] Resume verifies checkpoint consistency, skips done steps, caps retries.
- [ ] Kill-test at multiple points confirms exactly-once completion, no duplicate effects.
