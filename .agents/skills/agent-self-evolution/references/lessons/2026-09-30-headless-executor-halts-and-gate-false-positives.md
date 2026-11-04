# 2026-09-30 — Headless executor halts and gate false positives during a supervised dispatch

**Category:** `executor-harness-knobs-not-read-from-source` · `gate-string-scanner-false-positives` (recurrence)

## Failure cards

1. **gen `briefing_ack_halt`.** First headless dispatch stopped on turn 1: "brief must be consumed … Set GEN_BRIEFING_GATE=1". The knob is in gen's own source (`cmd/gen/outcome.go`); the supervisor launched before reading it (`dispatch.knobs_read_from_source` = false).
2. **gen `read_file_loop` halt.** A 7-section brief made the engine's loop detector kill the run while gen was still reading the spec's files; `GEN_SKIP_LOOP_DETECTION=1` (`internal/engine/home.go`) is the documented escape for supervised runs. Cost: one lost flight; fix: one brief per step (≤ ~4 KB) + the knob.
3. **ABG marker fell through to an expired wildcard.** `abg-guard start` on `main` writes a branch-scoped marker; after `git checkout -b docs/…` the PreToolUse hook read the `*` entry (expired 2026-09-20) and denied mutations. Fix: `abg-guard register --item #N --branch '*'` (or start on the branch). Same trap inside every gen worktree (tracked `.risegen/abg-active-work.json` is stale): start the item inside the worktree before launching.
4. **evolution-guard S10 false positive on a record file.** `floor.jsonl` (a brainstorm transcript that mentions sqlite/cassandra in the seats' text) is flagged "own-ledger / direct database connection from a pipeline"; agents may not edit `evolution-surfaces.yaml` nor use the human override, so the record could not be committed. Category `gate-string-scanner-false-positives` (2026-09-23 lesson) recurs: a detection defect first.
5. **Parallel Bash calls with different cwd.** Two tool calls in one turn, one `cd`-ing to another directory, made the hook evaluate the wrong repo's marker and deny an unrelated command.

## Generalized rules

- **Read the executor's knobs from its source before the first dispatch, and encode them in the launcher** (`launch_gen.sh`: env knobs, nohup, pid file, one-step brief). A halt whose message names its own knob is a supervisor defect, not an executor defect.
- **One brief = one step.** A brief that asks an executor to read a multi-section spec and implement it all invites the loop detector; split by commit.
- **Register the ABG item where the hook will look:** inside the worktree, and for `*` when the checkout is on a feature branch.
- **A record file is not a pipeline.** Scanner rules (S10 and kin) must exempt `memory-bank/**/*.jsonl` and every brainstorm record by construction; until the exemption lands (founder-owned file), keep the record out of the tree and name the block in `activeContext.md` — never override, never rename to dodge the pattern.
- **Never parallelise Bash calls that change cwd.** Hooks read the shared shell state.

## Detection

- `launch_gen.sh` asserts both knobs are set and the brief is < 6 KB; `abg-guard status` is run inside the worktree before launch and must print `valid: true`.
- Fixture for the scanner: a `floor.jsonl` sample containing `cassandra.cluster.Cluster(` inside a quoted seat body must NOT be an S10 hit (evolution-guard test, follow-up).

## Action plan

- [ ] evolution-guard: fixture + rule scope for record files (gen dispatch, holding-central-ai-assets) — founder to add `memory-bank/**/*.jsonl` to `scan.exempt_globs` meanwhile.
- [x] Session launcher pattern recorded (memory `gen-headless-dispatch-knobs`).
- [ ] `gen-prodops-enhancement/references/dispatch.md` §3: add the two knobs and the one-step-brief rule (docs dispatch).
