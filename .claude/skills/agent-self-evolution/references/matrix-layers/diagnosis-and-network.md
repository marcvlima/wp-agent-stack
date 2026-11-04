# Layer — diagnosis and network

## MUST before blaming the operator / ISP / “the internet”

1. Confirm a **process is listening** on the intended host:port.
2. Confirm **each NAT hop** targets the **current** private next-hop (re-probe DHCP WAN addresses; never assume last week’s IP).
3. Confirm **firewall** (UI + filter chains): default-deny may drop even when DNAT exists.
4. Probe with a **stable public name** (DDNS), not a remembered public IP.
5. Prefer external checkers over hairpin from inside the LAN.

## NEVER

- Drive a commercial ISP upgrade or other spend on a diagnosis that has not passed the above.
- Treat “port closed” as ISP filter when the origin has no listener.

## Seed lessons

- `lessons/2026-08-03-false-isp-port-block.md`
