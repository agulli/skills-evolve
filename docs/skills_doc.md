# Skill Catalog — Index

> **Generated file — do not hand-edit.** Regenerate with `scripts/gen-skills-catalog.sh`.
> The single source of truth is each skill's own `skills/<group>/<name>/SKILL.md` (its
> frontmatter and body). This index is a thin projection of that frontmatter, so it
> cannot drift. Routing lives in [`skills/ROUTING.md`](../skills/ROUTING.md); the
> telemetry spec in [telemetry_doc.md](telemetry_doc.md).

**59 skills across 7 lifecycle groups.** Follow any link for the full
procedure, when-to/when-not boundaries, output contract, and checklist.

## `design/` — Before code exists

- **[agent-architecture](../skills/design/agent-architecture/SKILL.md)** — Choose and document the right agent architecture (single-loop ReAct, workflow, handoffs, state graph, multi-agent) for a task before writing code.
- **[handoff-protocol](../skills/design/handoff-protocol/SKILL.md)** — Design the mechanics of multi-agent coordination — handoff conventions, shared vs. isolated state, message contracts between agents, and result-return — once you've chosen a multi-agent architecture.
- **[prompt-architecture](../skills/design/prompt-architecture/SKILL.md)** — Design or refactor an agent's system prompt as a structured, budgeted artifact — sections, context layers, and degradation order.
- **[requirements-interrogation](../skills/design/requirements-interrogation/SKILL.md)** — Force a structured requirements interview before designing or building an agent — extract what the agent must do, for whom, under what constraints, and how success is measured, one question at a time.
- **[tool-adversarial-reading](../skills/design/tool-adversarial-reading/SKILL.md)** — Review a proposed tool schema (JSON schema, OpenAPI spec, Python signature) by acting as the dumbest, most literal-minded model possible to expose ambiguity.
- **[tool-design](../skills/design/tool-design/SKILL.md)** — Design, review, or refactor an agent's tool definitions — granularity, schemas, naming, error contracts, and token cost of results.

## `build/` — While writing the agent

- **[context-engineering](../skills/build/context-engineering/SKILL.md)** — Engineer what occupies an agent's context window over a long run — token budgeting, compaction, summarization cadence, eviction policy, and result trimming — so it stays coherent and affordable across many turns.
- **[grounding-citation](../skills/build/grounding-citation/SKILL.md)** — Make an agent ground its claims in retrieved evidence and cite sources — verify quotes, attribute statements, and refuse or flag when unsupported — so answers are checkable and hallucinations are caught.
- **[mcp-server](../skills/build/mcp-server/SKILL.md)** — Scaffold, review, or debug an MCP server — transport choice, tool surface, auth, and packaging so agents can consume it.
- **[memory-design](../skills/build/memory-design/SKILL.md)** — Design an agent's memory system — what to remember, storage tiers, retrieval, and forgetting policy.
- **[multimodal](../skills/build/multimodal/SKILL.md)** — Design an agent's handling of non-text inputs and outputs — images, documents/PDFs, audio — including preprocessing, token/cost budgeting, grounding on visual evidence, and failure modes specific to each modality.
- **[retrieval-design](../skills/build/retrieval-design/SKILL.md)** — Design the retrieval layer for a knowledge agent — chunking, indexing, query construction, ranking, and how much retrieved content reaches the context — so answers are grounded in the right evidence at acceptable cost.
- **[skill-authoring](../skills/build/skill-authoring/SKILL.md)** — Write or review an Agent Skill (SKILL.md) so it triggers reliably, stays small in context, and produces checkable output.
- **[state-management](../skills/build/state-management/SKILL.md)** — Design durable state for long-running or resumable agents — checkpointing, resume-after-failure, idempotency, and human-in-the-loop pause/resume — so a multi-step run survives crashes, restarts, and waits without losing or duplicating work.

## `safety/` — Before anything touches prod

