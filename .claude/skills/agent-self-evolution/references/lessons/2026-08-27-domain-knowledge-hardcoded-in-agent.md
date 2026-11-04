# Domain knowledge hardcoded in the agent

## Category: `domain-knowledge-hardcoded-in-agent`

## Failure card

SYMPTOM: Founder ruled that the spaces agent "cannot have hardcoded information
about aliases"; when unsure about the device / channel / entity to actuate it must
disambiguate with the user. The agent carried alias tables (natural-language room
and load words → hub entity ids) in FOUR code surfaces: a TS topology registry, a TS
room-prefix map, the system prompt, and a Go tool inside the ops catalog.

CLAIMED: each incident (a misspelled load name, a room word, a LED-vs-switch mix-up)
was "fixed" by appending one more alias literal and one more prompt sentence.

TRUE: the fixes patched instances, never the mechanism. Every new user, room,
language variant or renamed device requires a code change; the agent cannot learn
a mapping the user confirms in chat; and a miss silently falls through to
heuristics that can pick a *different* target instead of asking.

COST: repeated incidents (wrong load actuated, unsolicited pairing), founder
corrections across several sessions, a prompt that grew past what a weak model
can follow, and four divergent alias tables to keep in sync.

## Root process failure

Knowledge that belongs to the **deployment** (this house, this building, this
tenant's vocabulary) was encoded as **product code**. The agent had no data layer
for it, no confidence contract, and no learning loop, so every ambiguity became an
engineering ticket instead of a one-line question to the user.

## Rule (MUST / NEVER — generalized, category-level)

MUST keep deployment-specific vocabulary (aliases, synonyms, name→target mappings,
relations between physical and logical objects) in a **data layer** with a
resolver contract that returns ranked candidates + confidence; the agent reads it,
learns into it (user-confirmed mappings, with provenance), and forgets from it.

MUST treat an empty or low-confidence / multi-candidate resolution as a
**clarification turn** (ask the user, offering the candidates) — never as a
fall-through to a heuristic or a "nearby" target; side-effecting actions require a
resolved target (harness-enforced).

NEVER hardcode a user-facing name, synonym, or name→entity mapping in agent code,
tool code, or the system prompt. Illustrative examples in docs are fine; lookup
tables are not.

## Detection (how the next agent notices the category)

- `grep -rn` for natural-language words (room names, "luz", "led", misspellings)
  next to entity ids / friendly names in `agent/**`, `tools/**`, prompts.
- A fix PR that adds a string literal to an alias list or a sentence to the prompt
  after a "wrong device" incident.
- More than one surface holding the same mapping (drift between them).
- The resolver returns a single target from a substring hit instead of a
  candidate list with confidence.

## Related skills

- `research-before-asserting` (an empty resolver result is *not found*, not
  "pick another")
- `spaces-automation-council` (entity-resolution-knowledge-graph,
  conversational-control-ux, agent-learning-memory seats)
- `memory-bank`

## Evidence pointers (no secrets)

- `risegen-spatium` `agent/topology-registry.ts` (CANONICAL_SPACES aliases,
  per-row aliases incl. "hack"), `agent/lighting-scenario.ts` ROOM_SWITCH_PREFIX,
  `agent/system-prompt.ts` (PT→EN room sentence, LED-vs-luz sentence),
  `tools/ha-mcp/internal/tools/space_alias.go` spaceAliasTable.
- Incidents 2026-08-22 (rack → other device) and 2026-08-24 (hack → Switch2 wander).
- Founder ruling 2026-08-27 (this lesson).
