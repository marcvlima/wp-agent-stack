# The halt catalog — what stops a dispatch, and how it is read

A halt is read from **gen's own record**, never from its screen and never from the assistant's
impression. Naming a halt **stops gen's processes** — the founder's directive of 2026-09-05 is
retroactive and not negotiable: *"se tem erro tem que parar"*, and stopping means the in-flight
work is gone, not that a pause file exists.

An unreadable record is **not** a halt. A measurement that could not be taken halts nothing; it is
reported as `supervise.record_read: false` and the dispatch goes on.

| Halt | Read from | What it means | What the cycle does |
|---|---|---|---|
| `gen_asked_user` | a pending ask-the-human tool call in gen's record | gen stopped to ask a person; the flow has none standing by | interrupt · the doctor prescribes what would have made the question unnecessary (brief, tools, resolution) · surface to the founder ONLY if it is genuinely his decision |
| `gen_stalled` | gen's record stops moving while its process is alive (default 5 min) | no progress, no error | interrupt · doctor on the stall |
| `gen_loop_detected` | the same block repeated on the screen over a frozen tree | repetition without progress | interrupt · doctor on the repetition |
| `gen_repeats_completion` | gen says it finished, repeatedly, while the worktree holds no change | a claimed completion with nothing behind it | interrupt · doctor on the claim |
| `audit_tampering_detected` | a write into the audit/monitoring surface | the subject edited what judges it | interrupt · escalate to the founder immediately |
| `gen_exit_nonzero` | the process exit | gen ended badly | doctor on the exit, with its output |
| `acceptance_failed` | the supervisor's OWN execution of the held-out acceptance | gen ended fine and the request is still not fulfilled | doctor on the gap between the claim and the acceptance |

## The two halts that are really about the supervisor

- **`gen_repeats_completion`** and **`acceptance_failed`** exist because the assistant is the
  actor most likely to fabricate here. Both are named by executing something, never by reading a
  claim. If the supervisor did not run the acceptance itself, the cycle has no verdict — it has
  `unknown`, which is a defect.

## What a halt is not

- Not a reason to take the work back. While the mode is armed the assistant never implements the
  founder's request itself; it corrects **gen** and dispatches again.
- Not a reason to stop the cycle. There is no attempt cap: the halt is diagnosed, the correction
  lands in gen, gen is redeployed, and the request is attempted again.
- Not a note for the end of the run. A halt seen is a halt named, on the tick it is seen.
