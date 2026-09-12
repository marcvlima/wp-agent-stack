# Floor protocol — phases, entries, the round brief

This is the full protocol. SKILL.md is the index; this file is the contract
`scripts/floor.py` enforces.

## Session directory

Default: `memory-bank/<topic>/brainstorms/<session-id>/`.

Created by `floor.py open`. Holds `facts.md`, `floor.jsonl`, `session.json`
(roster + topic; derived from the `convene` entry if missing), and
`record.md` after `close`.

`floor.jsonl` is append-only. `seq` is 1-based and consecutive. A round N
entry always has a greater `seq` than every round N-1 entry — a
manifestation cannot land after the next round has opened.

## Entry schema

Every line of `floor.jsonl` is one JSON object with exactly these keys:

| Key | Type | Meaning |
|---|---|---|
| `seq` | int | 1-based, consecutive, assigned by `post`/`open` |
| `ts` | string | ISO-8601 UTC (`YYYY-MM-DDTHH:MM:SSZ`) |
| `round` | int | 0 = convene; caller-supplied thereafter |
| `phase` | string | `convene` \| `open` \| `research` \| `cross` \| `converge` \| `close` |
| `author` | string | seat id, or `host` |
| `author_kind` | string | `council` \| `individual` \| `host` |
| `type` | string | see tables below |
| `body` | string | the manifestation, verbatim |
| `addressed_to` | [string] | seat ids; required on `question` and `seat_absent` |
| `answers` | [int] | `seq`s this entry answers (questions, research requests, objections) |
| `requested_by` | string | seat id; required on `research_result`; empty otherwise |
| `refs` | [int] | `seq`s cited (required on `decision`: seat entries) |

No other file is the discussion. A host paraphrase, a subagent scratchpad,
or a "private note" is a side channel and a violation of invariant 2.

## Host types (closed verb set)

| Type | Phase | Body |
|---|---|---|
| `facts` | convene | the facts pack, copied from `facts.md` |
| `agenda` | convene | the topic and that the host holds no position |
| `convene` | convene | the roster as JSON `{"topic","seats":[{"id","kind"}]}` |
| `relay` | any | a pointer that round N is open; the brief **is** the floor, not this text |
| `research_result` | research | the result of a seat's request; `requested_by` names that seat; `answers` names the request `seq` |
| `protocol` | any | a protocol act that is not a deliberation (warning, round-not-closed, …) |
| `record` | close | the close: outcome, citations to seat `seq`s, and `escalated_to_ratifier` when there is no convergence |
| `seat_absent` | any | named absence; `addressed_to` is the missing seat; body contains the reason. Protocol act, not a position. |

A host `position`, `support`, `objection`, `decision`, or `research_request`
is rejected at `post` and named by `verify` (`host_verb_violation`,
`host_research_request`, `host_authored_decision`).

## Seat types

| Type | Typical phase | Must |
|---|---|---|
| `position` | open (also cross, as a restatement) | the seat's claim and the evidence it rests on |
| `proposal` | open or cross | a candidate solution, named as such; the only source of rows in the record's candidate-solutions table |
| `research_request` | open or cross | what to look up and why; never authored by the host |
| `question` | open or cross | `addressed_to` names present seats; those seats must answer before the round closes |
| `concede` | cross | what is conceded, and why; may `answers` a conflicting `position` |
| `refine` | cross | what changed, and why; may `answers` a question or a conflict |
| `hold` | cross | what is held, and why |
| `support` | converge | the proposal supported, and why |
| `objection` | converge | the proposal objected to, and why; a seat must `answers` it before consensus |
| `decision` | close | cites seat entries by `seq` in `refs` (and/or `answers`). Never authored by the host. |

## Phases in order

### 1. convene (round 0)

`open` writes three host entries and nothing else: `facts`, `agenda`,
`convene`. Seats do not speak.

### 2. open (round 1)

Each seat is handed the round-1 brief (the convene floor only) and posts
`position`, optional `research_request`s, optional `question`s. Openings
do not see each other; this is the one phase where that is intended.

### 3. research

