# Listing is not a live request

## Category: listing-as-liveness

## Failure card

SYMPTOM: Founder rejected an iteration that lost already-earned subject
tool calls and harness refuse evidence.

CLAIMED: Opening the next iteration was safe because the model catalog
listed the pin and the binary was fresh.

TRUE: Catalog listing ≠ chat/completions success. Prefill already failed
(`deadline exceeded`). Implement then showed `InvalidHTTPResponse` and
zero tools. Observer reported `session_reliability: clean`.

COST: A locked iteration that could only regress the prior measurement.

## Root process failure (not just technical bug)

A listing/status check was treated as a live-path proof. The next
iteration was opened on a dead request path.

## Rule (MUST / NEVER — generalized, category-level)

NEVER treat a catalog, inventory, or status listing as proof that a live
request path works. MUST fail-closed until the actual request succeeds.

## Detection (how the next agent notices the category)

The agent is about to start a measurement or implement step after only
a list/status command, with no successful request on the same path.

## Related skills

- `research-before-asserting`
- `ascent-loop-host` (product host preflight)

## Evidence pointers (no secrets)

- Product session `loopsess-c6537b0d0f314c1e` vs prior `loopsess-f07951ab036f40e3`
- TUI `InvalidHTTPResponse`; prefill probe fail-open then loop implement
