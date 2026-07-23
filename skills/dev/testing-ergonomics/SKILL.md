---
name: testing-ergonomics
description: Set up fast, cheap, deterministic tests for agent code — mock the model, stub tools, snapshot outputs, and unit-test tools without burning tokens or hitting the network. Use when agent tests are slow/flaky/expensive, when a tool needs a unit test, or when the only "test" is running the whole agent live.
---

# Testing Ergonomics

If the only way to test an agent is to run it live against the real model, developers stop testing. This skill makes agent tests fast, deterministic, and free — the layer *below* `eval-harness` (which measures end-to-end quality). Here we test the machinery: tools, parsing, control flow, prompt assembly.

## When to use
- Agent tests are slow, flaky, or cost tokens on every run.
- A tool or parsing/assembly function needs a unit test.
- The only existing "test" is exercising the full agent by hand.

## When NOT to use
- Measuring whether the agent is *good* end-to-end — that's `eval-harness` (which does hit the model, deliberately).
- Debugging one specific failing run — that's `local-replay`.

## Procedure

1. **Separate the deterministic machinery from the model call.** Tools, prompt assembly, output parsing, and control flow are ordinary code and should be unit-tested as such — no model, no network. If they're so tangled with the model call that you can't test them alone, that coupling is the first bug to fix.

2. **Unit-test tools directly.** Each tool is a function: test its happy path, its error contract (does it return an actionable, model-readable error?), and its result-size bound (`tool-design`). These tests are fast and free and catch the majority of "the agent is dumb" bugs, which are really tool bugs.

3. **Mock the model at the boundary.** For tests of agent control flow (does it loop correctly, handle `tool_use`, stop right), replace the model call with canned responses. Assert on *what the agent did with* a given model output, not on model quality. This makes agent-loop logic testable without tokens or flakiness.

4. **Snapshot prompt assembly.** The assembled prompt (system + tools + context) is a pure function of inputs — snapshot it. A snapshot diff catches accidental prompt changes, silent cache-busters (a timestamp creeping into the prefix — `cost-optimization`), and injection-surface changes, on every commit, for free.

5. **Keep the live-model layer thin and separate.** The few tests that genuinely need the real model (a smoke test, the eval harness) run in their own suite, not on every save. Tag them so `make test` stays fast and free while `make eval` (which costs tokens) runs deliberately in CI.

6. **Make the fast suite the default.** `make test` runs the deterministic suite in seconds with no network. If a developer's reflexive test command is slow or spends money, they won't run it — the ergonomics *are* the coverage.

## Output contract
A test suite split into: fast deterministic tests (tools, parsing, control flow via a mocked model, prompt snapshots) run by default with no network/tokens, and a separate tagged live/eval suite. Plus a note on how the model boundary is mocked so others can add tests the same way.

## Checklist
- [ ] Tools unit-tested directly (happy path, error contract, result-size bound).
- [ ] Model call mockable at a boundary; control-flow tests use canned responses.
- [ ] Prompt assembly snapshotted; cache-buster/injection changes surface as diffs.
- [ ] Live-model tests isolated in a separate tagged suite.
- [ ] Default `make test` runs in seconds, no network, no token spend.
