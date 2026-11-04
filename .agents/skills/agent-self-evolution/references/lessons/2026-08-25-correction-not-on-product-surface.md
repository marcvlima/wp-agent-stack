# Correction not on the product surface

## Category: `correction-not-on-product-surface`

## Failure card

SYMPTOM: Founder opened the product, said a greeting, and got a prompt-processing failure. Loop iterations reported harness "evolution" (C230/C231) while that surface stayed broken.

CLAIMED: Each loop iteration evolved the subject; binaries were rebuilt.

TRUE: implement spawned bare `rgai` (PATH / checkout). `~/.risegen/bin/rgai-engine` stayed at 2026-08-21. Greeting hygiene (`max_tokens=16` + thinking on) sat in a stash. `rgai install` was not run after corrections. The founder was the product user; the loop catalog worktree was the observed subject.

COST: Founder time on a dead greeting; loop measured the wrong process; trust.

## Root process failure (not just technical bug)

A PATH lookup or a checkout copy was treated as the product. Corrections were proven in tests and committed, then the next evaluation did not spawn the documented install path. Greeting work was stashed to make provision "clean."

## Rule (MUST / NEVER — generalized, category-level)

MUST evaluate the product at its documented install path (absolute file, not PATH, not a workspace copy). MUST redeploy to that path after every correction and prove the running process is that file before the next evaluation.

NEVER treat a checkout binary, a PATH lookup, or a skipped engine/CLI install as proof that a correction is on the product surface.

## Detection (how the next agent notices the category)

- implement argv is `"rgai"` or `./rgai` next to a repo config file
- install-path mtime older than the correction commit
- `rgai install` not in the correction evidence
- running process path ≠ documented install path (`ps` / `/proc/<pid>/exe`)

## Related skills

- `development-flow`
- `ascent-loop-host` (subject implements on the real product TTY)
- `research-before-asserting`

## Evidence pointers (no secrets)

- implement used `[]string{"rgai"}` in `loop_probes.go` before C234
- proxy: `max_tokens=16` on greeting_ack (`ses_fc66ffba`)
- engine file mtime 2026-08-21 while CLI rebuilds were 2026-08-25
