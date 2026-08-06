---
name: quality-enforcement
description: >
  Deterministic quality gates for agent-driven development — paired tests,
  quality-guard run evidence before git commit, block --no-verify. Skills teach;
  hooks enforce. Use when implementing features/fixes, before commit, when
  installing the holding quality harness, or after a regression escape.
---

# Quality Enforcement

**Mandate:** no production change ships without **paired tests** and a **green**
`quality-guard run` marker. Prompt compliance is not enough — hooks and git
backstops deny `git commit` when the gate fails.

Canonical plan: `docs/plans/2026-08-05-quality-enforcement-harness.md`  
Binary: `quality-guard` (this repo `quality-guard/`)  
Prior art: ABG `abg-guard` (skill teaches, hooks enforce).

## Progressive disclosure

| Load when | File |
|---|---|
| Always (matrix) | Holding always-on one-liner (tests + quality-guard) |
| This skill | You are here |
| Repo map | `quality-surfaces.yaml` at repo root |
| Install / fleet | `scripts/reconcile-quality-enforcement.sh` |

## Agent procedure (every production change) — NON-OPTIONAL

**FORBIDDEN:** asking the founder “should I write/run tests?”, “want me to commit tests?”, or treating the gate as optional. That is a process failure (category `policy-as-optional-prompt`). **Execute** the steps; do not offer them.

### 0. Binary present (before any other work) — NON-OPTIONAL

If hooks print `quality-guard: command not found`, `quality-guard UNAVAILABLE`, or
bootstrap fails: **install immediately**. Do not continue editing. Do not ask the founder.

```bash
export PATH="${HOME}/.local/bin:${PATH}"
# Prefer in-repo bootstrap (auto-builds from local clone or gh):
sh "$(git rev-parse --show-toplevel)/.risegen/quality-bootstrap.sh" version
# If bootstrap missing, build + wire:
#   cd ~/Developer/holding-central-ai-assets/quality-guard
#   go build -trimpath -o ~/.local/bin/quality-guard ./cmd/quality-guard
#   quality-guard install --repo "$(git rev-parse --show-toplevel)"
quality-guard version   # must print quality-guard 1.2+
```

Hooks (v1.2+): **never** leave bare `command not found`. They PATH-fix, run
`.risegen/quality-bootstrap.sh` (auto-install), then **fail-closed** with this
recipe on PreToolUse/Stop if the binary is still missing.

1. **Edit production code** and **edit/add tests** in the same surface (see map) — same change set.
2. **Run:** `quality-guard run` (must exit 0; writes `.risegen/quality-gate.json`).
3. **Status:** `quality-guard status` → `valid: YES`.
4. **Commit** without `--no-verify` / `-n` (always forbidden for agents).
5. If commit or **Stop** is denied: follow the recipe in the deny message — do not invent workarounds; do not ask the founder for permission to obey policy.

Hooks (v1.1+): **Stop** blocks ending a turn when production is dirty without a green marker (bounded 2×).

## Surface map

`quality-surfaces.yaml` maps globs → `gate_cmd` (+ optional `system_cmd` for
`blast: critical`). Template: `quality-enforcement/templates/quality-surfaces.yaml`.

- **Never** edit the surface map or hook configs as an agent unless the founder
  asked — quality-guard denies those paths.
- **Human override only:** `QUALITY_GUARD_OVERRIDE=<reason>` env, or founder-approved
  commit trailer policy when configured.

## Install (single repo) / fleet

```bash
# build binary (or let quality-bootstrap.sh do it)
cd /path/to/holding-central-ai-assets/quality-guard
go build -trimpath -o ~/.local/bin/quality-guard ./cmd/quality-guard

# wire repo (hooks + bootstrap + surfaces template + pre-commit)
quality-guard install --repo /path/to/product-repo
# edit quality-surfaces.yaml for the product (install will not overwrite existing)

# fleet:
# ./scripts/reconcile-quality-enforcement.sh --fleet
```

## Complements

| Skill | Role |
|---|---|
| `development-flow` | After green gate: rebuild/redeploy before user retest |
| `agent-self-evolution` | Record escapes that slipped the gate |
| `research-before-asserting` | Diagnosis before claiming root cause |
| `agentic-backlog` | ABG evidence_meta should include gate_cmd/exit when closing tasks |

## What this is not

- Not a substitute for human review of design.
- Not “run the full monorepo suite on every keystroke” — gate is at **commit/CI**.
- Not infallible zero bugs — **fail-closed for the defined policy** + metrics.
