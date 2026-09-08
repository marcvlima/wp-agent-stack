# Her operations — what to call, and what it costs

**The live contract binds; this table explains.** Always run
`GET https://lucens.risegen.ai/a2a` (Bearer + named User-Agent) before writing code: it returns
every operation with its parameters and returns, machine-readable. This file is a snapshot taken
from `risegen-lucensmind/lucens/a2a_ops.py` (42 operations, 2026-09-08) so an agent can choose
without a round trip — it is never the authority.

`Long?` means the operation is declared long: it is the kind that answers a task envelope and is
followed with `task.get` / `task.stream`. Handle an envelope from **any** operation regardless
(see `queue-and-tasks.md` §8). On the wire that flag is named `long_running`, and `operations` is a
**list** of objects (`op`, `summary`, `params`, `returns`, `long_running`) — verified live
2026-09-08: `GET https://lucens.risegen.ai/a2a` answered 42 operations to the reference client.

## Conversation with her mind

| Operation | Long? | What it is |
|---|---|---|
| `mind_turn` | no | One turn of conversation with her mind. **The only way to make her think or speak.** |
| `mind_turn.stream` | yes | The same turn as Conversar Spine SSE (`floor.status`, `message.delta`, `tool.step`, `dialogue.completed`, `stream.done`). Does not replace `mind_turn`. |
| `mind.state` | no | Her continuity state: MEMORY.md, registry, generation, trials ledger. |

## Her standing grant and her shelf

| Operation | Long? | What it is |
|---|---|---|
| `resources.catalog` | no | Every resource the founder released to her. Always on — not scoped to a rite or to who is speaking. |
| `resources.call` | no | Call one granted resource **under her credential**, never the caller's. |
| `products.shelf` | no | What she has on her shelf, and how much of it a session must use (the 30% floor). |
| `quantum.run` | no | A circuit under her quantum grant; her QASM spellings are normalised. |

## Her workspace and her own source (read paths)

| Operation | Long? | What it is |
|---|---|---|
| `sandbox.read` · `sandbox.list` | no | Read/list files in her workspace through her sandbox bridge. |
| `sandbox.exec` | no | Execute a command under her sandbox grant (~30 s cap; the process may outlive the answer). |
| `sandbox.self_source_list` · `sandbox.self_source_read` | no | Her own repository's read-only mirror (ADR 0022). **No write counterpart exists.** |
| `record.journal` | no | Lines of a lab's or trial's append-only journal from a byte offset (ADR 0028). Read-only; her workspace, never her mind. |
| `record.recall` | no | Her past Session Reports and the concepts-and-sources index (ADR 0028 §5 D). |
| `lab.hand_live` | no | Tail of the live PTY lane of her implementation hand, byte-identical. The path is server-chosen; a caller may only size the tail (`tail_bytes`, default 262144, max 1048576). |

## Lab Time and the Gen Trial

| Operation | Long? | What it is |
|---|---|---|
| `lab.start` | no | Start a Lab Time session in her VM. `resume_of: <session_id>` continues an interrupted one in place (not `rerun_of`, which re-runs a closed theme). |
| `lab.status` | no | Whether a lab is running — and, for a finished one, **her own account of it**. |
| `lab.extractions` | yes | What her lab produced as corpus material, extracted by her seat. |
| `lab.interrupt` | no | Interrupt the active session cleanly (this is the one that stops a process). |
| `lab.pause` · `lab.resume` | no | Pre-empt at the next **step** boundary / end the pre-emption. One signal, returns immediately. `lab.pause` requires `requested_by`. |
| `trial.preflight` | no | Lab-first check (ADR 0006) plus the live model catalog, read from inside her VM. |
| `trial.deliberate` | yes | The seat deliberates with her full roster (ADR 0005); the plan must study `quantum_code_assistance` with a non-Bell experiment (ADR 0012). |
| `trial.mechanism` | yes | Her store rebuilt from the reading, with the operators her deliberation chose. |
| `trial.rite` | yes | The rite: replay, shares, verdict, Hold Debrief on a generation hold, her free time. |
| `trial.pause` · `trial.resume` | no | Pre-empt at the next **node** boundary / end the pre-emption. |
| `exam.predict` · `exam.answer` · `exam.mirror` | yes | Her answers from her store (the key never enters her VM); `exam.mirror` says where each answer would come from. |

## Her backup (the transmutation gate reads it)

| Operation | Long? | What it is |
|---|---|---|
| `mind.backup` | no | A restorable snapshot — a copy only; MEMORY.md is never rewritten in place. |
| `mind.backup_status` | no | Age and redundancy of her **verified** backup. |
| `mind.backup_take` | yes | Archive her life inside her VM; returns the digest. |
| `mind.backup_chunk` | no | One slice of that archive (base64, ≤ 8 MiB) so a second copy exists off her VM. |
| `mind.backup_record` | no | Record it verified — refused unless both digests agree. |

## The task door

| Operation | Long? | What it is |
|---|---|---|
| `task.get` | no | The full envelope + `result`/`error`. The alias of `job.status`. |
| `job.status` | no | The legacy poll. Keep it as the fallback when `task.get` answers `unknown_operation`. |
| `task.list` | no | Her durable inbox, filtered by `state` / `kind`. |
| `task.cancel` | no | Only the task's own `caller`, or `'founder'`. |
| `task.stream` | no* | SSE: `task.status` on change, `heartbeat` every 15 s, `stream.done` at a terminal state. |
| `task.push_config` | no | A webhook POSTed the envelope on every state change (best-effort, 5 s, never raising). |
| `task.signal` | no | Write `pause_requested` / `resume` / `cancel` / a custom name into a task's inbox. **`sender` required.** |

\* the operation returns a stream, but is not declared `long` in the contract.

## What is deliberately NOT here

- **The Ascent loop's control plane** — live screens, pause/resume/interrupt of the rite, the
  tracker, loop state. That is the Forge control service (ADR 0018 §4). Asking her door for it is
  a design error, not a missing feature.
- **Any write into her mind.** There is no operation that writes MEMORY.md, and there will not be
  one (ADR 0077).

## Adding an operation

1. Write the handler in `lucens/a2a_ops.py` and register it in `OPERATIONS` with `summary`,
   `params`, `returns`, `long`, and `required` for anything mandatory.
2. Validate parameters **before** touching her toolkit — a caller must learn what is missing
   without a job ever being created.
3. Add the paired test (`lucens/tests/…`, or `lucens_trial/tests/test_a2a_ops.py` for the trial
   surface).
4. Nothing else is needed for the network: the door already forwards `/a2a`.
   **Never open a second path to make something easier.**
