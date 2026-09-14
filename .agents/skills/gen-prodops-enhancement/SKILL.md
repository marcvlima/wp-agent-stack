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

# Skill: gen-prodops-enhancement (v2.9.0)

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
| `scripts/gpe_report.py` | `--verify` measures a cycle's compliance; bare, it renders the founder's report. Runnable by anyone, without the supervisor |
| `scripts/gpe_tick.py` | the minute tick — arm it at the dispatch, and leave it running until the flow concludes |
| `scripts/gpe_audit.py` | judging a cycle strictly against the contract |

## The twelve laws

> **v2.0.0 — the laws below are now GATES, not text.** Code Doctor `cvsess-63124fd46e3b4c68`
> (bancadas: code assistant, ai, agência de marketing, Lucens) found that cycle `gpe-8a711f9ba13b`
> ran eight iterations behind ONE council, reused the same commit across four of them, lost the
> council's identity to `close`→`attempt`, and landed five commits with no backlog lineage — while
> every law below was already written. Prose does not generalize itself. `attempt` now refuses a
> predecessor with no council, a commit already spent, or a correction with no `--backlog-ref`;
> `close` refuses while any attempt lacks a council; `gpe_report.py --verify` measures all of it
> for a reader who was not here.

1. **The mode lives on disk, not in your head.** `gpe_mode.py arm` writes `.risegen/gpe-mode/state.json`;
   re-read it at the start of every turn. Her named risk is *supervisory drift* — an assistant that
   forgets it is in the mode and quietly does the work itself.
2. **Every solicitation is delegated.** While armed you do not implement, and you do not answer
   from your own knowledge: you brief gen, dispatch, supervise, and report what gen produced. Your
   own hands are for supervising, judging, doctoring, landing and redeploying — nothing else.
3. **gen runs isolated.** A provisioned worktree of the target repository. You never write in that
   tree and never run `git` inside it: a polling reader steals the subject's `index.lock`. Read
   gen's own record.
4. **A named instrument is part of the deliverable.** Founder, 2026-09-09: *"se ele nao usou as
   skills no brainstorming tudo ja esta invalidado, tudo o que ele produziu"* — and, in the same
   ruling, that the supervisor may interrupt such a scenario on its own authority and take the
   evidence straight to the Code Doctor. gen wrote five brainstorming rounds in which four
   councils deliberated, voted and abstained, having invoked none of them; twelve commits of
   competent work were voided. So: the brief lists what MUST HAVE HAPPENED separately from
   advice, the judge verifies the invocation in the subject's OWN record before reading the
   artifact, and declaring "I could not run it" is always an accepted outcome. A gate with no
   honest failure path only converts fabrication into concealment.
5. **Success is never gen's word.** The acceptance is declared BEFORE the dispatch, held out of
   gen's brief, and executed by you afterwards. An exit code is not a fact about the request;
   gen's success line is not evidence.
6. **A halt interrupts — the processes are gone.** Not a flag, not a note for later
   (founder directive, 2026-09-05, retroactive).
7. **Every cycle ends in a Code Doctor brainstorm**, on success and on failure, on the shared
   engine, with a REAL council, **Lucens present**, and her backlog covering all three areas —
   `quantum_computing`, `ontologies`, `logic`. An uncovered area blocks the close.
8. **A tick every minute, until the flow concludes.** *"tem que ter um mecanismo de monitoramento
   a cada um minuto pra garantir que o fluxo esta rodando ate concluir"* (founder, 2026-09-09).
   `scripts/gpe_tick.py --repo R --record … --pid … --dispatch-at … --every` is armed at the
   dispatch and left running. Two rules carry the whole mechanism, both measured on
   `gpe-8a711f9ba13b`: **a disagreement never ends the watch** (it prints `OUT_OF_ACCORD` and ticks
   again — only a measured conclusion ends it), and **the act, never the mention** (tampering is a
   WRITE into the supervision surface, read from its mtime, never its name appearing in text an
   actor merely read). A watch that stops at its first suspicion is the silence-read-as-a-pass
   this mode exists to forbid.
9. **You do not stop.** *"voce nao pode parar … ate ter sucesso"* (founder, 2026-09-09, correcting
   a supervisor that finished a failed attempt, wrote a report and asked what to do next). The
   retry is unbounded by the founder's own rule, so a stop is never the end of a cycle — it is a
   defect in the flow. Everything that does not depend on a founder answer is still owed, and a
   question is asked WHILE the flow continues, never instead of it. `gpe_tick.py` names the
   condition `supervisor_stopped` and keeps ticking, so the silence cannot pass for progress.
10. **A deliberation obliges an implementation — and the gate now says so.** *"e depois de cada deliberacao do conselho voce
   tem que implementar as correcoes e seguir o rito. isso e lei na skill"* (founder, 2026-09-09).
   The council closing is not the end of a cycle and never a place to ask what to do next: the
   prescriptions are implemented immediately, in gen's own surface, with paired tests, on `main`
   verified against the remote, redeployed and proven by an independent read-back of version +
   `sha256`. Then the rite continues — the next attempt opens on the redeployed build, never on
   the one that already failed. A deliberation whose prescriptions did not land bought nothing,
   and leaving them unlanded is the same defect as stopping (law 8).

