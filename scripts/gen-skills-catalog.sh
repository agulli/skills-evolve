#!/usr/bin/env bash
# Generates docs/skills_doc.md — a THIN catalog index derived from each skill's
# SKILL.md frontmatter. The single source of truth is the SKILL.md files; this
# index is a projection of their frontmatter, so it cannot drift. Do not
# hand-edit the output — run this script to regenerate it.
set -euo pipefail
cd "$(dirname "$0")/.."
OUT=docs/skills_doc.md

SKILL_GROUPS=(design build safety eval ops evolve dev)
tag() { case "$1" in
  design) echo "Before code exists";;
  build)  echo "While writing the agent";;
  safety) echo "Before anything touches prod";;
  eval)   echo "Is it actually good?";;
  ops)    echo "Running in production";;
  evolve) echo "Self-evolving agents";;
  dev)    echo "Developer inner loop";;
esac; }

total=$(find skills -name SKILL.md | wc -l | tr -d ' ')
{
  echo "# Skill Catalog — Index"
  echo
  echo "> **Generated file — do not hand-edit.** Regenerate with \`scripts/gen-skills-catalog.sh\`."
  echo "> The single source of truth is each skill's own \`skills/<group>/<name>/SKILL.md\` (its"
  echo "> frontmatter and body). This index is a thin projection of that frontmatter, so it"
  echo "> cannot drift. Routing lives in [\`skills/ROUTING.md\`](../skills/ROUTING.md); the"
  echo "> telemetry spec in [telemetry_doc.md](telemetry_doc.md)."
  echo
  echo "**$total skills across ${#SKILL_GROUPS[@]} lifecycle groups.** Follow any link for the full"
  echo "procedure, when-to/when-not boundaries, output contract, and checklist."
  echo
  for g in "${SKILL_GROUPS[@]}"; do
    [ -d "skills/$g" ] || continue
    echo "## \`$g/\` — $(tag "$g")"
    echo
    for d in skills/"$g"/*/; do
      f="${d}SKILL.md"; [ -f "$f" ] || continue
      name=$(sed -n 's/^name: //p' "$f" | head -1)
      desc=$(sed -n 's/^description: //p' "$f" | head -1)
      what="${desc%% Use *}"   # keep the "what"; drop the "Use when…" trigger clause
      echo "- **[$name](../$f)** — $what"
    done
    echo
  done
} > "$OUT"
echo "wrote $OUT ($(wc -l < "$OUT") lines, $total skills)"
