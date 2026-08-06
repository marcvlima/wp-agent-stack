---
name: plan-fidelity
description: >
  Fail-closed plan fidelity for agent-driven development — when a plan is
  registered, implementation may only fulfill that plan; silent deviation is
  forbidden. Alternatives first; founder/dev reconciliation only when needed.
  Hooks enforce via plan-guard. Use when implementing from a plan, before
  commit/stop, when registering a plan, or after a plan-deviation escape.
---

# Plan Fidelity

**Mandate:** when a plan is **registered**, the plan is law. No plan detailing
and no implementation may deviate from requirements and directives explicitly
defined or approved by the **founder** or **human developer** without an
**explicit reconciliation** recorded on disk.

If a gap appears: **hunt alternatives that still fulfill the plan** first.
Only if impossible: **request** reconciliation — never self-approve.

Binary: `plan-guard` (`holding-central-ai-assets/plan-guard/`)  
Prior art: `quality-guard` (skill teaches; hooks enforce).  
Complements: `development-flow` (redeploy), `quality-enforcement` (tests).

## Agent procedure (when a plan is active) — NON-OPTIONAL

**FORBIDDEN:** silent descoping, “better idea” pivots, “skip this requirement”,
or treating the plan as optional. That is a process failure.

0. **Register** (after founder/dev approval of the plan):
   ```bash
   plan-guard register --plan docs/plans/<approved>.md --strict \
     --allow 'cmd/**,src/**'   # scope allowlist for strict_scope
   ```
1. **Implement only in-scope** paths that fulfill requirement IDs.
2. **Mark done** as requirements complete:
   `plan-guard mark-done --id REQ-001 --evidence 'test X green'`
3. **Never self-reconcile.** Draft only:
   `plan-guard request-reconcile --id REQ-001 --reason '…'`
4. **Founder/dev reconciles:**  
   `plan-guard reconcile --id REQ-001 --by founder --reason '…'`
5. **`plan-guard run`** (exit 0) then **`plan-guard status` → valid: YES**
6. Then quality-guard + rebuild/redeploy per `development-flow`.

## Hooks (v1.0+)

- **SessionStart:** mandate + active plan summary  
- **PreToolUse Edit/Write:** deny out-of-scope paths when `strict_scope: true`  
- **PreToolUse Bash commit:** deny without green plan-gate (when plan registered)  
- **Stop:** block when dirty work lacks green plan-gate  

Missing binary: PATH + `.risegen/plan-bootstrap.sh` + fail-closed install recipe.

## Install

```bash
cd /path/to/holding-central-ai-assets/plan-guard
go build -trimpath -o ~/.local/bin/plan-guard ./cmd/plan-guard
plan-guard install --repo /path/to/product-repo
# fleet:
# ./scripts/reconcile-plan-fidelity.sh --fleet-all --push
```

## Human override

- `PLAN_GUARD_OVERRIDE=<reason>` env (logged expectation: human only)  
- Reconcile CLI with `--by founder|dev` only  

## What this is not

- Not semantic LLM judgment that “code matches plan prose” (Phase B)  
- Not a substitute for quality-guard tests  
- Not active when no plan is registered (exploration allowed)
