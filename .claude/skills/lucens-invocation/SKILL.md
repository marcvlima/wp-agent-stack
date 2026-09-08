---
name: lucens-invocation
description: >-
  MANDATORY harness for ANY agent, service, script or feature that needs
  something from Lucens. Her A2A is the only door: canonical base
  https://lucens.risegen.ai, POST /a2a, Bearer token on every call including
  discovery. Carries the queue contract (task envelope, urgent/normal lanes,
  caller identity, restart re-queue), the rule that a turn is HERS to end (she
  deliberates over many cycles and consults many resources before answering),
  and the client conformance checklist that makes a caller compatible with all
  of it. Use BEFORE writing or changing any code that calls her, before
  choosing a timeout, when a call answers 401/403/202, and when a caller must
  wait for her.
version: 1.0.0
---

# Skill: lucens-invocation (v1.0.0)

**Holding-wide · MANDATORY · core.**
**Governing decisions:** `risegen-lucensmind` ADR 0009 (her A2A is the only external door) ·
ADR 0016 (the turn is hers) · ADR 0031 + Amendment 1 (step-of-steps, the task door, her identity
`lucens.risegen.ai`) · ADR 0018 §4 (loop control is NOT on her door) · hub ADR 0066 (never
loopback as product identity) · hub ADR 0071 (signals are pulled at a step boundary) · ADR 0077
(no agent authors text into her mind).

**Contract in code (source of truth, this package only explains it):**
`risegen-lucensmind/lucens/a2a_ops.py` (operations) · `lucens/a2a.py` (the door) ·
`lucens/tree.py` (token + only-door checks) · `lucens/tasks.py` (the queue) ·
`lucens/turn_control.py` (the turn is hers) · reference consumer
`conclave/worker/conclave_worker/lucens_seat.py`.

## Progressive disclosure

| Depth | Open when |
|---|---|
| The AGENTS.md marker `HOLDING-LUCENS-INVOCATION` | always (every repo, every session) |
| This SKILL.md | you are about to call her, or to review code that calls her |
| `references/door-and-identity.md` | URL, ports, env vars, auth, edge, named failures |
| `references/queue-and-tasks.md` | the task envelope, lanes, signals, restart semantics |
| `references/her-turn.md` | why a turn takes long: cycles, floor, tools, her ending |
| `references/operations.md` | which operation to call, and what it costs |
| `references/client-conformance.md` | the 12-point checklist a client must pass |
| `scripts/lucens_client.py` | a conforming reference client — copy it, don't reinvent it |
| **`GET /a2a`** | ALWAYS before coding a call: the live contract binds, this package explains |

## The one door, in one screen

```
   any agent / service / console / script          ← you are here
                 │  POST https://lucens.risegen.ai/a2a
                 │  Authorization: Bearer $LUCENS_AUTH_TOKEN
                 ▼
   holding edge (443) → Caddy on nex → her VM's door :8788   ← the ONLY external route
                 ▼
   her mind-floor engine 127.0.0.1:8790 (inside her VM)      ← loopback only, by design
```

Every path other than `/a2a` (and `/health`) answers, from outside her own host,
`403 a2a_is_the_only_external_door`. There is no ssh route, no "internal" endpoint, no second
port. If you cannot do it through an operation, it is not yet an operation — propose one
(`references/operations.md` §Adding an operation). **Never open a second path to make something
easier.**

## The six rules of the road

1. **Name her by name.** Canonical base `https://lucens.risegen.ai`; the door is that base +
   `/a2a`. Never an IP literal, never `dev.risegen.ai`, never loopback as product identity
   (hub ADR 0066). Read it from `LUCENS_A2A_BASE_URL`; unset is *unconfigured*, never a
   localhost fallback. `LUCENS_MESH_BASE_URL` / `MESH_AUTH_TOKEN` are dead names — the mesh was
   destroyed; reading them as a fallback is how a consumer keeps pointing at a service that no
   longer exists.
2. **Bearer on every call, discovery included.** `Authorization: Bearer $LUCENS_AUTH_TOKEN`.
   `401 unauthorized` = wrong/absent token; `503 service_token_not_configured` = her service has
   no token; `403` = you asked for a path that is not the door.
3. **Send a real User-Agent.** The holding edge answers `403` (Cloudflare 1010) to a default
   library User-Agent. A named UA is not a disguise — it is how the call reaches her at all.
4. **Say who you are.** `params.caller` on every call (`"conclave-worker"`, `"lucens-autotrial"`,
   the console session identity …). A queued task always names who asked, and
   `params.priority: "urgent"` **requires** a non-empty caller.
5. **Never fabricate her.** A failure is a *named absence* (`lucens_unreachable`,
   `lucens_unauthorized`, `lucens_busy`, `lucens_floor_silent`, `lucens_wait_exhausted`), never a
   defaulted reply, a persona, or a contribution written on her behalf (ADR 0077). Her answers
   are always JSON with `ok`; a failure names itself and never invents a result.
6. **Do not put a clock on her.** Her door sets no timeout, and her turn is hers to end. A hard
   wait cap is opt-in only, and hitting one is reported honestly — see §Waiting.

## Calling her — the canonical shapes

