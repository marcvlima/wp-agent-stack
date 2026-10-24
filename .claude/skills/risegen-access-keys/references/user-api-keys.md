# User API keys (Family A)

The primary credential for RiseGen Inference. One key per user, reused across assistants.

## Reuse (always first)

1. Check `~/.risegen/credentials.json` for `gateway_api_key` and `gateway_url`.
2. `GET {gateway_url}/models` with `Authorization: Bearer {gateway_api_key}` and a named `User-Agent` header.
3. HTTP 200 with a `data` array → the key is valid. Reuse it. Stop.

## Create (only when reuse fails)

Requires a JWT session of the human user (`auth.RequireJWTSession`).

```
POST https://nex-global.risegen.ai/v1/api-keys
Content-Type: application/json
Authorization: Bearer {user_jwt}

{"name": "<assistant>-inference", "scopes": ["inference"]}
```

Handler: `api/internal/platform/handlers.go` `handleCreateAPIKey`. Omitted `scopes` default to `inference`.

## Scopes

Authority: `api/internal/auth/types.go` `AllScopes`:

| Scope | Description |
|---|---|
| `inference` | Run inference on any model |
| `admin` | Administrative operations |
| `connector` | Connector lifecycle management |
| `sessions` | Session management |
| `quantum:research` | Quantum computing research access |

The OpenAPI `/v1/api-keys` enum lists only `inference`, `admin`, `connector`. The Go types are the authority; the OpenAPI enum lags.

## Consult existing keys

```
GET https://nex-global.risegen.ai/v1/api-keys
Authorization: Bearer {user_jwt}
```

Returns: `id`, `name`, `prefix`, `scopes`, `revoked`, `created_at`, `last_used_at`. Does **not** return the raw secret.

## Reveal a key (owner only, audited)

```
GET https://nex-global.risegen.ai/v1/api-keys/{id}/reveal
Authorization: Bearer {user_jwt}
```

Hub ADR 0062: a secret is not shown only once. The owner can always re-read it.

## Product bind

Bind a key to a product scope for automatic reuse:

```
POST https://nex-global.risegen.ai/v1/api-keys/product-bind
Content-Type: application/json
Authorization: Bearer {user_jwt}

{"product": "code"}
```

`auth.ProductBindScopes`:

| Product | Scopes | Display name |
|---|---|---|
| `code` | `inference` + `sessions` | RiseGen Code |
| `connector` | `connector` + `inference` | RiseGen Connector |

Response field `reused: true` when an existing decryptable product key is returned.

This route exists in Go (`api/internal/platform/handlers.go`) and is absent from `api/openapi.yaml`.