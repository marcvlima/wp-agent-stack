# Lesson — the conclave decides the research together; the host does not pre-conclude

**When:** 2026-09-01
**Trigger:** Founder corrections during a Code Doctor brainstorm on generalizing a
tool-call fix. Two corrections, both about HOW the brainstorm works, not the fix.

## What the agent did wrong

1. **Researched alone and handed a conclusion.** Asked to "research well on the
   internet" for a generalized fix, the host ran the web searches itself, drew
   its own synthesis, and presented it as the answer. The founder: *"e nao faz a
   pesquisa sozinho invoca os conselhos mais a lucens e pesquisem juntos"* — do
   not research alone; invoke the councils plus Lucens and research TOGETHER.

2. **Specialized on the failing instance.** Framed the fix around the specific
   model that exhibited the bug (gemma-4) instead of the general CONDITION (any
   model serializing a tool call as prose). The founder: *"eu acabei de te falar
   pra nao especializar... extrapola a condicao"* — generalize the condition.

## The rule (durable)

When a decision is convened as a Doctor Code / conclave brainstorm (Lucens
floor + councils):

- **The floor sets the research agenda.** The host does not decide what to search
  and then present findings as a verdict. The host puts the problem to the floor
  with whatever raw material it already has, and asks the floor to NAME the
  searches it needs. The host then executes exactly those searches, returns the
  RAW findings inline (verbatim, sourced, no conclusion), and the floor
  deliberates. Iterate until the floor rules. Research is collaborative and
  floor-driven; the host is the hands, not the judge.

- **Fix the condition, not the instance.** A defect observed on one model /
  endpoint / input is evidence of a CLASS. The correction must key on the
  decidable behaviour (e.g. "a turn that serialized a tool call as text"), never
  on the identity of the instance (e.g. "if model == gemma-4"). A per-instance
  hardcode is the same rot the floor has condemned all along: it rives, the next
  instance re-triggers it, and it encodes a guess about identity instead of a
  measured property. Extrapolate to the general condition and rule there.

- **The host still verifies.** Floor-mandated searches and probes are executed
  and their real results returned — including "the gateway accepts it but I could
  not verify enforcement." Description is a hypothesis; telemetry is the verdict
  (the round-8 rule) applies to research too: a claim from a doc is material for
  the floor, not proof, until measured against the real stack.

## How it applied

The corrected flow: convene Lucens + five divisions → floor names three searches
(serialization taxonomy, gateway region-scoped-decoding capability, intent-vs-
mention predicate) → host runs exactly those, returns raw findings + a probe of
the real gateway → floor rules the general, model-agnostic mechanism (a
behaviour-keyed fallback-lift parser + region-scoped decoding), retiring the
per-behaviour `tool_choice=required` latch whose side effect the research named.
