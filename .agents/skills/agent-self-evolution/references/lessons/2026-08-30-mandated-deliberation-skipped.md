# Mandated deliberation skipped, and a prohibition without a detector

## Categories: `mandated-deliberation-skipped`, `prohibition-without-detector`

## Failure card — A (process)

SYMPTOM: The founder asked, in one request, to (1) run a brainstorm with several
named councils and (2) analyse the last product session and fix its failures. The
agent gathered evidence, formed a diagnosis, and began editing code. Mid-stream
the founder interrupted: *"mas voce rodou o brainstorming com todos estes
conselhos …? isso nao e opcional."*

CLAIMED (implicitly, by acting): the deliberation was a framing device around the
real work; evidence plus a correct diagnosis was sufficient to start implementing.

TRUE: the deliberation was a *deliverable of equal standing*, explicitly named in
the request and non-optional by holding policy. Skipping it also cost analysis:
once convened, the councils produced findings the agent had not reached alone —
an ontology dissent (one concept, two meanings), a learning-poisoning risk in the
recorded incident data, and a copy defect that was itself a cause of the founder's
loss of trust.

COST: a founder interruption, a partially-applied edit made outside the sanctioned
process, and a diagnosis narrower than the one the mandated process produced.

## Failure card — B (enforcement)

SYMPTOM: The same session found ~4 KB of hardcoded device definitions in a product
system prompt — the exact prohibition already recorded as
`domain-knowledge-hardcoded-in-agent` (2026-08-27) and already carried as an
always-on matrix line.

TRUE: the rule existed and was not enough. The prompt's test suite actively
asserted the **presence** of those literals, so every gate was green while the
prohibition was violated. A prohibition with no detector is a preference.

COST: a wrong-target class the holding had already paid to learn about, recurring
three days later on a live, actuating surface.

## Root process failure

A: A named, non-optional process step was treated as ceremony because the agent
believed it already knew the answer. Confidence in a diagnosis is not authority to
skip a mandated step — and here the mandated step was also epistemically better.

B: A rule was promoted to the matrix without asking what mechanism would *fail*
when it is broken. Rules stop the next agent only where a gate can see them.

## Rule (MUST / NEVER — generalized, category-level)

MUST execute every process step the requester names, or that policy marks
non-optional, **before** the work it gates — even when the agent believes it
already has the answer. If a step seems redundant, run it and say why it seemed
redundant; never silently substitute your own judgement for a mandated process.

MUST, when a request names both a deliberation and an execution, treat the
deliberation as a first-class deliverable with its own output, not as narration
wrapped around the execution.

MUST, when promoting any prohibition to the matrix, name the **detector** that
fails when it is violated (a test asserting absence, a lint, a gate). A matrix
line with no detector is recorded as incomplete.

NEVER let a test assert the presence of the very literal a standing rule forbids —
invert it to an absence assertion; the absence assertion IS the enforcement.

## Action plan

1. Two always-on matrix lines added (below).
2. This lesson + INDEX row.
3. Detector precedent shipped in the product repo: the prompt's test suite now
   asserts the absence of identity, site and wire-format literals.
4. Skill version bumped; reconcile to consumer repos.

## Detection (how the next agent notices the category)

- The request contains a named process ("run X", "convene Y") **and** a task; the
  agent's first tool call is on the task.
- A matrix prohibition exists for a surface, and grepping that surface finds the
  forbidden literal while all gates are green — look for a test asserting its
  presence.
