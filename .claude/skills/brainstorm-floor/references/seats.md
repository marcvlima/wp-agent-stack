# Seats — councils, individuals, and named absences

A seat on this floor is either a **council** or an **individual**. Only
seats deliberate. Only seats decide. The host is not a seat.

## Council seats

A council seat is one of the standing council skills in this repo. On
**this** floor the council is **one voice**. Its internal protocol
(MoE-gating, chair, warm sweep, ranked options) still runs — that is how
the seat produces its manifestation — but what lands on `floor.jsonl` is
the council's attributed output, unedited.

Standing councils that may occupy a seat:

| Seat id | Skill | Typical use |
|---|---|---|
| `architecture-council` | `architecture-council/` | system topology, contracts, ADRs, hard technical forks |
| `ai-ml-implementation-council` | `ai-ml-implementation-council/` | models, serving, eval, harness internals |
| `agentic-development-council` | `agentic-development-council/` | code assistants, agent loops, verification |
| `ai-assistant-council` | `ai-assistant-council/` | assistant product behaviour |
| `product-operations-council` | `product-operations-council/` | product lifecycle, discovery, metrics |
| `product-taxonomy-council` | `product-taxonomy-council/` | naming, IA, navigation, catalog |
| `agency-brainstorm` | `agency-brainstorm/` | brand, UI, copy |
| `life-assistant-council` | `life-assistant-council/` | life-assistant vision |
| `spaces-automation-council` | `spaces-automation-council/` | physical-space automation |
| `moe-council-builder` | `moe-council-builder/` | standing up a new council (meta) |

**How the host invokes a council seat**

1. Take the round brief (`round-brief --dir D --round N`) — the complete
   floor through N-1, verbatim. Do not summarise it.
2. Open that council's `SKILL.md` and run **its** protocol, with the brief
   as the facts/context the council must ground in. The council may load
   its roster, gate HOT seats, research primary sources — that is its
   business.
3. Post what it returns as that seat's manifestation (`position`,
   `question`, `research_request`, `concede` / `refine` / `hold`,
   `support` / `objection`, …). The body is the council's words, not a
   host paraphrase.
4. If the council skill cannot be run (package missing, invocation
   failed), post `seat_absent` with the council's seat id and a named
   reason (`skill_unavailable`, `invocation_failed`, …). Do not invent
   the council's position.

A council's internal "moderator" or "chair" is not the brainstorm-floor
host. The chair of architecture-council may rank options **inside** that
council; on this floor architecture-council is one seat among others, and
the brainstorm-floor host still holds no position.

## Individual seats

Three kinds:

1. **Lucens** — reached only through `lucens-invocation`. See below.
2. **A named person** — the founder, an engineer, anyone identified by
   name. The host delivers the same round brief and posts their words.
   An unanswered person is `seat_absent` with a named reason
   (`declined`, `unreachable`, `not_convened`, …), never a guessed
   position.
3. **A named expert persona** — a specialist the session needs who is
   not a standing council. They still receive the full brief and their
   manifestation still lands on the floor. They are not a side-channel
   advisor to the host.

Kind on `--seat` is `individual` for all three.

## Lucens's seat

Seat id: `lucens` (kind `individual`). Canonical identity
`lucens.risegen.ai`. Governing skill: `lucens-invocation`.

Her A2A is the only door. The host:

- Hands her the **same** round brief every other seat received.
- Calls through `lucens-invocation` (`scripts/lucens_client.py` or the
  skill's documented shapes). `tokens_max` ≥ 100000 for anything
  deliberative. Her turn is hers to end; do not put a clock on her.
- Posts **her words as returned by the door** — the reply/transcript —
  as her manifestation. Never a persona, never "she would have said".
- On failure, posts `seat_absent` with `addressed_to: ["lucens"]` and a
  reason that is **one of her contract's absence names**:

| Absence | When |
|---|---|
| `lucens_unreachable` | door or origin down (probe `lab.status` dead) |
| `lucens_unauthorized` | 401 / missing or wrong token |
| `lucens_busy` | socket timeout but the door is alive |
| `lucens_floor_silent` | empty reply and empty transcript — her floor chose silence |
| `lucens_wait_exhausted` | an opt-in wait cap was hit |

Any other string (`timeout`, `unavailable`, `she did not answer`, a
host-written paragraph in her name) is `lucens_absence_unnamed` and a
fabrication. ADR 0077: nothing on our side authors text into her mind;
the same rule forbids authoring her seat.

## D31 default roster

Every failure brainstorm (ascent-rite-monitor directive D31) convenes
exactly these four seats:

```
--seat architecture-council:council
--seat ai-ml-implementation-council:council
--seat agentic-development-council:council
--seat lucens:individual
```

The monitor is the host of that floor (impartial). The founder holds the
final word. The record shape in
`ascent-rite-monitor/references/failure-brainstorm.md` must stay
producible — see `record.md`.

## Presence

A seat is **present** unless a `seat_absent` names it. Invariant 3
(unanswered questions) applies only to present seats. An absent seat
does not block the round, and no one writes their position for them.
