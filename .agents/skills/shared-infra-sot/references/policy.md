# Policy — shared infrastructure knowledge (enforced by this skill)

## Source of Truth

| What | Where |
|---|---|
| Topology, inventory, runbooks, edge CLI, evidence | **`lakenbeach/holding-shared-infra`** |
| Cold-start index | `holding-shared-infra/docs/INDEX.md` |
| Agent behavior / progressive disclosure | **This skill** (`@holding-central-ai-assets/shared-infra-sot`) |
| General secrets | `holding-general-secrets` |
| Agent skills (councils, etc.) | `holding-central-ai-assets` (not edge runtime SoT) |

## Anti-volatility (NON-NEGOTIABLE)

Reusable infrastructure truth **must not** live only in agent sessions.

| Class of knowledge | Destination (same work block) |
|---|---|
| Topology / hostnames / PF / DNS aliases | SoT `inventory.yaml` + runbook |
| How to operate a device | SoT `docs/runbooks/*` |
| Why we chose a path | SoT `docs/decisions/*` |
| One-off proof | SoT `evidence/*` + Last verified on runbook |
| In-progress only | SoT `memory-bank/` (not topology SoT) |

**Session-end gate:** if infra truth changed and exists only in chat → not done.

## MUST

1. Open SoT `docs/INDEX.md` before asserting LAN/edge topology.
2. Use DDNS / LAN aliases as durable identity — never public IP as “current” in plans.
3. Treat `holding-central-ai-assets/dev-host` as **deprecated SoT** (MOVED stub).
4. Mutate inventory-managed CF/edge via `rg-dev-host` from the SoT repo.
5. Reconcile this skill into every holding repository.

## NEVER

1. Invent CPE/edge procedure from chat memory alone.
2. Re-enable cloudflared for home-managed hostnames (SoT policy: forbidden).
3. Fork full runbooks into product AGENTS.md.
4. Commit secrets, age keys, or plaintext env.
5. Hardcode Xiaomi WAN DHCP address as permanent.

## Failure → self-evolution

Category when violated: **session-only-infra** or **invented-topology**.  
Run `agent-self-evolution` and ensure this skill’s marker is present on the failing repo.
