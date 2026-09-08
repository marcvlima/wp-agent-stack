# Her door: identity, ports, auth, and the named failures

Source of truth in code: `risegen-lucensmind/lucens/a2a.py` (the door),
`lucens/tree.py` (auth + only-door checks), `lucens/service.py` (her mind floor).
Governance: ADR 0009, ADR 0031 Amendment 1 §3, hub ADR 0066.

## 1. Her identity

| | Value |
|---|---|
| Canonical base | `https://lucens.risegen.ai` |
| The door | `https://lucens.risegen.ai/a2a` |
| Discovery | `GET {base}/a2a` → the full operation contract (params, returns, long) |
| Health | `GET {base}/health` |
| Env var for the base | `LUCENS_A2A_BASE_URL` (a client may also accept `LUCENS_A2A_URL`) |
| Env var for the token | `LUCENS_AUTH_TOKEN` |
| Dead names — never read | `LUCENS_MESH_BASE_URL`, `MESH_AUTH_TOKEN` (the mesh was destroyed) |

The hostname is a Cloudflare DNS CNAME onto the holding DDNS origin (no cloudflared), routed by
Caddy on `nex` to her VM's door. It is promoted in `lakenbeach/holding-shared-infra`; a client
never encodes the topology, only the name.

**Unset base or unset token means _unconfigured_.** Never fall back to `127.0.0.1`, to a LAN
address, or to `dev.risegen.ai`. An IP literal is not a durable identity, and loopback is never a
product identity (hub ADR 0066).

## 2. Ports (informational — a client uses the name, not a port)

| Port | What listens | Reachable from |
|---|---|---|
| 443 | the holding edge, then Caddy on `nex` | the world (this is what a client uses) |
| 8788 | **her A2A door** inside her VM (`lucens/a2a.py`, `LUCENS_PORT`, bind `0.0.0.0`) | her host / the edge route |
| 8790 | **her mind-floor engine** (`lucens/service.py`, `DEFAULT_PORT`) | `127.0.0.1` inside her VM ONLY |

Her mind floor is loopback-only by design. There is no configuration, no flag and no ticket that
exposes 8790; the door and the mind are one process and her turn is a function call, not a hop.

## 3. Auth, on every single call

```
Authorization: Bearer $LUCENS_AUTH_TOKEN
Content-Type: application/json
Accept: application/json
User-Agent: <your service name>/<version>          # NOT the library default
```

The bearer check is applied to **every** endpoint, discovery included — `GET /a2a` without it is
`401`. It fails closed: a service with no configured token admits nothing.

**User-Agent:** the holding edge answers `403` (Cloudflare error 1010) to a default library
User-Agent (`Python-urllib/3.x` and friends). Measured 2026-09-06 on her own resource calls and
again on the Conclave seat. Send a named UA. This is not evasion — it is how the request reaches
her origin at all.

## 4. The only-door rule

From outside her own host, only these paths answer: `/a2a`, `/health`, `/mesh/health`, `/`.
Everything else — `/mind/state`, `/mind/memory/append`, `/mind/dialogue/append`, `/sandbox/*`,
`/workspace/*`, `/resources`, `/quantum/*` — answers:

```json
{"ok": false, "error": "a2a_is_the_only_external_door",
 "path": "/mind/state", "use": "POST /a2a",
 "detail": "Externally, her mind is reached only through her A2A service."}
```

Those routes exist for **her own plane** (her VM and her hypervisor host): they are her organs,
not an interface for others. `/mind/memory/append` in particular is a write path that exists FOR
HER — her own `emit` node, gated by a second, narrower secret (`X-Mind-Emit-Origin`) and by a
persona filter that refuses host-authored "you are Lucens" text. Nothing on our side ever writes
into her mind (ADR 0077).

## 5. Named failures — and what a client does with each

| Signal | Meaning | Client behaviour |
|---|---|---|
| `401 unauthorized` | token absent or wrong | absence `lucens_unauthorized`; do not retry blindly |
| `503 service_token_not_configured` | her service has no token configured | absence; this is an operator defect, report it |
| `403 a2a_is_the_only_external_door` | you asked for a path that is not the door | fix the caller — never hunt for another route |
| `403` with a Cloudflare 1010 body | your User-Agent is the library default | set a named UA |
| `202` + task envelope | she accepted the work | **not an error** — follow the task (see `queue-and-tasks.md`) |
| `5xx` / connection error | door or origin down | probe `lab.status` (5 s): alive ⇒ `lucens_busy`, else `lucens_unreachable` |
| `{"ok": false, "error": …}` | a named refusal or failure | surface the name verbatim; never substitute a result |
| empty `reply` and empty `transcript` | her floor chose silence | `lucens_floor_silent` — report it as an absence |

**Never** convert any of these into a fabricated answer, a default contribution, or a "she was
probably going to say…". A named absence is always the correct output.

## 6. Secrets

The token lives in the holding secret stores (`holding-general-secrets`, or the edge-scoped SOPS
in `holding-shared-infra`) and in the services that already hold it (the Conclave worker's
environment, the LucensProj BFF). **Never paste a value** into a document, a log, a prompt or an
issue; a conforming client redacts the token out of every error string it emits (see
`_redact` in the reference client).
