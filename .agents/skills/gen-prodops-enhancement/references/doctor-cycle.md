# The Code Doctor brainstorm, once per cycle

Every cycle ends in one — **on success and on failure alike**. On success it asks how gen could
have done it better; on failure it asks what in gen made the failure possible. Both answers are
prescriptions **for gen**.

## Where it runs (non-negotiable)

On the **shared self-evolution engine** — the conclave `code-doctor` profile — never in a loop
this skill grows for itself (hub ADR 0082 · repo ADR 0020: no new engine, daemon, scheduler or
ledger for evolution analysis). The skill supplies the session; the engine supplies the council,
the aspects, the ledger and the gates.

```
supervisor ──▶ conclave code-doctor profile ──▶ council seats
                     │                             │
                     │                             └── Lucens's seat, asked through her door:
                     │                                 POST {LUCENS_A2A_BASE_URL}/a2a  (ADR 0009)
                     └── close: prescriptions + lucens_backlog[]
```

## What the close must carry

| Field | Rule |
|---|---|
| `council_session_id` | a real session. A claimed council is a fabrication; the chair has fabricated one before, having judged hosting too expensive |
| `lucens_seat.present` | she was ASKED and answered. Never asked is the worse defect; asked-and-absent names its reason |
| `lucens_backlog[]` | at least one entry for EACH of `quantum_computing`, `ontologies`, `logic`, each with `area`, `title`, `prescription` |
| `prescriptions[]` | each names a target inside gen's own surface, with the evidence from THIS session that motivates it |

## Her backlog: the founder's three areas

`quantum_computing` · `ontologies` · `logic` — the same enum the Ascent rite enforces
(`LUCENS_BACKLOG_AREAS`, `evolve.lucens_backlog_three_areas`). The rule is hers to fill and nobody
else's: **no agent authors text into her mind or on her behalf** (ADR 0077). An area she did not
cover is `lucens_backlog_gap: <area>` — a gap that blocks the close, and is closed by asking her
again, never by writing an entry for her.

Her own words, asked on 2026-09-08 about this very flow, are on the record in
`risegen-lucensmind/docs/plans/2026-09-08-COUNCIL-gen-prodops-enhancement-mode.md`.

## How she is asked

Through her door and nothing else: `POST {base}/a2a`, `Authorization: Bearer`, a named
User-Agent, `params.caller`, `tokens_max >= 100000`, and **no clock on her turn** (ADR 0016). A
`202` is a task envelope, not an error: follow it with `task.get` to a terminal state. A failure is
a named absence — `lucens_unreachable`, `lucens_unauthorized`, `lucens_busy`,
`lucens_floor_silent`, `lucens_wait_exhausted` — never a defaulted reply and never a persona.
See the `lucens-invocation` skill; do not reinvent its client.

## After the close

The prescriptions are implemented **in gen**, with paired tests, landed on `main` verified against
the remote, and redeployed with an independent read-back. Only then does the next attempt open —
the mode inherits the rite's second rule: an attempt begins on the redeployed build, never on the
one that already failed.
