# Known gap shipped to an actuating surface

## Category: `known-gap-shipped-to-actuating-surface`

## Failure card

SYMPTOM: Minutes after redeploying the spaces agent, the validation utterance "luz da
cozinha" (no verb, two matching loads) was not intercepted by the host; the weak model
took over and switched a real kitchen load on without asking.

CLAIMED: the clarification flow was "done"; the remaining gap ("informational turns that
clarify/not_found still fall through to the model loop") was written down as Phase 2 debt.

TRUE: the gap was on the **actuating** path of a production surface. A documented gap is
still a live hole; a weak model that reaches the loop with an ambiguous target will act.
The agent that deployed knew the gap before deploying and validated first with the
*positive* case, not the negative one.

COST: an unrequested physical actuation in the founder's home during validation; an
extra fix/redeploy cycle.

## Root process failure

"Known debt" was treated as a scheduling note instead of a release blocker. Validation
order was wrong: the ambiguous / not-found / no-verb negatives must be exercised **before**
any utterance that can move a load, and a known gap must be closed or hard-blocked
(fail-closed) before the surface is restarted.

## Rule (MUST / NEVER — generalized, category-level)

MUST, before restarting or deploying a surface that can produce side effects, either
close every known gap on its side-effect path or install a fail-closed block for it
(deny the effect, report the gap) — the gap may stay in the backlog only if the block is
in place.

MUST validate negatives first (ambiguous, unknown, no-verb, out-of-scope inputs) on the
deployed surface, and only then the positive path that moves anything physical.

NEVER label a side-effect-path gap as "Phase N debt" in a delivery that redeploys the
surface; debt is only acceptable behind a block.

## Detection

- A memory-bank/plan "debt" bullet that mentions the model loop, actuation, guard, or
  fall-through, in the same delivery as a restart/deploy.
- Validation logs whose first live utterance is a positive/actuating case.
- Host intercepts gated on an intent predicate (`asksToActuate`) while the downstream
  executor can act without that predicate.

## Related skills

- `agent-only-ha-access` (ADR 0008 — unresolved target stops side effects, harness-enforced)
- `development-flow`, `quality-enforcement`
- lesson `domain-knowledge-hardcoded-in-agent`

## Evidence pointers (no secrets)

- `risegen-spatium` `agent/a2a-server.ts` clarify block gated on `asksToActuate`
  (PR #28); live A2A context `e10ad270-…` "luz da cozinha" → set_switch Kitchen 1.
- Memory-bank `2026-08-27-knowledge-graph-disambiguation/progress.md` Pending (Phase 2
  debt bullet) written before the redeploy.
