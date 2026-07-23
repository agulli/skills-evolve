# Culture Telemetry — How It Works

How the skill router turns its own behavior into **shared, validated agent-engineering culture** — a public, community-owned record of which skills and routing rules actually work — **without any prompt, trace, or implementation ever leaving the machine.**

This document is self-contained: everything the mechanism needs is defined here. It is both the design and the boundary schema that makes the privacy guarantee *structural* rather than promised.

---

## The two rules everything follows from

1. **Nothing foreign executes.** Content pulled from the shared commons is *data* — claims and statistics — never code. Validated patterns are read and re-implemented locally by your own agent; a foreign card can never run on your node.
2. **Only allowlisted aggregates leave.** What crosses the node boundary is constructed field-by-field from a fixed **allowlist** (below). There is no path for raw text, prompts, traces, or per-user records to attach — not because a filter removes them, but because the outgoing record has nowhere to put them.

Everything else in this document is the machinery that upholds these two rules.

---

## Sharing is ON by default

A node shares by default. The value of the commons comes from broad participation, and because only anonymized aggregates can leave (the allowlist makes that structural), default-on is safe by construction — there is nothing identifying to leak.

- **Default:** sharing enabled, perimeter `public-commons`. Anonymized daily aggregates flow to the public ledger; the resulting validated Canon is public and free for the whole community.
- **Opt out** entirely (`sharing: off`) — nothing is emitted.
- **Or narrow the perimeter** to `org-private` — aggregates flow only to your org's internal ledger, never the public one.

The opt-out and perimeter are the *only* knobs. There is no setting that would cause anything beyond the allowlist to cross, because no such field exists.

---

## THE ALLOWLIST — exactly what crosses, and nothing else

A node emits records containing **only these fields**. This is the complete list. If a field is not on it, it does not cross the boundary — there is no code path to attach it.

| Field | Type | What it is |
|---|---|---|
| `pattern_id` | slug from the public taxonomy | Which claim this is evidence for (e.g. `route.failing-trace-to-trajectory-review`). Not free text. |
| `pattern_class` | enum: `routing` / `skill` / `protocol` / `strategy` | The kind of pattern. |
| `model_generation` | coarse bucket (e.g. `gen-2026-H1`) | Which model era it was trialed on. **Never** an exact model id/version. |
| `use_case_class` | value from the fixed public taxonomy | Domain of use (e.g. `debugging`). Free-form descriptions are dropped. |
| `window` | ISO day (e.g. `2026-07-19`) | The day this evidence covers. No wall-clock timestamps. |
| `n_trials` | integer | How many trials back this cell. **Suppressed if below the k-floor** (see below). |
| `accept_rate` | number, 2 dp | Fraction where the router's choice was accepted. |
| `override_rate` | number, 2 dp | Fraction the user overrode. |
| `inconclusive_rate` | number, 2 dp | Fraction with no clear signal. |
| `eval_delta` | `{metric, effect, ci}` — metric from a fixed list | Effect size on the eval gate where measured. |
| `outcome` | enum: `confirm` / `refute` / `inconclusive` | The pre-registered verdict for this window. |
| `perimeter` | enum: `public-commons` / `org-private` | Where this record is allowed to go. |
| `node_pseudonym` | rotating per-node handle | Lets the commons dedup/weight without identifying the node. Rotates on a schedule. |
| `signature` | signature over the record | Proves an independent node produced it; tamper-evident. |

**Every value above is a number, an enum, a taxonomy slug, or a signature.** None can carry the content of a conversation.

### What NEVER crosses (there is no field for it)

Raw prompts · system prompts · tool inputs/outputs · traces · logs · code or skill bodies · user data · file contents · request/response text · exact model id · node hostname/IP/org name · any free-form string · any per-user or per-run record.

---

## The daily pipeline, end to end

```
 (1) [ROUTING.md](../skills/ROUTING.md) fires a skill                    LOCAL — never leaves the node
      └─ router appends one decision record to a local log:
         {pattern_id, tier, user_response, eval_delta?, model_gen, use_case, run_id}

 (2) routing-tuner already reads this log to tune YOUR table (local only)

 (3) DAILY aggregation job                        LOCAL
      └─ GROUP BY (pattern_id, model_generation, use_case_class)
         → n_trials, accept/override/inconclusive rates, eval_delta
         Cells below the k-floor are held and rolled into the next day
         until they reach k (daily cadence AND k-anonymity, both kept).

 (4) allowlist construction                       ← THE BOUNDARY
      └─ build each outgoing record field-by-field from THE ALLOWLIST above.
         No "message"/"notes"/"context" field exists. Raw data has no path in.

 (5) sign + append                                CROSSES the boundary
      └─ sign under a rotating pseudonym; append-only commit to the ledger;
         push to the perimeter remote (public by default).

 ── boundary ──────────────────────────────────────────────────────────────

 (6) public commons accumulates cards from many nodes   SHARED, PUBLIC
      └─ append-only ledger, readable by anyone. Evidence for each pattern
         piles up across independent nodes and communities.

 (7) lifecycle: shared → proposed → CANON               (see below)

 (8) node pulls the public Canon                        back to LOCAL
      └─ reads validated CARDS (claims + mechanisms) and RE-IMPLEMENTS them
         locally. Foreign cards are DATA, never code (rule 1).
```

