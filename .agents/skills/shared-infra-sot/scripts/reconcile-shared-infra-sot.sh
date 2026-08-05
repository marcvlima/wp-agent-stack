#!/usr/bin/env bash
# Vendor shared-infra-sot + ensure AGENTS.md SoT block in every holding repo.
set -euo pipefail

HOLDING="$(cd "$(dirname "$0")/../.." && pwd)"
SKILL_SRC="$HOLDING/shared-infra-sot"
MARKER_BEGIN="<!-- HOLDING-SHARED-INFRA-SOT:BEGIN -->"
MARKER_END="<!-- HOLDING-SHARED-INFRA-SOT:END -->"
DEP="marcvlima/holding-central-ai-assets/shared-infra-sot"
DRY_RUN="${DRY_RUN:-0}"

DEFAULT_REPOS=(
  "$HOLDING"
  "/Users/marcusviniciusdelima/risegen/holding-shared-infra"
  "/Users/marcusviniciusdelima/risegen/risegen-inference-connector"
  "/Users/marcusviniciusdelima/risegen/risegen-hub"
  "/Users/marcusviniciusdelima/risegen/risegen-ai-platform"
  "/Users/marcusviniciusdelima/risegen/risegen-code"
  "/Users/marcusviniciusdelima/risegen/risegen-agentic-backlog-gate"
  "/Users/marcusviniciusdelima/risegen/risegen-dex"
  "/Users/marcusviniciusdelima/risegen/risegen-shared"
  "/Users/marcusviniciusdelima/risegen/risegen-tools"
  "/Users/marcusviniciusdelima/risegen/risegen-lucensmind"
  "/Users/marcusviniciusdelima/risegen/risegen-model-runtime"
  "/Users/marcusviniciusdelima/risegen/risegen-designsystem"
  "/Users/marcusviniciusdelima/risegen/risegen-brandsystem"
  "/Users/marcusviniciusdelima/risegen/risegen-spatium"
  "/Users/marcusviniciusdelima/risegen/risegen-opencode-engine"
  "/Users/marcusviniciusdelima/risegen/designsystem-master"
  "/Users/marcusviniciusdelima/risegen/hub"
  "/Users/marcus/Developer/risegen/risegen-hub"
  "/Users/marcus/Developer/risegen/risegen-ai-platform"
  "/Users/marcus/Developer/risegen/risegen-code"
  "/Users/marcus/Developer/risegen/risegen-inference-connector"
  "/Users/marcus/Developer/risegen/risegen-agentic-backlog-gate"
  "/Users/marcus/Developer/risegen/risegen-dex"
  "/Users/marcus/Developer/risegen/risegen-shared"
  "/Users/marcus/Developer/risegen/risegen-tools"
  "/Users/marcus/Developer/risegen/risegen-lucensmind"
  "/Users/marcus/Developer/risegen/risegen-model-runtime"
  "/Users/marcus/Developer/risegen/risegen-designsystem"
  "/Users/marcus/Developer/risegen/risegen-brandsystem"
  "/Users/marcus/Developer/risegen/risegen-spatium"
  "/Users/marcus/Developer/risegen/risegen-opencode-engine"
  "/Users/marcus/Developer/risegen/designsystem-master"
  "/Users/marcus/Developer/risegen/hub"
  "/tmp/holding-secrets-work/holding-general-secrets"
)

if [[ -n "${REPOS:-}" ]]; then
  # shellcheck disable=SC2206
  REPO_LIST=($REPOS)
else
  REPO_LIST=("${DEFAULT_REPOS[@]}")
fi

