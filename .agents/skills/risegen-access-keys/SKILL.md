# risegen-access-keys — create, look up, or reuse RiseGen credentials

Three credential families. Do not collapse them.

## Family A — user inference API key

What a provider form wants. **Reuse first.**

1. Read `~/.risegen/credentials.json`. If `gateway_api_key` is non-empty and `gateway_url` is set, `GET {gateway_url}/models` with `Authorization: Bearer` and a named `User-Agent`. HTTP 200 with a `data` array means the key is valid — reuse it. Do not create another.
2. Create only when reuse fails, and only with a JWT session of the human user (`auth.RequireJWTSession`). `POST {nexus}/v1/api-keys` with `{"name":"<assistant>-inference","scopes":["inference"]}`. Omitted scopes default to `inference`.
3. Scope authority: Go types in `api/internal/auth/types.go` (`AllScopes`: `inference`, `admin`, `connector`, `sessions`, `quantum:research`). The OpenAPI `/v1/api-keys` enum lists only `inference`, `admin`, `connector` — the Go types are the authority.
4. Consult: `GET {nexus}/v1/api-keys` returns `id`, `name`, `prefix`, `scopes`, `revoked`, `created_at`, `last_used_at`. It does not return the raw secret.
5. Owner re-read: `GET {nexus}/v1/api-keys/{id}/reveal` (owner only, audited). Hub ADR 0062: a secret is not shown only once.
6. **product-bind**: `POST {nexus}/v1/api-keys/product-bind` with `{"product":"code"}` or `{"product":"connector"}`. `auth.ProductBindScopes`: `code` = `inference`+`sessions` ("RiseGen Code"); `connector` = `connector`+`inference` ("RiseGen Connector"). Response field `reused: true` when an existing decryptable product key is returned. This route exists in Go and is absent from `api/openapi.yaml`.

Nexus base: `https://nex-global.risegen.ai`

## Family B — device access (OAuth 2.0 Device Authorization Grant, RFC 8628)

Yields a session. Use that session for Family A.

1. `POST {nexus}/oauth/device/code` as `application/x-www-form-urlencoded` with `client_id` of a registered application (example: `rga` for RiseGen AI Code). Unregistered `client_id` → 400 `invalid_client`.
2. Response: `device_code`, `user_code`, `verification_uri`, `verification_uri_complete`, `expires_in`, `interval`.
3. Human approves at the verification URI. `POST {nexus}/oauth/device/verify` with the web session and `user_code`.
4. Poll `POST {nexus}/oauth/token` with `grant_type=urn:ietf:params:oauth:grant-type:device_code`, `device_code`, `client_id`. While waiting: error `authorization_pending`. Do not poll faster than `interval`.
5. Success: `access_token` (JWT session), `refresh_token`, `expires_in`, `scope`. That `access_token` is **not** the long-lived gateway API key. After it arrives, call product-bind or `POST /v1/api-keys`.
6. 403 `access_denied` means the Code service is not activated for that user.

## Family C — application client credentials

Identify an application. Not a substitute for Family A in a provider API-key field.

- **Nexus external clients**: `POST {nexus}/v1/admin/oauth-clients` (owner_admin). Raw `client_secret` is returned and recoverable via `GET {nexus}/v1/admin/oauth-clients/{clientID}/reveal`. Rotate is the route next to reveal. Secrets are not shown once.
- **Ecosystem apps**: `POST /v1/oauth/apps` on the global service (`api/internal/globalapps/handlers.go` `handleCreateApp`) returns `client_id` and `client_secret`. The struct comment says the secret is shown at creation. Inspect the current handler before claiming the secret is unrecoverable. Do not invent a reveal route.

A code assistant that only needs RiseGen Inference uses Family A, via Family B when it has no session. Family C is for when the assistant, or the product it is configuring, is itself a registered application.

## Rules

- Never write a raw key, `client_secret`, `refresh_token`, or `Authorization` header into git, a skill file, a committed log, or a chat transcript.
- Never fall back to localhost or an IP as the product base.
- Reuse before create.

## References

- [User API keys](references/user-api-keys.md)
- [Device grant](references/device-grant.md)
- [Application keys](references/application-keys.md)