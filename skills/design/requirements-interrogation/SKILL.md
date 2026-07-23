---
name: requirements-interrogation
description: Force a structured requirements interview before designing or building an agent — extract what the agent must do, for whom, under what constraints, and how success is measured, one question at a time. Use when starting a new agent, when requirements are vague or assumed, when a stakeholder says "build me an agent that does X," or when you're about to make architecture decisions without clear requirements.
---

# Requirements Interrogation

The most expensive agent failure mode is building the wrong thing confidently. An agent architect who skips requirements gathering will silently fill in ambiguity with assumptions — and those assumptions become load-bearing walls that are expensive to remove. This skill forces a structured interview *before* any design or code, extracting requirements one question at a time instead of guessing.

## When to use
- Starting a new agent or agentic feature with vague requirements ("build me a support bot").
- The stakeholder described *what* but not *for whom*, *under what constraints*, or *how we'll know it works*.
- About to choose an architecture (`agent-architecture`) but the requirements aren't concrete enough to evaluate options.
- Inheriting a half-built agent with no written requirements.

## When NOT to use
- Requirements are already documented and concrete — don't re-interview.
- A trivial change to an existing agent (bug fix, prompt tweak) — requirements are the existing behavior.
- You've already run this interview and the stakeholder approved the output.

## Procedure

1. **Ask one question at a time.** Do not dump a questionnaire. Ask, wait for the answer, then ask the follow-up that the answer implies. Batching questions gets shallow answers; sequencing gets real ones.

2. **Cover the six requirement areas** in this order (each builds on the previous):

   | Area | Key questions |
   |---|---|
   | **Purpose** | What does the agent do? What problem does it solve? What happens today without it? |
   | **Users** | Who uses it? What do they know? What do they expect? How technical are they? |
   | **Inputs & triggers** | What starts the agent? What data does it receive? What format? What volume? |
   | **Outputs & actions** | What does the agent produce? What side effects does it have? What systems does it touch? |
   | **Constraints** | Latency budget? Cost budget? Accuracy requirement? Compliance/privacy rules? What must it never do? |
   | **Success criteria** | How do we know it's working? What metric? What's the bar? Who judges? |

3. **Surface assumptions immediately.** After each answer, state what you're now assuming and ask the stakeholder to confirm or correct. Example:
   ```
   ASSUMPTION: The agent will handle English-only queries.
   ASSUMPTION: Response time should be under 5 seconds.
   ASSUMPTION: The agent should refuse to discuss competitor products.
   → Correct me now or I'll design with these.
   ```

4. **Push back on "it should just be smart."** When a requirement is vague, don't accept it — rephrase it as a concrete scenario and ask if that's what they mean. "It should handle edge cases" → "If a user asks about a product we discontinued, should the agent say 'we no longer carry that' or redirect to a similar product?"

5. **Write the requirements document.** After the interview, produce a structured requirements doc covering all six areas, with the assumptions that were confirmed and the decisions that were made. This document becomes the input to `agent-architecture`.

6. **Get explicit sign-off.** Do not proceed to design until the stakeholder has reviewed and approved the requirements. Changes after architecture selection are 10x more expensive than changes here.

## Anti-rationalization

| The agent will try to… | The correct response is… |
|---|---|
| "I have enough context to start building" | You have enough context to start *asking questions*. Requirements ≠ a chat message. |
| "The requirements are obvious from the description" | Obvious requirements produce the worst surprises. State them and get confirmation. |
| "I'll figure out the edge cases as I build" | Edge cases discovered during build are 10x more expensive to handle than edge cases discovered here. |
| "Let me just prototype something and iterate" | Prototyping without requirements means iterating toward an unknown target. |
| Skip this because the user seems impatient | An impatient stakeholder who gets the wrong agent is more upset than one who waited 10 minutes for good questions. |

## Output contract
A requirements document covering all six areas (purpose, users, inputs, outputs, constraints, success criteria), with stated assumptions confirmed by the stakeholder, ready to feed into `agent-architecture`.

## Checklist
- [ ] Interview conducted one question at a time, not batched.
- [ ] All six requirement areas covered with concrete answers.
- [ ] Assumptions surfaced and confirmed or corrected by stakeholder.
- [ ] Vague requirements pushed back on and made concrete.
- [ ] Requirements document written and approved before proceeding to design.
