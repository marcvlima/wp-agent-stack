# Authorized work stayed off the default branch

## Category: delivery-left-off-default-branch

## Failure card

SYMPTOM: The requester said the change should already be on the default branch.
CLAIMED: The change was delivered because it was implemented, tested, and published from a side worktree.
TRUE: Both default branches still pointed at the parent commits. The change existed only as a staged index in side worktrees. The published artifact's receipt named that parent.
COST: A correction turn, and a published build whose source was not yet the branch people pull.

## Root process failure (not just technical bug)

The agent treated a green gate and a published binary as the end of the turn. Landing on the default branch was left as a later step that still needed a separate ask. Authorization to build and publish already included authorization to land.

## Rule (MUST / NEVER — generalized, category-level)

MUST: Once the requester has authorized a change, the same turn commits it and pushes the default branch of every repository the change touches. Before the turn ends, the remote default-branch ref contains the change.

NEVER: End that turn with the change only in a worktree, the index, or a side branch. A green gate, a staged index, or a published artifact built from uncommitted files is not delivery.

## Detection (how the next agent notices the category)

Before ending a turn the requester treated as delivery, compare `git rev-parse <default>` with `git ls-remote origin refs/heads/<default>` and confirm that commit contains the paths the turn changed. If the remote default branch does not, the turn is not done. A handoff that says "uncommitted" after the requester asked for the result is this category.

## Related skills

- `agent-self-evolution` (this lesson)
- `quality-enforcement` (the gate is a prerequisite of the commit, not a substitute for it)
- `rise-flow` (which branch is the default, and where the checkout sits)

## Evidence pointers (no secrets)

- Requester correction, 2026-10-14: the delivered change was still only on side worktrees.
- Remote default branches after the correction: one repository `396da1b` then docs `0329ec9`; the other `ff2fc60`.
- The published artifact's embedded receipt still named the parent commit, because the artifact was built before the commit.
