---
name: skill-maintenance
description: Keep a growing skill library healthy — prune dead skills, merge near-duplicates, fix overlapping triggers, and retire skills stale for the current model generation. Use when the library grows past ~30 skills, when two skills fire on the same moment, when a skill never triggers, or on a scheduled library review.
---

# Skill Maintenance

A skill library rots the way a codebase does: duplicates accumulate, triggers overlap, and skills go stale as models change — but nobody owns the cleanup, so it compounds. `skill-distillation` adds skills and does a one-off overlap check; this skill owns the library's *ongoing* health. Past ~30–40 skills it's the difference between a sharp toolkit and a junk drawer.

## When to use
- The library has grown past ~30 skills, or growth has outpaced curation.
- Two skills fire on the same moment (routing ambiguity), or a skill never fires.
- Multiple evolution triggers target the same skill (dispatch to `evolution-conflict` for resolution).
- Scheduled library review, or after a model-generation turnover.

## When NOT to use
- Authoring or improving a single skill — that's `skill-authoring`.
- The library is small and clean — maintenance is overhead you don't need yet.

## Procedure

1. **Inventory usage from the routing log.** Pull each skill's fire rate, accept/override rate, and last-fired date from the router log (`routing-tuner`, `culture-telemetry`). This is the health data: a skill that never fires, always gets overridden, or hasn't fired in months is a maintenance candidate. Curate from evidence, not opinion about which skills "feel" useful.

2. **Prune the dead.** A skill that never triggers is either mis-described (fix the trigger via `skill-authoring`) or genuinely unused (retire it). Dead skills aren't free — every one is context the router weighs and a human scans. Retiring a skill is a healthy act, not a failure; keep the library to what earns its place.

3. **Merge near-duplicates.** Skills that overlap in scope confuse the router (which fires?) and the reader (which do I use?). Merge them into one, or sharpen the boundary between them so each owns a distinct moment. This is the failure mode `skill-distillation` warns about, caught library-wide rather than per-addition.

4. **Fix overlapping triggers.** Where two skills' descriptions match the same behavioral moment, the router miscasts. Disambiguate the descriptions (which is the routing-table fix in `routing-tuner`) so each moment routes to exactly one skill. Run the both-directions trigger test (`skill-authoring`) across the ambiguous pair.

5. **Retire what's stale for the model generation.** A skill tuned to an old model's quirks can be wrong on the current one (Culture Engineering's decay law). Re-validate skills against the current generation; retire or update those whose advice no longer holds. Tie this to `model-migration` — a generation turnover is a scheduled maintenance trigger.

6. **Coordinate with evolution: conflict priority and locking.** When `evolution-scan` detects multiple pending triggers on the same skill, apply them in priority order: safety/compliance > failure clusters > override clusters > model staleness. Take an advisory lock (`<skill-name>.evolution-lock`) before modifying a skill file during maintenance, to prevent concurrent evolution diffs from colliding. Dispatch to `evolution-conflict` for cases where two triggers propose contradictory changes. Release the lock after the maintenance pass completes.

7. **Keep the taxonomy and docs coherent.** As skills move, merge, or retire, update the group taxonomy, the routing table, and the documentation so they stay in sync. A library whose docs describe skills that no longer exist (or omit ones that do) has already started to rot. Leave the map matching the territory.

## Output contract
A maintenance report: the usage inventory (fire/override/last-fired per skill), pruned skills with reasons, merges/boundary-sharpenings applied, trigger-overlap fixes, staleness retirements tied to model generation, and the taxonomy/routing/doc updates that keep everything in sync.

## Checklist
- [ ] Per-skill usage pulled from the routing log (fire/override/last-fired).
- [ ] Never-firing skills either re-described or retired.
- [ ] Near-duplicates merged or their boundaries sharpened.
- [ ] Overlapping triggers disambiguated; both-directions trigger test run on ambiguous pairs.
- [ ] Skills stale for the current model generation re-validated, updated, or retired.
- [ ] Concurrent evolution triggers prioritized (safety > failure > override > staleness); advisory lock used; contradictions routed to `evolution-conflict`.
- [ ] Taxonomy, routing table, and docs updated to match the current library.
