#!/usr/bin/env bash
# Agent Skills — installer
#
# Places the skill directories where your agent environment loads skills from,
# and tells you how to wire the router. Vendor-neutral: it detects common
# environments and lets you override the target.
#
# Usage:
#   ./install.sh                 # detect environment, install to it (asks first)
#   ./install.sh --dir PATH      # install into an explicit skills directory
#   ./install.sh --global        # install to the per-user (home) skills dir
#   ./install.sh --wire-routing  # ALSO append ROUTING.md to the instruction file (asks first)
#   ./install.sh --list          # just show what was detected, install nothing
#   ./install.sh --dry-run       # show what would happen, change nothing
#
# The installer never modifies anything outside the chosen skills directory
# unless you pass --wire-routing, and even then it asks before writing.

set -euo pipefail
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_GROUPS=(design build safety eval ops evolve dev)

DIR=""; GLOBAL=0; WIRE=0; LIST=0; DRY=0
while [ $# -gt 0 ]; do
  case "$1" in
    --dir) DIR="$2"; shift 2 ;;
    --global) GLOBAL=1; shift ;;
    --wire-routing) WIRE=1; shift ;;
    --list) LIST=1; shift ;;
    --dry-run) DRY=1; shift ;;
    -h|--help) sed -n '2,22p' "$0"; exit 0 ;;
    *) echo "unknown arg: $1" >&2; exit 2 ;;
  esac
done

say() { printf '%s\n' "$*"; }
run() { if [ "$DRY" = 1 ]; then say "  would: $*"; else eval "$*"; fi; }

# --- 1. Detect the environment's skills directory ---------------------------
# Maps a project/home marker → (skills dir, instruction file). First match wins.
# Format: "marker|skills_subdir|instruction_file"
PROJECT_ENVS=(
  ".claude|.claude/skills|CLAUDE.md"
  ".antigravity|.antigravity/skills|.antigravity/rules"
  ".codex|.codex/skills|AGENTS.md"
  ".gemini|.gemini/skills|GEMINI.md"
  ".cursor|.cursor/skills|.cursorrules"
  ".grok|.grok/skills|CLAUDE.md"
)
HOME_SKILLS=""; INSTR_FILE=""
detected=""
for e in "${PROJECT_ENVS[@]}"; do
  IFS='|' read -r marker sub instr <<<"$e"
  if [ -e "$marker" ]; then detected="$sub"; INSTR_FILE="$instr"; break; fi
done

if [ "$GLOBAL" = 1 ]; then
  # Per-user install — default to the most common home skills location present.
  for h in "$HOME/.claude/skills" "$HOME/.config/agent-skills"; do HOME_SKILLS="$h"; break; done
  DIR="${DIR:-$HOME_SKILLS}"
fi

# Resolve the target dir. Priority: explicit --dir > detected marker > ask the user.
# We do NOT silently guess for an unrecognized environment — that would drop files
# where the tool never looks. If we can't detect and can't ask, we stop.
if [ -z "$DIR" ] && [ -z "$detected" ] && [ "$LIST" != 1 ]; then
  if [ "$DRY" != 1 ] && [ -t 0 ]; then
    say "No known environment detected (.claude/.antigravity/.codex/.gemini/.cursor/.grok)."
    say "Enter your tool's skills directory (where it scans for SKILL.md files)."
    printf 'Skills directory: '; read -r DIR
    [ -n "$DIR" ] || { say "No directory given. See INSTALL.md for per-tool paths. Aborting."; exit 1; }
  else
    say "No environment detected and none given. Re-run with --dir PATH (see INSTALL.md)." >&2
    exit 1
  fi
fi
DIR="${DIR:-${detected:-.claude/skills}}"

if [ "$LIST" = 1 ]; then
  say "Detected environment marker  : ${detected:-none (will ask, or use --dir)}"
  say "Target skills directory      : $DIR"
  say "Instruction file (for router): ${INSTR_FILE:-CLAUDE.md}"
  say "Skills available to install  : $(find "$REPO_DIR" -name SKILL.md | wc -l | tr -d ' ')"
  exit 0
fi

# --- 2. Confirm, then copy each skill (flattened by name) -------------------
say "About to install into: $DIR"
if [ "$DRY" != 1 ] && [ -t 0 ]; then
  printf 'Proceed? [y/N] '; read -r ok; case "$ok" in y|Y) ;; *) say "aborted."; exit 0 ;; esac
fi
run "mkdir -p '$DIR'"

count=0
for g in "${SKILL_GROUPS[@]}"; do
  [ -d "$REPO_DIR/skills/$g" ] || continue
  for skill in "$REPO_DIR/skills/$g"/*/; do
    [ -f "${skill}SKILL.md" ] || continue
    name="$(basename "$skill")"
    run "cp -R '$skill' '$DIR/$name'"   # installed layout: <dir>/<skill-name>/SKILL.md
    count=$((count+1))
  done
done
say "Installed $count skills into $DIR"

# --- 3. Router wiring -------------------------------------------------------
INSTR="${INSTR_FILE:-CLAUDE.md}"
if [ "$WIRE" = 1 ]; then
  say "Wiring ROUTING.md into $INSTR"
  if [ "$DRY" != 1 ] && [ -t 0 ]; then
    printf 'Append the router block to %s? [y/N] ' "$INSTR"; read -r ok
    case "$ok" in y|Y) ;; *) WIRE=0 ;; esac
  fi
  if [ "$WIRE" = 1 ]; then
    if [ "$DRY" = 1 ]; then say "  would: append ROUTING.md rules to $INSTR";
    else
      { printf '\n<!-- agent-skills:routing:start -->\n';
        cat "$REPO_DIR/skills/ROUTING.md";
        printf '\n<!-- agent-skills:routing:end -->\n'; } >> "$INSTR"
      say "Appended router block to $INSTR"
    fi
  fi
else
  say ""
  say "NEXT STEP — wire the router (one-time):"
  say "  Copy the rules in $REPO_DIR/skills/ROUTING.md into your always-loaded"
  say "  instruction file ($INSTR). Or re-run with --wire-routing to append it automatically."
fi

say ""
say "Done. The router will now trigger skills from user behavior. Overrides always win."
