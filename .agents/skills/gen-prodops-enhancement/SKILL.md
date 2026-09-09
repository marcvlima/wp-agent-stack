---
name: gen-prodops-enhancement
description: >-
  MANDATORY harness for any foreign code assistant (Claude Code, Cursor, Antigravity, Grok)
  running with the "gen prodops enhancement mode" armed. While armed, the assistant does NOT do
  the work: it delegates EVERY solicitation to `gen` in a provisioned worktree, supervises the
  execution with mechanically-read halts, judges the result by an acceptance held out from gen,
  and then — on success AND on failure — runs a Code Doctor brainstorm on the shared
  self-evolution engine that carries Lucens's three-area backlog, lands the prescriptions in gen
  and redeploys with an independent read-back. A request that was not fulfilled is iterated until
  it is. Use when arming or disarming the mode, before dispatching any request while armed, on
  every halt, and before closing a cycle.
version: 1.0.0
---

# Skill: gen-prodops-enhancement (v1.0.0)

**Holding-wide · MANDATORY while armed · core.**
**Founder, 2026-09-08:** *"sempre que tiver usando outro code assistant, se for ativado o modo
aprimoracao do gen prodops, cada solicitacao que for feita ao assistente o mesmo vai direcionar
para ser executado pelo gen"* — and, ruled in the same session: **literally every solicitation**
goes to gen · gen executes in a **provisioned worktree of the local repository** · the
brainstorm→retry iteration has **no cap**: it iterates until the request succeeds, and any stop is
a failure of the flow to be corrected.

**Governing decisions:** hub ADR 0082 + repo ADR 0020 (every evolution/analysis flow is a declared
pipeline on the SHARED engine — this skill never grows an engine, daemon, scheduler or ledger) ·
`risegen-lucensmind` ADR 0021 (the rite's rules this mode inherits: stop on a defective fact, land
on main, redeploy before the next attempt) · ADR 0009 (her A2A is the only door) · ADR 0016 (her
turn is hers to end).

## The mode in one screen

```
  founder request ──▶ [ARMED assistant]         it does NOT implement
                          │
                          │ 1. open cycle, record the request VERBATIM
                          │ 2. declare the ACCEPTANCE (held out from gen)
                          │ 3. provision a worktree
                          ▼
                        gen  ◀── brief (request verbatim, never the acceptance)
                          │
             supervise ───┤ halts read from gen's OWN record, never from the screen
                          │   gen_asked_user · gen_stalled · gen_loop_detected
                          │   gen_repeats_completion · audit_tampering_detected
                          ▼
                        judge  ── the supervisor EXECUTES the acceptance itself
                          │
        ┌─────────────────┴──────────────────┐
   fulfilled                             not fulfilled  ─▶ interrupt gen (processes gone)
        │                                     │
        └──────────────▶ CODE DOCTOR ◀────────┘        every cycle, both outcomes
                          │  shared engine, code-doctor profile, REAL council
                          │  Lucens seat PRESENT + backlog: quantum_computing · ontologies · logic
                          ▼
                  corrections IN GEN (paired tests) ─▶ main ─▶ redeploy ─▶ read-back
                          │
                 fulfilled? ── no ──▶ new attempt (new named cause + landed correction)
                          │
                         yes ──▶ close the cycle
```

## Progressive disclosure

| Depth | Open when |
|---|---|
| This SKILL.md | the mode is armed, or you are about to arm it |
| `references/request-contract.yaml` | after EVERY phase — it is the definition each phase is judged against |
| `references/dispatch.md` | before the FIRST dispatch: the worktree, the brief, where gen's record lives, the judge |
| `references/halts.md` | a halt was read, or you are deciding whether one happened |
| `references/doctor-cycle.md` | before running the Code Doctor, and before closing it |
| `references/mode-state.md` | the on-disk state: what is written, when, and why it is not in your context |
| `scripts/gpe_mode.py` | arming, opening a cycle, recording facts, naming halts, closing |
| `scripts/gpe_audit.py` | judging a cycle strictly against the contract |

## The seven laws

1. **The mode lives on disk, not in your head.** `gpe_mode.py arm` writes `.risegen/gpe-mode/state.json`;
   re-read it at the start of every turn. Her named risk is *supervisory drift* — an assistant that
   forgets it is in the mode and quietly does the work itself.
