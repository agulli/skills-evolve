---
name: skill-authoring
description: Write or review an Agent Skill (SKILL.md) so it triggers reliably, stays small in context, and produces checkable output. Use when creating a new skill, when an existing skill fires on the wrong tasks or never fires, or when converting tribal knowledge into a skill.
---

# Skill Authoring

A skill is a procedure the agent loads *at the moment of need*. The two failure modes are: it never triggers (bad description), or it triggers and the agent still improvises (advice instead of procedure).

## When to use
- Creating a new skill for this library or a project's `.claude/skills/`.
- A skill fires on wrong tasks, never fires, or gets loaded then ignored.
- Turning a runbook, checklist, or "ask Antonio how we do X" knowledge into a skill.

## When NOT to use
- The knowledge is needed on *every* task → it belongs in CLAUDE.md or the system prompt, not a skill.
- It's a one-off task → just do the task.

## Procedure

1. **Name the trigger moment.** Complete the sentence: "The agent should load this when it is about to ___." If you can't finish it with a concrete action, this is documentation, not a skill.

2. **Write the frontmatter description as a matching target.** It must contain: what the skill does, the trigger conditions (including the words a user would actually type), and — if prone to misfiring — what it does NOT cover. The harness matches on this text alone; the body is invisible until loaded.

3. **Structure the body** with the library contract: When to use / When NOT to use / Procedure (numbered, imperative steps) / Output contract / Checklist. Prose advice goes inside a step or gets cut.

4. **Make every step executable.** Each step should be checkable as done/not-done by reading the transcript. "Consider the edge cases" is not a step; "list the edge cases for X and Y in the output" is.

5. **Budget the context.** SKILL.md ≤ ~150 lines. Reference tables, long examples, and scripts go in `references/` or `scripts/` inside the skill directory, with a one-line pointer in the body ("read `references/rubric.md` before scoring"). The agent pays for every line on every trigger.

6. **Add an anti-rationalization table.** The most dangerous failure mode is: the skill fires, the agent reads it, and then talks itself out of following it. For each step that the agent is likely to skip or shortcut, add a row to an `## Anti-rationalization` table: "The agent will try to [skip/shortcut]" → "The correct response is [why it matters and what to do instead]." Seed the table from experience — what shortcuts have agents actually taken when this skill was active? Three to five rows is enough; more than eight is noise.

7. **Test the trigger, both directions.** Run 3 prompts that *should* trigger it and 2 adjacent prompts that *shouldn't*. Fix the description — not the body — until 5/5. Then run one full end-to-end use and confirm the checklist is actually completable.

## Output contract
A skill directory: `<name>/SKILL.md` (+ optional `references/`, `scripts/`), passing the trigger test 5/5, with the test prompts noted in the PR/commit message.

## Checklist
- [ ] Trigger moment stated as a concrete action.
- [ ] Description contains what + when + user vocabulary; anti-triggers if needed.
- [ ] Body follows the contract; every step transcript-checkable.
- [ ] SKILL.md ≤ 150 lines; heavy material in `references/`.
- [ ] Anti-rationalization table present with 3–8 rows; seeded from observed agent shortcuts.
- [ ] Trigger test 5/5 (3 positive, 2 negative); one end-to-end run completed.
