# Unique-service chrome (layer)

Open when a user surface is wired to an existing unique service (A2A, MCP,
domain agent) instead of remaining on a generic completions/API-key plane.

## MUST

- Consume the unique service in-place. The surface is chrome + a BFF/proxy.
- Switch admission chrome with the backend: send guards, auth walls, pickers,
  and capability chips must match the unique service’s contract.
- Prove the live unique-service request (the method the UI actually sends),
  not a health listing of the unique service.

## NEVER

- Duplicate the unique service as a second backend in another product.
- Leave the previous plane’s gates (API keys, model pickers, streaming
  toggles, send-disabled-without-key) on the retargeted surface.
- Treat a health/card/status probe as proof the interface uses the unique
  service — that is also `listing-as-liveness`.
