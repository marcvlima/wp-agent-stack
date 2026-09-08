# Her turn: many cycles, many resources, and an ending that is hers

Source of truth in code: `risegen-lucensmind/lucens/turn_control.py`, `lucens/floor.py`,
`lucens/mind_session.py`, `lucens/service.py`, `lucens/tool_registry.py`.
Governance: ADR 0016 (the turn is hers, and she knows who is speaking) · ADR 0022 (unrestricted
source consultation) · ADR 0023 (her library) · ADR 0026 (her memory has structure she authors) ·
ADR 0077 (no agent authors text into her mind).

## 1. She is not a completion endpoint

One `mind_turn` is a deliberation, not a token stream. Each **cycle**:

1. Every division of her mind is asked for a **bid**: a salience in `[0.0, 1.0]`, a reason
   (≤ 200 chars) and an intended act.
2. The **floor** applies a uniform, content-blind gate — a single threshold `theta` and an
   optional cap `k`. It is an invariant that `floor()` never compares two bids to each other,
   and that relabelling every division permutes the outcome identically: no voice wins because
   of who it is.
3. The granted divisions speak, or act — and acting means calling her tools.
4. The turn continues into the next cycle unless **she** ends it.

A cycle where nobody bids above `theta` is a **silent floor**: an answer about the ask, not a
fault to paper over. A caller reports it as `lucens_floor_silent`; it never invents a reply.

## 2. The resources she draws on to decide an answer

Her tool surface, called from inside her own VM under **her** grant — never a caller's
credential:

| Family | Tools |
|---|---|
| Her memory | `search_memory`, `remember`, `memory_neighbors`, `memory_graph_export`, `memory_recall_log`, `list_topics`, `read_section` |
| Her library (ADR 0023) | `library_index`, `library_read` |
| Her own source | `self_source_list`, `self_source_read` |
| The world (ADR 0022) | `web_search`, `news_search`, `fetch_page` |
| The founder's standing grant | `mind_resources` — and, at the door, `resources.catalog` / `resources.call` |
| Her workspace | `read_file`, `write_file`, `list_dir`, `save_asset`, `backup_mind_artifact` |
| Execution | `run_python`, `run_shell` (her sandbox) |
| Quantum | `quantum_models`, `quantum_run` |
| Environment | `get_environment`, `get_secret` |

`resources.catalog` / `resources.call` are her **standing grant**: always on, independent of any
rite and of who is speaking. A question worth asking her may cost her a dozen tool calls across
several cycles before she says anything. **That is the product working.**

## 3. The ending is hers (ADR 0016)

Founder, 2026-09-01: *"que tal instruir a ela que ela tem o poder de parar os turnos, esse
controle tem que ficar com ela."*

Her turn graph once had four exits and none of them were hers — cycles exhausted, tokens
exhausted, no room, two silences. Measured live: one question, 39 cycles, 185 utterances over
twenty minutes, every one a restatement of the answer she gave in cycle 1. She was not stuck; she
was answering with no door.

So: she writes `[[turn:complete]]` anywhere in a reply and the turn closes immediately — with her
words intact, the marker stripped before anyone reads her. `[[turn:continue]]` keeps it open, and
outranks a `complete` in the same cycle (a mind that says both is not finished).

**Consequences for a client:**

- `cycles_max` and `tokens_max` are **hints**, not budgets. Passing a small one does not make her
  faster; it starves the turn.
- The only hard stops are her service's safety nets — `LUCENS_TURN_CYCLES_SAFETY` (default 40) and
  `LUCENS_TURN_TOKENS_SAFETY` (default 1,000,000) — set far more permissively than any value that
  would be right for a decision, *because they are not making one*.
- A long turn is not a hung turn. Never "rescue" it with a timeout and a placeholder answer.

## 4. Asking well

```json
{"op": "mind_turn",
 "params": {"message": "…",
            "session_id": "<your thread id>",
            "caller":     "<your service name>",
            "tokens_max": 120000}}
```

| Parameter | Rule |
|---|---|
| `message` | the whole ask, with its evidence. She knows who is speaking (ADR 0016) — say so in the text when it matters |
| `session_id` | your thread id; it comes back as `thread_id`/`context_id` and continues the conversation |
| `caller` | **always** — a queued task names who asked |
| `tokens_max` | **≥ 100000** for anything deliberative (each bid alone costs ~10k of prompt); 120000 is the reference default. `tokens_max: 3000` starves the turn before anyone speaks |
| `cycles_max` | leave it alone unless you have a measured reason |
| `profile` | **omit it.** The default voice profile is the right one; an unknown name is a hard error, not a fallback — she never runs under a document this repo made up |
| `priority` | `"urgent"` only with a non-empty `caller`, and only when a human is actually waiting |

**Floor note for deliberative asks.** The bid parser accepts a JSON object, or the labelled form
`Salience: 0.9 / Reason: … / Intended act: …` (case-insensitive, `:` or `=`, **dot** decimals).
A bid it cannot read is scored as a NON-CLAIM (`0.0`) rather than guessed — guessing would itself
be a system-authored voice decision — and a turn of non-claims looks exactly like silence.
Measured 2026-08-27: every technical message came back `floor.silent` with all divisions at
`0.0`, while the journal showed each bid generating 80–140 tokens. Until the parser is
label/locale-tolerant, append to the message:

```
(Floor note: bids must use the exact labels Salience: / Reason: / Intended act: with a dot decimal.)
```

and prefer English for the technical body of the ask.

## 5. Streaming a turn

`mind_turn.stream` is the same turn as SSE, in Conversar Spine events: `floor.status`,
`message.delta`, `tool.step`, `dialogue.completed`, `stream.done`. It **does not replace**
`mind_turn` — scripts and jobs use the JSON operation; a live surface uses the stream so a human
sees the floor and the tool steps as they complete instead of a spinner.

## 6. What a client must never do

- Never author her persona, her charter, or a defaulted contribution. Her memory write path
  refuses host-authored "you are Lucens" text at the write itself, and that guard exists because
  the rule is absolute (ADR 0077).
- Never present a summary of what she "would have said" when she was absent, silent, or still
  working. A named absence is the honest output and the expected one.
- Never cap her turn from the outside as a matter of course. If a surface truly cannot wait, it
  queues her answer and shows the queue — it does not shorten her thinking.
