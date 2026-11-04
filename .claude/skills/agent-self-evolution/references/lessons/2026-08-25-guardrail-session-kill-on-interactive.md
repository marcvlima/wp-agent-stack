# Guardrail session-kill on an interactive surface

## Category: `guardrail-session-kill-on-interactive`

## Failure card

SYMPTOM: Founder sent two phrases in the interactive coding product; the
assistant aborted as ngram degeneration and told them to start a new session.
CLAIMED: C236 (scope greeting-ngram paint to autonomous) was enough.
TRUE: The ngram detector counted global token frequency (`func`, Portuguese
`o `), so ordinary coding/prose aborted the turn; `degeneration_loop` then
session-killed interactive at abortCount=1 / painted halt. The founder
asked for a robust coding assistant, not a narrower latch.
COST: Trust; a coding session died on the second phrase.

## Root process failure (not just technical bug)

Fail-closed session-kill, designed for unattended loops that retry hundreds
of times, was left armed on the interactive user surface. A turn-scoped
quality abort was treated as “this session cannot continue.” The first
correction (C236) answered the log line, not the product requirement.

## Rule (MUST / NEVER — generalized, category-level)

MUST keep fail-closed session-kill for unattended/autonomous loops only.
NEVER promote a turn-scoped quality abort (repetition, ngram, empty decode)
into “start a new session” on an interactive user surface. A live user
message always proceeds; the abort, if any, stops that stream only.

## Detection (how the next agent notices the category)

- User-facing copy names a new session after one or two ordinary turns.
- A quality detector uses global token frequency on source/prose.
- Interactive and autonomous share the same deny latch.
- Founder says the assistant is “too sensitive” / not robust.

## Related skills

- `mandatory-soft-skills-for-agents` (definitive product fix, not a latch tweak)
- `development-flow` (redeploy the install path after the correction)
- `agent-self-evolution`

## Evidence pointers (no secrets)

- Founder 2026-08-25: two phrases → degeneration; then “não seja sensível assim”.
- Live proxy: `ngram_loop` partial_runes≈290 then `degeneration_loop` aborts=1 painted=true.
- C237: consecutive ngram + interactive never `DenyNextModelCall`.
