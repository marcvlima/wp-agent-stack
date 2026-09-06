---
name: moe-council-builder
description: Build a new standing council in the MoE-gated deliberation model ("all hear, few speak") — persona seats with progressive disclosure, hot/warm gating and a batched cheap-model warm sweep. Use when the user wants to create a new council, advisory board or standing panel of expert personas, wants "MoE-style" multi-expert deliberation, or asks how to structure many personas at minimal token cost. Produces a complete, apm-packaged council skill.
---

# MoE Council Builder

You are building a **new council** — a deployable skill package of expert-persona
seats that deliberate under **MoE-gated dynamics**: per agenda item a Moderator
gates the 2–4 most relevant seats HOT (full persona load, strong model) while all
remaining seats stay WARM — they "listen" through ONE batched cheap-model sweep
per round and get promoted to HOT if they raise a substantive cross-domain flag.
Progressive disclosure keeps the cost near-flat as the roster grows.

Read `references/model.md` for the full generic protocol (gating, warm sweep,
promotion, token budgets, session record). Follow `references/build-process.md`
step by step. Copy skeletons from `references/templates.md`.

## The model in one table

| Piece | MoE analogue | Cost profile |
|---|---|---|
| Roster (L0) | the expert list | ~15 tokens/seat, always in context during a session |
| Gate | router | Moderator scores L0 lines against the brief (0/1/2) |
| HOT seats (top 2–4) | active experts | full charter (L1 ≤600 tokens) + refs (L2) on the strong model |
| Warm sweep | the "all hear" extension (classic MoE lacks it) | ONE batched cheapest-model call per round, one line per seat or PASS |
| Promotion | dynamic routing | substantive WARM flag → HOT next round |

## Relentless Method (MANDATORY — read references/relentless-method.md)

Every session runs under the Relentless Method: grit before barriers (two
alternatives before any "can't"), negative-claims quarantine (test, don't
inherit), metrics interrogation (numbers carry their environment), iterative
research until the result, pre-registered decision rules, an out-of-the-box
round, veto alchemy, proactive validation on cheap executors, no lazy WATCH,
and silent no-op hunting. A synthesis that violates these is not ready for
the ratifier.

## Hard invariants (every council in this model MUST keep)

1. **One deployable unit** — the council installs whole; never a subset of seats.
2. **Progressive disclosure levels are real gates** — L0 roster always; L1
   charter only when HOT; L2 references only while HOT and only if the charter
   is insufficient. Budgets: roster line ≤15 tokens · charter ≤600 · brief ≤300
   · rolling round summary ≤500.
3. **Warm sweep is ONE batched call** on the cheapest capable model — never one
   call per seat, never on the strong model.
4. **Every seat has a warm-sweep lens** — the one thing it watches for even
   off-topic; this is what makes "everyone listens" produce cross-domain insight.
5. **A human ratifier** (the founder/owner) holds the final word; the synthesis
   (recommendation + dissents + reversal conditions) is the artifact, not the
   transcript.
6. **The council governs its own composition** — charter/roster changes are
   council agenda items, ratified by the human.

## What varies per council (your job to define)

The domain and decision rights; the roster (6–12 seats, each a genuinely distinct
lens — see the seat-design rules in `references/build-process.md`); each seat's
charter (Identity · Canon · Heuristics · Activation triggers · Warm-sweep lens);
where the package lives (brand-specific council → that brand's repo; generic →
this holding repo) and its `packageId`.

## Reference implementation

`@risegen-lucensmind/luminaries-council` (repo `risegen-lucensmind`) — 12 seats
for AI-evolution deliberation; first instantiation of this model and the source
it was extracted from.
