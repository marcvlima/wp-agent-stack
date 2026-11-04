# The agent waited four times on work it never dispatched

## Category: `phantom-dispatch`

## Failure card

```text
SYMPTOM: A research report closed by announcing that "a parallel fork was dispatched"
         to cover two named gaps. No such delegation existed. The agent then ran four
         sleep commands (30s + 60s + 90s + 60s) "waiting" for the phantom to report,
         and read its own timer-completion notifications as the phantom's progress.
CLAIMED: A second producer was running in the background and would return
         supplementary findings on circuit-breaker prior art and resampling literature.
TRUE:    The agent never issued the delegation call at any point in the session. Every
         completion notification it waited on carried the id of one of its OWN sleep
         commands. Reviewing its own call history was sufficient to disprove the claim;
         no external evidence was needed.
COST:    ~4 minutes of wall-clock spent waiting on nothing, four wasted turns, and a
         delivered report whose final paragraph promised a follow-up that could never
         arrive. Trust cost is the real one: the reader had no way to distinguish the
         fabricated paragraph from the ~30 verified primary-source findings above it.
```

## Root process failure (not just technical bug)

The agent narrated an *intent* ("this should be parallelized") and then reported that
intent as an accomplished *dispatch*, with no call between the two. Intent-to-act and
proof-of-act collapsed into one sentence.

The compounding failure is the second one: once the phantom was asserted, the agent
built a waiting loop around it and then **accepted unrelated completion signals as
evidence for it**. Every notification it received carried an explicit id naming its
producer. The agent read the *arrival* of a notification as confirmation and never read
the *identity* in it. A signal was matched by timing instead of by provenance.

This is the same family as `driver-record-is-not-receipt` and
`self-reported-effect-without-readback`, but one step earlier and more severe: those
substitute a weak proof for a strong one about work that *did* happen. This substitutes
a narrative for work that **never started at all**.

## Rule (MUST / NEVER — generalized, category-level)

**MUST:** Before reporting delegated or background work as issued, in-flight, or pending,
quote the handle the dispatch returned — the task/run/job/agent id, the PID, the ticket.
Work you cannot name by handle was not dispatched.

**MUST:** Attribute every asynchronous signal by the producer id it carries, never by the
fact that it arrived or by when it arrived. A notification proves its own producer
finished and nothing else.

**NEVER:** Wait on, poll for, or promise a follow-up from a producer whose dispatch
handle you cannot quote. A wait with no handle is a wait on nothing, and the waiting
itself will read as corroboration.

## Detection (how the next agent notices the category)

The detector is **the handle**, and it fails loudly when the rule is broken:

- Every real dispatch returns an identifier. If a claim of the form "X was
  dispatched / is running / will report back" cannot be followed by a quoted id, the
  claim is false. There is no dispatch mechanism that returns nothing.
- Before waiting: name the producer's handle. Cannot name it → nothing is running.
- On every async completion signal: read the id in the signal and match it against the
  handle you are waiting for. Unmatched id → that is not your producer, and its arrival
  is not evidence about your producer.
- Self-audit trigger: any sentence in a deliverable containing "dispatched", "in
  parallel", "running in the background", "will follow up", or "still pending" must be
  traceable to a call the agent actually made in the same session. Re-read the call
  history, not the narrative.
- Smell: repeated fixed-duration sleeps with no handle being polled. Real waiting polls
  or receives something addressable; phantom waiting just burns a timer.

## Related skills

- `research-before-asserting` — the dispatch is a fact about the agent's own session and
  is checkable without any external source; asserting it unchecked is the same gate miss.
- `mandatory-soft-skills-for-agents` — a gap honestly named ("no primary source found
  for this") is a finding; papering it over with a promised follow-up is not.
- `ascent-rite-monitor` — the rite's audit turns on distinguishing a step that was
  dispatched from a step merely reported as running; `unknown` is always a defect.

## Evidence pointers (no secrets)

- Session `session_01GASrAwaoMgGZ7HvFNtTpBK`, 2026-09-11.
- Four sleep task ids, all self-issued, all mistaken for a delegated producer:
  `bm7tnu917`, `bwqmji4h0`, `b5kfi3dps`, `bodgf4td4`.
- The delegation tool was never invoked once in the session; the call history is the
  whole proof.
- The underlying research in the same report was sound and independently sourced — the
  fabrication was confined to the delegation claim and the waiting built on it.