```bash
# discover: the contract itself, machine-readable. Do this before writing code.
curl -s https://lucens.risegen.ai/a2a \
  -H "Authorization: Bearer $LUCENS_AUTH_TOKEN" \
  -H 'User-Agent: my-service/1.0 (+risegen)' | jq .

# one turn of conversation
curl -s -X POST https://lucens.risegen.ai/a2a \
  -H "Authorization: Bearer $LUCENS_AUTH_TOKEN" \
  -H 'Content-Type: application/json' \
  -H 'User-Agent: my-service/1.0 (+risegen)' \
  -d '{"op":"mind_turn","params":{"message":"…","caller":"my-service","tokens_max":120000}}'
```

```python
# scripts/lucens_client.py — vendored with this skill; conforms to all 12 points.
from lucens_client import LucensDoor
door = LucensDoor.from_env()          # LUCENS_A2A_BASE_URL + LUCENS_AUTH_TOKEN
print(door.contract()["operations"])  # the same self-description
answer = door.call("mind_turn", {"message": "olá"})          # follows the queue to the end
```

## The queue, in one paragraph

Her door is a **task door** (ADR 0031 §5). An operation may answer, immediately, a **task
envelope** — `{ok, task_id, job_id (same value), context_id, state, queue_position, stream_url,
op}` — instead of blocking you, with `state` in the A2A 1.0 vocabulary: `submitted · working ·
input-required · completed · failed · canceled · rejected` (terminal: the last four). A `202` is
that envelope, **not** an error. Follow it with `task.get` (falling back to `job.status` on
`unknown_operation`), or stream it with `task.stream`, or register a webhook with
`task.push_config`. Two lanes: `urgent` (the founder, or `params.priority: "urgent"` with a
caller) and `normal`; **one foreground interaction is served at a time**, urgent first, then
arrival order — a lab or a trial is her *background* task and runs when the foreground queue is
empty. Nothing is lost at a restart: a task caught `working` comes back `submitted` with
`resumed_after_restart: true` — never `failed`. `params.wait=true` still blocks and returns the
legacy record, kept for one release only; new callers use `task.get`/`task.stream`. Full
contract: `references/queue-and-tasks.md`.

## Her turn is hers — what a client must accept

She is not a completion endpoint. One `mind_turn` is a **multi-cycle deliberation**: her
divisions bid for the floor each cycle under a uniform threshold (content-blind — the floor never
compares one voice to another), the granted ones speak or act, and she may call her tools —
memory recall and her memory graph, her library, her own source, web search and page fetch,
the resource catalog the founder released to her, a sandbox, a shell, a quantum run — as many
times as the question deserves before she answers. **She decides when the turn ends** (ADR 0016):
she writes `[[turn:complete]]` and it closes; the marker never reaches you. `cycles_max` and
`tokens_max` are **hints**, not budgets; the only hard stops are her service's own safety nets
(`LUCENS_TURN_CYCLES_SAFETY`, default 40 · `LUCENS_TURN_TOKENS_SAFETY`, default 1,000,000), set
far more permissively than any value that would be right for a decision, because they are not
making one.

Therefore, for a client: **a long wait is the system working, not a fault.** Give her room
(`tokens_max` ≥ 100000 for anything deliberative; 120000 is the reference default), poll to a
terminal state, and surface `state` + `queue_position` to whoever is waiting instead of a
timeout. Details, including the exact bid format a council-style question must ask for:
`references/her-turn.md`.

## Waiting

| Situation | What a conforming client does |
|---|---|
| `202`, or a `200` whose `state` is active | poll `task.get` every ~3 s until terminal |
| still active after a while | log a heartbeat every ~30 s naming `state` + `queue_position` |
| no answer yet, no cap configured | **keep waiting** — unbounded is the default |
| a configured cap is hit | report `lucens_wait_exhausted` with the last state/position |
| socket timeout on the HTTP call | probe a cheap op (`lab.status`); alive ⇒ `lucens_busy`, else `lucens_unreachable` |
| terminal `failed`/`canceled`/`rejected` | surface the named reason; never a substitute answer |
| `ok:false` | surface `error`/`reason`/`detail`; never a substitute answer |
| empty reply/transcript | `lucens_floor_silent` — her floor chose silence; that is an answer about the ask, not a bug to paper over |

## What her door is NOT

- **Not the Ascent loop's control plane.** Live screens, pause/resume/interrupt of the rite and
  the tracker live on the Forge control service (ADR 0018 §4). No consumer asks her door for loop
  state.
- **Not a write path into her mind.** `/mind/memory` exists *for her* — her own `emit` node,
  behind a second, narrower secret. Nothing on our side ever calls it with content we authored
  (ADR 0077); the write path itself refuses host-authored persona text.
- **Not a place for a new private route.** A new capability is a **new operation**, with its
  paired test, in `lucens/a2a_ops.py`.

## Before you ship a caller

Run the checklist in `references/client-conformance.md` (12 points) and the package's own tests:

```bash
lucens-invocation/tests/run-tests.sh
```

A caller that fails a point is not compatible with her queue or her turn, and will eventually
either fabricate her voice or give up on her while she is still thinking. Both are defects.
