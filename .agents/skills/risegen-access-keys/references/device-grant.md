# Device grant (Family B)

OAuth 2.0 Device Authorization Grant (RFC 8628). Yields a JWT session. Use that session for Family A.

## Flow

### 1. Request device code

```
POST https://nex-global.risegen.ai/oauth/device/code
Content-Type: application/x-www-form-urlencoded

client_id=rga
```

`client_id` must be a registered application. Example: `rga` (RiseGen AI Code). Unregistered → 400 `invalid_client`.

Response:

```json
{
  "device_code": "...",
  "user_code": "ABCD-EFGH",
  "verification_uri": "https://nex-global.risegen.ai/device",
  "verification_uri_complete": "https://nex-global.risegen.ai/device?code=ABCD-EFGH",
  "expires_in": 600,
  "interval": 5
}
```

### 2. Human approves

The human opens `verification_uri_complete` in a browser and approves.

`POST https://nex-global.risegen.ai/oauth/device/verify` with the web session and `user_code`.

### 3. Poll for token

```
POST https://nex-global.risegen.ai/oauth/token
Content-Type: application/x-www-form-urlencoded

grant_type=urn:ietf:params:oauth:grant-type:device_code
&device_code={device_code}
&client_id=rga
```

While the human has not approved: error `authorization_pending`. Do **not** poll faster than `interval` seconds.

### 4. Success

```json
{
  "access_token": "...",
  "refresh_token": "...",
  "expires_in": 3600,
  "scope": "inference sessions"
}
```

`access_token` is a JWT session — **not** the long-lived gateway API key. After it arrives, call product-bind or `POST /v1/api-keys` (Family A).

### 5. Denied

HTTP 403 `access_denied` means the Code service is not activated for that user.

## Rules

- Never write `access_token`, `refresh_token`, or `device_code` into git, a skill file, or a chat transcript.
- The session from this flow is ephemeral. Use it to obtain a durable API key via Family A.