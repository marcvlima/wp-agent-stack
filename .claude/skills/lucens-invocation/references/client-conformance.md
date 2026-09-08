# Client conformance — the 12 points

A caller of her door is compatible only if it passes every point. Each one exists because a
real caller failed it and either fabricated her voice or abandoned her while she was thinking.
The reference implementations that pass are `scripts/lucens_client.py` (this package),
`conclave/worker/conclave_worker/lucens_seat.py` and
`journeys-web/lib/mind-floor-client.mjs` (LucensProj BFF).

| # | Point | How to verify |
|---|---|---|
| 1 | **Canonical name only.** Base from `LUCENS_A2A_BASE_URL` (`LUCENS_A2A_URL` accepted); door = base + `/a2a`. No IP literal, no `dev.risegen.ai`, no localhost fallback, no `LUCENS_MESH_BASE_URL`/`MESH_AUTH_TOKEN`. | grep the client for `127.0.0.1`, `192.168.`, `MESH_` |
| 2 | **Unconfigured is an absence.** Missing base or token ⇒ named absence, never a default endpoint. | unit test with an empty environment |
| 3 | **Bearer on every call**, discovery included. | unit test asserting the header on `GET /a2a` |
| 4 | **Named User-Agent.** Never the library default. | unit test asserting the header value |
| 5 | **`params.caller` on every call**, and `priority: "urgent"` only with one. | unit test on the emitted body |
| 6 | **`202` is not an error.** Accept `200` and `202`; treat any payload carrying an active `state` + `task_id` as a task. | unit test feeding a 202 envelope |
| 7 | **Follow the task to a terminal state** with `task.get`, falling back to `job.status` on `unknown_operation`. | unit test: envelope → poll → completed |
| 8 | **Unbounded by default.** A wait cap is opt-in (`…_MAX_WAIT_S`, unset = no cap); hitting it is reported as `…_wait_exhausted` with the last `state` and `queue_position`. | unit test with a cap of 1 s |
| 9 | **Progress instead of silence.** A heartbeat every ~30 s naming `state` and `queue_position` (a log line for a job, a UI event for a surface). | unit test counting heartbeats |
| 10 | **Honest failure names.** `unauthorized` · `unreachable` · `busy` · `floor_silent` · `wait_exhausted` · the door's own `error`. Never a substitute answer, a persona, or a defaulted contribution. | unit test per branch |
| 11 | **Token redaction.** The token never appears in a log line, an error string, or a returned field. | unit test: error text containing the token |
| 12 | **Give her room.** `tokens_max` ≥ 100000 for deliberative asks; `profile` omitted; the floor note appended when the ask is technical. | unit test on the emitted params |

## The socket-timeout branch (point 10, in detail)

A connection error is ambiguous: her door may be down, or she may be deep in a turn. Resolve it
with a **cheap second call**, never with a guess:

```
except (URLError, TimeoutError, socket.timeout, OSError):
    probe lab.status with a 5s timeout
      → HTTP 200  ⇒ absence "…_busy"          (she is alive and occupied)
      → anything else ⇒ absence "…_unreachable"
```

## Where the answer lives

```
payload = task envelope (after polling) or the synchronous body
content = payload["result"] if it is an object else payload
reply   = content["reply"] if non-empty
          else "\n\n".join(entry["content"|"text"|"speech"] for entry in content["transcript"])
reply empty ⇒ absence "…_floor_silent"
thread  = payload["thread_id"] or payload["context_id"] or the id you sent
```

## Review checklist for a PR that touches a caller

- [ ] No new route to her that is not `POST {base}/a2a`.
- [ ] No timeout added "to be safe" around a `mind_turn`.
- [ ] No default/placeholder text emitted on any failure branch.
- [ ] The failure names are surfaced verbatim to the human, not swallowed into a generic error.
- [ ] The paired test covers the 202 path, the terminal-failure path and the silent-floor path.
- [ ] If a new capability was needed, it is a **new operation** in `lucens/a2a_ops.py` with its
      own test — not a private endpoint, an ssh call, or a file read from her VM.