- **[agent-identity](../skills/safety/agent-identity/SKILL.md)** — Design who an agent acts as and what it's authorized to do — delegated identity, per-user permission boundaries, OAuth scope minimization, and the confused-deputy problem.
- **[compliance-mapping](../skills/safety/compliance-mapping/SKILL.md)** — Translate regulatory and policy obligations (GDPR, CCPA, sector rules, internal policy) into concrete agent controls and the audit evidence that proves them.
- **[guardrails](../skills/safety/guardrails/SKILL.md)** — Design and place guardrails for an agent — input validation, output filtering, tool permission tiers, and human-approval gates.
- **[injection-audit](../skills/safety/injection-audit/SKILL.md)** — Audit an agent for prompt injection — map untrusted data paths into context and test whether embedded instructions can hijack behavior.
- **[output-safety](../skills/safety/output-safety/SKILL.md)** — Screen and constrain what an agent says or generates — harmful/toxic content, unsafe advice, off-policy claims, and brand/compliance violations — before it reaches a user.
- **[privacy](../skills/safety/privacy/SKILL.md)** — Classify and protect personal data an agent touches — PII inventory, minimization, redaction-at-source, retention, residency, and the anonymization contract for anything that leaves the node.
- **[sandbox-policy](../skills/safety/sandbox-policy/SKILL.md)** — Choose and configure the execution sandbox for agent-run code — isolation level, filesystem/network policy, resource limits, and escape review.
- **[secrets-management](../skills/safety/secrets-management/SKILL.md)** — Handle credentials an agent uses — where API keys and tokens live, scoping, rotation, injection at egress, and keeping secrets out of prompts, logs, and traces.
- **[supply-chain-vetting](../skills/safety/supply-chain-vetting/SKILL.md)** — Vet a third-party skill, MCP server, tool, or model before it runs in your agent — because installing it executes its instructions in your context.

## `eval/` — Is it actually good?

- **[adversarial-review](../skills/eval/adversarial-review/SKILL.md)** — Subject a non-trivial agent design decision to a fresh-context adversarial review before it stands — spawn a reviewer biased to disprove, not approve.
- **[eval-harness](../skills/eval/eval-harness/SKILL.md)** — Build an evaluation harness for an agent — task set, graders, baselines, and a runnable pass/fail gate.
- **[llm-judge](../skills/eval/llm-judge/SKILL.md)** — Design and calibrate an LLM-as-judge grader — rubric, prompt, bias controls, and validation against human labels.
- **[model-card](../skills/eval/model-card/SKILL.md)** — Document an agent's capabilities, limitations, intended use, and evaluated performance in a standard card — so users, reviewers, and future maintainers know what it can and can't do without reverse-engineering it.
- **[silent-failure-audit](../skills/eval/silent-failure-audit/SKILL.md)** — Review only runs marked "Successful" to hunt for instances where the agent hallucinated a success message but quietly failed to execute the actual task.
- **[synthetic-task-generation](../skills/eval/synthetic-task-generation/SKILL.md)** — Thicken an evaluation suite by extrapolating highly plausible synthetic variations from real production tasks.
- **[trajectory-review](../skills/eval/trajectory-review/SKILL.md)** — Analyze agent transcripts/traces to find where and why runs go wrong — failure taxonomy, first-divergence analysis, and ranked fixes.
- **[verifier-design](../skills/eval/verifier-design/SKILL.md)** — Design and stress-test the pass/fail check (registrar, deterministic assertion, or grader) behind an eval — not the tasks, the check itself.

## `ops/` — Running in production

- **[agent-incident](../skills/ops/agent-incident/SKILL.md)** — Respond to a live agent misbehaving in production — contain blast radius, diagnose from traces, remediate, and turn the incident into regressions.
- **[agent-observability](../skills/ops/agent-observability/SKILL.md)** — Instrument a production agent — trace structure, the metrics that matter, cost/token accounting, and alerts.
- **[cost-governance](../skills/ops/cost-governance/SKILL.md)** — Control agent spend at the org/fleet level — budgets, per-tenant quotas, spend caps, attribution, and anomaly alerts — so many agents and users don't add up to a surprise bill or a runaway.
- **[cost-optimization](../skills/ops/cost-optimization/SKILL.md)** — Reduce an agent's cost and latency without dropping quality — measurement, prompt-cache hygiene, model routing, context diet, and batching.
- **[deployment](../skills/ops/deployment/SKILL.md)** — Ship an agent change safely — shadow, canary, staged rollout, and fast rollback gated on live metrics — so a bad prompt/tool/model change is caught on a fraction of traffic instead of all of it.
- **[human-review-escalation](../skills/ops/human-review-escalation/SKILL.md)** — Format a high-signal escalation request when an agent must hand off to a human — context, what was tried, the exact blocker, and actionable options.
- **[latency-optimization](../skills/ops/latency-optimization/SKILL.md)** — Reduce an agent's user-perceived latency — streaming, parallel tool calls, speculative/prefetch work, model-for-latency, and turn reduction — without losing quality.
- **[model-migration](../skills/ops/model-migration/SKILL.md)** — Move an agent to a new model generation without regressing — re-baseline evals, re-tune prompts for the new model's behavior, re-check breaking API changes and cost/latency, and roll out safely.
- **[model-routing](../skills/ops/model-routing/SKILL.md)** — Route each request or step to the right model by difficulty, cost, latency, and a quality floor — with fallback when the chosen model fails or refuses.
- **[reliability-engineering](../skills/ops/reliability-engineering/SKILL.md)** — Make an agent survive the failures of everything it depends on — model timeouts/rate limits, tool errors, provider outages — with retries, fallbacks, circuit breakers, and graceful degradation.

