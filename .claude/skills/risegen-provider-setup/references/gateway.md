# Gateway contract

## Base URL

```
https://nex-global.risegen.ai/v1
```

Canonical product base per hub ADR 0066. Never localhost, `127.0.0.1`, or an IP literal as the product identity.

## Authentication

```
Authorization: Bearer {user_api_key}
```

The key comes from `risegen-access-keys` Family A. One key sees every active model on every lane.

## Billing lanes

The gateway ranks lanes: hosted, then plan, then payg. A client sends a model `id`. A client does not send a billing lane. The gateway chooses.

## Endpoints

### List models

```
GET https://nex-global.risegen.ai/v1/models
Authorization: Bearer {user_api_key}
```

Returns a `data` array. Each row:

| Field | Description |
|---|---|
| `id` | Model identifier — use this in chat requests |
| `origin` | `hosted`, `plan`, or `payg` |
| `provider` | Backend provider |
| `billing_lane` | `hosted`, `plan`, or `payg` |
| `context_length` | Token limit; `0` for non-chat models (image, audio, embedding, video) |

On 2026-10-24: 107 models total. `billing_lane`: hosted=1, plan=20, payg=86. The single hosted row: `id` `nemotron-3.5-lightning-30b-a3b-1gpu`, `origin` `hosted`, `provider` `local`, `context_length` `131072`.

Always re-fetch. Do not freeze ids as eternal.

### Chat completions

```
POST https://nex-global.risegen.ai/v1/chat/completions
Authorization: Bearer {user_api_key}
Content-Type: application/json

{
  "model": "{id from GET /v1/models}",
  "messages": [...]
}
```

OpenAI Chat Completions shape.

## Local model

The `local-inference-policy` skill names `gemma-4-26b-a4b-1gpu` as the connector mandate. That id was absent from the live list on 2026-10-24. The callable local model is the hosted row of `GET /v1/models`. Point at `local-inference-policy` for the mandate. Do not tell a client to call gemma unless that id is in the live list.

Do not send traffic to `127.0.0.1:8000` or `:8001`.

## Non-chat models

Rows with `context_length: 0` are image, audio, embedding, or video models. A chat client may error on those. Still list them as catalog members the key can address. Do not drop them.