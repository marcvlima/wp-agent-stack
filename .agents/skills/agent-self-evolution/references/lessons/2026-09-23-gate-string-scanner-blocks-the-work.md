# 2026-09-23 — An enforcement gate that scans strings blocks the work it protects

**Category:** `gate-string-scanner-false-positives`

## Failure card

- **Symptom:** Every agent in the holding (Claude Code, gen, Grok, Cursor) reports the ABG
  gate as slow and error-prone. In a 30-day corpus of 1,116 sessions the guard denied 110
  actions; 18 of them were read-only commands (`env | sed 's/…/=<x>/'`, `grep '>>>>>>>'`,
  `python3 -c` writing to the scratchpad); `ABG_GUARD_OVERRIDE` was used 106 times (74 for
  read-only work); 20 % of A2A calls failed; registering one task cost 9 tool calls, 4 denies
  and ~10 turns before any product mutation.
- **Claimed:** the gate protects product mutations at millisecond cost with < 2 % false
  positives; the skill (409 lines, 23 rules) makes first attempts succeed.
- **True:** the classifier byte-scanned the raw command for `>` and substring-matched
  protected paths (`pkg/guard/policy.go:56-81, :282-296`), so any `>` inside a grep/sed
  pattern or a heredoc was a "write"; the deny recipe was four steps and three network calls;
  the skill contradicted the validator (200 vs 350–800 chars, ops that return `400 unknown
  op`, a "GraphQL fast path" that does not exist in code); every real `set_status` returned
  a false 422 because a board-mirror mutation failed after the label had already landed.
  Record: `risegen-agentic-backlog-gate/memory-bank/abg-fast-path/brainstorms/2026-09-22-abg-bottleneck/record.md`.
- **Cost:** ~16.5 min of pure gate latency to close one feature (33 writes × ~30 s), habitual
  overrides that void the gate, duplicate trees created on retry, agents abandoning the door
  for raw `gh`, and the founder's trust in every gate in the holding.

## Generalized rule

**An enforcement gate classifies by parsing intent, never by scanning the command string;
a read-only or scratch-scoped action is never denied; every deny message is one copy-paste
command that completes the registration; every false positive becomes a permanent fixture
the gate's tests must pass; and a contract an agent must follow is generated from the code
that enforces it, never hand-written beside it.** A gate whose recipe has more than one step,
whose classifier has no fixture corpus, or whose prose disagrees with its validator is a
throughput defect first and a policy second.

Detection: a deny on a command whose first token is a read verb (`ls`, `cat`, `grep`, `sed`
without `-i`, `env`, `printenv`, `echo`, `find`, `curl` GET); an override reason that names a
read-only action; a Stop hook that blocks a session whose dirty set contains no production
surface; a skill rule count that grows release over release; a documented op that the live
service answers with "unknown op".

## Action plan

- Matrix always-on MUST line added (below): "Gates parse intent; deny recipes are one command;
  false positives become fixtures; contracts are generated from the enforcing code."
- ABG remediation WP-A…E (executable spec `docs/plans/2026-09-23-abg-fast-path-executable-spec.md`):
  board-mirror never fails a transition; guard classifier on `mvdan.cc/sh` AST with the 18+3
  false positives as fixtures; `abg-guard start` / `abg-guard done` one-command recipe; per-node
  index; generated one-screen skill v3.0.0 + JSON schema + typed client; SLO instruments.
- Reconcile this card and the matrix line into every holding repo with the standard sync.