# Discover git repos under RISEGEN_ROOT (one level of children)
if [[ -n "${RISEGEN_ROOT:-}" && -d "${RISEGEN_ROOT}" ]]; then
  for g in "$RISEGEN_ROOT"/*/.git; do
    [[ -d "$g" ]] || continue
    REPO_LIST+=("$(dirname "$g")")
  done
fi

# Dedupe existing paths (bash 3.2 compatible — no associative arrays)
UNIQUE=()
_tmp_list="$(mktemp)"
for r in "${REPO_LIST[@]}"; do
  [[ -d "$r" ]] || continue
  [[ -d "$r/.git" || -f "$r/AGENTS.md" || -f "$r/apm.yml" ]] || continue
  (cd "$r" && pwd) >>"$_tmp_list"
done
while IFS= read -r key; do
  [[ -n "$key" ]] || continue
  UNIQUE+=("$key")
done < <(sort -u "$_tmp_list")
rm -f "$_tmp_list"

write_sot_block() {
  local out="$1"
  cat >"$out" <<EOF
$MARKER_BEGIN
## Shared infrastructure SoT (NON-NEGOTIABLE)

**Skill:** \`shared-infra-sot\` (\`@holding-central-ai-assets/shared-infra-sot\`).
**Knowledge repo:** \`lakenbeach/holding-shared-infra\` — open \`docs/INDEX.md\` first.
- Never invent residential/edge/CPE topology from chat memory.
- Durable infra truth changed this block → promote to that repo (runbook/inventory/ADR/evidence) before claiming done.
- Runtime CLI/inventory: **that repo** — not \`holding-central-ai-assets/dev-host\` (deprecated SoT).
- Secrets: general → \`holding-general-secrets\`; edge-scoped → shared-infra SOPS; never paste values.
- cloudflared for home-managed hostnames: **forbidden**.

**Depth:** skill package + SoT \`docs/INDEX.md\` (progressive disclosure).
$MARKER_END
EOF
}

ensure_apm_dep() {
  local repo="$1"
  local apm="$repo/apm.yml"
  if [[ ! -f "$apm" ]]; then
    if [[ "$DRY_RUN" == "1" ]]; then
      echo "  [dry] would create apm.yml"
      return
    fi
    cat >"$apm" <<YAML
name: $(basename "$repo")
version: 1.0.0
description: APM project for $(basename "$repo")
targets:
  - claude
dependencies:
  apm:
    - marcvlima/holding-central-ai-assets/agent-self-evolution
    - $DEP
includes: auto
scripts: {}
YAML
    echo "  created apm.yml"
    return
  fi
  if grep -qF "shared-infra-sot" "$apm" 2>/dev/null; then
    echo "  apm dep present"
    return
  fi
  if [[ "$DRY_RUN" == "1" ]]; then
    echo "  [dry] would add apm dep"
    return
  fi
  python3 - "$apm" "$DEP" <<'PY'
from pathlib import Path
import sys
p = Path(sys.argv[1])
dep = sys.argv[2]
text = p.read_text()
if "shared-infra-sot" in text:
    raise SystemExit(0)
lines = text.splitlines()
out = []
inserted = False
for i, line in enumerate(lines):
    out.append(line)
    if (not inserted) and line.strip() == "apm:":
        indent = "    - "
        if i + 1 < len(lines) and lines[i + 1].lstrip().startswith("-"):
            raw = lines[i + 1]
            indent = raw[: len(raw) - len(raw.lstrip())] + "- "
        out.append(f"{indent}{dep}")
        inserted = True
if not inserted:
    if "dependencies:" not in text:
        out.append("dependencies:")
        out.append("  apm:")
        out.append(f"    - {dep}")
    else:
        out.append(f"    - {dep}")
p.write_text("\n".join(out) + "\n")
PY
  echo "  apm dep added"
}

vendor_skill() {
  local repo="$1"
  local dest_agents="$repo/.agents/skills/shared-infra-sot"
  local dest_claude="$repo/.claude/skills/shared-infra-sot"
  if [[ "$DRY_RUN" == "1" ]]; then
    echo "  [dry] would vendor skill → .agents + .claude"
    return
  fi
  mkdir -p "$(dirname "$dest_agents")" "$(dirname "$dest_claude")"
  rm -rf "$dest_agents" "$dest_claude"
  cp -R "$SKILL_SRC" "$dest_agents"
  cp -R "$SKILL_SRC" "$dest_claude"
  # do not copy .git if any
  rm -rf "$dest_agents/.git" "$dest_claude/.git" 2>/dev/null || true
  echo "  vendored skill"
}

ensure_agents_block() {
  local repo="$1"
  local agents="$repo/AGENTS.md"
  local tmp
  tmp="$(mktemp)"
  write_sot_block "$tmp"
  if [[ "$DRY_RUN" == "1" ]]; then
    echo "  [dry] would upsert AGENTS.md SoT block"
    rm -f "$tmp"
    return
  fi
  if [[ ! -f "$agents" ]]; then
    {
      echo "# $(basename "$repo") — Instructions for Agents"
      echo
      cat "$tmp"
      echo
    } >"$agents"
    echo "  created AGENTS.md with SoT block"
    rm -f "$tmp"
    return
  fi
  if grep -qF "$MARKER_BEGIN" "$agents" 2>/dev/null; then
    python3 - "$agents" "$tmp" "$MARKER_BEGIN" "$MARKER_END" <<'PY'
from pathlib import Path
import sys
agents, block, b, e = Path(sys.argv[1]), Path(sys.argv[2]).read_text(), sys.argv[3], sys.argv[4]
text = agents.read_text()
start = text.find(b)
end = text.find(e)
if start == -1 or end == -1:
    raise SystemExit("markers incomplete")
end += len(e)
# keep trailing newline after end marker content
rest = text[end:]
if rest.startswith("\n"):
    pass
new = text[:start] + block.rstrip() + "\n" + rest.lstrip("\n")
if not new.endswith("\n"):
    new += "\n"
agents.write_text(new)
PY
    echo "  refreshed SoT block"
  else
    # prepend after first heading if present
    python3 - "$agents" "$tmp" <<'PY'
from pathlib import Path
import sys
agents = Path(sys.argv[1])
block = Path(sys.argv[2]).read_text().rstrip() + "\n\n"
text = agents.read_text()
lines = text.splitlines(keepends=True)
if lines and lines[0].startswith("#"):
    # insert after first line + following blanks
    i = 1
    while i < len(lines) and lines[i].strip() == "":
        i += 1
    new = "".join(lines[:i]) + "\n" + block + "".join(lines[i:])
else:
    new = block + text
if not new.endswith("\n"):
    new += "\n"
agents.write_text(new)
PY
    echo "  inserted SoT block"
  fi
  rm -f "$tmp"
}

echo "shared-infra-sot reconcile  skill_src=$SKILL_SRC  dry_run=$DRY_RUN"
echo "targets: ${#UNIQUE[@]}"
if [[ ! -d "$SKILL_SRC" ]]; then
  echo "ERROR: skill source missing: $SKILL_SRC" >&2
  exit 1
fi

for repo in "${UNIQUE[@]}"; do
  echo "== $repo =="
  ensure_apm_dep "$repo"
  vendor_skill "$repo"
  ensure_agents_block "$repo"
done

echo "done."