## `evolve/` — Self-evolving agents

- **[accretion-refactor](../skills/evolve/accretion-refactor/SKILL.md)** — Consolidate and shrink a bloated system prompt or skill by removing dead instructions, resolving contradictory constraints, and pruning rules added in panic.
- **[culture-telemetry](../skills/evolve/culture-telemetry/SKILL.md)** — Emit anonymized, signed usage statistics daily from the skill router to a shared public git commons as pattern-trial evidence, so validated agent-engineering norms accumulate across communities without any implementation, prompt, or trace ever leaving home.
- **[evolution-canary](../skills/evolve/evolution-canary/SKILL.md)** — Monitor a recently auto-applied skill change during its canary period — track override rate and eval scores post-apply, auto-revert on regression, promote to permanent on stability.
- **[evolution-conflict](../skills/evolve/evolution-conflict/SKILL.md)** — Resolve conflicts when multiple evolution triggers fire on the same skill simultaneously — prioritize by severity, sequence changes, detect contradictions, and escalate when two proposed fixes oppose each other.
- **[evolution-meta](../skills/evolve/evolution-meta/SKILL.md)** — Tune the evolution mechanism's own thresholds — override-rate trigger, failure-cluster minimum, canary duration, trust-earning count — based on evidence from past evolution cycles.
- **[evolution-propagate](../skills/evolve/evolution-propagate/SKILL.md)** — Propagate a promoted skill change beyond the local node — sync to other local projects, open an org PR with CI gating, or contribute evidence to the public commons via culture-telemetry. Also propagate reverts downstream.
- **[evolution-scan](../skills/evolve/evolution-scan/SKILL.md)** — Run a periodic evolution sweep — scan the routing log and telemetry for trigger conditions (high override rates, failure clusters, model shifts, distillation candidates), classify each by type and risk, and dispatch to the appropriate skill.
- **[feedback-harvesting](../skills/evolve/feedback-harvesting/SKILL.md)** — Systematically collect and structure feedback signals about an agent — explicit corrections, implicit signals (edits, overrides, abandonment), and outcomes — into a ranked improvement queue.
- **[routing-tuner](../skills/evolve/routing-tuner/SKILL.md)** — Turn skill-routing misfires and misses into gated edits to the routing table, so autonomous skill selection gets more precise over time.
- **[self-improvement-loop](../skills/evolve/self-improvement-loop/SKILL.md)** — Design a bounded self-improvement loop where an agent proposes changes to its own prompts, skills, or memory, gated by evals and review.
- **[skill-distillation](../skills/evolve/skill-distillation/SKILL.md)** — Distill successful agent trajectories into new or improved skills — extract the reusable procedure, generalize it, and validate it transfers.
- **[skill-maintenance](../skills/evolve/skill-maintenance/SKILL.md)** — Keep a growing skill library healthy — prune dead skills, merge near-duplicates, fix overlapping triggers, and retire skills stale for the current model generation.

## `dev/` — Developer inner loop

- **[agent-code-review](../skills/dev/agent-code-review/SKILL.md)** — Review a change to agent code for the failure modes generic code review misses — prompt/tool edits, context and cost impact, non-determinism, and safety-surface changes.
- **[agent-scaffolding](../skills/dev/agent-scaffolding/SKILL.md)** — Stand up a new agent project with the right structure from the first commit — layout, config, eval stub, observability hooks, and a runnable dev loop — so the developer starts productive instead of assembling boilerplate.
- **[codebase-onboarding](../skills/dev/codebase-onboarding/SKILL.md)** — Get productive fast in an existing agent codebase you didn't write — locate the prompt, tools, control loop, config, evals, and traces, and map how a request flows through them.
- **[local-replay](../skills/dev/local-replay/SKILL.md)** — Reproduce a single failing agent run locally and step through it, so a developer can debug one bad trajectory fast instead of guessing or re-running blind.
- **[prompt-experimentation](../skills/dev/prompt-experimentation/SKILL.md)** — Run a disciplined prompt/config experiment — variants, a fixed task set, one metric, and a kept winner — so prompt changes are decisions with evidence instead of vibes.
- **[testing-ergonomics](../skills/dev/testing-ergonomics/SKILL.md)** — Set up fast, cheap, deterministic tests for agent code — mock the model, stub tools, snapshot outputs, and unit-test tools without burning tokens or hitting the network.

