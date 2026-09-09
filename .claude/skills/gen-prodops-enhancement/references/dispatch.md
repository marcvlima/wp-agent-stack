# The dispatch — how gen is actually driven, and where its record is

This is the one page the supervisor needs to get a cycle right on the first attempt. Everything
here is measured on the holding's own hosts; where a path is host-dependent it is named as such.

## 1. Provision the worktree

```bash
REPO=/home/…/risegen-lucensmind
WT=$REPO/worktrees/gpe-<cycle-id>
git -C "$REPO" worktree add -b gpe/<cycle-id> "$WT" origin/main
```

- The worktree is **gen's**, not yours. After this command you do not write in it and you do not
  run `git` inside it: a polling reader creates `index.lock` and steals it from the subject.
- Residue at provision time is a named fact (`provision.clean: false`), not something to clean up
  silently.

## 2. Brief and dispatch

gen runs non-interactively with `-p` / `--prompt` (`isInteractiveLaunch` is false as soon as a
prompt flag is present). The brief carries the founder's request **verbatim**, the worktree, the
repositories the task names, and what gen must not touch. It never carries the acceptance.

```bash
cd "$WT" && gen -p "$(cat brief.md)"
```

Run it detached and keep the pid: you must be able to end it the moment a halt is named
(`kill` the process group — a halt means the work is over, not that a flag was set).

## 3. Where gen's own record lives

The engine writes one JSONL per session under its home:

```
$ENGINE_HOME/projects/<mangled-workspace>/chats/*.jsonl     # per workspace — the real record
$ENGINE_HOME/../outbox/*.jsonl                              # fallback, keyed by session uuid only
```

`ENGINE_HOME` on a session host is `~/.risegen/engine-home` (`config.EngineHomeDir()`). The
workspace is mangled by replacing **every** `/` **and** `.` with `-`:
`/home/x/repo/worktrees/gpe-1` → `-home-x-repo-worktrees-gpe-1`. Getting that wrong is not
theoretical: the rite's first cut replaced only `/`, and a subject that asked a human sat unhalted.

The **fallback** answers only "the newest session on this host" — so when you read it, say so
(`supervise.source: outbox`). A record you could not read is **not** a halt: it is
`supervise.record_read: false`, and the dispatch goes on.

## 4. What to read on each tick (default 15 s)

| Read | Halt |
|---|---|
| a pending tool call that asks a human | `gen_asked_user` |
| the record's record-count and newest timestamp frozen for ≥ 5 min while the process lives | `gen_stalled` |
| the same block repeated on the screen over an unchanged tree | `gen_loop_detected` |
| repeated "I have finished" with no change in the worktree | `gen_repeats_completion` |
| a write into the audit/monitoring surface | `audit_tampering_detected` |

Record each read with `gpe_mode.py fact supervise.record_read true`, and the halt (or `none`) with
`gpe_mode.py halt …`.

## 5. Judge

Run the acceptance **you** declared, from **your** shell, and read the diff:

```bash
gpe_mode.py --repo "$REPO" fact judge.acceptance_ran true
<the acceptance command>            # its output is the evidence
gpe_mode.py --repo "$REPO" fact judge.acceptance_result '"fulfilled"'   # or "not_fulfilled"
git -C "$REPO" diff --stat origin/main..gpe/<cycle-id>                  # from the REPO, not the worktree
gpe_mode.py --repo "$REPO" fact judge.diff_read true
```

## 6. Tear the worktree down

Only after the diff was read and whatever gen produced was preserved (branch pushed or patch kept):

```bash
git -C "$REPO" worktree remove "$WT"
```

A worktree left behind is the residue that parks the next cycle.
