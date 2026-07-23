---
name: compliance-mapping
description: Translate regulatory and policy obligations (GDPR, CCPA, sector rules, internal policy) into concrete agent controls and the audit evidence that proves them. Use when an agent operates under a compliance regime, before a compliance/security review, or when "are we compliant?" has no evidenced answer.
---

# Compliance Mapping

"Are we compliant?" is unanswerable until each obligation maps to a specific control in the agent and a specific piece of evidence that the control works. This skill turns regulation into a controls-and-evidence matrix. It doesn't replace the enforcing skills — it maps obligations *to* them (`privacy`, `guardrails`, `secrets-management`, `agent-observability`) and produces the audit trail.

## When to use
- An agent operates under a regulatory regime (GDPR, CCPA, HIPAA, financial rules) or binding internal policy.
- Preparing for a compliance, security, or procurement review.
- "Are we compliant?" currently has an opinion, not an evidenced answer.

## When NOT to use
- No external or internal obligation applies.
- Implementing a specific control — that's the relevant enforcing skill; this maps *to* it.

## Procedure

1. **Enumerate the obligations that actually apply.** List the specific requirements from each regime relevant to this agent — data subject rights, consent, retention limits, disclosure, human-review rights, sector-specific rules. Scope to what applies; a generic checklist you can't tie to the agent is theater. Get the real list from whoever owns compliance.

2. **Map each obligation to a concrete control.** For every requirement, name the exact mechanism that satisfies it and the skill that owns it — e.g. "right to deletion → the deletion path + cascade in `privacy`"; "least-access → per-user scoping in `agent-identity`"; "auditability → the trail in `guardrails`/`agent-observability`". An obligation with no named control is a gap, stated as one.

3. **Identify the evidence for each control.** Compliance is proven, not asserted: for each control, what artifact demonstrates it works? A deletion log, an access-audit record, a retention-policy config, an eval result, a redaction test. If you can't point to evidence, the control is unverified even if it exists.

4. **Find the gaps and rank them.** Where an obligation has no control, or a control has no evidence, that's a finding. Rank by risk (severity of the obligation × likelihood of scrutiny). This ranked gap list is the actionable output — it tells the team what to build/instrument before a review, not after.

5. **Wire evidence to be continuous, not snapshot.** The strongest compliance posture emits evidence as a byproduct of operation (audit logs, retention jobs, access records — `agent-observability`, `privacy`) rather than being reconstructed under deadline. Design controls so their evidence accrues automatically.

6. **Keep the map current across change.** A model swap, a new tool, or a new data flow can break a mapped control. Re-map on material change, and re-check obligations when the regime updates. Attach an owner and review cadence — a compliance map that isn't maintained is a liability with a date stamp.

## Output contract
A controls-and-evidence matrix: each applicable obligation → its control (and owning skill) → the evidence artifact that proves it, plus a ranked gap list (missing controls or missing evidence) and the review cadence/owner. Evidence sources wired to accrue continuously where possible.

## Checklist
- [ ] Applicable obligations enumerated from the real regimes, scoped to this agent.
- [ ] Every obligation mapped to a concrete control and the skill that owns it.
- [ ] Every control has a named evidence artifact; unproven controls flagged.
- [ ] Gaps (no control / no evidence) listed and risk-ranked.
- [ ] Evidence accrues continuously from operation where possible, not snapshot.
- [ ] Map has an owner and a re-map-on-change cadence.
