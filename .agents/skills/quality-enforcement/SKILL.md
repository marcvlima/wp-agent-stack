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
| Scoped gate, lint, waves, tail-remediation | `references/scoped-gate.md` |
| Repo map | `quality-surfaces.yaml` at repo root |
| Install / fleet | `scripts/reconcile-quality-enforcement.sh` |

## Agent procedure (every production change) — NON-OPTIONAL

**FORBIDDEN:** asking the founder "should I write/run tests?", "want me to commit tests?", or treating the gate as optional. That is a process failure (category `policy-as-optional-prompt`). **Execute** the steps; do not offer them.

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

Hooks (v1.2.1+): the hook **command string** may only interpolate `${HOME}` and
`${PATH}`. Hosts (Grok) scan `$NAME` before exec and skip the hook when the
name is not in the environment — a shell loop `$d` in the inline recipe made
every quality-guard hook `hook not executed`. Acquire loops live in
`quality-bootstrap.sh`, never in the command string. A skipped hook is a
harness failure, not a license to continue.

1. **Edit production code** and **edit/add tests** in the same surface (see map) — same change set.
2. **Run:** `quality-guard run` (must exit 0; writes `.risegen/quality-gate.json`).
3. **Status:** `quality-guard status` → `valid: YES`.
4. **Commit** without `--no-verify` / `-n` (always forbidden for agents).
5. If commit or **Stop** is denied: follow the recipe in the deny message — do not invent workarounds; do not ask the founder for permission to obey policy.

Hooks (v1.1+): **Stop** blocks ending a turn when production is dirty without a green marker (bounded 2×).

## Run modes (v1.3.0+)

| Mode | Command | Behaviour |
|---|---|---|
| dirty (default) | `quality-guard run` | Gate only surfaces whose `prod_globs` match the git-status dirty set. |
| full | `quality-guard run --full` | Gate every surface with `blast != none`, regardless of the dirty set. |
| since | `quality-guard run --since <ref>` | Dirty set = `git diff --name-only $(git merge-base <ref> HEAD)...HEAD` ∪ git status. Used by the CI PR job. |
| shadow | `quality-guard run --shadow` | Additionally compute the Go scope shadow (§4 of the plan); execution unchanged. |
| json | `quality-guard run --json` | Print the marker to stdout after writing it. |

## Marker fields (v1.3.0+)

The `.risegen/quality-gate.json` marker carries, in addition to the legacy fields:

| Field | Meaning |
|---|---|
| `surfaces` | Per-surface results: `id`, `cmd`, `exit`, `duration_ms`, `started_at`, `executed_tests` (-1 = unknown runner), `runner` (go / pytest / vitest / jest / unknown). |
| `duration_ms` | Total wall-clock duration of the run. |
| `executed_tests_total` | Sum of known test counts; -1 if none known. |
| `content_fingerprint` | SHA-256 over `status \t path \t sha256(file bytes)` for every file in the dirty set (deleted files hash as `-`). |
| `mode` | `dirty` / `full` / `since`. |
| `since_ref` | The ref passed to `--since`, when applicable. |
| `scope_shadow` | Go reverse-dependency closure per hit surface (see `references/scoped-gate.md`). |
| `guard_version` | Binary version that produced the marker. |

**Zero-is-red (fail-closed):** a hit surface (`blast != none`) whose runner adapter returns **0** executed tests makes the run red with reason `quality-guard: surface %q executed zero tests (%s) — a gate that runs nothing is not green`. A `-1` (unknown runner) is **not** red. A hit surface whose `gate_cmd` is empty or `true` is red with reason `surface %q has no gate command`.

## `validate --lint` (v1.3.0+)

`quality-guard validate --lint` (and the CI job) adds these checks, exit 1 on any **deny**:

| ID | Condition | Severity |
|---|---|---|
| `mask` | `gate_cmd` contains `\|\| true` or `; true` at the end of any segment | deny |
| `no-gate` | `blast != none` and `gate_cmd` empty or `true` | deny |
| `overlap` | Two surfaces with `blast != none`, different `gate_cmd`, whose `prod_globs` overlap (identical glob string, or catch-all in one and same-extension glob in the other) | deny |
| `zero-files` | A surface with `blast != none` whose `prod_globs` match no file in the tree | deny in `validate --lint`; warn in `run` |
| `template-residue` | A surface `id` in {go, python, typescript} with the template command and zero files | deny in `validate --lint`; warn in `run` |
| `blast-ratio` | Files matched by `prod_globs` vs. test files under the command's directory | report only |