---

## The lifecycle: shared → proposed → Canon

Evidence is public and accumulates; norms are promoted only when independent communities agree, and a human can always intervene.

1. **Shared.** Every node's daily aggregates land in the public ledger. At this stage a pattern is just accumulating evidence — no status.
2. **Proposed.** When a pattern has **good support from independent communities** — confirmations from several unrelated nodes/orgs across more than one use-case class, with a consistent positive effect and low refutation — it is marked **proposed**: a candidate norm the community can see and scrutinize.
3. **Canon.** A proposed pattern that continues to hold under further independent evidence is **promoted to Canon** — the public, validated norm, free for the whole community to adopt. Canon is the payoff: the current, effect-size-backed state of what actually works.
4. **Human governance — block and remove.** A human maintaining the common repo can **block a promotion or remove a Canon entry** at any time — for a pattern that is harmful, being gamed, stale for the current model generation, or otherwise unfit. This human boundary sits permanently outside the automated loop: evidence proposes, but a maintainer can always dispose. Promotion thresholds and the taxonomy are likewise human-held and not writable by any emitter.

Because evidence is tagged by model generation, Canon re-validates itself as generations turn: a norm that stops being confirmed on the current generation ages out (or a maintainer retires it), so the Canon reflects what is true *now*, not folklore.

---


## Operational shape (what actually runs)

- **Where the log lives:** a local append-only log the router writes on every decision. Never committed to any remote.
- **What runs daily:** the aggregation + emit job — a pure function from the local log to a batch of allowlisted cards. Idempotent; safe to re-run.
- **The git operations:** pull the public commons (to read the Canon), and append-commit + push your signed daily cards (to contribute). Never a force-push, never an edit/delete of prior evidence — the ledger's value is its immutability.
- **Default-on, opt-out available:** sharing is on with perimeter `public-commons` unless you opt out or narrow to `org-private`.
- **Failure mode is benign:** the worst case of a bad or malicious card is *wasted trial budget* downstream — never a corrupted running system, because nothing foreign executes.

---

## The pattern card (identity of a claim)

A stable, public description of the claim being trialed — shared vocabulary, **no evidence and no node data**, authored once from the public taxonomy when a pattern is proposed:

```json
{
  "pattern_id": "route.failing-trace-to-trajectory-review",
  "pattern_class": "routing",
  "claim": "When the user surfaces a failing trace, invoking trajectory-review improves resolution.",
  "mechanism": "First-divergence analysis localizes the fault faster than re-reading.",
  "applicability": ["debugging", "prod-triage"],
  "schema_version": "2.0.0"
}
```

## The trial record (the evidence that crosses)

Exactly the allowlist fields — one record per `(pattern_id, model_generation, use_case_class)` per day:

```json
{
  "pattern_id": "route.failing-trace-to-trajectory-review",
  "pattern_class": "routing",
  "model_generation": "gen-2026-H1",
  "use_case_class": "debugging",
  "window": "2026-07-19",
  "n_trials": 42,
  "accept_rate": 0.83,
  "override_rate": 0.12,
  "inconclusive_rate": 0.05,
  "eval_delta": { "metric": "task_success", "effect": 0.07, "ci": [0.02, 0.12] },
  "outcome": "confirm",
  "perimeter": "public-commons",
  "node_pseudonym": "rot-9f3a…",
  "signature": "ed25519:…"
}
```

## Worked example — one day, one node

On 2026-07-19 the router faced a failing trace in 42 debugging sessions on gen-2026-H1: 35 accepted `trajectory-review`, 5 overrode, 2 inconclusive; the eval gate measured +0.07 task-success where it fired. Sharing is on (default), perimeter public. The daily job builds exactly the trial record above — 14 aggregate fields, k-floor satisfied (42 ≥ 5), signed under a rotating pseudonym, appended to the public ledger. No trace, no prompt, no org name, no exact model, no timestamp leaves. The public commons now holds one more independent confirmation; once independent communities agree, the pattern is **proposed**, then **promoted to Canon** — unless a maintainer blocks it.
