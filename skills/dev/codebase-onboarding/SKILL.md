---
name: codebase-onboarding
description: Get productive fast in an existing agent codebase you didn't write — locate the prompt, tools, control loop, config, evals, and traces, and map how a request flows through them. Use when inheriting or joining an unfamiliar agent, before changing an agent you don't fully understand, or when onboarding a teammate.
---

# Codebase Onboarding

An unfamiliar agent codebase hides its behavior in three places at once — the prompt, the tools, and the control loop — and a newcomer who changes one without understanding the others breaks it. This skill is the fast orientation: find the load-bearing pieces and trace one request end to end before touching anything.

## When to use
- Inheriting or joining an agent you didn't build.
- About to change an agent whose behavior you don't fully understand.
- Onboarding a teammate (produce the map for them).

## When NOT to use
- You built it and know it — skip.
- Setting up a *new* project — that's `agent-scaffolding`.

## Procedure

1. **Find the five load-bearing locations first.** Before reading broadly, locate: (a) the system prompt(s), (b) the tool/capability definitions, (c) the agent control loop, (d) the config surface (model, effort, limits), (e) the eval harness and where traces land. These five explain most behavior; everything else is support. If any is missing, that absence is itself the most important finding (and a job for `agent-scaffolding`).

2. **Read the prompt as the spec.** The system prompt is the agent's real specification — read it before the code. Note its constraints, procedures, and output contract; those tell you what the code is *trying* to do, which is faster than inferring intent from control flow.

3. **Trace one real request end to end.** Take a single representative input and follow it: prompt assembled → model called → tools invoked → results folded back → response. Use a real trace (`agent-observability`) if one exists. This one path teaches more than reading every file, and reveals which components are actually on the hot path.

4. **Run it before you change it.** Get the dev loop working locally (`make dev` or equivalent; `local-replay` on a real trace). An agent you can't run, you can't safely modify. If it won't run in a few minutes, fixing that is your first contribution.

5. **Locate the guardrails and the gate.** Find what the agent is *allowed* to do (`guardrails` — the R/W/X/$ surface) and what gates changes (`eval-harness`). Changing behavior without knowing these two is how newcomers cause incidents.

6. **Write the map you wish you'd had.** Capture the five locations, the request flow, how to run/eval/read-a-trace, and the top surprises. This becomes the onboarding doc (it belongs next to the scaffold README) and pays for itself with the next person — or with you in three months.

## Output contract
An orientation map: the five load-bearing locations (with paths), a one-request end-to-end flow, run/eval/trace instructions confirmed working, the guardrail + gate locations, and the top surprises. Committed as onboarding documentation.

## Checklist
- [ ] Prompt(s), tools, control loop, config, eval+traces all located by path.
- [ ] System prompt read as the spec before diving into code.
- [ ] One real request traced end to end.
- [ ] Agent runs locally; dev/replay loop confirmed working.
- [ ] Guardrail surface and eval gate identified.
- [ ] Orientation map committed for the next person.
