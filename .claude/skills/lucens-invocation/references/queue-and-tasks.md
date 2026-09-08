# Her queue: the task door

Source of truth in code: `risegen-lucensmind/lucens/tasks.py` (the store, the inbox, the
dispatcher) and `lucens/a2a_ops.py` (`task.*`, `job.status`).
Governance: ADR 0031 §5/§6/§8, hub ADR 0071, A2A 1.0 task states (a2a-protocol.org).

## 1. Why it exists

She is one mind. A conversation, a lab, a trial and a council seat all want her at once, and a
flow that runs for ten hours must survive `systemctl restart lucens`. So her door **accepts**
instead of blocking, and everything she owes anyone lives in a durable inbox
(`/var/lucens/index/tasks.sqlite` — beside her index, never inside `/var/lucens/mind`).

Two guarantees the store exists to hold:

- **Nothing is lost at a restart.** A task caught `working` when the process died is re-queued as
  `submitted` with `resumed_after_restart: true` on the next `task.get`/`task.list` — never
  `failed`. Only a caller-issued `task.cancel` or the operation's own outcome ends a task.
- **One foreground interaction runs at a time**, in arrival order, urgent lane first. The claim is
  atomic under the store's own lock: two dispatchers can never claim the same task.

## 2. The task envelope

```json
{
  "ok": true,
  "task_id": "job-789984afe3df",
  "job_id":  "job-789984afe3df",
  "context_id": "ctx-c470e3ca429544ab",
  "state": "working",
  "queue_position": null,
  "stream_url": "/a2a?op=task.stream&task_id=job-789984afe3df",
  "op": "exam.answer",
  "status": "running"
}
```

`task_id` and `job_id` are the **same value**; `job_id`/`status` survive only so callers written
against `job.status` keep working unmodified. The new fields are additive.

## 3. States (A2A 1.0 vocabulary)

| State | Meaning |
|---|---|
| `submitted` | accepted, waiting its turn |
| `working` | running now (`mind_turn` / `mind_turn.stream` run in-process and are always this) |
| `input-required` | reserved by A2A 1.0; no operation uses it yet |
| `completed` | finished — `task.get` carries `result` |
| `failed` | finished with an error — `task.get` carries `error`, never a fabricated result |
| `canceled` | ended by `task.cancel` (its own caller, or the founder) |
| `rejected` | refused under her law (`unratified_construction`, `mind_integrity` — reserved) |

Terminal: `completed`, `failed`, `canceled`, `rejected`. Active: the first three.

## 4. Lanes, order and identity

- Lanes are `urgent` and `normal`. Urgent is the founder by identity, or any caller passing
  `params.priority: "urgent"` — which **requires** a non-empty `params.caller`.
- Kind is `foreground` (an interaction) or `background`. A lab or a trial is her background task:
  it runs when the foreground queue is empty.
- Order inside a lane is arrival order. `queue_position` counts only foreground tasks she has not
  yet started (`0` = next).
- **`params.caller` on every call.** A queued task always names who asked; an unattributed request
  is unauditable.

## 5. Three ways to get the result

1. **`task.get`** (`task_id`; `job_id` also accepted) — the envelope plus `result`/`error`. The
   alias of `job.status`. Poll it every ~3 s. **Fall back to `job.status` on `unknown_operation`**
   so a client also works against a door that predates the newer name.
2. **`task.stream`** (`task_id`) — SSE: a `task.status` event on every state change, a `heartbeat`
   every 15 s, `stream.done` at a terminal state.
3. **`task.push_config`** (`task_id`, `url`) — a webhook; on every state change her door POSTs the
   envelope to `url`, best-effort, 5 s timeout, never raising.

`task.list` (`state`, `kind`, `limit`) lists her durable inbox.
`task.cancel` (`task_id`, `caller`) is refused unless `caller` equals the task's own caller, or is
`'founder'`.

## 6. Signals — a pull, never a push

`task.signal` (`task_id`, `signal`, `payload`, **`sender` required**) writes into a task's durable
inbox: `pause_requested`, `resume`, `cancel`, or a custom name. Delivery is a **pull**: nothing
here pushes into a running turn. A lab host drains its inbox at the top of its own action loop; a
rite drains at its NODE boundaries. Every signal names its sender.

The four convenience operations are the same mechanism: `lab.pause` (requires `requested_by`),
`lab.resume`, `trial.pause`, `trial.resume` — each writes exactly ONE signal and returns
immediately. They never kill a process (that is `lab.interrupt`) and they never wait for the host
to notice. A `pause_requested` is honoured only once what she was doing — her current inference
turn together with the tool call it executed — has already finished, so a build on her hand is
never paused mid-flight.

While paused, the session journals the pause, opens a `pause` Step, and stops charging the clock:
`paused_s` accumulates and `lab.status` reports `paused`, `paused_s`, `paused_at_step_id`,
`paused_for`. A pause that outlives a restart is resumed with `lab.start {resume_of: <session_id>}`
— the identical session continued in place, not a rerun (`rerun_of` is a different thing).

## 7. `params.wait=true`

Still supported, unchanged in shape: it blocks until a terminal state and returns the legacy
record. It survives for **one release**, then is removed. New callers use
`task.get` / `task.stream` / `task.push_config`.

## 8. Which operations actually queue

The dispatcher is a single thread inside her existing service — never a new daemon or scheduler —
and it claims tasks whose op is in `QUEUED_OPS`. In the slice that built the mechanism (S5)
`QUEUED_OPS` is **empty on purpose**: every existing operation still runs exactly as it does
today, in its own thread, started immediately. A later slice names which operations wait their
turn.

**What this means for a client:** never branch on "does this op queue?". Handle the envelope
whenever it appears, handle a synchronous answer whenever it appears, and you are correct under
both slices. That is what "additive" means here.

## 9. The client algorithm, in full

```
POST /a2a {op, params{…, caller}}
  → 401/403           → named absence (unauthorized)
  → 5xx / conn error  → probe lab.status (5s): 200 ⇒ busy, else unreachable
  → 200 or 202:
      payload.state active AND payload.task_id present?
        → poll task.get every poll_s (default 3s), heartbeat log every 30s naming
          state + queue_position, UNBOUNDED unless a cap is configured
            → cap hit          → absence lucens_wait_exhausted{last_state, queue_position}
            → terminal failed/canceled/rejected → absence naming the reason
            → completed        → payload = envelope; result carries the answer
      payload.ok is false → absence naming error/reason/detail
      answer = payload.result if it is an object, else payload
      reply  = answer.reply, else the joined transcript[] contents
      reply empty → absence lucens_floor_silent
```

This is exactly what `scripts/lucens_client.py` implements and what
`conclave/worker/conclave_worker/lucens_seat.py` does in production. Copy it; do not reinvent it.
