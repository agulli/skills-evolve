---
name: tool-design
description: Design, review, or refactor an agent's tool definitions — granularity, schemas, naming, error contracts, and token cost of results. Use when adding tools to an agent, when an agent misuses or ignores its tools, or when reviewing an MCP server's tool surface.
---

# Tool Design

Tools are the agent's UI. Most "the model is dumb" bugs are actually tool-design bugs: wrong granularity, ambiguous descriptions, or error messages the model can't act on.

## When to use
- Adding or changing tools for an agent (including MCP server tool surfaces).
- The agent picks the wrong tool, loops retrying a tool, or ignores a tool it should use.
- A tool result regularly floods the context window.

## When NOT to use
- Implementing the server plumbing itself (use `mcp-server`).
- The problem is *when* to call tools, not *which* — that's prompt procedure (use `prompt-architecture`).

## Procedure

1. **Set granularity from the task, not the API.** One tool per *agent-level intention*, not per endpoint. `search_orders(query)` beats `list_orders` + `filter_orders` + `sort_orders`. Merge tools that are always called in sequence; split tools whose description needs the word "or".

2. **Write the description for the model, not the docs site.** Each description must answer: what it does, when to prefer it over sibling tools, and what it returns. If two tools' descriptions could be swapped without looking wrong, the model can't choose between them either.

3. **Design the schema defensively:**
   - Required params only for what's truly required; defaults for everything else.
   - Enums over free strings whenever values are enumerable.
   - No param the model must copy verbatim from a previous result if the tool could look it up itself (copy steps are where hallucinated IDs enter).

4. **Design the error contract.** Every error message must be *actionable by the model*: state what was wrong and what to do differently ("date must be YYYY-MM-DD, got '3/4/25'"), never a bare stack trace or "internal error". Distinguish retryable from non-retryable explicitly.

5. **Budget the results.** Measure the token size of a typical and a worst-case result for each tool. Any tool that can return >2k tokens needs pagination, a `limit` default, or a summary mode. The agent's context is your most expensive resource.

6. **Test with the model, not just unit tests.** Give the agent 5 realistic tasks and count: wrong-tool selections, malformed calls, retry loops. Iterate on descriptions/schemas until all three hit zero on the sample.

## Output contract
The tool definitions (schema + description) plus a short design note: granularity rationale, per-tool worst-case result size, error contract summary, and the model-in-the-loop test results.

## Checklist
- [ ] Every tool maps to one agent intention; no always-called-together pairs.
- [ ] Descriptions are mutually distinguishing (swap test passes).
- [ ] Enumerable params are enums; no verbatim-copy params where avoidable.
- [ ] Every error message states what to do differently; retryable flagged.
- [ ] Worst-case result size measured; >2k-token tools have limits or summaries.
- [ ] 5-task model test run: zero wrong-tool picks, malformed calls, retry loops.
