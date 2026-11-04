# Chrome not retargeted with the backend

## Category: chrome-not-retargeted-with-backend

## Failure card

SYMPTOM: Founder corrected that the console interface must use the unique
service; the send path had been pointed at that service while the visible
chrome still required the previous plane’s API-key wall and model picker.

CLAIMED: Wiring the conversation client to the unique-service protocol
meant the console used that service.

TRUE: The composer still refused to send without an Inference API key and
the page still blocked on the keys list. Health/card of the unique service
was treated as interface proof.

COST: Trust — the unique service was live, but the user-visible surface
still belonged to the old plane.

## Root process failure (not just technical bug)

Backend retarget without chrome retarget. A protocol adapter is not the
interface. Admission walls left on the old plane keep the unique service
unreachable from the product UI.

## Rule (MUST / NEVER — generalized, category-level)

MUST switch admission chrome with the backend when a user surface is
retargeted to an existing unique service. NEVER leave the previous plane’s
auth walls, pickers, or send guards in place. NEVER reimplement the unique
service as a second backend.

## Detection (how the next agent notices the category)

The request path says unique-service, but the same screen still loads keys,
models, or send-disabled-without-key from the previous plane. A health/card
probe is green while the composer cannot send.

## Related skills

- `research-before-asserting`
- `development-flow`
- layer `unique-service-chrome.md`

## Evidence pointers (no secrets)

- Console agent conversation still gated on `/v1/api-keys` after A2A BFF
- Unique-service health/card 200 is not a SendMessage from the UI
