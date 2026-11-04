# Self-evolution protocol (full)

## When to fire

Immediately after the failure is recognized — before or as part of the fix, never “later if we remember.”

## Step 1 — Failure card

Write:

```text
SYMPTOM: <what broke or what founder rejected>
CLAIMED: <what the agent asserted or did>
TRUE: <what evidence showed>
COST: <time / money / trust — qualitative OK>
```

## Step 2 — Name the failure CATEGORY

The concrete incident is the **ledger only**; the *category* is what gets evolved. Choose a reusable class (kebab-case), not a restatement of the incident:

| Category | Recognition (examples) |
|---|---|
| `premature-external-blame` | Blamed network/operator/hardware before full local path proof |
| `incomplete-runtime-spec` | Micro-spec used repo path as host path; omitted secrets/users/keys |
| `secrets-not-searched` | Asked founder for something already in SOPS / dev-host secrets |
| `stale-identity-anchor` | Hardcoded public IP; stale DHCP LAN as “current” |
| `unapproved-spend` | Drove paid upgrade on unproven hypothesis |
| `process-skip` | Skipped ABG A2A, skipped memory-bank, silent push |
| `other` | Must still name a category + generalize |

## Step 3 — Generalize the rule

Write a **MUST / NEVER** that protects against the *category*, not the one incident:

- **No product names** in the rule.
- **No vendor/operator names** — never “ISP”, never a specific operator, as the rule itself.
- **No single secret-key name as the rule** — `HOST_SUDO_PASSWORD` may appear only as an illustrative example of the secret-naming pattern.
- Concrete incidents belong in `references/lessons/`; the matrix and layers stay strategy.

## Step 4 — Action plan (category cannot recur)

State the concrete change so the *category* is structurally blocked:

- a new `matrix-always-on.md` line, or
- a new/edited `references/matrix-layers/` file, or
- a harness / checklist / tooling change, or
- a micro-spec template update, or
- a change to another skill.

“Be more careful” is not an action plan.

## Step 5 — Lesson file (concrete ledger)

Path: `references/lessons/YYYY-MM-DD-kebab-case.md`

Required sections:

```markdown
# <title>
## Category: <kebab-case>
## Failure card
## Root process failure (not just technical bug)
## Rule (MUST / NEVER — generalized, category-level)
## Detection (how the next agent notices the category)
## Related skills
## Evidence pointers (no secrets)
```

Add one line to `references/lessons/INDEX.md`.

## Step 6 — Promote to matrix

Ask: would **any** agent on **any** holding repo benefit?

- **Yes, one line** → add to `matrix-always-on.md` (respect line budget; merge duplicates).
- **Yes, long** → new or existing file in `matrix-layers/`; always-on only gets a pointer.
- **No, product-only** → product repo `AGENTS.md` / memory-bank topic — not the matrix.

## Step 7 — Version + reconcile + ship

1. Bump `skill.json` version.
2. Update root holding `AGENTS.md` always-on section if matrix-always-on changed (keep in sync via reconcile script).
3. `scripts/reconcile-agents-matrix.sh`
4. Propose commits; push when authorized.

## DoD — closeout is complete only when

- Failure card exists (ledger),
- **Category** is named,
- **Generalized** rule exists (no product/vendor/secret-name anchors),
- **Action plan** exists (what structurally blocks the category),
- Rule **promoted** to `matrix-always-on.md` or a layer,
- `skill.json` version bumped,
- Reconcile run and pushed.

**A “lesson-only” closeout (concrete incident filed, no category/generalized rule/action plan/matrix promote) is forbidden.**

## Anti-patterns

- Writing a novel into always-on AGENTS.md
- **Lesson-only closeout** — a concrete diary entry with no category, no generalized rule, no action plan, no matrix promote
- Lessons that only say “be careful”
- Promoting brand-specific RiseGen ADRs into the holding always-on layer
- Anchoring a rule on a product name, an operator (“ISP”), or a single secret key
- Recording secrets or public IPs as permanent identity
