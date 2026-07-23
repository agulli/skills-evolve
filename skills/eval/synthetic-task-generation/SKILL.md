---
name: synthetic-task-generation
description: Thicken an evaluation suite by extrapolating highly plausible synthetic variations from real production tasks. Use when an eval suite has too few real examples to be statistically significant, when preparing for a rare event (e.g., Black Friday), or when testing a model's resilience to noise and parameter shifts.
---

# Synthetic Task Generation

Eval suites must be grounded in reality, but reality doesn't always provide enough volume to achieve statistical significance. This skill thickens a thin eval suite by taking a seed of real tasks and generating dozens of plausible, challenging variations without relying entirely on imagination.

## When to use
- You have a core set of real tasks (e.g., 10), but need 50+ to reliably gate a release.
- You need to test edge cases that are possible but haven't happened yet in production.
- You want to test the agent's resilience to varied phrasing, noise, and typos.

## When NOT to use
- You have zero real tasks. Do not generate an entire eval suite from scratch; the agent will optimize for what you imagined, not reality.
- The agent is already failing the real, core tasks. Fix the core first.

## Procedure

1. **Extract the Seed.** Select 5-10 completely real tasks from production that the agent currently passes. These are the seeds.
2. **Identify the Axes of Variation.** For each seed, determine how it can plausibly vary in reality:
   - *Parameter shift:* (e.g., changing a date from "yesterday" to a specific holiday format).
   - *Noise injection:* (e.g., adding conversational filler, tangents, or frustration to the user prompt).
   - *Constraint layering:* (e.g., adding "Do this under 10 seconds" or "Format as XML").
3. **Generate the Synthetic Set.** For each seed, generate 3-5 variations across the identified axes. 
4. **Enforce Plausibility.** Review the generated tasks. Discard any task that requires capabilities the agent fundamentally doesn't have, or represents a scenario a user would realistically never encounter.
5. **Preserve the Success Criteria.** Ensure the generated task still has a mathematically or logically checkable success criterion. If the variation makes the success condition ambiguous, discard it.
6. **Tag as Synthetic.** In the eval harness, explicitly tag these tasks as `synthetic: true`. When reporting scores, always report the "Real" slice separately from the "Synthetic" slice.

## Anti-rationalization

| The agent will try to… | The correct response is… |
|---|---|
| Generate completely random, unrelated tasks. | Anchor firmly to the real seed tasks. Extrapolate, do not invent from scratch. |
| Make the tasks impossibly difficult. | The goal is robust testing, not guaranteeing failure. Keep variations plausible. |
| Forget to define success criteria for the new tasks. | A task without a checkable outcome is useless for an eval harness. |
| Mix synthetic and real tasks in the final score. | Always maintain a separate "Real" slice score to ensure the agent is actually improving on reality. |

## Output contract
A JSON or YAML array of newly generated eval tasks, complete with inputs, context, and explicit checkable success criteria, tagged as synthetic, ready to be injected into the harness.

## Checklist
- [ ] Seeds drawn from real, passing production tasks.
- [ ] Variations created across plausible axes (noise, parameter shifts).
- [ ] Tasks deemed implausible or uncheckable have been discarded.
- [ ] Success criteria clearly defined for every new task.
- [ ] All new tasks explicitly tagged as synthetic.
