# Scoped quality gate — reference

Depth for `quality-enforcement/SKILL.md` v1.3.0. Canonical plan:
`docs/plans/2026-09-30-scoped-quality-gate.md`. Record:
`memory-bank/2026-09-30-scoped-quality-gate/brainstorms/20260930-scoped-quality-gate/record.md`.

## Lint table (`quality-guard validate --lint`)

| ID | Condition | Severity |
|---|---|---|
| `mask` | `gate_cmd` contains `\|\| true` or `; true` at the end of any segment | deny |
| `no-gate` | `blast != none` and `gate_cmd` empty or `true` | deny |
| `overlap` | Two surfaces with `blast != none`, different `gate_cmd`, whose `prod_globs` overlap: an identical glob string, or a catch-all (`**/*.<ext>`, `**/*.{...}`) in one and any glob of the same extension in the other | deny |
| `zero-files` | A surface with `blast != none` whose `prod_globs` match no file in the tree (walk excludes `.git`, `node_modules`, `vendor`, `.venv*`, `worktrees`, `.worktrees`, `.risegen`, `.claude`, `.agents`, exemptions) | deny in `validate --lint`; warn in `run` |
| `template-residue` | A surface `id` in {go, python, typescript} with the template command and zero files | deny in `validate --lint`; warn in `run` |
| `blast-ratio` | Files matched by `prod_globs` and the test files under the directory the command names; printed, never a deny | report |

`run` calls the lint in warn mode for every surface it hits and denies only `mask`, `no-gate`, and `overlap` on **hit** surfaces.

## Marker JSON schema (v1.3.0+)

```jsonc
{
  // --- legacy fields (unchanged) ---
  "valid": true,
  "prod_fingerprint": "sha256:...",
  "dirty_files": ["path/to/file.go"],
  "timestamp": "2026-09-30T12:00:00Z",

  // --- new fields (v1.3.0) ---
  "surfaces": [
    {
      "id": "go",                    // surface identifier
      "cmd": "go test ./...",        // gate command executed
      "exit": 0,                     // exit code
      "duration_ms": 1234,           // wall-clock duration in milliseconds
      "started_at": "2026-09-30T12:00:00Z",  // execution start time
      "executed_tests": 42,          // test count from runner adapter; -1 = unknown
      "runner": "go"                 // go | pytest | vitest | jest | unknown
    }
  ],
  "duration_ms": 1234,               // total wall-clock duration
  "executed_tests_total": 42,        // sum of known counts; -1 if none known
  "content_fingerprint": "sha256:...", // SHA-256 over status\tpath\tsha256(file bytes) for dirty set
  "mode": "dirty",                   // dirty | full | since
  "since_ref": "origin/main",        // only when mode=since
  "scope_shadow": [                  // only when --shadow; see below
    {
      "surface": "go",
      "module": "github.com/...",
      "changed_pkgs": ["./pkg/a"],
      "selected_pkgs": ["./pkg/a", "./pkg/b"],
      "total_test_pkgs": 15,
      "ratio": 0.133,
      "widened": false,
      "widen_reason": "",
      "graph_hash": "sha256:..."
    }
  ],
  "guard_version": "1.4.0"           // binary version
}
```

### Scope shadow fields

| Field | Meaning |
|---|---|
| `surface` | Surface ID this shadow belongs to. |
| `module` | Go module path (from `go.mod`). |
| `changed_pkgs` | Packages containing changed Go files. |
| `selected_pkgs` | Test-bearing packages in the reverse dependency closure plus changed packages. |
| `total_test_pkgs` | Total test-bearing packages in the module. |
| `ratio` | `len(selected_pkgs) / total_test_pkgs`. |
| `widened` | True when widen-on-doubt triggered (shadow equals full surface). |
| `widen_reason` | Why widen-on-doubt triggered (empty when `widened: false`). |
| `graph_hash` | SHA-256 of the dependency graph used for this computation. |

## CI workflow template (verbatim from `internal/install.go`)

```yaml
# managed-by: quality-guard install (do not hand-edit; re-run install)
name: quality-gate
on:
  pull_request:
  push:
    branches: [main, master]
  schedule:
    - cron: "17 3 * * *"
  workflow_dispatch:
concurrency:
  group: quality-gate-${{ github.ref }}
  cancel-in-progress: false
jobs:
  gate:
    runs-on: ubuntu-latest
    timeout-minutes: 120
    steps:
      - uses: actions/checkout@v4
        with: { fetch-depth: 0 }
      - uses: actions/setup-go@v5
        with: { go-version: "1.22" }
      - name: Build quality-guard (missing binary is fatal)
        run: |
          set -euo pipefail
          git clone --depth 1 https://x-access-token:${{ secrets.HOLDING_ASSETS_TOKEN }}@github.com/marcvlima/holding-central-ai-assets.git .qg-src
          (cd .qg-src/quality-guard && go build -trimpath -o "$RUNNER_TEMP/quality-guard" ./cmd/quality-guard)
          echo "$RUNNER_TEMP" >> "$GITHUB_PATH"
          quality-guard version
      - name: Validate surface map (lint)
        run: quality-guard validate --lint
      - name: Gate
        run: |
          set -euo pipefail
          if [ "${{ github.event_name }}" = "pull_request" ]; then
            quality-guard run --since "origin/${{ github.base_ref }}" --shadow
          else
            quality-guard run --full --shadow
          fi
      - name: Marker
        if: always()
        run: cat .risegen/quality-gate.json || true
```

## Wave 1 follow-up dispatches

| # | Repo | Change | Acceptance held by the supervisor |
|---|---|---|---|
| W1-a | risegen-gen-prodops | `internal/astq/astq.go` `walkGo`: skip repo-root `worktrees/` and `.worktrees/` (anchored, not any depth) + paired test | 4 named tests pass; production-caller sets identical; re-timed on the 89 k-file tree |
| W1-b | risegen-lucensmind | Per-test grace override in the fake-proc headless tests only (or explicit `grace_s` on the post-loop `verify_events_stream`); watch-loop deadline keeps its default; Term-field drift repair | Identical sorted pass-id list (baseline captured twice); 3 timed runs; mutation check; one test keeps nonzero grace |
| W1-c | risegen-code | `cmd/rgai` `sessionScript` field for the 30 s exit tail, default unchanged; C358 RED keeps its real budget | Pass set identical; mutation check; 3 timed runs |