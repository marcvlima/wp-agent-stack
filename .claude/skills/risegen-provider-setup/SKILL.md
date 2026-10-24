# risegen-provider-setup — configure RiseGen AI as a provider

Configures RiseGen AI as an inference provider in code assistants, IDEs, and SDKs. The credential comes from `risegen-access-keys` Family A.

## Gateway

- Base URL: `https://nex-global.risegen.ai/v1`
- Header: `Authorization: Bearer {user_api_key}`
- Chat: `POST {base}/chat/completions`
- Model list: `GET {base}/models` — use each row's `id`. Also note `origin`, `provider`, `billing_lane`, `context_length`.
- One key sees every active model on every billing lane. The gateway chooses the lane.
- Hosted/local model: the row with `origin: hosted`. On 2026-10-24 that id was `nemotron-3.5-lightning-30b-a3b-1gpu`. Always re-fetch the list. Do not freeze the id as eternal.
- Some rows are image, audio, embedding, or video (`context_length: 0`). A chat client may error on those. Still list them as catalog members the key can address. Do not drop them.
- Do not send traffic to `127.0.0.1:8000` or `:8001`.
- The `local-inference-policy` skill names `gemma-4-26b-a4b-1gpu` as the connector mandate. That id was absent from the live list on 2026-10-24. The callable local model is the hosted row of `GET /v1/models`. Point at `local-inference-policy` for the mandate. Do not tell a client to call gemma unless that id is in the live list.

## Products

See [references/products.md](references/products.md) for per-product setup instructions. Trae IDE uses provider `custom_openai_compatible` with the **Full URL** switch off. Claude Code speaks the Anthropic Messages shape — do not set `ANTHROPIC_BASE_URL` to the RiseGen OpenAI base.

## Gateway reference

See [references/gateway.md](references/gateway.md) for the full gateway contract.

## Scripts

- `scripts/seed_trae_cache.py` — seeds the Trae IDE local SQLite cache with RiseGen models. Best-effort; Trae's server sync may overwrite.

## Rules

- Never write a raw API key into a skill file, a committed log, or a chat transcript.
- Never fall back to localhost or an IP as the product base.
- Always re-fetch `GET /v1/models` before telling a user which model ids are available.