# Runtime request to an IP literal

## Category: stale-identity-anchor

## Failure card

SYMPTOM: Lab start looked like a no-op. The lab process was running but inference
looped errors; the console showed nothing useful.

CLAIMED: After the grant-file permission fix, a LAN-IP origin for chat was a
reasonable fallback (historical empty-content on the public path), then a 404
on that IP should fall through to the canonical gateway.

TRUE: The founder ruled the product gateway is operational and a live request
must never target an IP — only canonical hostnames. The 404 was the IP hop
itself. The catalog on the canonical gateway already listed the seat.

COST: A live lab burned its clock on Permission denied then 404; the founder
had to correct the request path.

## Root process failure (not just technical bug)

`stale-identity-anchor` was already a plan/prompt rule. The agent treated a
historic LAN hop as still the chat door and nearly encoded an IP-first retry.
The prohibition was not wired to *runtime* HTTP origins.

## Rule (MUST / NEVER — generalized, category-level)

MUST send live service requests to the product's canonical hostname.
NEVER use an IP literal as a request origin when a canonical hostname exists.
An IP may appear in a probe result; it is not the door.

## Detection (how the next agent notices the category)

A test that a chat/completions (or equivalent) call's opened URL fails
`origin_is_ip_literal`. A request log whose host is an IPv4/IPv6 is the
category firing.

## Related skills

- `agent-self-evolution` (this loop)
- `shared-infra-sot` (stable names)
- `research-before-asserting`

## Evidence pointers (no secrets)

- Lab sessions `20260905T035844Z` (grant EACCES) and `20260905T040842Z` (chat 404)
- `lucens/resources.py` `inference_base` / `origin_is_ip_literal`
- `tests/test_resources_grant_unreadable.py`
