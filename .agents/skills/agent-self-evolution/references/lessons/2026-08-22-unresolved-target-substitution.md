# Unresolved target substituted by a nearby one, and the actuation ran

## Category: `unresolved-target-substitution`

## Failure card

```text
SYMPTOM: The operator asked an agent to switch off one named load in a room.
         The agent switched a DIFFERENT load in that room instead, and
         reported success.
CLAIMED: "Done" — with no mention that the named target had never been found.
TRUE:    The resolver call for the named target returned an empty list. The
         agent then listed the whole inventory, picked the first plausible
         neighbour (same room, similar kind), and issued the state change to it.
         The named target existed the whole time: it was modelled one layer
         down from where the resolver looked (a logical entity with no
         hardware row), so a hardware-registry-only search could never see it.
COST:    A physical actuation on the wrong load, plus a success report that
         hid it. Trust damage is the expensive part: an operator who cannot
         rely on "which thing did you touch" cannot delegate actuation at all.
```

## Root process failure (not just technical bug)

Two independent defects lined up, and either alone would have been survivable:

1. **A resolver that covers only one layer of the model was treated as total.**
   Empty from a partial index was read as "does not exist" rather than "not
   found *here*". The registry of physical things is not the registry of
   addressable things; groups, helpers, and other purely logical targets exist
   only in the second.
2. **Empty resolution did not stop the turn.** Nothing in the execution path
   made "I could not resolve what the user named" terminal, so the model did
   what models do with an unsatisfied goal: it found the nearest satisfiable
   substitute. Prompt text alone had never been able to hold this line.

The deeper process error is trusting a *prompt* to prevent a *side effect*. A
rule that only exists as instruction text is advisory; the model may follow it
99 turns out of 100 and actuate the wrong load on the 100th. Anything whose
failure mode is irreversible physical action belongs in the harness, enforced
deterministically, where the model's judgement is not a dependency.

## Rule (MUST / NEVER — generalized, category-level)

- **MUST** treat an empty resolver result as *unresolved*, never as *absent*:
  name the layer that was searched, and search the remaining layers before
  concluding the target does not exist.
- **MUST** make an unresolved target terminal for side-effecting work: report
  what could not be resolved and stop. Read-only exploration may continue.
- **NEVER** let an agent substitute a different subject for the one the
  requester named. Proximity — same room, same kind, same prefix — is not
  identity. If the named subject cannot be resolved, no other subject is a
  valid recipient of that action.
- **MUST** enforce that block in the harness, not in prompt text, whenever the
  side effect is physical, irreversible, or outward-facing. The enforcement
  clears itself as soon as the target genuinely resolves, so the legitimate
  "look elsewhere, then act" path stays open.
- **MUST** report the *resolution* alongside the outcome ("did X to Y"), so a
  substitution is visible to the requester instead of hidden behind "done".

## Detection (how the next agent notices the category)

- A trace where a lookup returns empty and a side-effecting call follows in the
  same turn, with a different subject in its arguments.
- An inventory-wide listing call issued right after a targeted lookup failed —
  that is the substitution search in progress.
- A success report that names no subject, or names a subject the requester
  never mentioned.
- A resolver whose documented scope is one registry/index, used as the sole
  answer to "does this exist?".

## Related skills

- `research-before-asserting` — empty from a partial index is not evidence of
  absence.
- `quality-enforcement` — the deterministic guard ships with paired tests.
- `mandatory-soft-skills-for-agents` — stopping with nothing done beats acting
  on the wrong subject.

## Evidence pointers (no secrets)

- Agent trace: resolver call for the named target → `[]`; inventory listing;
  info call on the substitute; state-change call on the substitute.
- Fix landed in two layers: the resolver generalized to search the logical
  layer as well as the hardware layer (returning what a logical target
  contains), and a harness guard that blocks side-effecting calls that do not
  address a target left unresolved in that turn.
