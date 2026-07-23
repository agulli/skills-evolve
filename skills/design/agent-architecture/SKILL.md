---
name: agent-architecture
description: Choose and document the right agent architecture (single-loop ReAct, workflow, handoffs, state graph, multi-agent) for a task before writing code. Use when starting a new agent, when an existing agent has outgrown its pattern, or when someone asks "should this be multi-agent?".
---

# Agent Architecture Selection

Pick the **simplest architecture that meets the requirements**, and record why. Over-architecting is the #1 failure mode: most "multi-agent" systems should have been one agent with good tools.

## When to use
- Starting a new agent or agentic feature.
- An existing agent misses steps, loops, or blows its context budget — signs it has outgrown its pattern.
- Reviewing a design doc that proposes multi-agent.

## When NOT to use
- The task is a fixed pipeline with no decisions (write a script, not an agent).
- You're tuning prompts inside an already-chosen architecture (use `prompt-architecture`).

## Procedure

1. **Characterize the task** along four axes. Write the answers down:
   - **Branching**: is the path fixed (pipeline), decided once (router), or decided continuously (agent loop)?
   - **Horizon**: how many tool calls to complete? (<5, 5–30, 30+)
   - **Context**: does the working set fit one context window across the whole task?
   - **Specialization**: do subtasks need *different* tools/prompts/permissions, or just different data?

2. **Map to the decision ladder** — take the first rung that fits, going top to bottom:

   | Rung | Pattern | Choose when |
   |------|---------|-------------|
   | 1 | Plain LLM call / prompt chain | No tool use, no branching |
   | 2 | Workflow (fixed steps, LLM inside steps) | Branching decided once, path knowable in advance |
   | 3 | Single agent loop (ReAct) | Continuous decisions, horizon < ~30 calls, one toolset |
   | 4 | Agent + subagents (fan-out) | Context won't fit — subtasks need isolation, results summarize back |
   | 5 | Handoffs / router | Subtasks need *different* prompts+tools+permissions |
   | 6 | State graph | Long-lived process needing resume, retry, human-in-the-loop gates |
   | 7 | Peer multi-agent | Genuinely concurrent actors with independent goals (rare) |

3. **Stress the choice** with the three costs every rung above 3 adds: latency (serialized model calls), debuggability (distributed traces), and error compounding (each hop multiplies failure probability). If you can't name the concrete benefit that pays these costs, go down a rung.

4. **Write the decision record** (output contract below) into the repo, e.g. `docs/adr/agent-architecture.md`.

## Output contract
A decision record containing: the four axis answers, the chosen rung and pattern, the rungs rejected and why, the context budget per component, and the escalation trigger — the observable symptom that would justify moving up a rung later.

## Anti-rationalization

| The agent will try to… | The correct response is… |
|---|---|
| Jump straight to multi-agent because "it's a complex problem" | Complexity is not the criterion — specialization and context isolation are. Most complex problems are one agent with good tools. |
| "Let me just start building and figure out the architecture as I go" | Architecture decisions made during build are 10x harder to change. Spend 15 minutes on the decision ladder now. |
| Skip the stress test (step 3) because "the benefits are obvious" | If you can't name the concrete latency/debuggability/error cost, you can't justify the rung. Go down. |
| Choose rung 6–7 because "we might need it eventually" | You-Ain't-Gonna-Need-It applies to architecture. Pick the lowest rung that works today; the escalation trigger tells you when to go up. |

## Checklist
- [ ] All four axes answered with evidence, not guesses.
- [ ] Chosen the *lowest* rung that fits; each rejected lower rung has a stated reason.
- [ ] Every component has a stated context budget and toolset.
- [ ] Escalation trigger is observable (a metric or failure mode, not a feeling).
- [ ] Decision record committed to the repo.

