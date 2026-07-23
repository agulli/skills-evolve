---
name: routing-tuner
description: Turn skill-routing misfires and misses into gated edits to the routing table, so autonomous skill selection gets more precise over time. Use when the model triggers the wrong skill (or none) at a moment it should have, when users repeatedly override AUTO/PROPOSE firings, or on a scheduled review of the routing log.
---

# Routing Tuner

This is the skill that makes *self-driving skill use improve over time*. The router in `ROUTING.md` decides which skill fires at each moment; this skill decides whether those decisions were right and tightens the table when they weren't. It is the concrete loop between autonomous triggering (model owns) and routing policy (human owns).

## When to use
- A skill fired on the wrong moment (**misfire**), or a failure happened where a skill should have fired but didn't (**miss**).
- Users repeatedly override the same AUTO/PROPOSE firing ("not now", "skip it") — a cluster of the same correction.
- Dispatched an override-cluster by `evolution-scan` (its scheduled sweep is what triggers this on nodes running the evolution pipeline — you don't need a separate schedule).

## When NOT to use
- **Scheduling** the review — on an evolving node that's `evolution-scan`'s job; this skill is the *fix* it dispatches to, reachable either reactively (a human notices overrides) or from a scan. Same fix either way.
- Tuning a single skill's *own* trigger description in isolation — that's `skill-authoring` step 6. This skill tunes the **table that arbitrates between skills**.
- The skill fired correctly but then performed badly — that's `trajectory-review` on the skill's procedure, not a routing problem.

## Procedure

1. **Log every routing decision as data.** The router must emit one record per firing (and per suppressed candidate): `{timestamp, moment_signal, skill_fired, tier, candidates_considered, user_response, run_id}`. `user_response` is the label — `accepted` / `overridden` / `explicitly_invoked` / `corrected_to:<skill>`. Without this log there is nothing to tune; standing up the log is step zero.

1b. **Compute per-skill override rates continuously.** As part of the log, maintain a rolling per-skill override rate (sliding window, minimum N≥10 invocations). When any skill exceeds the evolution trigger threshold (default 30%), flag it for `evolution-scan`. This is the bridge between routing and evolution: routing-tuner owns the measurement, `evolution-scan` owns the dispatch.

2. **Classify each imperfect decision.** Walk records where `user_response ≠ accepted`:
   - **Misfire** — fired when it shouldn't have (user overrode, or redid the task without it). The fix lives in an *anti-trigger*.
   - **Miss** — should have fired but didn't (a failure/incident occurred, or the user manually invoked what the router should have caught). The fix lives in a *new/broadened trigger row*.
   - **Miscast** — right moment, wrong skill (user corrected to a sibling). The fix is a *disambiguation* between two rows whose signals overlap.
   - **Wrong tier** — right skill, but AUTO annoyed the user (should PROPOSE) or PROPOSE blocked a routine action (should AUTO). The fix is a *tier change*, not a trigger change.

3. **Cluster before touching the table.** Group by `(moment_signal, classification)`. One override is noise; ≥3 records sharing a signal and classification is a cluster worth a diff. Rank clusters by frequency × cost (a missed `agent-incident` outranks a chatty `tool-design`).

4. **Propose the smallest table diff per top cluster** — exactly one of: add/tighten an anti-trigger, add/broaden a trigger row, add a disambiguation clause between two rows, or change one row's tier. One diff per iteration — simultaneous edits make the signal unattributable (same discipline as `self-improvement-loop`).

4b. **For misfires: draft the anti-trigger automatically.** When the classification is *misfire*, extract the common signal from the override cluster (the moment description users were in when they rejected). Draft an anti-trigger clause: a "When NOT to use" addition or a trigger-description narrowing that excludes this signal. Do not just classify and wait — produce the candidate fix. The fix is still gated (step 5) and risk-tiered (step 6).

5. **Gate on a routing eval set, not on the triggering cases.** Maintain a labeled set of moments with their correct routing decision (seed it from `skill-authoring`'s 3-positive/2-negative trigger tests, grow it from every confirmed misfire/miss). The diff must (a) fix its cluster and (b) not regress overall routing precision/recall on the full set. A change that only helps the cases it was derived from is overfitting the router.

6. **Apply with provenance; escalate tier changes.** Commit each accepted diff with its cluster, before/after routing scores, and iteration ID. Trigger/anti-trigger diffs can auto-apply once the tuner has a track record; **tier changes always need human approval** (they move the AUTO/PROPOSE/ASK boundary, which is human-owned policy), and any change touching an X/$ skill's routing always asks.

## Output contract
A routing-tuning report: the log window reviewed, cluster table (signal × classification × frequency × cost), the table diff applied per top cluster, before/after routing precision & recall on the eval set, and the new eval cases added. The `ROUTING.md` diff lands in version control; the routing eval set lives beside it.

## Checklist
- [ ] Routing decisions are logged with the `user_response` label; log window stated.
- [ ] Per-skill override rate computed on a rolling basis; skills exceeding threshold flagged for `evolution-scan`.
- [ ] Every imperfect decision classified misfire / miss / miscast / wrong-tier.
- [ ] Diffs target clusters (≥3 shared-signal records), ranked by frequency × cost.
- [ ] One diff per iteration, gated on the full routing eval set — not just the triggering cases.
- [ ] Tier changes and X/$ routing changes went through human approval.
- [ ] Confirmed misfires/misses added as routing eval cases; diff committed with provenance.
