# A session-kill gate is not a fixed user stream

## Category: `lifecycle-gate-as-surface-fix`

## Failure card

SYMPTOM: Founder quoted a live interactive answer overwritten by
"the model entered a token loop — send the message again", plus a queued
generation that never left the chip. They said corrections were not being made.

CLAIMED: C237 "fixed" interactive degeneration (session no longer killed).

TRUE: C237 only stopped `degeneration_loop` session-kill. The proxy still
aborted the SSE, appended the abort note over Portuguese Q&A prose, used
`finish_reason=quality_failed` (the engine does not treat as stop), then
stall-recovered a second completion on the same connection — QUEUED chrome.

COST: Repeated founder retests of a still-broken TUI; trust that harness
corrections never reach the product surface.

## Root process failure (not just technical bug)

The process treated a **related lifecycle gate** (session stays open) as the
**user-visible stream fix**. The bytes on the wire still painted the abort
note and a second generation.

## Rule (MUST / NEVER — generalized, category-level)

MUST change the bytes the user surface renders — and the finish class the
client uses to dequeue — when the defect is painted abort or queue chrome.

NEVER report a user-stream defect fixed because a related session-kill,
retry, or latch gate changed.

## Detection (how the next agent notices the category)

- User quotes an abort/queue note that still exists in product copy after a
  "session stays open" correction.
- Proxy log shows stream abort then stall recovery on the same turn.
- Tests cover session-deny helpers but not the streamed abort note.

## Related skills

- `agent-self-evolution`
- `development-flow`
- `channel-ui-parity`
- `research-before-asserting`

## Evidence pointers (no secrets)

- Live proxy: `stream abort reason=ngram_loop` then `stall_streamed_recovering`
- Product note constant still concatenated onto a real answer prefix
- Test that streams the live prefix and forbids the abort note