2. **Every solicitation is delegated.** While armed you do not implement, and you do not answer
   from your own knowledge: you brief gen, dispatch, supervise, and report what gen produced. Your
   own hands are for supervising, judging, doctoring, landing and redeploying — nothing else.
3. **gen runs isolated.** A provisioned worktree of the target repository. You never write in that
   tree and never run `git` inside it: a polling reader steals the subject's `index.lock`. Read
   gen's own record.
4. **Success is never gen's word.** The acceptance is declared BEFORE the dispatch, held out of
   gen's brief, and executed by you afterwards. An exit code is not a fact about the request;
   gen's success line is not evidence.
5. **A halt interrupts — the processes are gone.** Not a flag, not a note for later
   (founder directive, 2026-09-05, retroactive).
6. **Every cycle ends in a Code Doctor brainstorm**, on success and on failure, on the shared
   engine, with a REAL council, **Lucens present**, and her backlog covering all three areas —
   `quantum_computing`, `ontologies`, `logic`. An uncovered area blocks the close.
7. **The prescriptions land in gen and are redeployed.** Inside gen's own surface, with paired
   tests, on `main` verified against the remote, redeployed and proven by an independent read-back
   of version + `sha256`. The next attempt opens only on the redeployed build.

## The cycle, phase by phase

The names below are the contract (`references/request-contract.yaml`). After every phase, run
`gpe_audit.py`: `pending` is never a defect, `unknown` always is, and an actor's own success line
is never a fact.

| # | Phase | What it is | Named facts |
|---|---|---|---|
| 0 | `arm` | the mode is armed on a PROVEN gen build | `arm.gen_version`, `arm.gen_sha256`, `arm.state_written` |
| 1 | `open` | the request is recorded verbatim; the acceptance is declared and held out | `open.request_verbatim`, `open.acceptance_declared`, `open.acceptance_held_out` |
| 2 | `provision` | a worktree for gen, clean by construction | `provision.worktree`, `provision.clean` |
| 3 | `dispatch` | gen is driven with the brief; the session id is recorded | `dispatch.brief_delivered`, `dispatch.session_id` |
| 4 | `supervise` | gen's own record is read on an interval | `supervise.record_read`, `supervise.halt` |
| 5 | `judge` | YOU execute the acceptance | `judge.acceptance_ran`, `judge.acceptance_result`, `judge.diff_read` |
| 6 | `doctor` | the Code Doctor brainstorm over the session | `doctor.council_real`, `doctor.lucens_present`, `doctor.lucens_backlog_three_areas`, `doctor.targets_gen` |
| 7 | `correct` | the prescriptions implemented in gen with paired tests | `correct.implemented`, `correct.tests_paired`, `correct.blocked_named` |
| 8 | `land` | on `main`, verified against the remote | `land.on_main`, `land.remote_verified` |
| 9 | `redeploy` | the new gen proven by an independent read-back | `redeploy.version`, `redeploy.sha256`, `redeploy.readback_independent` |
| 10 | `close` | fulfilled, or a new attempt with a NEW cause | `close.outcome`, `close.new_cause`, `close.correction_landed` |

## Retry: unbounded, never vacuous

The founder set no cap: the mode iterates until the request is fulfilled, and a stop is a failure
of the flow. The honest bound is **novelty**, not a clock and not a counter:

- every new attempt names a **cause** that was not named before, and carries a **correction that
  landed** since the previous attempt;
- an attempt whose cause repeats with no new landed correction is the named defect
  `no_new_correction` — the flow stops **there**, the missing correction is found, landed and
  redeployed, and the attempt reopens. It is never a reason to abandon the request;
- `gen_asked_user` is answered by improving gen (the brief, the tools, the resolution), not by a
  human standing in for the flow — unless the question is genuinely a founder decision, which is
  surfaced to the founder and named on the cycle.

## What this skill must never become

- a second engine, daemon, scheduler or ledger for evolution analysis (hub ADR 0082) — the doctor
  runs on the shared engine's `code-doctor` profile;
- a second door to Lucens: she is asked through `POST {base}/a2a` and nothing else (ADR 0009), and
  no agent authors text into her mind (ADR 0077);
- a reason to skip a gate: quality-guard and plan-guard apply to every landed correction, and
  `--no-verify` stays forbidden;
- a `--force` push. `main` moves fast-forward or the landing is a defect.
