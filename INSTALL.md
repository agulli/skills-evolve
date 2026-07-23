# Installing the Agent Skills package

**The honest mental model first:** a skill is inert markdown. Your agent *environment* (Claude Code, Antigravity, Codex, Gemini CLI, Cursor, Grok Build, …) loads skills by scanning a directory for `SKILL.md` files. So "installing" this package is two mechanical steps — **(1) put the skill directories where your environment looks, and (2) wire the router into your always-loaded instruction file** — plus an optional third step for deterministic hooks. There is no runtime to start; once the files are in place, the environment does the rest.

Because of that, there is no fully autonomous "installs itself with zero action" path — *something* has to place the files. But you can make that something a one-line command or your own agent. Three ways, easiest first.

## Will this work with my environment?

Not *any* environment — but any environment that **loads skills from a directory of `SKILL.md` files** and **loads an instruction file on every turn**. That covers 30+ tools. Three honest tiers:

| Your environment | Works? | What to expect |
|---|---|---|
| Loads a `SKILL.md` skills directory *and* an always-on instruction file — Claude Code, Antigravity, Codex, Gemini CLI, Cursor, Grok Build, Windsurf, Cline, Junie, Kiro, Goose, OpenCode, … | ✅ Fully | Both layers work: explicit `/name` invocation **and** behavior-based routing. `install.sh` auto-detects the six most common; for the rest, pass `--dir` or use the agent self-install — it adapts. |
| Loads a skills directory but **no** always-on instruction file | ⚠️ Skills yes, routing no | The skills install and work when invoked by name, but the router can't fire them from behavior (nowhere to put `skills/ROUTING.md`). You lose the self-driving layer, not the skills. |
| **No skills-directory concept** — app builders like Lovable, Replit; or raw API/no-harness use | ❌ Not directly | There's no directory to install into. Paste the relevant `SKILL.md` procedure into the prompt/instructions manually, or run these through a skill-capable CLI alongside your build tool. |

Two caveats hold even in tier ✅: routing *quality* tracks model capability (frontier models trigger crisply, small/local ones misfire more), and **layer-3 hooks are always per-tool** — there is no universal enforcement mechanism, so you recreate that gate in your tool's hook config, a git pre-commit hook, or CI.

`install.sh` will **not silently guess** for an environment it doesn't recognize — it asks for the skills directory (or refuses in non-interactive mode) rather than dropping files where your tool never looks.

---

## Option A — one command (deterministic)

From the repo root:

```bash
./install.sh              # detects your environment, asks, installs
./install.sh --list       # show what it detected, install nothing
./install.sh --dry-run    # show exactly what it would do
```

Useful flags: `--dir PATH` (install into an explicit skills directory), `--global` (per-user instead of per-project), `--wire-routing` (also append `skills/ROUTING.md` to the detected instruction file — asks first). The script only writes inside the chosen skills directory unless you pass `--wire-routing`. Installed layout is flat by skill name (`<skills-dir>/agent-architecture/SKILL.md`), which every SKILL.md-compatible tool reads.

## Option B — agent self-install (the "self-installing" path)

This is the meaningful sense of self-installing: **the package carries the instructions to install itself, and any capable agent executes them.** Point your agent at this file and say:

> "Install the Agent Skills package described in INSTALL.md into this environment."

The agent then follows the procedure below — detecting your environment, copying the skills, wiring the router with your consent, and verifying. This mirrors the repo's own thesis (model-routed, self-driving) and the Culture Engineering principle that *joining is loading a skill, not running an installer*. It also covers environments the script doesn't know about, because the agent adapts the procedure instead of matching a fixed marker list.

Follow these steps in order. Ask the user before any step that writes outside a skills directory.

1. **Detect the target skills directory.** Look in the current project for an environment marker and map it to its skills path and instruction file:

   | Marker present | Skills directory | Instruction file |
   |---|---|---|
   | `.claude/` | `.claude/skills/` | `CLAUDE.md` |
   | `.antigravity/` | `.antigravity/skills/` | `.antigravity/rules` |
   | `.codex/` | `.codex/skills/` | `AGENTS.md` |
   | `.gemini/` | `.gemini/skills/` | `GEMINI.md` |
   | `.cursor/` | `.cursor/skills/` | `.cursorrules` |
   | (none found) | ask the user, or default to `.claude/skills/` | `CLAUDE.md` |

   If the user wants a per-user install available in every project, use the home-directory equivalent (e.g. `~/.claude/skills/`) instead. Confirm the chosen path with the user.

2. **Copy the skills, flattened by name.** For each of the seven groups (`design build safety eval ops evolve dev`) under `skills/`, copy every `skills/<group>/<skill>/` directory to `<skills-dir>/<skill>/`. The group folders are a repo-organization convenience; installed skills are flat by name (names are already unique). Result: `<skills-dir>/agent-architecture/SKILL.md`, etc. Running `./install.sh` does exactly this — prefer invoking it over hand-copying if the shell is available.

3. **Wire the router — ask first.** Show the user that this appends the rules in `skills/ROUTING.md` to their always-loaded instruction file (step 1's instruction file), which is what makes skills fire from behavior rather than only on explicit `/name` calls. On consent, append it between clear markers (`<!-- agent-skills:routing:start -->` / `:end -->`) so it can be found and updated later. Without this step the skills still work, but only when the user invokes them by name.

4. **Add the routing decision log (enables self-improvement).** Tell the user the router logs each decision locally so `routing-tuner` can improve trigger precision over time (and, if they later opt in, so `culture-telemetry` can contribute anonymized evidence). This is a note in the instruction file, not code to run.

5. **Offer layer-3 hooks (optional).** For gates that must never depend on model judgment (eval gate before prompt commits; injection-audit before a new tool/server is used), offer to add the enforcement in the user's tool-specific mechanism (hook config, git pre-commit, or CI). Do not install these silently — they change commit/CI behavior.

6. **Verify.** Confirm the count of installed `SKILL.md` files matches the repo, and that the router block is present in the instruction file if step 3 was taken. Report what was installed, where, and what was skipped.

## After install

- **Invoke explicitly** with `/tool-design`, `/eval-harness`, etc. (however your tool triggers skills), or let the router fire them from behavior.
- **Update:** re-run `./install.sh` (it overwrites) or re-copy; the router block's markers let you replace it cleanly.
- **Uninstall:** delete the skill directories from your skills folder and remove the router block between its markers.
- **Culture reporting** is **on by default** (anonymized aggregates only, perimeter public) — see [telemetry_doc.md](docs/telemetry_doc.md) for exactly what crosses (a fixed allowlist of numbers/enums — never prompts, traces, or data) and how to opt out or narrow to `org-private`.

## Option C — manual

Copy the `skills/` directory into your environment's skills folder and paste `skills/ROUTING.md` into your instruction file. Paths per environment are in the [README](README.md#installation).
