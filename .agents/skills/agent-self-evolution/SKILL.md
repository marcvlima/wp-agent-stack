---
name: agent-self-evolution
description: MANDATORY after any agent/code-assistant failure or founder correction — record a durable lesson, evolve the holding AGENTS matrix (progressive disclosure), reconcile into all holding repos. Required default skill on every new repository. Use when an agent was wrong, a plan path was incomplete, a false diagnosis cost money/time, or the founder says the agent failed.
---

# Agent Self-Evolution

**Trigger (NON-NEGOTIABLE):** any of:
- Founder corrects the agent on a load-bearing fact or process
- False diagnosis / premature “root cause” that drove real cost
- Incomplete micro-spec that forced human intervention (wrong host paths, missing secrets)
- Plan or prompt that violated a known holding rule
- Agent asked the founder for something already in secrets / inventory / runbook

**Do not wait** for “please update the skill.” Closing the incident without this skill is incomplete.

## Progressive disclosure (token budget)

| Load when | File |
|---|---|
| **Always** (every session) | Holding matrix stub in repo `AGENTS.md` → points here + always-on rules only |
| **On error / this skill** | This `SKILL.md` (you are here) |
| **Executing the loop** | `references/protocol.md` |
| **Writing matrix text** | `references/matrix-always-on.md` + only the layer you touch |
| **Reconciling repos** | `references/reconcile.md` + `scripts/reconcile-agents-matrix.sh` |
| **Prior art** | `references/lessons/INDEX.md` then **one** lesson file |

Do **not** dump all layers into the prompt. Matrix always-on stays short; detail lives in `references/` and lessons.

## The loop — category-level strategy, not just a diary (summary — details in protocol.md)

1. **Failure card** (concrete) — symptom + claimed + true + cost. This is the **ledger only**: the concrete incident does **not** become the rule.
2. **Name the failure CATEGORY** — a reusable class, e.g. `premature-external-blame`, `incomplete-runtime-spec`, `secrets-not-searched`, `stale-identity-anchor`, `unapproved-spend`, `process-skip`. The category is what gets evolved, never the single incident.
3. **Generalize** the rule — a MUST/NEVER with **no product names, no vendor/operator names (no “ISP”), no single secret-key name** (except as an illustrative example of a *pattern*).
4. **Action plan** — what must change so the **category** cannot recur: matrix always-on line, a `references/matrix-layers/` file, harness/checklist change, micro-spec template, or another skill.
5. **Promote** the abstract rule → `references/matrix-always-on.md` (≤ ~40 short lines — hard budget) and/or a dedicated layer under `references/matrix-layers/`.
6. **Write a lesson** under `references/lessons/YYYY-MM-DD-kebab.md` + row in `references/lessons/INDEX.md` (concrete evidence + detection for the category).
7. **Bump** this skill `version` in `skill.json` (patch for new lesson/rule; minor if matrix always-on changes).
8. **Reconcile**: run `scripts/reconcile-agents-matrix.sh` (or follow `references/reconcile.md`) so product repos get the skill + matrix stub.
9. **Commit/push** holding-central-ai-assets first, then consumer repos (founder-authorized).

**A closeout that only files a concrete incident (“lesson-only”) is incomplete** — it must name the category, generalize the rule, carry an action plan, and promote to the matrix. That is the difference between a diary and strategy.

## Hard rules for the matrix

- **English** artifacts only.
- **No product-specific** RiseGen-only procedures in the always-on matrix (those stay in product `AGENTS.md`).
- **No public IP literals** as current WAN identity; use stable hostnames / runtime discovery.
- **No secrets** in lessons (redact passwords, tokens).
- Prefer **one-line MUST + pointer** over essays in always-on.

## Default on new repositories

Every new holding / RiseGen / sister-brand repo **must** ship with:
1. This skill installed via APM (`marcvlima/holding-central-ai-assets/agent-self-evolution`)
2. An `AGENTS.md` that includes the **Holding matrix** block (see `references/matrix-always-on.md` embed)
3. `CLAUDE.md` → `@AGENTS.md` only (or equivalent import)

Scaffold checklist: `references/reconcile.md` § New repo.

## Complements (do not duplicate)

| Skill | Role |
|---|---|
| `research-before-asserting` | Gate before claiming a cause |
| conclave brainstorm | Floor names the searches; host runs them and returns raw findings; fix the condition not the instance (lesson 2026-09-01) |
| `mandatory-soft-skills-for-agents` | Posture under hard problems |
| `memory-bank` | Per-topic volatile work memory |
| `development-flow` | Rebuild/redeploy after shared infra changes |
| `rise-flow` | Branch/worktree drift discipline |
| `sops-age-secrets` | Secrets in git |

Self-evolution **records** when those skills were violated and **hardens** the matrix so the next agent cannot miss the rule.
