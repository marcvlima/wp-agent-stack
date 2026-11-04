# Lesson — an executor fault is never a verdict about the subject (2026-08-21)

**Category:** `environment-fault-laundered-as-measurement`

## Failure card (ledger only)

- **Symptom:** an autonomous evaluation loop scored an iteration `regressed` against the
  subject under test, with guardrail breaches, although the subject never ran.
- **Claimed:** "the oracle already passes with the defect in place" (attempt 1); "the
  interface never became ready" (attempt 3); "goal regression on task T3".
- **True:** (1) the evaluator's own shell had no compiler/test toolchain on `PATH`; the
  runner reported the spawn error with exit code 0 and every reader that looked only at the
  exit code called it green — a missing `npx` was read the same way as a red test; (2) the
  declared subject pin never reached the adapter (the orchestrator held it in state but did
  not put it on the command line), so the product opened on its default; (3) a shared model
  serve was saturated by another tenant between the preflight probe and the launch, and a
  fixed probe budget expired — reported as a generic boot failure, charged to the subject.
- **Cost:** three launch attempts, one full evaluation cycle recording a false `regressed`
  verdict, ~1 h of host time; a close whose recommendations the ledger silently rejected
  because the step schema and the emission gate disagreed on the hypothesis fields.

## Generalized rule (MUST / NEVER)

- **NEVER** read "the command could not start" as a result. A runner MUST surface spawn
  failures as an *unrunnable* state (POSIX 126/127 semantics) distinct from pass and fail,
  and every scorer MUST treat unrunnable as unknown/infrastructure, never as green and never
  as a regression.
- **MUST** verify the executor's own environment before attributing any outcome to the
  subject: toolchains on the adapter's `PATH`, declared pins actually present on the launch
  command line, dependencies reachable — and re-check time-varying resources (shared
  serves, queues) immediately before the launch, not only at session open.
- **MUST** name the state, not the symptom, when an external dependency fails:
  saturated / unreachable / credential unusable are different states with different next
  actions; a generic "never became ready" charges the wrong party.
- **NEVER** let a contract the host cannot see decide silently: when a step schema and a
  downstream gate disagree, the gate's rejection MUST surface before the close is published.

## Action plan (category-level)

1. Matrix always-on: one line — *an executor fault is never a verdict* (this lesson).
2. Harness: runners map spawn errors to 126/127 and carry a reason; preconditions/verify
   lanes read it; pre-launch resource probes with numbers; classified dependency failures.
3. Host checklists: toolchain + pin + resource preflight as first-attempt items; every
   attempt's report kept as evidence; attempts that never reached the subject are mechanism
   evidence, never laundered into the subject's score.
4. Contracts: step schemas state the same required fields the gate checks; the gate's
   rejection pauses publish.

## Detection

- An evaluation that concludes in seconds with "already passes" or "red" on a suite that
  normally takes minutes.
- A verdict against the subject with zero requests/turns attributed to it.
- A probe latency at launch >3x the preflight latency; a queue depth > 0 on a shared serve.
- Emission/ledger rejections present in a session whose close reads "published".

**Evidence (redacted):** Ascent Loop iteration `loopsess-34eaf4a834b24fba` (2026-08-21),
corrections D1–D9 in risegen-code PR #284 and risegen-lucensmind PR #141.
