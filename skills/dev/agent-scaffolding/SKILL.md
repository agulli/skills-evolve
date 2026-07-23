---
name: agent-scaffolding
description: Stand up a new agent project with the right structure from the first commit — layout, config, eval stub, observability hooks, and a runnable dev loop — so the developer starts productive instead of assembling boilerplate. Use when starting a new agent from scratch, or when an existing agent has grown without a coherent project structure.
---

# Agent Scaffolding

The first hour of a new agent project decides whether the next month is pleasant. This skill lays down a structure where the eval harness, observability, and dev loop already exist as stubs — so those never become "later" tasks that never happen. It is the on-ramp; deeper design lives in `agent-architecture` and `prompt-architecture`.

## When to use
- Starting a new agent, feature, or service from scratch.
- An existing agent has no coherent structure (prompt inline in a 2000-line file, no eval, no traces).

## When NOT to use
- Choosing the architecture pattern itself — run `agent-architecture` first (this skill instantiates that decision).
- A one-off script that isn't really an agent — don't scaffold a project for a prompt.

## Procedure

1. **Fix the minimal viable structure**, not a framework cathedral. A working agent project needs, from commit one: the prompt(s) as versioned files (not string literals), the tool/capability definitions, a config surface (model, effort, limits) separated from code, an eval directory, and a place traces land. Create the directories empty-but-named so nobody has to invent them under pressure.

2. **Externalize config from code.** Model id, effort/temperature, token limits, and feature flags go in one config file, not scattered constants. This is what makes model-migration, cost work, and A/B trivial later — and impossible if hardcoded now.

3. **Seed the eval harness as a stub** (`eval-harness` proper comes later). Even 2 tasks with a pass/fail check and a `make eval` entry point means the gate exists before there's pressure to skip it. An agent that ships before its harness directory exists rarely gets one.

4. **Wire observability from turn one** (`agent-observability` for depth). At minimum: every run gets a trace id, and prompt/tool/model versions are stamped. Retrofitting trace plumbing after a production incident is the expensive path.

5. **Make the dev loop runnable in one command.** `make dev` (or equivalent) runs the agent on a single fixed input and prints the trace. If a new developer can't exercise the agent in under a minute, the inner loop is already broken — pair with `local-replay` for the debug loop.

6. **Write the README as you go** — how to run it, run evals, read a trace, and the one architectural decision from `agent-architecture`. The scaffold's README is the onboarding surface (`codebase-onboarding` consumes it).

## Output contract
A committed project skeleton: versioned prompt files, tool/config surfaces, an eval stub with a `make eval` entry point, trace plumbing with version stamping, a one-command `make dev`, and a README covering run/eval/trace/decision. Everything runnable; nothing hardcoded that should be config.

## Checklist
- [ ] Prompts and tools are versioned files, not inline string literals.
- [ ] Model/effort/limits/flags live in one externalized config surface.
- [ ] Eval directory + `make eval` stub exist with ≥2 tasks and a pass/fail check.
- [ ] Every run emits a trace id with prompt/tool/model versions stamped.
- [ ] `make dev` exercises the agent on one input in under a minute.
- [ ] README covers run, eval, read-a-trace, and the architecture decision.
