# Driver send log is not product receipt

## Category: `driver-record-is-not-receipt`

## Failure card

SYMPTOM: Founder asked why Code had not received a simple question. Several
driven sessions sat on an empty composer (`Ask anything`) for minutes, then
`/exit`, while the harness reported a pasted briefing.

CLAIMED: The driver had "pasted" the prompt (`recordedInput` = `[Pasted ~N lines]`).

TRUE: That label is written by the driver itself. The product screen never
showed the chip; the model was never called (`time_to_first_tool_call_ms=0`).
Extra Enter after bracketed paste is a race, not delivery.

COST: Multiple loop iterations measured a subject that never saw the question.
Founder trust: a simple objective looked like subject failure.

## Root process failure (not just technical bug)

The process treated **its own write** as **the product's read**. Detection of
"undelivered" (halt and doctor) is not the same as **ensuring** delivery.

## Rule (MUST / NEVER — generalized, category-level)

MUST prove the product surface accepted each driven prompt or interaction
before counting that turn as delivered.

NEVER treat the driver's send log, a synthetic paste chip, or a source-level
CR count as receipt.

## Detection (how the next agent notices the category)

- Turn input is a driver-forged chip while the live capture has no matching
  product chrome (no paste chip, no driven text).
- First-token / first-tool counters stay zero after a "pasted" turn.
- Tests that only inspect sender source (CR counts, sleeps) stay green while
  a fixture that withholds the product ack stays silent.

## Related skills

- `agent-self-evolution`
- `research-before-asserting`
- product evaluation: real TTY, subject-implements

## Evidence pointers (no secrets)

- Product screen vs driver `recordedInput` on the driven session log
- Completions / tool-call counters on that same turn
- Harness `ensureDelivered` re-sends the payload until the product acks
