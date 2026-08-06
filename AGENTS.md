# wp-agent-stack — Instructions for Agents

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
