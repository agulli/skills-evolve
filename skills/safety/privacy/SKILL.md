---
name: privacy
description: Classify and protect personal data an agent touches — PII inventory, minimization, redaction-at-source, retention, residency, and the anonymization contract for anything that leaves the node. Use when an agent handles user data, before logging or telemetry that could carry personal data, or when data crosses a trust or organizational boundary.
---

# Agent Privacy

Privacy is a data-flow property, not a policy document. The engineering is: know what personal data enters, minimize it, redact it before it's stored or shipped, and prove that nothing identifying crosses a boundary it shouldn't. Anonymization is the load-bearing control — get it wrong and "aggregate telemetry" leaks individuals.

## When to use
- An agent ingests, stores, or transmits user data (messages, files, profiles, behavior).
- Before adding logging, tracing, or telemetry that could carry personal data.
- Data crosses a boundary: node → shared repo, org → commons, service → third party.

## When NOT to use
- The data is non-personal and non-proprietary throughout (public docs, synthetic fixtures).
- Access control / blast radius of *actions* — that's `guardrails`. Privacy governs *data at rest and in flight*.

## Procedure

1. **Inventory personal data by flow, not by field.** For each entry point, record: what personal data arrives, its sensitivity (identifier / quasi-identifier / sensitive-category), where it flows (context window, logs, memory, tools, telemetry), and where it comes to rest. You cannot protect data whose path you can't draw.

2. **Minimize at ingestion.** Drop what the task doesn't need before it enters context — the cheapest PII to protect is the PII you never took. Prefer references (IDs the agent can resolve on demand) over inlining records; prefer ranges/buckets over exact values (age band, not birthdate) wherever the task tolerates it.

3. **Redact at the source, not at read time.** Strip or tokenize identifiers *as they're written* to any store — logs, traces, memory, telemetry. Redaction applied at read time means the raw data already sat in the store waiting to leak. Keep a reversible tokenization vault only where re-identification is genuinely required, and gate it like an X/$ action (`guardrails`).

4. **Set retention and deletion on day one.** Every personal-data store carries a purpose, a TTL, and a deletion path (including a user-deletion request path). Data with no expiry and no delete path is a liability that only grows. Cascade deletion to derived stores (memory, embeddings, caches).

5. **Define the boundary-crossing / anonymization contract.** For anything that leaves the node or org, specify exactly what may cross — and prove it carries no personal data:
   - **Allowed to cross:** aggregate counts, rates, effect sizes, coarse categorical tags (model generation, use-case class). **Never:** raw text, prompts, traces, IDs, free-form fields, or any per-individual record.
   - **k-anonymity floor:** suppress or bucket any aggregate cell backed by fewer than *k* distinct subjects (k ≥ 5 is a reasonable default) — small cells re-identify.
   - **No free-text egress:** free-form strings can carry anything; they never cross a boundary as-is. Categorize into a fixed enum or drop.
   - **Structural enforcement:** the crossing is built so raw data *cannot* be attached (allowlist schema, not a denylist filter) — the [[culture-telemetry]] emitter is the worked example of this contract.

6. **Verify by trying to leak.** Audit real logs/telemetry/exports for personal data that slipped through; attempt re-identification on a sample of "anonymized" output using quasi-identifier joins. A privacy design with no leak-attempt is unverified.

## Output contract
A privacy design doc: the per-flow data inventory, minimization and redaction points, retention/deletion policy per store, the boundary-crossing contract (allowlist schema + k-floor), and the leak-attempt results. Redaction and the egress allowlist land as code, not prose.

## Checklist
- [ ] Every personal-data flow drawn end to end; sensitivity classified.
- [ ] Minimized at ingestion (references over records, buckets over exact values).
- [ ] Redaction/tokenization happens at write time to every store, including telemetry.
- [ ] Every store has purpose + TTL + deletion path; deletion cascades to derived data.
- [ ] Boundary crossings use an allowlist schema with a k-anonymity floor; no free-text egress.
- [ ] Leak-attempt + re-identification test run on real output.
