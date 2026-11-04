#!/usr/bin/env bash
# Vendor agent-self-evolution skill + ensure Holding matrix block in AGENTS.md
set -euo pipefail

HOLDING="$(cd "$(dirname "$0")/../.." && pwd)"
SKILL_SRC="$HOLDING/agent-self-evolution"
MARKER_BEGIN="<!-- HOLDING-MATRIX:BEGIN -->"
MARKER_END="<!-- HOLDING-MATRIX:END -->"

DEFAULT_REPOS=(
  "$HOLDING"
  "${HOME}/Developer/risegenai/risegen-hub"
  "${HOME}/Developer/risegenai/risegen-ai-platform"
  "${HOME}/Developer/risegenai/risegen-code"
  "${HOME}/Developer/risegenai/risegen-inference-connector"
  "${HOME}/Developer/risegenai/risegen-agentic-backlog-gate"
  "${HOME}/Developer/risegenai/risegen-dex"
  "${HOME}/Developer/risegenai/risegen-shared"
  "${HOME}/Developer/risegenai/risegen-tools"
  "${HOME}/Developer/risegenai/risegen-lucensmind"
  "${HOME}/Developer/risegenai/risegen-model-runtime"
  "${HOME}/Developer/risegenai/risegen-designsystem"
  "${HOME}/Developer/risegenai/risegen-brandsystem"
  "${HOME}/Developer/risegenai/risegen-spatium"
  "${HOME}/Developer/risegenai/risegen-opencode-engine"
  "${HOME}/Developer/risegenai/designsystem-master"
  "${HOME}/Developer/risegenai/hub"
)

if [[ -n "${REPOS:-}" ]]; then
  # shellcheck disable=SC2206
  REPO_LIST=($REPOS)
else
  REPO_LIST=("${DEFAULT_REPOS[@]}")
fi