`pending` lists open `research_request`s. The host executes each (see
`research.md`) and posts `research_result` with `requested_by` = the
asking seat and `answers` = the request `seq`. Results are on the floor
before any later `cross`. The host does not add requests of its own.

### 4. cross (minimum two distinct rounds; no cap)

For round N, each present seat receives `round-brief --round N` — the
complete floor through round N-1, verbatim. The seat must:

1. Answer every `question` addressed to it (`answers` contains that `seq`).
2. Respond to every `position` that conflicts with its own.
3. Then `concede`, `refine`, or `hold`, with a stated reason.

A new `research_request` pauses `cross`: run `research`, then continue.
A round with an unanswered `question` addressed to a **present** seat
does not close. `pending` must be empty of such questions before round
N+1 receives any entry.

### 5. converge

Only after two distinct `cross` rounds exist on the floor. Proposals on
the table are the positions still held. Each present seat posts `support`
or `objection` with a reason. An `objection` must be answered by a seat
(`answers` that `seq`) before the proposal can be recorded as consensus.

### 6. close

`floor.py close --outcome consensus|consensus_with_dissent|no_convergence`
writes `record.md` and a host `record` entry. The outcome is derived from
the seats, by one function shared with `verify`. `close` refuses
(`outcome_mismatch`, naming both) when `--outcome` contradicts that
derivation, before writing anything:

- every present seat `support`s, no unanswered `objection` → `consensus`
- support plus named, answered objections that were not conceded →
  `consensus_with_dissent` (dissenters named)
- otherwise → `no_convergence` + `escalated_to_ratifier`

The host does not post `decision`. A seat may. A `decision` must cite
seat entries by `seq`. Under `no_convergence` there is no chosen option.
`chosen` is never taken from a `support` body's first line; without a
seat `decision` entry the record says so. The candidate-solutions table
is built only from `proposal` entries.

A second `close` is refused. `reclose --reason … --outcome …` supersedes
a defective close on the record (protocol entry + new `record` entry;
`record.md` rewritten; nothing deleted) and runs the same refusal.

## The round brief (invariant 1)

`round-brief --dir D --round N` is a **pure function of `floor.jsonl`**:
every line whose `round` is strictly less than N, in file order, verbatim.
It takes no seat id. It does not filter by `author`. Two seats asking for
round N receive byte-for-byte the same brief.

That is the whole of "discussão real". A brief that omits a dissent, a
research result, or another seat's position is isolated deliberation.

## Pending

`pending --dir D` lists:

- unanswered `question`s (no later entry `answers` that `seq`) whose
  `addressed_to` includes a present seat
- open `research_request`s (no later `research_result` that `answers`
  that `seq`)

The host runs this before opening the next round and before `close`.

## Worked example

Topic: "pause 18 — four readers, one producer". Seats: `architecture-council`
(council), `lucens` (individual). Facts pack is the artifact excerpts.

**Round 0 convene.** Host posts `facts` (the excerpts, no recommendation),
`agenda` ("the host holds no position"), `convene` (the two-seat roster).

**Round 1 open.** Architecture posts a `position` (the write boundary does
not enforce shape) and a `question` addressed to Lucens (what did her
floor observe on the producer). Lucens posts a `position` (the producer
is an LLM whose shape varies) and a `research_request` (which readers
accept `item` vs `correction`, with commits).

**Research.** Host executes the request, posts `research_result` with
`requested_by: lucens` and `answers: [<request seq>]`. Architecture sees
it on the next brief; Lucens sees it too.

**Round 2 cross.** Each seat gets the full floor through round 1. Lucens
answers the question (`answers: [<question seq>]`). Architecture responds
to Lucens's position, then `refine`s. Lucens `hold`s with a reason.

**Round 3 cross.** Same, with the round-2 floor included. Architecture
`concede`s the producer-variation claim. Lucens `refine`s the proposed
fix (enforce shape at write).

**Converge.** Architecture `support`s "enforce shape at the write
boundary". Lucens `support`s the same.

**Close.** `outcome=consensus`. `record.md` names the chosen solution,
cites the supporting `seq`s, and does not invent a host ranking.

A third seat that never spoke would have been a `seat_absent` with a
named reason — not a paragraph "they would have agreed".
