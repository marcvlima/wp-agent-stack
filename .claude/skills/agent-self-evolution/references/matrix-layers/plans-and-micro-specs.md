# Layer — plans and micro-specs

## MUST in every executable micro-spec

| Field | Example |
|---|---|
| Host identity | a stable name — `user@<host-alias>`, never a bare IP (see NEVER below) |
| **Absolute** path on host | `/home/risegenai/edge/scripts/apply-cf-only-firewall.sh` |
| Repo path (if different) | `holding-central-ai-assets/dev-host/edge/scripts/...` |
| Secrets keys | `HOST_SUDO_PASSWORD` from `~/.config/risegen/dev-host/secrets.env` |
| Done when | command + expected output |
| Evidence path | `dev-host/evidence/TE.3-fw.txt` |

## NEVER

- Write only a repo-relative path and expect the agent to “find it on the server.”
- Leave “sudo somehow” without the secret key name or a founder-approved break-glass.
- Pin a bare IP as a host's durable identity — in a micro-spec, a runtime config,
  a test fixture or an example. Hosts get decommissioned; the address outlives the
  machine in every file that copied it, and the next agent then diagnoses a dead
  host as a broken product (category `stale-identity-anchor`). Use the stable
  name (LAN alias / DDNS / service hostname); when an address is genuinely
  needed, resolve it at runtime.

  Founder ruling 2026-08-30, on a host the shared-infra SoT had recorded as dark
  two days earlier: *"nada pode apontar para o 96 ainda"* — nothing may still
  point there. It was still pinned in a product's runtime config, in a test
  fixture, in an older memory-bank topic's "live instance" line, and as the
  example host identity in THIS file.

## Seed lessons

- `lessons/2026-08-03-incomplete-micro-spec-paths.md`
