---
name: skill-distillation
description: Distill successful agent trajectories into new or improved skills — extract the reusable procedure, generalize it, and validate it transfers. Use when an agent keeps re-deriving the same solution, when a hard-won session should become permanent capability, or as the "learn" step of a self-evolving agent.
---

# Skill Distillation

When an agent solves something hard, the solution usually dies with the session. Distillation turns winning trajectories into skills — the difference between an agent with experience and an agent with amnesia.

## When to use
- The agent solved the same class of problem from scratch ≥3 times (re-derivation waste).
- A session produced a hard-won, non-obvious procedure worth keeping.
- The `self-improvement-loop` needs its "convert wins into capability" step.

## When NOT to use
- The knowledge is a single fact or preference → that's a memory write (`memory-design`), not a skill.
- One successful run of a novel task → wait for recurrence; skills distilled from n=1 encode luck.

## Procedure

1. **Select trajectories worth distilling.** From traces, find task clusters that recur AND succeed with high effort (many turns, backtracking, trial-and-error) — high effort + recurrence = high distillation value. Gather ≥2 successful trajectories of the cluster, plus failed attempts of the same task if available (they show what the skill must warn against).

2. **Extract the load-bearing path.** Strip each trajectory to the decisions and actions that mattered: which checks were done before acting, what order proved necessary, which tool patterns worked, where the dead ends were. Diff multiple successes: what's common is the procedure; what varies is parameterization.

3. **Generalize with named parameters.** Replace run-specific values (paths, names, versions) with parameters and a step for how to discover them. Every generalization must be backed by variation actually seen across trajectories — generalizing from one observation invents behavior nobody verified.

4. **Write the skill via `skill-authoring`** — full contract: trigger description in user vocabulary, numbered procedure, checklist. Fold the observed dead ends in as explicit warnings ("do X before Y; Y first corrupts Z — seen in trace #123"). Keep trace references in the commit, not the skill body.

5. **Validate transfer, not recall.** Run the agent WITH the skill on (a) one original task — must match or beat the original trajectory's turns/cost, and (b) two *new* instances of the class it never saw — must succeed without re-deriving. If (b) fails, the skill is a transcript summary, not a procedure; return to step 3.

6. **Check the library before landing**: does an existing skill cover this (extend it instead)? Does the new skill's trigger overlap an existing description (run both skills' negative trigger tests)? Library rot — five near-duplicate skills — is the distillation failure mode that compounds.

## Output contract
A skill directory passing the `skill-authoring` checklist, plus a distillation note in the PR: source trajectory IDs, effort saved (turns/cost, before vs. with-skill), transfer test results on unseen instances, and the library-overlap check.

## Checklist
- [ ] Source cluster recurs (≥2 successes); not distilled from n=1.
- [ ] Procedure = intersection of successes; dead ends folded in as warnings.
- [ ] Every generalization backed by observed variation.
- [ ] Transfer validated on 2 unseen instances, not just the source tasks.
- [ ] Measured effort reduction reported (turns/cost before vs. after).
- [ ] Library checked for overlap; extended rather than duplicated where possible.
