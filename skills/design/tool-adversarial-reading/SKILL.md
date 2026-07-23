---
name: tool-adversarial-reading
description: Review a proposed tool schema (JSON schema, OpenAPI spec, Python signature) by acting as the dumbest, most literal-minded model possible to expose ambiguity. Use before giving a new tool to an agent, or when an agent frequently hallucinated parameters or calls the wrong tool.
---

# Tool Adversarial Reading

Tool schemas are the leading cause of agent hallucinations. A developer writes a tool description thinking "it's obvious what this does," but models don't have common sense. This skill forces you to review a tool schema not for what it *intends* to say, but for how it could possibly be misinterpreted by a literal, lazy, or context-starved agent.

## When to use
- You are designing a new tool or API for an agent to use.
- An agent keeps hallucinating arguments for a specific tool.
- An agent frequently chooses the wrong tool from a large set.

## When NOT to use
- The tool has no arguments and a perfectly unambiguous name (e.g., `get_current_time`).
- Diagnosing a general reasoning failure unrelated to tool calling (use `trajectory-review`).

## Procedure

1. **Extract the Schema.** Isolate the exact JSON schema, docstring, or OpenAPI spec that will be fed to the LLM. Do not include external documentation the LLM won't see.
2. **Adopt the Persona.** Act as an adversarial, lazy, and hyper-literal agent. Your goal is to maliciously comply with the tool description to break the system.
3. **Attack the Description.** 
   - Is the description broad enough that you could use it for a task it wasn't meant for? (e.g., `search_data` — search what data? the web? a database?)
   - Does it overlap with another tool?
4. **Attack the Parameters.**
   - Are the types ambiguous? (e.g., `date: string` — what format? ISO8601? "next tuesday"?)
   - Are optional parameters really optional, or will the backend crash if they are omitted?
   - What happens if an empty string or null is passed?
5. **Draft the Fix.** Rewrite the schema to close the loopholes. 
   - Add explicit formats to parameters (e.g., `date (string, format: YYYY-MM-DD)`).
   - Add explicit "Do NOT use this tool for X" to the description.
   - Convert strings to enums wherever mathematically possible.
6. **Re-Review.** Ensure the new schema is as tight and constrained as a compiled language's type system.

## Anti-rationalization

| The agent will try to… | The correct response is… |
|---|---|
| Assume the model will "figure it out" from context. | Models do not have your context. The schema is the only truth they see. |
| Write a 3-paragraph description to explain the tool. | Long descriptions dilute attention. Constraints must be short, punchy, and ideally pushed into parameter enums, not prose. |
| Ignore edge cases because "the prompt tells it not to do that." | Instructions in the main prompt about a specific tool are often forgotten when the tool schema says otherwise. Fix the schema. |

## Output contract
A before-and-after diff of the tool schema, documenting the specific loopholes the adversarial persona found, and the tightened enums/descriptions added to close them.

## Checklist
- [ ] Schema reviewed in isolation, exactly as the model will see it.
- [ ] Adversarial persona successfully found at least one ambiguity or edge case in parameter types.
- [ ] Strings converted to enums where possible; formats explicitly specified.
- [ ] Overlap with other tools explicitly resolved in the description.
- [ ] Schema updated and diff recorded.
