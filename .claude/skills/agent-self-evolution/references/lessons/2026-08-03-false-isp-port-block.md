# False ISP port-block diagnosis drove avoidable cost

## Failure card

- **SYMPTOM:** Public TCP 80/443 appeared closed; edge cutover stalled.
- **CLAIMED:** ISP filters 80/443; commercial plan needed / long wrong-path debugging.
- **TRUE:** After CPE fix (modem VS_ppp0, UI firewall Accept, listener on target), 80/443/8443 opened; carrier confirmed no block.
- **COST:** Time, trust, pressure toward business ISP plan under unproven hypothesis.

## Root process failure

Premature diagnosis as fact (`research-before-asserting` violation). Incomplete local path checklist. Public IP treated as stable narrative anchor.

## Rule (MUST / NEVER)

- **MUST** prove listener + each NAT hop (current private next-hop) + firewall + external check on **DDNS hostname** before blaming ISP.
- **NEVER** put public IP literals in plans/prompts as current identity.
- **NEVER** drive spend on an unproven filter hypothesis.

## Detection

Agent says “ISP blocks” or “operator filters” without listing the four checks above.

## Related skills

`research-before-asserting`, `mandatory-soft-skills-for-agents`, layer `diagnosis-and-network`.

## Evidence pointers

Holding evidence under `dev-host/evidence/` (port checks on DDNS name; modem VS fix). No secrets.
