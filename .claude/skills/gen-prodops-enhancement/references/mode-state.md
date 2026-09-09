# The state on disk — why the mode is not kept in your context

Lucens named the failure mode of a thin supervisor protocol: **supervisory drift** — *"without the
rigid state-transitions of a LoopProgram, the assistant might forget it is in enhancement mode,
treating a gen failure as a simple error to be bypassed"*. The Agentic Development Council's
`harness-agent-loop` seat named the same rule from the other side: loop state lives in the harness,
serialized per session, never re-inferred from the transcript.

So the mode is a file.

```
<repo>/.risegen/gpe-mode/state.json
{
  "armed": true,
  "armed_at": "2026-09-08T22:41:03Z",
  "repo": "/home/…/risegen-lucensmind",
  "gen": {"version": "…", "sha256": "…", "path": "…"},
  "cycles": [
    {
      "id": "gpe-…",
      "request": "<the founder's words, verbatim>",
      "acceptance": {"command": "…", "declared_at": "…", "held_out": true},
      "attempts": [
        {"n": 1, "worktree": "…", "session_id": "…", "facts": {…},
         "halt": "gen_stalled", "cause": "…", "correction": {"commit": "…", "redeployed": true}}
      ],
      "outcome": "new_attempt"
    }
  ]
}
```

## The rules of the file

- **Read it at the start of every turn while armed.** If it says armed, you do not implement.
- **Write a fact when it is measured**, not when it is expected. `pending` is honest; a fact
  written ahead of its measurement is the beginning of a fabricated close.
- **Never edit it to make an audit pass.** A guard denial is an input to the founder, never an
  obstacle to route around; rewriting the state a harness reads is the one thing this mode may
  never do.
- The file is per repository, and it is not a ledger: the durable record of what the doctor
  prescribed lives in the shared Evolution Ledger, where the engine put it.
