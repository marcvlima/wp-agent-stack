# Forbidden actor as peer of the allowed occupant

## Category: `forbidden-actor-as-peer`

## Failure card

- **SYMPTOM:** Founder, 2026-09-02 (session `9ef606c6`, verbatim): the mind must
  not answer on the product assistant tab — the assistant must. 2026-09-14
  Antigravity session `81f9b394` added a mind persona and a mind A2A transport
  as peers of the assistant, defaulted the assistant HTTP fallback to the
  mind's journeys host, and left the allowed occupant's transport unwired.
- **CLAIMED:** "wire to the assistant turn server" / shared dialogue for every
  agent.
- **TRUE:** The assistant tab still wrapped the mind's console surface with no
  turn-host override. `quality-guard` e2e already asserts the tab never speaks
  as the mind; the HTTP fallback still posted to the mind's dialogue door.
- **COST:** Founder correction; the prohibition had to be restated.

## Root process failure (not just technical bug)

A named prohibition existed in a session and a product plan, but there was no
detector that failed when the forbidden actor was re-exported as a persona or
when the assistant chrome resolved to the mind's host. An unused transport
class named after the allowed occupant passed for wiring.

## Rule (MUST / NEVER — generalized, category-level)

**NEVER** expose a forbidden actor as a persona, transport, fallback, or
liveness probe of the allowed occupant of a role. A named prohibition is a
detector: the test fails if the forbidden actor is importable on that surface
or if the resolved turn host is theirs.

## Detection (how the next agent notices the category)

- A surface that lists two named actors as interchangeable `persona` /
  `transport` values for the same role.
- An HTTP fallback whose default host is the forbidden actor's host.
- A comment that claims the allowed occupant's transport while the call path
  still uses the forbidden actor's client.
- Tests that instantiate the forbidden actor's transport as a success case.

## Related skills

- `agent-self-evolution` (this loop)
- `prohibition-without-detector` (a rule with no failing test)
- layer `references/matrix-layers/actor-roles.md`

## Evidence pointers (no secrets)

- Founder session `9ef606c6-a2e1-4c7d-a01a-0dd107edc9fe` (2026-09-02T22:23:36)
- Antigravity commit `2c486aa` (session `81f9b394-db82-430c-bd1c-f9b463c97ec0`)
- Detector: product `core/src/shared/dialogue/__tests__/dialogue.test.ts`,
  `core/src/shared/dialogue/__tests__/hosts.test.ts`,
  `core/src/pages/__tests__/gen-channel.test.ts`
