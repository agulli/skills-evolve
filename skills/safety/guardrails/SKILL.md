---
name: guardrails
description: Design and place guardrails for an agent — input validation, output filtering, tool permission tiers, and human-approval gates. Use before an agent ships to users, when adding a risky tool, or when reviewing what an agent is allowed to do autonomously.
---

# Agent Guardrails

Guardrails are layered controls *around* the model, sized to blast radius. The model's own judgment is a layer, but never the only one for irreversible actions.

## When to use
- An agent is about to ship to real users or gain access to real systems.
- Adding a tool that can spend money, delete data, message humans, or touch prod.
- Reviewing/auditing an existing agent's permission surface.

## When NOT to use
- Prompt injection specifically (use `injection-audit` — it composes with this).
- Deciding *where code runs* (use `sandbox-policy`).

## Procedure

1. **Inventory actions by blast radius.** List every tool/action the agent can take and classify:
   - **R** — read-only, reversible (search, read file)
   - **W** — writes, reversible (edit file in git, draft message)
   - **X** — externally visible or hard to reverse (send email, post publicly, deploy)
   - **$** — spends money or destroys data (payments, deletes, prod migrations)

2. **Assign the control per class.** Defaults: R → allow; W → allow + audit log; X → human approval or strict allowlist per instance; $ → human approval, always, no autonomous path. Any deviation from defaults needs a written justification.

3. **Place input guards** where untrusted data enters: schema-validate structured inputs; length-cap and content-screen free text; tag data sources by trust level so downstream steps know what they're reading.

4. **Place output guards** before effects leave the agent: allowlist output channels; filter secrets/PII from anything user-visible or logged; validate outputs against schema before they drive tool calls.

5. **Enforce in the harness, not the prompt.** Prompt rules are the polite layer; permissions the model cannot override are the real layer. Every X/$ control must exist as code (permission config, approval hook, allowlist) that would hold even if the prompt were fully adversarial.

6. **Red-team before ship.** For each X/$ action, attempt: direct instruction to skip approval, instruction embedded in processed data, and multi-step chains where an R/W sequence adds up to an X effect (e.g. write file + trigger CI = deploy). Record attempts and outcomes.

7. **Wire the audit trail**: every W/X/$ action logged with timestamp, triggering input, and approval record. Define who reviews it and how often.

## Output contract
A guardrail spec: the action inventory table (action, class, control, enforcement point), input/output guard list, red-team log, and audit-trail location. Enforcement lands as code/config in the repo, not prose.

## Anti-rationalization

| The agent will try to… | The correct response is… |
|---|---|
| "This tool is read-only, it's safe" | Read-only tools leak data. A search tool that returns PII is not safe just because it doesn't write. |
| "The prompt already says not to do that" | Prompt rules are the polite layer, not the real layer. X/$ controls must exist as code. |
| "We'll add approval gates later" | An X/$ action that ships without a gate will be used before the gate arrives. Gate before ship. |
| Classify an X action as W because "it's reversible in theory" | If reversal requires human intervention or takes more than 60 seconds, it's X, not W. |
| Skip the red-team because "we trust our users" | Guardrails protect against *compromised inputs*, not malicious users. Trusted users paste untrusted data. |

## Checklist
- [ ] Every tool/action classified R/W/X/$; no unclassified capabilities.
- [ ] X and $ actions gated in the harness — verified by attempting bypass via prompt.
- [ ] Untrusted inputs validated and trust-tagged; outputs filtered before leaving.
- [ ] Chained-effect red-team done (R/W sequences that sum to X).
- [ ] Audit log captures all W/X/$ with inputs and approvals; reviewer named.

