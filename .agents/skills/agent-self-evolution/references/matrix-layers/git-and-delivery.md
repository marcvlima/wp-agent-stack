# Layer — git and delivery

## MUST

1. Founder-authorized commits; session/agent trailers when the project requires them.
2. After platform/connector/edge changes: rebuild/redeploy before asking humans to test (`development-flow`).
3. Pre-flight drift (`rise-flow`) before large work.
4. Status vocabulary: `ideation` · `in progress` · `refining` · `done` — **done** only with pending list empty or cancelled with reason.
5. An authorized change is delivered only when the remote default branch contains it. Detector, before the turn ends: `git ls-remote origin refs/heads/<default>` names a commit that contains the paths the turn changed. A green gate, a staged index, a side worktree, or a published artifact built before that commit does not satisfy the detector (category `delivery-left-off-default-branch`).

## NEVER

- Silent `git push` of secrets.
- Closing ABG/feature **done** while SKIPs that are in-scope remain without owner tasks.
