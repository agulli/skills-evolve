---
name: evolution-propagate
description: Propagate a promoted skill change beyond the local node — sync to other local projects, open an org PR with CI gating, or contribute evidence to the public commons via culture-telemetry. Also propagate reverts downstream. Use after evolution-canary promotes a change, or to review the propagation backlog.
---

# Evolution Propagate

A skill improvement that stays on one machine helps one person. Propagation turns local wins into shared capability — but only after the change has survived its canary. This skill owns the pipeline from "promoted locally" to "available everywhere it should be," with gates at every boundary.

## When to use
- `evolution-canary` has promoted a change (status `"permanent"`).
- Reviewing the backlog of promoted-but-not-propagated changes.
- A local revert needs to propagate downstream to org or other projects.

## When NOT to use
- The change hasn't survived canary yet — let `evolution-canary` finish.
- Publishing anonymized telemetry aggregates — that's `culture-telemetry` (aggregates, not diffs).
- Deploying an agent to production — that's `deployment`.

## Procedure

1. **Read the propagation backlog.** Pull all changes with canary status `"permanent"` and propagation status `null` or `"pending"`. Each entry has: change hash, skill name, diff, provenance, canary results.

2. **Local propagation (same machine, multi-project).** For each local project that has this skill installed (scan known install paths from `install.sh` config or a local registry): diff the promoted version against the installed version. If different, apply directly (global installs) or propose the sync with a one-line summary of what changed and the canary evidence.

3. **Org propagation (central registry).** If an org skill registry is configured:
   - Open a PR to the org repo with: the diff, provenance (trigger + evidence), canary results (before/after metrics, duration).
   - The PR triggers the org-wide `eval-harness` in CI.
   - **Low/Medium risk changes:** If CI passes, mark for auto-merge after a 48-hour cooldown. Any org member can veto during the cooldown by commenting on the PR.
   - **High/Critical risk changes:** Require explicit human approval on the PR.
   - Log the PR URL and status.

4. **Public propagation (evidence contribution).** The skill diff itself never crosses the public boundary — only anonymized usage aggregates do. Confirm that `culture-telemetry` is configured and will pick up the routing log entries for this skill on the next daily run. The public pipeline is: local evidence → `culture-telemetry` aggregates → public commons → Canon lifecycle. This skill does not bypass that pipeline.

5. **Revert propagation (downstream cleanup).** When a change is reverted locally (by `evolution-canary` or manually):
   - Check: was this change already propagated to other local projects? If yes, revert there too.
   - Check: was an org PR opened? If yes, open a revert PR with the regression evidence.
   - Log the downstream revert chain.

6. **Update propagation status.** For each change processed, update: `{propagation_status, local_targets_synced, org_pr_url, org_pr_status, revert_chain}`.

## Output contract
A propagation report per change: destinations reached, PRs opened (with URLs), CI results, cooldown status, and any revert propagation performed. The propagation registry is the persistent state.

## Checklist
- [ ] Only promoted (post-canary) changes enter the propagation pipeline.
- [ ] Local projects synced or sync proposed with canary evidence.
- [ ] Org PR opened with provenance + canary results; CI-gated; auto-merge on cooldown for Low/Medium risk.
- [ ] High/Critical risk org PRs require human approval.
- [ ] Public propagation deferred to `culture-telemetry` — no skill diffs cross the public boundary.
- [ ] Reverts propagated downstream to local projects and org PRs.
