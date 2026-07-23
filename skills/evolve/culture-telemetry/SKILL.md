---
name: culture-telemetry
description: Emit anonymized, signed usage statistics daily from the skill router to a shared public git commons as pattern-trial evidence, so validated agent-engineering norms accumulate across communities without any implementation, prompt, or trace ever leaving home. Use when a node reports usage evidence, when publishing which skills/routing rules actually work, or when configuring the daily culture-sharing job.
---

# Culture Telemetry

Each skill and each routing rule is a **falsifiable pattern**: a claim ("when the user pastes a failing trace, trajectory-review helps") with a mechanism. A node's local logs — accept/override rates, eval deltas — are *pre-registered trial evidence* for those patterns. This skill turns those local trials into anonymized, signed statistics and appends them daily to a shared public commons, so the community learns which norms are real. The full self-contained mechanism, allowlist, and lifecycle are in `../../../docs/telemetry_doc.md`; the local decision log comes from [[routing-tuner]] and the anonymization contract from [[privacy]].

**The hard rule: nothing foreign executes, and implementations/traces structurally cannot leave the node. Only allowlisted aggregate statistics cross a boundary — by allowlist, never by filter. Sharing is ON by default (perimeter public); the allowlist is what makes default-on safe.**

## When to use
- Configuring or running the daily culture-sharing job on a node.
- Publishing which skills / routing rules earn their place, with effect sizes.
- Reviewing what a node contributes to the public commons.

## When NOT to use
- Tuning *this* node's own routing table — that's `routing-tuner` (local; no boundary crossing).
- Any export that would carry raw prompts, traces, code, or per-user records — that is out of scope by construction, not by configuration.

## Procedure

1. **Confirm the sharing setting and perimeter.** Sharing is **on by default** with perimeter `public-commons` (anonymized aggregates → public ledger; validated Canon is public and free). A node may opt out entirely, or narrow to `org-private` (aggregates stay inside the org). These are the only knobs — no setting can widen what crosses beyond the allowlist.

2. **Aggregate local trials daily.** Run the aggregation as a **daily** job. From the `routing-tuner` decision log, group by `(pattern_id, model_generation, use_case_class)` and compute `n_trials`, `accept_rate`, `override_rate`, `inconclusive_rate`, and `eval_delta` (effect size from the `eval-harness` gate where available). One record per pattern per generation per use-case class per day.

3. **Build the outgoing record from THE ALLOWLIST** (the exact field list in `../../../docs/telemetry_doc.md`). It holds only numbers, enums, taxonomy slugs, and a signature — construct it field-by-field from an empty record. There is no `message`/`notes`/`context` field, so raw text, prompts, traces, IDs, and exact model ids have no path to attach.

4. **Enforce the structural privacy guards.** k-anonymity floor (default k=5): suppress any cell below k and **roll it into the next day** until it reaches k — preserving both daily cadence and anonymity. Coarse tags only (`model_generation` bucket, taxonomy `use_case_class`). Rotating per-node pseudonym over the signature so trials are verifiable and dedup-able without identifying the node.

5. **Report three outcomes, pre-registered.** Each record reports `confirm` / `refute` / `inconclusive` against a threshold set before the window — never a binary. Refutations and inconclusives are first-class: they narrow a pattern's applicability, which is how the community learns boundaries rather than folklore.

6. **Append, sign, push — daily.** Append-only commit (never edit/delete prior evidence — the public ledger is the audit trail), signed, pushed to the perimeter remote. Contributing evidence is all this skill does: it never promotes. Promotion to Canon and any block/removal are human-held governance on the common repo (see `../../../docs/telemetry_doc.md` → lifecycle).

7. **Verify the boundary before first push.** Attempt to leak: inspect a real outgoing daily batch for any free-text, ID, exact-model, or per-record field; attempt re-identification via quasi-identifier joins (per `privacy`). Confirm every cell meets the k-floor. An emitter that hasn't been leak-tested must not be pointed at a shared remote.

## Output contract
An emitter (config + code) running daily, plus per day: the outgoing batch of allowlisted, signed trial records, the sharing/perimeter setting, and the leak-test result. The public commons receives append-only, signed, k-floored aggregate records — and by construction nothing else. Allowlist and lifecycle live in `../../../docs/telemetry_doc.md`.

## Checklist
- [ ] Sharing setting + perimeter confirmed (default-on/public unless opted out or narrowed).
- [ ] Aggregation runs daily per (pattern, model generation, use-case class) with n, rates, eval delta.
- [ ] Outgoing record built from the allowlist; no path for text/traces/IDs/exact-model to attach.
- [ ] k-anonymity floor enforced; sub-k cells rolled to next day, not leaked or force-emitted.
- [ ] Three-outcome (confirm/refute/inconclusive), pre-registered; refutations emitted, not hidden.
- [ ] Append-only, signed under a rotating pseudonym; generation-tagged; pushed daily.
- [ ] Leak-test + re-identification attempt passed before pointing at a shared remote.
