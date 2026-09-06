# Build process — creating a new MoE-gated council

Eight steps. Do them in order; each has a gate.

## 1. Define domain and decision rights

One sentence: what class of decisions does this council deliberate, and **who
ratifies** (a named human). No ratifier → no council.
*Gate:* the sentence exists and the ratifier agreed.

## 2. Decide where it lives

Brand- or product-specific council → that organization's repo. Generic across
the holding's organizations → `holding-central-ai-assets`. `packageId` follows
the home: `@<repo>/<council-name>`.
*Gate:* home repo chosen and consistent with its charter.

## 3. Design the roster (6–12 seats)

Seat-design rules:

- Each seat is a **genuinely distinct lens** — if two seats would argue alike on
  most agenda items, merge them.
- Prefer lenses that *conflict productively* (e.g. open-endedness vs.
  evaluation rigor); consensus-by-construction is a wasted council.
- Name seats by lens (`causality-evaluation`), never by person.
- 6 is the floor (below that, just consult ad hoc); 12 the practical ceiling
  (the gate still works above it, but charter maintenance decays).
- Reserved seats (foreseen but empty) are allowed — list them in the roster as
  reserved.
- Every seat gets an L0 line ≤15 tokens: `**<slug>** — <lens>`.

*Gate:* roster reviewed by the ratifier; no two seats collapse into one.

## 4. Write the charters (≤600 tokens each)

Use the template in `templates.md`. Five sections, all mandatory:
**Identity** (who the persona is, in its field's own terms) · **Canon** (the
lineages/authors/works it thinks with — real ones) · **Heuristics** (how it
judges: 4–6 sharp, falsifiable rules, not platitudes) · **Activation triggers**
(when the Moderator should gate it HOT) · **Warm-sweep lens** (the ONE thing it
watches for even off-topic).
*Gate:* every charter fits the budget and its heuristics would produce different
advice than any other seat's.

## 5. Assemble the package

```text
<council-name>/
├── SKILL.md            ← Moderator protocol (from templates.md; council-specific
├── skill.json             frontmatter description with the roster summarized)
└── references/
    ├── roster.md
    ├── seats/<slug>/charter.md
    ├── session-brief.md
    ├── warm-sweep.md
    └── relentless-method.md  ← copied verbatim from any canonical council skill (mandatory)
```

*Gate:* the package installs as one unit (`cp -r` into `.claude/skills/`) and
the skill triggers on its description.

## 6. Write `skill.json`

Skeleton in `templates.md`. Schema `schema.apm.dev/skill/v1.0.0`, semver from
`1.0.0`, `documents` mapping roster/brief/sweep, `directories.references`.
*Gate:* valid JSON, packageId matches the home repo.

## 7. Pilot with measurement

Run ONE real agenda item end to end. Record the session record (gating table,
promotions, synthesis) AND the token-spend estimate vs. a naive all-seats-hot
baseline. The pilot is the acceptance test of both the roster (did the right
seats gate hot? did any warm flag surface an insight?) and the budgets.
*Gate:* ratifier reviews the pilot synthesis and the cost delta.

## 8. Governance from day one

- Charter/roster changes are council agenda items, ratified by the human.
- Version-bump `skill.json` on every change (patch wording / minor new seat or
  capability / major protocol break).
- Keep the evolution hook (model.md §Evolution) logging from the first session.

## Anti-patterns (reject these during review)

- A seat that is a job title with no canon or falsifiable heuristics.
- Warm sweep implemented as N calls, or on the strong model.
- Charters that summarize the domain instead of taking positions in it.
- A council without a ratifier, or one whose synthesis is a transcript.
- Skipping the pilot measurement ("it obviously saves tokens" — prove it).
