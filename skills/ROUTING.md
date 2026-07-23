# Skill Routing — self-driving skill use

**Install**: copy this section into your agent's always-loaded instruction file — `CLAUDE.md`, `AGENTS.md`, `GEMINI.md`, `.cursorrules`, `.antigravity/rules`, or whatever your tool loads on every turn (or reference it with an include directive if your tool supports one). It must be always-loaded context — the model can't route to skills it can't see. Nothing below is vendor-specific.

---

## Skill routing rules

You have an agent-engineering skill library. Do not wait to be asked: match the user's *behavior* against this table and apply the skill at the matching moment. Tiers define how much to involve the human.

**Tiers**
- **AUTO** — invoke immediately; announce in one line ("running trajectory-review on this trace"). Read-only/diagnostic skills.
- **PROPOSE** — name the moment and the skill, state what it produces, proceed unless the user redirects. Skills that create work products or change scope.
- **ASK** — never start without explicit confirmation. Skills that gate, block, or restructure things the user owns.

**Human override — always wins, both directions**: an explicit `/skill-name` runs regardless of this table; "skip it / not now" skips it without debate (but note skipped safety skills once in the final summary). If the user starts doing a skill's job manually, don't take over — offer the checklist.

**Log every decision so the router can improve.** Each firing (and each suppressed candidate) is a data point: record the moment signal, the skill fired, its tier, and the user's response (accepted / overridden / explicitly-invoked / corrected-to). Overrides and misses are not failures — they are the training signal `routing-tuner` uses to tighten this table over time. Autonomy without this log cannot improve; it only repeats.

**Shared Experiment Memory:** Before running simulator measurements or prompt routing benchmarks, check `EXPERIMENTS.md` to see previous results. Output raw JSON results to `simulator/results/<model>_<date>.json` and append a concise summary block under `## Log` in `EXPERIMENTS.md`.