`run` calls the lint in warn mode for every surface it hits and denies only `mask`, `no-gate`, and `overlap` on **hit** surfaces (a repo is never bricked by an unhit template surface; CI's `validate --lint` is where the full deny lands).

## Wave order

0. **Measure + marker + CI + red repairs** — proof-carrying marker fields, content-bound fingerprint, deterministic execution order, executed-test count with zero-is-red, `run --full/--since/--json`, managed CI workflow.
1. **Wait remediation + lint** — surface hygiene lint (`validate --lint`), tail-remediation dispatch rule.
2. **Go scope shadow → default under ratio < 0.4** — reverse-dependency closure recorded in `scope_shadow`; widen-on-doubt is non-negotiable; shadow only in this release (never changes what runs).
3. **Modularity ratchet advisory → deny** — future.
4. **Decomposition** — future.

## Tail-remediation dispatch rule (v1.3.0+)

Before dispatching a remediation for a slow test: grep every reader of the knob; use a per-test override, never module- or env-wide; the supervisor holds acceptance on the diff — identical sorted pass-id list captured twice, executed count equal, three timed runs with load recorded, mutation check that the rewritten test goes red under a mutated constant, production default unchanged, allowlist checked with `git diff --stat`.

## Founder-ratification items

No commit-path exclusion, tier move, or waiver ledger without founder ratification. The following are **not** implemented and require founder ratification before any agent acts on them:

1. Failing every legacy marker once (this release keeps legacy comparison).
2. CI required-check status for `quality-gate` on main (and the `HOLDING_ASSETS_TOKEN` secret).
3. Any commit-path exclusion or tier move.
4. The human waiver ledger and the tail-budget number.
5. Optional lane split.

## Widen-on-doubt (non-negotiable)

When computing the Go scope shadow, any of these conditions widens the shadow to the full surface (`widened: true`): a non-Go changed file matching the surface (`.cql`, `testdata/`, `go:embed` candidates, `go.mod`, `go.sum`), a changed file whose package cannot be resolved, a `go list` error, or an empty selection over a non-empty change. This is non-negotiable — the shadow must never under-report.

## Measurements that show it worked

| Fact | Source |
|---|---|
| Gate wall dominated by a few waiting tests, not by count: risegen-code 296 s (top-5 tests 59.7 %), gen-prodops Go 259 s (one test 189 s = 73 %), lucensmind part 2 657 s (16 tests ≈30 s = 77.7 %) | Record seq 177–180, 223, 285 |
| Static selection would not shorten those walls today: projected scoped/full wall ratio 0.999 (rgai), 0.997 (gen-prodops Go), 0.976 (lucensmind V2); 0.128 only for ai-platform api | Record seq 284 |
| Content hashing of the dirty set costs milliseconds | Record seq 175 §4 |
| Lint-worthy surface defects exist fleet-wide: template surfaces with zero files, `\|\| true` masks, overlapping globs with different commands, 12 surfaces > 500 test functions per changed file | Record seq 175 §3 |

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

# wire repo (hooks + bootstrap + surfaces template + pre-commit + managed CI workflow)
quality-guard install --repo /path/to/product-repo
# edit quality-surfaces.yaml for the product (install will not overwrite existing)

# fleet (local mode — installs into each tree without switching branches):
# ./scripts/reconcile-quality-enforcement.sh --fleet

# fleet with push (throwaway worktrees off origin/<default>, never touches live
# checkouts; commits, pushes branch, opens PR and merges):
# ./scripts/reconcile-quality-enforcement.sh --fleet --push

# dry-run (prints what would be staged and the commit message per repo, no writes):
# ./scripts/reconcile-quality-enforcement.sh --fleet --dry-run
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
- Not "run the full monorepo suite on every keystroke" — gate is at **commit/CI**.
- Not infallible zero bugs — **fail-closed for the defined policy** + metrics.