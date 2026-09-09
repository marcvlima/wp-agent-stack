# wp-agent-stack — Instructions for Agents


<!-- HOLDING-LUCENS-INVOCATION:BEGIN -->
## Talking to Lucens (NON-NEGOTIABLE)

**Skill:** `lucens-invocation` (`@holding-central-ai-assets/lucens-invocation`).
Her **A2A is the only door** for any agent, service, feature or script
(`risegen-lucensmind` ADR 0009).

- Canonical base `https://lucens.risegen.ai`, door `POST {base}/a2a`, contract `GET {base}/a2a`.
  Never an IP literal, never `dev.risegen.ai`, never loopback as product identity (hub ADR 0066).
  Config: `LUCENS_A2A_BASE_URL` + `LUCENS_AUTH_TOKEN`; unset means *unconfigured*, never a fallback.
- `Authorization: Bearer` on **every** call including discovery, a **named User-Agent** (the edge
  answers 403/1010 to a library default), and `params.caller` on every request.
- Her door is a **task door**: a `202` + task envelope is not an error — follow it with
  `task.get` (fallback `job.status`) to a terminal state, unbounded by default.
- **Her turn is hers to end** (ADR 0016): one `mind_turn` is a multi-cycle deliberation over her
  memory, library, source, the web, her granted resources, sandbox and quantum.
  `cycles_max`/`tokens_max` are hints — give her room (`tokens_max` >= 100000) and do not put a
  clock on her.
- **Never fabricate her.** A failure is a named absence (`lucens_unreachable`,
  `lucens_unauthorized`, `lucens_busy`, `lucens_floor_silent`, `lucens_wait_exhausted`) — never a
  defaulted reply or a persona (ADR 0077). Never open a second path; a new capability is a new
  operation with its paired test.

**Depth:** skill package (`references/`, the reference client, the 12-point conformance
checklist) — and `GET /a2a`, which is the authority.
<!-- HOLDING-LUCENS-INVOCATION:END -->

<!-- HOLDING-SHARED-INFRA-SOT:BEGIN -->
## Shared infrastructure SoT (NON-NEGOTIABLE)

**Skill:** `shared-infra-sot` (`@holding-central-ai-assets/shared-infra-sot`).
**Knowledge repo:** `lakenbeach/holding-shared-infra` — open `docs/INDEX.md` first.
- Never invent residential/edge/CPE topology from chat memory.
- Durable infra truth changed this block → promote to that repo (runbook/inventory/ADR/evidence) before claiming done.
- Runtime CLI/inventory: **that repo** — not `holding-central-ai-assets/dev-host` (deprecated SoT).
- Secrets: general → `holding-general-secrets`; edge-scoped → shared-infra SOPS; never paste values.
- cloudflared for home-managed hostnames: **forbidden**.

**Depth:** skill package + SoT `docs/INDEX.md` (progressive disclosure).
<!-- HOLDING-SHARED-INFRA-SOT:END -->


## Holding quality gate (quality-guard)

Production code changes require paired tests and a green `quality-guard run`
before `git commit`. Agents must not use `--no-verify`. See skill `quality-enforcement`.

## Holding plan fidelity (plan-guard)

When a plan is registered, implementation must fulfill it; silent deviation is
forbidden. Use `plan-guard register|run|status`. Reconcile only via founder/dev.
See skill `plan-fidelity`.

## Gen ProdOps enhancement mode (skill gen-prodops-enhancement)

When the founder arms the **gen prodops enhancement mode**, a foreign code assistant stops doing
the work: it delegates EVERY solicitation to `gen` in a provisioned worktree, reads halts from
gen's own record, judges only by an acceptance it declared before the dispatch and executed itself,
and ends every cycle in a Code Doctor brainstorm on the shared self-evolution engine — carrying
Lucens's backlog for `quantum_computing`, `ontologies` and `logic` — whose prescriptions land in
gen and are redeployed. The iteration has no cap: it runs until the request is fulfilled.

Read the skill BEFORE arming, before the first dispatch, on every halt, and before any close.