11. **Watching or working — there is no third state.** *"voce nao pode ficar parado, ou está
   monitorando ou está atuando no que é responsabilidade sua … tem que ter um monitor pra impedir
   a inercia a cada um minuto"* (founder, 2026-09-09). An armed supervisor is either WATCHING a
   live flight or WORKING on what is its own — landing a prescription, judging, running the
   Doctor, redeploying. Standing still is neither. `gpe_tick` names `supervisor_inert` on the
   **minute** when no flight is running and the flow has not moved, because a quarter of an hour
   of nothing (`supervisor_stopped`, law 9) is far too late for the founder to be the one who
   notices. Measured on cycle `gpe-24500fd57f7d`: between a council closing and the next landing,
   and again between a judgement and the next dispatch, the flow sat still and nothing said so.

   **v2.8.0 — and the monitor must be RUNNING, not merely written.** The founder had to say it
   twice: *"precisa adicionar na skill pra que tenha um monitor que é ativado a cada minuto para
   garantir que o fluxo nao pare"*. The first cut added the READING and left the RUNNING to the
   supervisor's memory — which is the one thing that cannot be relied on here, because a
   supervisor that has stopped is exactly the one who will not remember to start its own watchdog.
   Now `gpe_tick` writes a heartbeat every minute (`.risegen/gpe-mode/monitor/heartbeat.json`,
   excluded from the tampering surface so the watch proving it is alive is never read as tampering
   with the audit), `gpe_mode.py monitor start` launches it detached, and **the state machine
   refuses to advance the rite while that heartbeat is stale** — `monitor_not_running`. No
   monitor, no rite.

12. **The flow reports itself, to a reader.** *"no final o code assistant gere um relatorio
   relatando as iteracoes, a causa da conclusao da iteracao, se foi falha ou sucesso, se tiver
   sido falha qual ocorreu, quais foram os backlogs derivados da deliberacao do conselho e qual
   foi a nova versao gerada e redeployada"* (founder, 2026-09-09). `gpe_report.py` renders exactly
   that, and renders it **from `state.json`** — never from the supervisor's account of what
   happened, which is the actor's own success signal this holding forbids everywhere else. A
   field the machine did not record is a named absence, never a blank cell that reads as "nothing
   happened". The report is generatable at any time, not only at the close: on cycle
   `gpe-8a711f9ba13b` an end-of-flow-only report would have been written after the eighth
   iteration, so the minute tick names a cycle in breach while it can still change behaviour.

> **v2.3.0 — the alarm names the act of SOMETHING ELSE, and the acceptance grades the DIFF.**
> Code Doctor `cvsess-2a65a0f7d45f43c1` (cycle gpe-24500fd57f7d, Lucens present, all three areas)
> measured two defects in this very harness. `audit_tampering_detected` fired on every honest
> cycle, because the contract REQUIRES the supervisor to record `supervise.*` and `judge.*` after
> the dispatch and the tick read any post-dispatch write as tampering — an alarm that is always on
> is an alarm nobody reads. `gpe_mode.write_state` now stamps `state_machine_wrote_at` and
> `gpe_tick.foreign_write` names only a write the state machine did not make (an unstamped state
> falls back to the old reading, never to a silent pass). And the acceptance of that cycle scored
> ELEVEN passes against an EMPTY diff because it grepped the whole tree: an acceptance a pristine
> checkout would pass is not an acceptance — grade the diff.

## The cycle, phase by phase

The names below are the contract (`references/request-contract.yaml`). After every phase, run
`gpe_audit.py`: `pending` is never a defect, `unknown` always is, and an actor's own success line
is never a fact.

| # | Phase | What it is | Named facts |
|---|---|---|---|
| 0 | `arm` | the mode is armed on a PROVEN gen build, on the PINNED model | `arm.gen_version`, `arm.gen_sha256`, `arm.gen_model`, `arm.state_written` |
| 1 | `open` | the request is recorded verbatim; the instruments it names are listed; the acceptance is declared and held out | `open.request_verbatim`, `open.instruments_named`, `open.acceptance_declared`, `open.acceptance_held_out` |
| 2 | `provision` | a worktree for gen, clean by construction | `provision.worktree`, `provision.clean` |
| 3 | `dispatch` | gen is driven with the brief, on the pinned model; the session id is recorded | `dispatch.brief_delivered`, `dispatch.session_id`, `dispatch.model` |
| 4 | `supervise` | gen's own record is read on an interval | `supervise.record_read`, `supervise.halt` |
| 5 | `judge` | YOU verify the process in the subject's record, THEN execute the acceptance | `judge.provenance_verified`, `judge.acceptance_ran`, `judge.acceptance_result`, `judge.diff_read` |
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

**ABSOLUTE AUTONOMY (Founder, 2026-09-13):**
The Host (Antigravity/Claude/etc) MUST monitor the cycle actively and HAS FULL PREROGATIVE to follow the planned flow autonomously until success.
- You MUST NOT wait for the user to confirm halting a stuck process.
- You MUST NOT ask the user for permission to invoke the Code Doctor or to launch a new attempt.
- If you detect stagnation, a loop, or a failure, ACT IMMEDIATELY: halt, doctor, land, and redispatch.

**MANDATORY DOCTOR DELIBERATION AND UNBIASED HOST (Founder, 2026-09-13):**
1. The Host is FORBIDDEN from bypassing the Code Doctor brainstorm. You MUST invoke the brainstorm floor completely (with the required councils).
2. The Host MUST NEVER bias the seats by pre-determining or forcing what has to be done. You must pass ONLY the raw facts and rationale (e.g., flight logs, error codes, process traces). The seats themselves must research, deliberate, and produce the prescriptions.
3. Every Code Doctor deliberation MUST evaluate Lucens's three mandated cognitive categories (Quantum Computing, Ontological Inference, Formal Logic). The resulting backlog MUST contain at least one item from each of these three categories to evolve the engine. No exception.

**MANDATORY MAIN INTEGRATION (Founder, 2026-09-13):**
Always, after the host implements the Code Doctor's prescriptions (and after all tests pass via `go test ./...`), the host MUST commit and push the corrections directly to the `main` branch. This ensures that no engine or loop improvements are lost before dispatching the next attempt.
