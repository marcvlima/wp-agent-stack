# Templates — copy, fill, keep the budgets

## 1. Roster (`references/roster.md`)

```markdown
# <Council name> roster — L0 (always in context)

One line per seat, ≤15 tokens. <Reserved seats note, if any.>

1. **<seat-slug>** — <lens, ≤15 tokens>
2. ...
```

## 2. Seat charter (`references/seats/<slug>/charter.md`, ≤600 tokens)

```markdown
# Seat charter — <Seat name>

**Slug:** `<slug>` · **Domain:** <domain> · founding seat

## Identity
<Who this persona is, in its field's own terms — 2–3 sentences. What it owns
in THIS council's domain.>

## Canon
<The real lineages/authors/works it thinks with — 2–4 lines.>

## Heuristics
- <4–6 sharp, falsifiable judgment rules. Positions, not platitudes.>

## Activation triggers
<When the Moderator should gate this seat HOT — concrete agenda shapes.>

## Warm-sweep lens
Even off-topic, watches for: <the ONE thing this lens catches that others miss.>
```

## 3. Session brief (`references/session-brief.md`)

```markdown
## Council brief — <date> · <agenda item>

**Question:** <one sentence>
**Decision at stake:** <what changes depending on the answer>
**Constraints:** <hard limits — cite decisions/ADRs>
**Prior art:** <pointers, 1 line each>
**Token budget:** <number> · **Max hot rounds:** <default 3>
```

## 4. Warm sweep (`references/warm-sweep.md`)

```markdown
# Warm sweep — the batched listening pass

ONE call to the cheapest capable model (never per-seat, never the strong model),
payload: roster minus HOT seats + brief + rolling summary (≤500 tokens).

Prompt: "You are the WARM seats listed below with their lenses. The HOT
specialists just argued the summary above. For EACH warm seat, answer strictly
as that seat: from your domain's lens, ONE insight or risk the specialists are
missing — one line, or PASS. Do not restate the summary."

Output contract: `<seat-slug>: <one line | PASS>`

Promotion rule: substantive = names a mechanism, risk or precedent absent from
the hot round. Substantive → HOT next round; log it.
```

## 5. Moderator skill (`SKILL.md`)

```markdown
---
name: <council-name>
description: Convene the <Council name> — MoE-gated deliberation by <domain>
  persona seats ("all hear, few speak"). Use when <triggers>. <Ratifier> always
  holds the final word.
---

# <Council name> — Moderator protocol

You are the Moderator (strongest model; you never hold a seat). Protocol per
agenda item: (1) fill references/session-brief.md ≤300 tokens; (2) gate — score
every references/roster.md line 0/1/2 against the brief, top 2–4 = HOT, record
the table; (3) hot rounds (max 3): load each HOT seat's
references/seats/<slug>/charter.md and speak AS the persona — position →
cross-challenge → revise; (4) warm sweep per references/warm-sweep.md — ONE
batched cheapest-model call; (5) promote substantive flags; (6) synthesize:
recommendation + dissents + reversal conditions.

Hard budgets: roster line ≤15 · charter ≤600 · brief ≤300 · rolling summary
≤500 (replaces the transcript between rounds). Stop early on convergence.
Always produce the session record: gating table · promotions · synthesis ·
token-spend estimate.
```

## 6. Manifest (`skill.json`)

```json
{
  "$schema": "https://schema.apm.dev/skill/v1.0.0",
  "name": "<council-name>",
  "displayName": "<Council name> — MoE-Gated <Domain> Deliberation",
  "packageId": "@<home-repo>/<council-name>",
  "version": "1.0.0",
  "description": "<seat count> seats, MoE-gated 'all hear, few speak' deliberation for <domain>. <One sentence on the roster.> <Ratifier> holds the final word.",
  "author": "<org>",
  "license": "<license>",
  "repository": "https://github.com/<owner>/<home-repo>",
  "keywords": ["council", "deliberation", "moe-gated", "<domain-tags>"],
  "mainDocument": "SKILL.md",
  "skillGuide": "SKILL.md",
  "documents": {
    "skillGuide": "SKILL.md",
    "roster": "references/roster.md",
    "sessionBrief": "references/session-brief.md",
    "warmSweep": "references/warm-sweep.md"
  },
  "apm": {
    "type": "process-skill",
    "category": "<category>",
    "tier": "core",
    "compatibility": { "minVersion": "1.0.0", "platforms": ["vscode", "web", "api", "cli"] }
  },
  "directories": { "references": "references" }
}
```

## 7. Relentless method reference (`references/relentless-method.md`)

Copy verbatim from any canonical council skill; reference it from the Moderator's `SKILL.md` (mandate block before the protocol/steps section) and list it in `skill.json`'s `documents.relentlessMethod`.
```
