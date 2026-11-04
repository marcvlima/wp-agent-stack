# 2026-08-05 — UI authored outside the design/brand SoT

**Category:** `authoring-without-sot-grounding`

## Failure card (ledger — the incident, not the rule)

- **Symptom:** agent generated a console UI prototype (connectors enrollment
  flow) with an invented visual identity — wrong accent color, generic dark
  chrome, ad-hoc components.
- **Claimed:** "grounded in brand" after peeking at one logo component in the
  consumer app.
- **True:** the governing design-system and brand-system repos were **already
  cloned as sibling checkouts** on the same machine, carrying tokens, core
  component CSS, and explicit non-negotiable laws (single accent, code-on-void,
  SVG-only icons, glass surfaces) plus a rule zero: "no UI is born or changed
  outside this system". The agent never searched for them before authoring.
- **Cost:** founder had to reject the artifact and order the repo cloned; full
  prototype rework.

## Generalized rule (what evolves)

**Before authoring ANY artifact governed by a system-of-record — UI/visual
artifacts (prototypes, mocks, HTML, components, slides), brand-touching copy,
or similarly governed outputs — the agent MUST first locate and consume the
governing system repositories: search sibling checkouts of the current repo's
parent directory and the organization's repo list for design-system/
brand-system (or equivalent SoT) repos, and consume their tokens/components/
laws directly (link or vendor with source commit). An artifact authored
outside its governing system is invalid by default — regenerate, do not patch.**

Detection: about to write HTML/CSS/visual mock + no design-token file loaded
in context → stop and search first.

## Action plan

- Matrix always-on: new NEVER line (see matrix-always-on.md item 8).
- Agency/design skills: Phase 0 grounding must include a **filesystem
  sibling-repo search** (parent dir + org repo list), not only the current
  repo's `.claude/skills`.
