# Application keys (Family C)

Client credentials that identify an application. Not a substitute for Family A in a provider API-key field.

## Nexus external clients

For applications registered as OAuth clients on the Nexus:

### Create

```
POST https://nex-global.risegen.ai/v1/admin/oauth-clients
Content-Type: application/json
Authorization: Bearer {owner_admin_jwt}

{"name": "my-app", "redirect_uris": ["http://localhost:8080/callback"]}
```

Requires `owner_admin` scope. Raw `client_secret` is returned in the response.

### Reveal

```
GET https://nex-global.risegen.ai/v1/admin/oauth-clients/{clientID}/reveal
Authorization: Bearer {owner_admin_jwt}
```

The `client_secret` is recoverable. It is not shown only once.

### Rotate

```
POST https://nex-global.risegen.ai/v1/admin/oauth-clients/{clientID}/rotate
Authorization: Bearer {owner_admin_jwt}
```

Rotates the secret. The new secret is returned.

## Ecosystem apps

For applications registered on the global service:

### Create

```
POST https://nex-global.risegen.ai/v1/oauth/apps
Content-Type: application/json
Authorization: Bearer {user_jwt}

{"name": "my-ecosystem-app"}
```

Handler: `api/internal/globalapps/handlers.go` `handleCreateApp`. Returns `client_id` and `client_secret`. The struct comment says the secret is shown at creation. Inspect the current handler before claiming the secret is unrecoverable. Do not invent a reveal route.

## When to use each family

| Need | Family |
|---|---|
| Call RiseGen Inference from any tool | Family A (user API key) |
| No session yet, need to get one | Family B (device grant) → then Family A |
| Register an application as an OAuth client | Family C |

A code assistant that only needs RiseGen Inference uses Family A, via Family B when it has no session. Family C is for when the assistant, or the product it is configuring, is itself a registered application.

## Rules

- Never write `client_secret` into git, a skill file, or a chat transcript.
- Never fall back to localhost or an IP as the product base.