write_matrix_block() {
  local out="$1"
  cat >"$out" <<EOF
$MARKER_BEGIN
## Holding matrix (NON-NEGOTIABLE — progressive disclosure)

**Skill (default on every repo):** \`agent-self-evolution\`
(\`@holding-central-ai-assets/agent-self-evolution\`).
After **any** agent failure or founder correction, run that skill
(failure card → category → generalized rule → action plan → matrix → reconcile)
before closing the incident.

**Always-on rules (full text in skill package):**
- Evidence before diagnosis (\`research-before-asserting\`).
- Decide-high / execute-low; verify executors with commands.
- No unplanned external spend; no commit/push without founder OK.
- English artifacts; Portuguese with the user.
- Memory-bank for non-trivial work.
- Stable names over volatile addresses (DDNS / LAN aliases — never an IP as durable identity, and never a live request to an IP literal when a canonical hostname exists).
- Micro-specs: absolute host paths + secret key names (\`HOST_SUDO_PASSWORD\`, …).
- Search secrets before asking the founder for passwords.
- Never substitute a nearby subject for the one the requester named; an empty or partial resolver result is *not found in that layer*, and an unresolved target stops side-effecting work (harness-enforced, not prompt-enforced).
- Shared infra SoT: \`lakenbeach/holding-shared-infra\` + skill \`shared-infra-sot\` (not chat memory).
- Set/scope membership comes from the product's own domain model, never a backend's grouping (areas, rooms, tags).
- Never report an effect from the actor's own success signal — read the affected state back independently.
- A recurrence of a known failure family is a detection defect first: add the missing measurement before fixing the new symptom.

**Depth (open only when needed):** skill \`references/matrix-layers/\` and \`references/lessons/\`.
**Canonical matrix file:** \`holding-central-ai-assets/agent-self-evolution/references/matrix-always-on.md\`.
$MARKER_END
EOF
}

ensure_apm_dep() {
  local repo="$1"
  local apm="$repo/apm.yml"
  local dep="marcvlima/holding-central-ai-assets/agent-self-evolution"
  if [[ ! -f "$apm" ]]; then
    cat >"$apm" <<YAML
name: $(basename "$repo")
version: 1.0.0
description: APM project for $(basename "$repo")
targets:
  - claude
dependencies:
  apm:
    - $dep
includes: auto
scripts: {}
YAML
    echo "  created apm.yml"
    return
  fi
  if grep -qF "agent-self-evolution" "$apm" 2>/dev/null; then
    echo "  apm dep present"
    return
  fi
  python3 - "$apm" "$dep" <<'PY'
from pathlib import Path
import sys
p = Path(sys.argv[1])
dep = sys.argv[2]
text = p.read_text()
if "agent-self-evolution" in text:
    raise SystemExit(0)
lines = text.splitlines()
out = []
inserted = False
for i, line in enumerate(lines):
    out.append(line)
    if (not inserted) and line.strip() == "apm:":
        # detect indent of next list item or use 2 spaces under apm
        indent = "  - "
        if i + 1 < len(lines) and lines[i + 1].lstrip().startswith("-"):
            raw = lines[i + 1]
            indent = raw[: len(raw) - len(raw.lstrip())] + "- "
        out.append(f"{indent}{dep}")
        inserted = True
if not inserted:
    out.append("dependencies:")
    out.append("  apm:")
    out.append(f"    - {dep}")
p.write_text("\n".join(out) + "\n")
PY
  echo "  apm dep added"
}

vendor_skill() {
  local repo="$1"
  for dest in "$repo/.agents/skills/agent-self-evolution" "$repo/.claude/skills/agent-self-evolution"; do
    mkdir -p "$(dirname "$dest")"
    rm -rf "$dest"
    cp -R "$SKILL_SRC" "$dest"
    rm -rf "$dest/.git"
    echo "  vendored → ${dest#"$repo/"}"
  done
}

ensure_agents_matrix() {
  local repo="$1"
  local agents="$repo/AGENTS.md"
  local tmp
  tmp="$(mktemp)"
  write_matrix_block "$tmp"
  if [[ ! -f "$agents" ]]; then
    {
      echo "# $(basename "$repo") — instructions for agents"
      echo
      cat "$tmp"
      echo
      echo "## What this repository is"
      echo
      echo "_TODO: product-specific instructions._"
    } >"$agents"
    rm -f "$tmp"
    echo "  created AGENTS.md"
    return
  fi
  python3 - "$agents" "$tmp" <<'PY'
from pathlib import Path
import re
import sys

agents = Path(sys.argv[1])
block = Path(sys.argv[2]).read_text().strip()
text = agents.read_text()
begin, end = "<!-- HOLDING-MATRIX:BEGIN -->", "<!-- HOLDING-MATRIX:END -->"
pat = re.compile(re.escape(begin) + r".*?" + re.escape(end), re.S)
if pat.search(text):
    text = pat.sub(block, text)
else:
    m = re.match(r"(#[^\n]*\n\n?)", text)
    if m:
        text = m.group(1) + block + "\n\n" + text[m.end() :]
    else:
        text = block + "\n\n" + text
if not text.endswith("\n"):
    text += "\n"
agents.write_text(text)
print("  AGENTS.md matrix ok")
PY
  rm -f "$tmp"
}

ensure_claude() {
  local repo="$1"
  local c="$repo/CLAUDE.md"
  if [[ -f "$c" ]] && grep -qi 'AGENTS' "$c"; then
    echo "  CLAUDE.md references AGENTS"
    return
  fi
  if [[ ! -f "$c" ]]; then
    echo '@AGENTS.md' >"$c"
    echo "  created CLAUDE.md"
  fi
}

echo "HOLDING=$HOLDING"
[[ -d "$SKILL_SRC" ]] || { echo "missing skill src"; exit 1; }

for repo in "${REPO_LIST[@]}"; do
  if [[ ! -d "$repo" ]]; then
    echo "SKIP missing $repo"
    continue
  fi
  echo "== $repo"
  ensure_apm_dep "$repo"
  vendor_skill "$repo"
  ensure_agents_matrix "$repo"
  ensure_claude "$repo"
done

# Also install global machine skill for Claude Code
GLOBAL="${HOME}/.claude/skills/agent-self-evolution"
mkdir -p "$(dirname "$GLOBAL")"
rm -rf "$GLOBAL"
cp -R "$SKILL_SRC" "$GLOBAL"
rm -rf "$GLOBAL/.git"
echo "GLOBAL vendored → $GLOBAL"

echo "DONE reconcile"
