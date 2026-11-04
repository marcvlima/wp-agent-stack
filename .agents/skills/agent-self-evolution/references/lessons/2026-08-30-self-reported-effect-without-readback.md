# A collective the agent could not express, and a success it could not prove

## Category: `backend-membership-as-domain-truth`, `self-reported-effect-without-readback`

## Failure card

```text
SYMPTOM: The user named a PLACE and a SET ("turn off the kitchen lights") and the
         assistant asked which of the room's two loads was meant. Second occurrence
         of the same family in four days.
CLAIMED: The utterance was ambiguous between rival candidates.
TRUE:    The resolver contract could express "which of N" but never "the N" — it had
         no cardinality at all. A live tokenizer probe showed the plural marker
         arriving INTACT and being consulted by no stage. Nothing was lost; something
         available was ignored.
COST:    A central verb below the market floor; the user corrected the same class of
         defect twice in one week.
```

Two further findings surfaced only because the fix was verified against reality
rather than against its own report:

```text
SYMPTOM: After the fix, the agent replied "turned off the 2 loads" — one relay was
         still on.
CLAIMED: The actuation tool reported `actuation_verified: true` for both.
TRUE:    Two commands to the SAME multi-channel module milliseconds apart had the
         second swallowed by the device, while verification still passed. Detected
         only by reading the physical state back independently.
```

```text
SYMPTOM: A whole-area actuation flag scoped by the BACKEND's area membership.
CLAIMED: "The area is the room."
TRUE:    The backend's area membership is device-derived. A channel of a module
         mounted in one room fed a load in ANOTHER room, so the flag silently
         actuated a different room's load and double-commanded one load at two
         layers. A flag that quietly does the wrong thing is worse than no flag.
```

## Root process failure (not just technical bug)

1. **Recurrence was treated as a new symptom rather than as a detection gap.** The
   first occurrence produced a guard; nothing produced a measurement. The same class
   escaped again because no utterance-level regression corpus and no counter existed.
2. **An upstream layer was blamed before it was tested.** A peer review attributed the
   miss to input-transcription losing grammatical number. One probe refuted it in
   seconds, and the true diagnosis was simpler and worse.
3. **Verification trusted the actor's own report.** The agent's success sentence and
   the tool's `verified` flag both said done; only an independent read of the
   physical state disagreed.

## Rule (MUST / NEVER — generalized, category-level)

- **MUST** derive set membership, grouping and scope from the product's own domain
  model, never from the replaceable backend's grouping primitives. A backend's
  grouping is a deployment artifact; when it disagrees with the domain model, the
  domain model is right and the backend is a detail.
- **NEVER** report an effect from the actor's own success signal. A tool's
  `verified`/`ok` flag and the agent's own summary are claims; the effect is proven
  by an independent read-back of the affected state. Where several commands target
  one shared physical unit, prefer one command carrying the whole set over one
  command per member — a race that drops the second write can still report success.
- **MUST** treat a recurrence of a known failure family as a **detection** defect
  first: before fixing the new symptom, add the measurement whose absence let the
  family return, and pre-register the adopt/reject rule the fix must satisfy.

## Detection (how the next agent notices the category)

- A scope/group/"all of X" feature reads membership from a backend registry, area,
  room or tag rather than from the product's own model → category 1.
- A completion claim in the transcript has no corresponding independent state read
  → category 2. Ask: "if this silently did nothing, what would have failed?" If the
  answer is "nothing", it is not done.
- The same user correction appears twice within a release window and the fix adds
  only behavior, no counter or corpus → the detection gap is still open.

## Related skills

`research-before-asserting` (test the upstream blame before inheriting it),
`quality-enforcement` (paired tests, pre-registered decision rule),
`development-flow` (rebuild/redeploy before retest — the second defect was only
visible after redeploying), `memory-bank`.

## Evidence pointers (no secrets)

- Product ADR recording the contract change and the dissents.
- Utterance-level regression corpus mirrored across both implementations of the
  resolver, asserting outcome AND member set.
- Live read-back showing the other room's load still energized while the named
  room's set went dark.
