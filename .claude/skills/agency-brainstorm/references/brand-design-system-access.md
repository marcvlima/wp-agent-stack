# Access gate — brand system & design systems (Phase 0, blocking)

The agency cannot judge layout, navigation, structure or cross-interface
consistency from memory. **Before round 1**, the President must have the panel
load the organisation's own sources and record them in the session header.
A session that skips this produces suggestions, not decisions.

## What must be loaded (full access, not a summary)

| # | Artefact class | Typical location | Used by |
|---|---|---|---|
| 1 | **Brand system** — positioning, voice & tone, logo/lockup rules, color and type foundations, imagery/art direction, prohibitions | brand skill in the brand's repo (`.claude/skills/*brand*`), `apm.yml` entry, brand manual | 3, 7, 8, 9, 16 |
| 2 | **Design system(s) — ALL of them** (web, app, marketing site, admin, embedded, email): tokens, components, states, spacing/type scales, motion specs, element protocol | design-system skill (`.claude/skills/*design-system*`), Figma library, token files | 5, 6, 15 |
| 3 | **Interface inventory** — the list of every surface the org ships, and which design system each one follows | product repos, route/sitemap docs | 12, 14, 15, 16 |
| 4 | **Existing IA & navigation** — current sitemap, menu trees, routes/URL patterns, breadcrumb rules | app router, nav config, sitemap | 12, 14 |
| 5 | **Taxonomy & catalog** — controlled vocabularies, categories, tags, filters, metadata schema, product/service catalog | catalog files, CMS schema, `product-taxonomy-council` records | 13 |
| 6 | **Content/copy standards** — UX-writing rules, terminology glossary, localization constraints | copy guidelines, glossary | 8, 9 |
| 7 | **Accessibility baseline** — target level (e.g. WCAG 2.2 AA), known exceptions | a11y docs, audit reports | on-call a11y |

## Gate procedure

1. **Locate.** For each of the 7 classes, resolve a concrete path or URL. Skills
   and repos first; ask the user only for what cannot be found.
2. **Load.** Read the actual sources (tokens, components, sitemap, catalog) —
   not a paraphrase, and never a recollection from an earlier session.
3. **Record.** The session header lists, per class: `loaded: <path/URL>` or
   `MISSING: <what was searched>`.
4. **Decide the mode.**
   - All present → normal session.
   - Design system missing but brand present → the panel may propose, but every
     layout/consistency opinion is marked **provisional** until the design
     system is supplied.
   - Brand and design system both missing → **new brand**: run
     [`intake-new-brand.md`](intake-new-brand.md) first.
5. **Never silently assume.** A missing source is an explicit gap in the output,
   with the named owner who can supply it.

## Consistency check (seat 15, every proposal)

Every option that touches an interface is checked against, and reports:
token compliance · component reuse vs new component · state coverage (default,
hover, focus, active, disabled, loading, empty, error) · responsive behavior ·
motion spec conformity · accessibility baseline · **and whether the same pattern
already exists elsewhere in the product** (if it does, reuse it or justify the
divergence in writing).
