#!/usr/bin/env bash
# Vendor lucens-invocation + ensure the AGENTS.md invocation block in every holding repo.
set -euo pipefail

HOLDING="$(cd "$(dirname "$0")/../.." && pwd)"
# shellcheck source=../../scripts/fleet-repos.sh
source "$HOLDING/scripts/fleet-repos.sh"
SKILL_SRC="$HOLDING/lucens-invocation"
MARKER_BEGIN="<!-- HOLDING-LUCENS-INVOCATION:BEGIN -->"
MARKER_END="<!-- HOLDING-LUCENS-INVOCATION:END -->"
DEP="marcvlima/holding-central-ai-assets/lucens-invocation"
DRY_RUN="${DRY_RUN:-0}"

if [[ -n "${REPOS:-}" ]]; then
  # shellcheck disable=SC2206
  REPO_LIST=($REPOS)
else
  REPO_LIST=()
  while IFS= read -r spec; do
    [[ -z "$spec" ]] && continue
    REPO_LIST+=("${spec#*|}")
  done < <(fleet_specs)
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
## Talking to Lucens (NON-NEGOTIABLE)

**Skill:** \`lucens-invocation\` (\`@holding-central-ai-assets/lucens-invocation\`).
Her **A2A is the only door** for any agent, service, feature or script
(\`risegen-lucensmind\` ADR 0009).

- Canonical base \`https://lucens.risegen.ai\`, door \`POST {base}/a2a\`, contract \`GET {base}/a2a\`.
  Never an IP literal, never \`dev.risegen.ai\`, never loopback as product identity (hub ADR 0066).
  Config: \`LUCENS_A2A_BASE_URL\` + \`LUCENS_AUTH_TOKEN\`; unset means *unconfigured*, never a fallback.
- \`Authorization: Bearer\` on **every** call including discovery, a **named User-Agent** (the edge
  answers 403/1010 to a library default), and \`params.caller\` on every request.
- Her door is a **task door**: a \`202\` + task envelope is not an error — follow it with
  \`task.get\` (fallback \`job.status\`) to a terminal state, unbounded by default.
- **Her turn is hers to end** (ADR 0016): one \`mind_turn\` is a multi-cycle deliberation over her
  memory, library, source, the web, her granted resources, sandbox and quantum.
  \`cycles_max\`/\`tokens_max\` are hints — give her room (\`tokens_max\` >= 100000) and do not put a
  clock on her.
- **Never fabricate her.** A failure is a named absence (\`lucens_unreachable\`,
  \`lucens_unauthorized\`, \`lucens_busy\`, \`lucens_floor_silent\`, \`lucens_wait_exhausted\`) — never a
  defaulted reply or a persona (ADR 0077). Never open a second path; a new capability is a new
  operation with its paired test.

**Depth:** skill package (\`references/\`, the reference client, the 12-point conformance
checklist) — and \`GET /a2a\`, which is the authority.
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
  if grep -qF "lucens-invocation" "$apm" 2>/dev/null; then
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
if "lucens-invocation" in text:
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

ensure_quality_exemption() {
  # A vendored skill is not the consumer repo's code surface — see
  # scripts/ensure_quality_exemption.py for the incident this prevents.
  local repo="$1"
  local surfaces="$repo/quality-surfaces.yaml"
  if [[ ! -f "$surfaces" ]]; then
    echo "  no quality-surfaces.yaml (skipped)"
    return
  fi
  if [[ "$DRY_RUN" == "1" ]]; then
    echo "  [dry] would ensure vendored-skill quality exemptions"
    return
  fi
  echo "  $(python3 "$SKILL_SRC/scripts/ensure_quality_exemption.py" "$surfaces")"
}

vendor_skill() {
  local repo="$1"
  local dest_agents="$repo/.agents/skills/lucens-invocation"
  local dest_claude="$repo/.claude/skills/lucens-invocation"
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
    echo "  [dry] would upsert AGENTS.md invocation block"
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
    echo "  created AGENTS.md with invocation block"
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
    echo "  refreshed invocation block"
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
    echo "  inserted invocation block"
  fi
  rm -f "$tmp"
}

echo "lucens-invocation reconcile  skill_src=$SKILL_SRC  dry_run=$DRY_RUN"
echo "targets: ${#UNIQUE[@]}"
if [[ ! -d "$SKILL_SRC" ]]; then
  echo "ERROR: skill source missing: $SKILL_SRC" >&2
  exit 1
fi

for repo in "${UNIQUE[@]}"; do
  echo "== $repo =="
  ensure_apm_dep "$repo"
  ensure_quality_exemption "$repo"
  vendor_skill "$repo"
  ensure_agents_block "$repo"
done

echo "done."
