# Product setup instructions

## Trae IDE 3.6.4

Measured on this machine. Bundle `/usr/share/trae`, user data `/home/marcus/.config/Trae`.

### Manual setup

1. Settings → Models → Add model → provider **Custom (OpenAI Compatible)**. Provider id `custom_openai_compatible`. Auth type `API_KEY` is `0`.
2. API format: **OpenAI Chat Completions**.
3. Base URL: `https://nex-global.risegen.ai/v1` with the **Full URL** switch **OFF**. Trae appends `/chat/completions`. Do not put `/chat/completions` in the base when that switch is off.
4. API key: from `risegen-access-keys` Family A.
5. One gateway model id per custom model. Trae does not import `GET /v1/models` by itself. Display name: `RiseGen · {id}`.
6. `config_source`: `Personal` is `3`. Preset Trae models use `config_source` `1`.

### Local cache

SQLite database: `/home/marcus/.config/Trae/User/globalStorage/state.vscdb`, table `ItemTable`.

Keys: `{userId}:AI.agent.model.model_list_map` and `{userId}_AI.agent.model.model_list_map`. `userId` on this install is the non-default key of `host_map` in `/home/marcus/.config/Trae/ModularData/ckg_server/local_env.json`. Measured `userId`: `7700055224313349127`. Host: `https://coresg-normal.trae.ai`.

Each value is a JSON object whose keys are function names (`builder`, `chat_v3`, `solo_agent`, and others) and whose values are lists of model objects.

### Durable registration

Trae's own `add_custom_model` call to that host, using the in-process Trae session. `ModelService.setOriginModelListMapAndCache` replaces the map with the server list (poll about 600s, and when the model-settings screen is open). A local sqlite insert is best-effort for the open window, not the durable record.

No Trae session token is on disk. Do not call that host from the script.

### Seed script

Run `scripts/seed_trae_cache.py` to populate the local SQLite cache with all gateway models. This is best-effort — Trae's server sync may overwrite.

## Generic OpenAI SDK or curl

```python
from openai import OpenAI

client = OpenAI(
    base_url="https://nex-global.risegen.ai/v1",
    api_key="{user_api_key from Family A}",
)
# model id from GET /v1/models
```

```bash
curl https://nex-global.risegen.ai/v1/chat/completions \
  -H "Authorization: Bearer {user_api_key}" \
  -H "Content-Type: application/json" \
  -d '{"model":"{id}","messages":[{"role":"user","content":"hello"}]}'
```

## Cursor

Settings → Models → override the OpenAI base URL to `https://nex-global.risegen.ai/v1`. API key from Family A. Add model ids from `GET /v1/models`. This matches Cursor's OpenAI-compatible override. The exact menu label can move.

## Codex CLI

In `~/.codex/config.toml`:

```toml
openai_base_url = "https://nex-global.risegen.ai/v1"
```

Do not invent other toml keys.

## Claude Code

Claude Code speaks the Anthropic Messages shape. Do not set `ANTHROPIC_BASE_URL` to the RiseGen OpenAI base. No Anthropic adapter was found for this gateway. The gateway path for Claude Code is not established. Do not invent a base URL.