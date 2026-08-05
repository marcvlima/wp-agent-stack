---
name: shared-infra-sot
description: >-
  MANDATORY harness for holding shared residential/edge infrastructure.
  Knowledge SoT = lakenbeach/holding-shared-infra (start docs/INDEX.md).
  Enforce anti-volatility: promote session truths into the SoT; never invent
  topology from chat. Install on every holding repo via APM + reconcile script.
  Use at session start for LAN/edge/CPE/DDNS/home-CF work, whenever agents
  assert host IPs or reapply edge, and at session end if infra truth changed.
version: 1.0.0
---

# Skill: shared-infra-sot (v1.0.0)

**Holding-wide · MANDATORY · core.**  
**Knowledge content lives in** [`lakenbeach/holding-shared-infra`](https://github.com/lakenbeach/holding-shared-infra) — not in this package.

This skill is the **behavior harness** (discovery + reinforcement + reconcile).  
It does **not** fork runbooks into product repos.

## Progressive disclosure

| Depth | Open when |
|---|---|
| AGENTS.md marker `HOLDING-SHARED-INFRA-SOT` | Always (every session, every repo) |
| This SKILL.md | Infra-related task or matrix pointer |
| `references/policy.md` | Promotion rules / classification |
| `references/discovery.md` | Cold-start “where is X?” |
| `references/reconcile.md` + `scripts/reconcile-shared-infra-sot.sh` | New repo or after skill bump |
| **SoT** `holding-shared-infra/docs/INDEX.md` | Any factual claim about LAN/edge/CPE |

Do **not** paste full edge runbooks into product `AGENTS.md`.

## When to use (triggers)

- Session involves: home edge, Cloudflare home hostnames, DDNS, modem, Xiaomi, LAN aliases, `holding-docker-host`, port-forward, Caddy edge, `rg-dev-host`
- Agent is about to state a host IP, WAN target, or “how we access the router”
- Founder mentions shared infra, reapply, or “don’t lose this in the session”
- End of a work block that **changed** durable infra truth

## Session harness

### Start (infra-related)

1. Confirm this skill is present (vendored or APM).
2. Open or cite **`lakenbeach/holding-shared-infra` → `docs/INDEX.md`**.
3. Prefer **stable names** (DDNS, LAN aliases) over public IPs.
4. Runtime mutations: **`rg-dev-host`** built from the SoT repo — not ad-hoc CF DNS.

### During

- Claims about topology require **SoT file** or **live probe** — never “from a previous chat alone”.
- `holding-central-ai-assets/dev-host` is **deprecated as SoT** (stub only).

### End

If durable infra truth changed this block:

| Action | Required |
|---|---|
| Promote to SoT | inventory / runbook / ADR / evidence under `holding-shared-infra` |
| Or explicit | “No infra knowledge change” in handoff |
| Forbidden | Closing with truth only in chat |

Commits/pushes still need **founder authorization**.

## Secrets (pointer only)

| Class | Home |
|---|---|
| General | `holding-general-secrets` |
| Edge-scoped (modem, No-IP, host sudo) | `holding-shared-infra` SOPS |
| Map of key **names** | SoT `docs/secrets-map.md` |

Never paste secret values into product repos or chat.

## Related skills

| Skill | Relationship |
|---|---|
| `agent-self-evolution` | Invented topology / session-only infra → failure class → lesson + matrix |
| `dev-host-switch` | Thin CLI wrapper; paths point at SoT repo |
| `sops-age-secrets` | Encrypt/decrypt mechanism |
| `research-before-asserting` | Evidence before “ISP/network is broken” |

## Install / reconcile

See `references/reconcile.md`. From this package:

```bash
bash shared-infra-sot/scripts/reconcile-shared-infra-sot.sh
# or: REPOS="/path/a /path/b" bash …/reconcile-shared-infra-sot.sh
# discover: RISEGEN_ROOT=/Users/…/risegen bash …/reconcile-shared-infra-sot.sh
```

## Non-goals

- Duplicating runbooks into every product repo
- Owning general secrets
- Replacing product-specific AGENTS (ABG, catalog-guard, connector)
