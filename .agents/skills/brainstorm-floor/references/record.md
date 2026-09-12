# The record — compatible with D31's failure brainstorm

`close` writes `record.md` in the session directory and a host `record`
entry on the floor. The record is what the seats did, not a host essay.

## Outcomes

| `--outcome` | When | Decision section |
|---|---|---|
| `consensus` | every present seat `support`s; no unanswered `objection` | `chosen` cites the supporting seat `seq`s |
| `consensus_with_dissent` | there is support; named seats objected, those objections were answered, and they did not concede | `chosen` plus **named** dissent (seat ids and their `seq`s) |
| `no_convergence` | the seats did not converge | **no chosen option**; `escalated_to_ratifier: yes`. Never a host call. |

The host passes `--outcome` as a derivation from the floor, not as a
preference. `verify` names `outcome_mismatch` when the flag disagrees
with the seats, `host_authored_decision` when a `decision` is hosted,
`missing_escalation` when `no_convergence` lacks
`escalated_to_ratifier`, and `host_call_without_convergence` when a
chosen option appears under `no_convergence`.

## Required headings

These headings are always present, so a D31 failure brainstorm remains
producible from this skill. Canonical shape:
`ascent-rite-monitor/references/failure-brainstorm.md`.

```markdown
# Brainstorm — <topic> · <UTC>

## Failure card
- fact (verbatim from the artifact): …
- step / node / actor: …
- first seen / recurrences (family): …

## Seats
- architecture (architecture-council): <position, or named absence>
- AI/ML (ai-ml-implementation-council): …
- code assistant (agentic-development-council): …
- Lucens (her A2A, task id, cycles, tokens): <her words as returned by
  the door — or lucens_unreachable | lucens_unauthorized | lucens_busy
  | lucens_floor_silent | lucens_wait_exhausted>

## Root cause (the chain, not the symptom)
1. producer: …
2. reader(s): …
3. divergence: …
4. why it was not caught: …

## Candidate solutions × impacts on the rest of the flow
| # | solution | steps/nodes/readers/actors touched (D25) | cost to the iteration | resilience | fluidity | speed |
|---|---|---|---|---|---|---|

## Decision
- chosen: …
- named dissent: …
- outcome: consensus | consensus_with_dissent | no_convergence
- escalated_to_ratifier: yes | no
```

For a session that is **not** a D31 failure, the same headings are
still written. Failure-card fields that the facts pack did not supply
are recorded as `n/a — not a D31 failure; see facts.md`. Seats that
are not the D31 four are listed with `- <id> (<kind>): …` in the same
Seats section. Lucens, when present, still uses the D31 Lucens line
(her words, or one of the five absence names).

## Seats section rules

- Every roster seat appears, present or absent.
- A present seat's line is its last `position` / `refine` / `hold` /
  `support` / `objection`, in its words (truncated only for the
  record's line budget, never rewritten as a host gloss).
- An absent seat's line is the named reason, not a guessed position.
- Lucens is never paraphrased. Absence names are the contract names.

## Decision section rules

- `chosen` is a proposal a seat supported, cited by `seq`. It is not a
  host ranking of seats.
- Under `no_convergence`, `chosen` is omitted or explicitly `none`;
  `escalated_to_ratifier` is `yes`; the founder is the next reader.
- Named dissent lists seat ids. Omitting a dissent is a host decision
  and a failed record.

## Path

D31 writes
`memory-bank/<topic>/brainstorms/<YYYYMMDD>-pause-<n>-<slug>.md` as a
single file and links it from the defect-table row. This skill writes
the same body as `record.md` inside the session directory
`memory-bank/<topic>/brainstorms/<session-id>/`. For a D31 session the
host (the monitor) may also copy `record.md` to the single-file path
the defect table expects. The body is the same either way; the
headings above are the compatibility contract.