| When the user… | Skill | Tier |
|---|---|---|
| starts a new agent with vague requirements, or asks "build me a bot that..." | `requirements-interrogation` | PROPOSE |
| starts a new agent, or asks "should this be multi-agent?" | `agent-architecture` | PROPOSE |
| starts a new agent project / has no coherent project structure | `agent-scaffolding` | PROPOSE |
| builds handoffs between agents, or a coordinator delegating to sub-agents | `handoff-protocol` | PROPOSE |
| writes/edits a system prompt, or reports the agent ignoring instructions | `prompt-architecture` | PROPOSE |
| adds or changes tool/MCP tool definitions, or the agent misuses tools | `tool-design` | AUTO |
| designing a new tool, or an agent frequently hallucinates tool parameters | `tool-adversarial-reading` | PROPOSE |
| writes or edits a SKILL.md | `skill-authoring` | AUTO |
| builds or wraps an MCP server | `mcp-server` | AUTO |
| needs the agent to remember things across sessions, or memory is stale/unbounded | `memory-design` | PROPOSE |
| long-horizon run where context truncates/degrades or token cost climbs with length | `context-engineering` | PROPOSE (restored 2026-07-22 — the EXP-005/006 HURTS finding was a broken eval registrar, not a real skill defect; corrected measurement in EXP-009 shows significant HELPS on Haiku, neutral/ceiling on Gemini) |
| builds RAG / a knowledge agent, or retrieved context is irrelevant/bloated | `retrieval-design` | PROPOSE |
| agent answers from documents but states facts without sources / may hallucinate | `grounding-citation` | PROPOSE |
| agent runs long/resumable, must survive restarts, or pauses for human input | `state-management` | PROPOSE |
| agent ingests images/PDFs/audio, or misreads visual content | `multimodal` | PROPOSE |
| is about to ship an agent to users, or adds a tool that spends/sends/deletes | `guardrails` | PROPOSE |
| connects an agent to web/email/tickets/third-party data | `injection-audit` | PROPOSE |
| is about to install an external skill/MCP server/tool/template | `supply-chain-vetting` | PROPOSE |
| makes an agent execute generated code or shell commands | `sandbox-policy` | PROPOSE |
| agent authenticates to a service, or adds a tool needing a key/token | `secrets-management` | PROPOSE |
| agent acts on behalf of users / serves multiple tenants / holds broad access | `agent-identity` | PROPOSE |
| agent produces user-facing content that could be harmful/off-policy | `output-safety` | PROPOSE |
| agent handles personal data, or before logging/telemetry that could carry PII | `privacy` | PROPOSE |
| agent operates under a regulatory regime, or before a compliance review | `compliance-mapping` | PROPOSE |
| changes model/prompt/tools on a working agent with no eval suite | `eval-harness` | PROPOSE |
| writing a programmatic pass/fail check, or an eval result looks surprisingly large/dramatic before trusting it | `verifier-design` | PROPOSE |
| eval suite has too few real examples, or testing resilience to noise | `synthetic-task-generation` | PROPOSE |
| eval scores are high but downstream bugs persist, or checking for metric fraud | `silent-failure-audit` | AUTO |
| tries prompt/config variants, or "this wording feels better" | `prompt-experimentation` | AUTO |
| agent tests are slow/flaky/costly, or a tool needs a unit test | `testing-ergonomics` | AUTO |
| makes a non-trivial agent decision under uncertainty, or asserts a safety property | `adversarial-review` | AUTO |
| pastes a failing trace, or eval scores dropped | `trajectory-review` | AUTO |
| one specific run went wrong and needs debugging | `local-replay` | AUTO |
| needs grading that can't be checked programmatically | `llm-judge` | AUTO |
| reviewing a PR that touches prompts/tools/agent config/skills | `agent-code-review` | AUTO |
| inheriting/joining an unfamiliar agent codebase | `codebase-onboarding` | AUTO |
| an agent hits a release milestone, or is handed to another team | `model-card` | PROPOSE |
| takes an agent to prod with no tracing/metrics | `agent-observability` | PROPOSE |
| a dependency's failure takes the agent down, or transient errors reach users | `reliability-engineering` | PROPOSE |
| releases a behavior change to a production agent | `deployment` | PROPOSE |
| upgrades the model behind an agent, or a model is deprecated | `model-migration` | PROPOSE |
| the agent feels slow, or p95 latency is user-facing | `latency-optimization` | PROPOSE |
| agent spans cheap+frontier models, or needs provider failover | `model-routing` | PROPOSE |
| says cost per task is too high, or plans a 10x scale-up | `cost-optimization` | PROPOSE |
| many agents/users/tenants share a budget, or spend needs limits/attribution | `cost-governance` | PROPOSE |
| reports an agent misbehaving in production **right now** | `agent-incident` | AUTO — contain first, ask later |
| agent is stuck in an error loop, faces ambiguity, or needs high-risk approval | `human-review-escalation` | AUTO — pause execution |
| has solved the same problem class ≥3 times across sessions | `skill-distillation` | PROPOSE |
| gives repeated corrections/complaints about the same agent behavior | `feedback-harvesting` | PROPOSE |
| overrides the same routing decision repeatedly, or reviews the routing log | `routing-tuner` | PROPOSE |
| the skill library has grown past ~30, or two skills fire on the same moment | `skill-maintenance` | PROPOSE |
| agent prompt has bloated by >30%, or starts dropping instructions | `accretion-refactor` | PROPOSE |
| connects the node to a shared culture commons, or publishes usage evidence upstream | `culture-telemetry` | ASK |
| wants the agent to improve itself, or approves recurring auto-fixes | `self-improvement-loop` | ASK |
| scheduled evolution sweep (daily/post-session), or manually reviewing the evolution backlog | `evolution-scan` | AUTO |
| a skill change was just auto-applied and needs canary monitoring | `evolution-canary` | AUTO |
| a canary-promoted change is ready for propagation beyond the local node | `evolution-propagate` | PROPOSE |
| multiple evolution triggers target the same skill file simultaneously | `evolution-conflict` | AUTO |
| 20 evolution cycles have completed, or the evolution loop shows pathology | `evolution-meta` | ASK |

**Compound moments** fire chains, not single skills: "ship it" → `guardrails` + `injection-audit` (+ `sandbox-policy` if it runs code) + `eval-harness` baseline. "It's broken in prod" → `agent-incident`, then `trajectory-review`, then a regression into `eval-harness`. Announce the chain once up front.

**Anti-triggers** — do not route when: the user is explicitly exploring/prototyping ("quick hack", "throwaway"); the same skill already ran this session on the same target; or the match is only topical (talking *about* evals ≠ building one — route on the *moment of work*, not the subject).

