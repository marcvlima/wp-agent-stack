# Yield after a phase has already returned

## Category: yield-after-phase-complete

## Failure card

SYMPTOM: standing delivery paused at the next host phase; the agent answered the human instead of continuing.
CLAIMED: "the implementation step of this iteration concluded" — treated as a stopping point.
TRUE: implement had returned (or hit its no-progress/budget limit). The locked iteration's next phase is evaluation (doctor), then corrections. Stopping to narrate is a stall.
COST: founder had to re-issue "if it already finished, why didn't you continue?"; hours of loop time idle.

## Root process failure (not just technical bug)

The 3-hour stale-cycle Stop guard only fires when `last_cycle` is old. A host can finish implement, update nothing, and Stop within minutes. The no-wait contract covered *running* waits, not *finished phases*.

## Rule (MUST / NEVER — generalized, category-level)

MUST start the next phase in the same breath when the current phase of a standing delivery has returned or hit its limit.
NEVER end a turn to report that a phase finished.

## Detection (how the next agent notices the category)

- Delivery paused on a host-conduct step (`evolve`, `corrections`, equivalent) and the agent is composing a status report instead of driving that step.
- Stop hook sees `host-phase.json` with `paused_on` in {evolve, corrections}.

## Related skills

- `ascent-loop-host` (no-wait; C219 host-phase)
- `mandatory-soft-skills-for-agents`

## Evidence pointers (no secrets)

- Founder 2026-08-24: continue after implement finished or hit its limit; do not stay stopped.
- Thread paused at evolve after implement `no_effect` / no-progress cut.
