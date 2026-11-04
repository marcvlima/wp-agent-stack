# Decided topology SoT not enforced

## Category: `decided-sot-not-enforced`

## Failure card

SYMPTOM: Founder asked why operational Nexus rows were in Postgres and said an ADR already forbids it.

CLAIMED: The agent treated “Postgres is operational leftover” as a new discovery, then invented a pgvector-only cut from chat instead of opening the accepted topology ADR first.

TRUE: Hub ADR 0026 (Postgres demoted to pgvector-only) is superseded by ADR 0027: Cassandra holds ALL operational data; Postgres is the knowledge layer (pgvector + Apache AGE). The FD-42 reconciliation note restates that. Product boot still opened DATABASE_URL, ran operational SQL migrations, and dual-wired Postgres repos as the default.

COST: Founder time diagnosing identity/login against the wrong store; leftover operational tables; a second correction that the policy was already decided.

## Root process failure (not just technical bug)

Accepted architecture ADRs were not the first source. The agent re-derived storage policy from live tables and chat, then over-tightened (cutting AGE) against the superseded “pgvector only” line instead of enforcing the live three-engine ADR.

## Rule (MUST / NEVER — generalized, category-level)

MUST open the accepted decision record for a topology/storage change before writing or deleting data, and enforce that record.

NEVER keep a dual product path that reopens a store the accepted ADR already removed from operational SoT.

NEVER re-decide an accepted topology from chat memory or leftover rows.

## Detection (how the next agent notices the category)

- Chat proposes a new storage rule whose slug already exists under `docs/decisions/`.
- Product boot still opens a DSN the ADR classified as non-operational.
- Default constructors target the superseded store and “flip” to the SoT only in an `if`.
- Leftover tables are treated as policy instead of drift against the ADR.

## Related skills

- `research-before-asserting`
- `plan-fidelity`
- `agent-self-evolution`

## Evidence pointers (no secrets)

- Hub `docs/decisions/0026-nosql-core-datastore-postgres-becomes-pgvector-only.md` (superseded).
- Hub `docs/decisions/0027-datastore-topology-cassandra-clickhouse-postgres.md` (accepted).
- Hub `docs/decisions/0026-0027-fd42-reconciliation-note.md`.
