# Incomplete micro-spec: repo path ≠ host path; sudo secret unused

## Failure card

- **SYMPTOM:** TE.3 CF-only firewall blocked; agent asked founder for sudo.
- **CLAIMED:** Password does not work / script missing at `~/dev-host/scripts/...`.
- **TRUE:** Script lived at `/home/risegenai/edge/scripts/apply-cf-only-firewall.sh`; `HOST_SUDO_PASSWORD` in `~/.config/risegen/dev-host/secrets.env`.
- **COST:** Founder interruption; delayed mandatory security control.

## Root process failure

Micro-spec listed only repo-relative path. No secrets key. Agent did not search host or secrets before escalating.

## Rule (MUST / NEVER)

- **MUST** put absolute runtime path + user@host + secret env key names in micro-specs.
- **MUST** search secrets before asking founder for passwords.
- **NEVER** invent `~/dev-host/...` when deploy layout is `~/edge/...`.

## Detection

Agent escalates for sudo/path without `find`/`ls` on host and without grepping secret key names.

## Related skills

layer `plans-and-micro-specs`, `secrets-and-host-access`; plan authors share fault when specs omit runtime paths.

## Evidence pointers

Applied nft table `inet risegen_edge`; evidence `dev-host/evidence/TE.3-fw-20260803.txt`.
