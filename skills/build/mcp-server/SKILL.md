---
name: mcp-server
description: Scaffold, review, or debug an MCP server — transport choice, tool surface, auth, and packaging so agents can consume it. Use when building a new MCP server, wrapping an internal API for agent access, or when an MCP server's tools misbehave inside a client like Claude Code.
---

# MCP Server Engineering

An MCP server is an adapter between an agent and a capability. Get four things right: transport, tool surface, auth, and failure behavior. Everything else is plumbing.

## When to use
- Building a new MCP server or wrapping an existing internal API for agents.
- An MCP server connects but tools fail, hang, or flood context inside the client.
- Reviewing a third-party MCP server before letting agents use it.

## When NOT to use
- Designing the tool schemas themselves in depth (use `tool-design` — it composes with this skill).
- The capability is only needed by one agent in one repo — a plain function/CLI tool is cheaper than a server.

## Procedure

1. **Justify the server.** MCP pays off when a capability is shared across clients/agents or crosses a trust/process boundary. If neither holds, write an in-process tool and stop.

2. **Choose transport:**
   - `stdio` — local, spawned per client, credentials from the user's environment. Default for dev tools.
   - Streamable HTTP — shared/remote server, multiple clients, central auth. Required for anything multi-user.

3. **Define the tool surface with `tool-design`.** Keep it under ~10 tools per server; agents choose poorly from large flat menus. Split by audience if bigger. Expose resources for read-only reference data instead of tools that just fetch.

4. **Handle auth explicitly.** stdio: environment variables, documented in README, never baked in. HTTP: OAuth or bearer tokens with per-user identity — the server must know *who* the agent acts for, or it becomes a confused deputy.

5. **Engineer the failure behavior:**
   - Timeouts on every upstream call; return an actionable error, never hang (a hung tool stalls the whole agent turn).
   - Truncate/paginate results server-side; the client's context is not your log sink.
   - Log requests server-side with tool name, duration, and error class — you will need this the first week.

6. **Verify in a real client.** Register with the target client (e.g. `claude mcp add`), then run 5 realistic tasks. Confirm: tools listed, chosen correctly, errors surfaced readably, nothing hangs. A server tested only with the inspector is not done.

## Output contract
The server package plus README covering: transport, install/registration command for each target client, required env vars/auth setup, tool list with one-line descriptions, and the 5-task client verification results.

## Checklist
- [ ] Server justified (shared or cross-boundary); otherwise in-process tool chosen.
- [ ] Transport matches deployment (stdio local, HTTP shared) with auth model stated.
- [ ] ≤ ~10 tools; schemas passed the `tool-design` checklist.
- [ ] Every upstream call has a timeout; every error actionable; results size-bounded.
- [ ] Registered and verified in the actual target client, 5 realistic tasks.
