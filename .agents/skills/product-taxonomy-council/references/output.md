# The deliverable — format of a council session

A session produces one document with six parts. Keep it decision-grade: honest trade-offs, verified facts, no faked confidence. State the **execution mode** used (delegated / in-context) and the **round count** at the top (exactly 2 — diverge, then converge; a 3rd only for a foundational family/platform restructure, with the reason recorded). Include the captured **system/business brief** the proposals were judged against, and — on a re-run — **what was previously rejected and why** (to show new proposals are fresh, not anchored).

## 1. Brief & grounding (short)

- **Decision:** the exact structural, navigation, or naming question and the definition of "good" (success criteria, target users, platform boundaries, expected lifespan).
- **Room:** the roles convened (and why that sizing).
- **Grounding facts:** locked routes/names/families (sitemaps + catalog + brand + prior ADRs) + current-state facts, each tagged **verified** (source) or **assumed** (flagged risk).

## 2. Structural & naming decision

```
### Decision — <chosen structure, navigation architecture, or name>
Type: <Platform Hierarchy | Navigation/Menu Architecture | Taxonomy/Metadata Schema | Product/Service Naming>
Family / Root: <the parent family, domain, or route root this belongs to>
Rationale: <one paragraph — why this structure/name, tied to grounding facts, user mental models, and research>

Assessment (ten lenses):
  - 1. Distinctiveness & Orthogonality:      …
  - 2. Information Scent & Findability:      … (labels clearly indicate destination)
  - 3. Cognitive Depth & Hierarchy Balance:  … (depth ≤ 3–4 levels, balanced breadth)
  - 4. Menu Architecture & Ergonomics:       … (desktop/mobile layout, mega-menu/sidebar behavior, wayfinding)
  - 5. Taxonomy & Metadata Rigor:            … (backstage facets, controlled vocabulary, SKOS alignment)
  - 6. Verbal-Identity & Labeling Clarity:   … (unambiguous, tone fit, zero filler jargon)
  - 7. Brand-Architecture & Ecosystem Fit:   … (matches branded house / endorsed model, anti-sprawl)
  - 8. Developer & Technical Coherence:      … (URL slug hierarchy, API/CLI namespace, route tree)
  - 9. Reversibility & Migration Impact:     cheap to change | costly to change — … (redirects, user disruption)
  - 10. Governance & Scalability:            … (extensibility for future features/SKUs)
```

## 3. Sitemap & navigation hierarchy specification

Provide the concrete tree diagram and menu component mapping:

```
### Sitemap / Hierarchy Tree (ASCII or Mermaid)
Root (/)
├── [Section / Global Tab 1] (/section-1)
│   ├── [Category / Subnav A] (/section-1/category-a)
│   │   ├── [Item / View 1] (/section-1/category-a/item-1)
│   │   └── [Item / View 2] (/section-1/category-a/item-2)
│   └── [Category / Subnav B] (/section-1/category-b)
└── [Section / Global Tab 2] (/section-2)
    └── [Direct View] (/section-2/view)
```

**Navigation & Menu Mapping:**
- **Primary / Global Navigation:** <items shown in top bar / root rail>
- **Secondary / Local Navigation:** <sidebar / nested drawer / sub-tab breakdown>
- **Contextual / Utility Navigation:** <action menus, profile, settings, contextual drawers>
- **Mobile Responsive Mapping:** <bottom tabs, hamburger drawer layout, sheet progression>
- **Breadcrumb Path:** `<Root> > <Section> > <Category> > <Item>`
- **Wayfinding & Active State:** <how "you are here" is visually and semantically conveyed (`aria-current`)>

## 4. Taxonomy, controlled vocabulary & metadata schema (if applicable)

The backstage classification schema powering search, filtering, and content relationships:

| Category / Facet Name | Allowed Values / Controlled Terms | Relationships (Parent/Child/Associated) | Metadata Tag / Key |
|---|---|---|---|
| | | | |

## 5. Alternatives considered

For each alternative seriously debated:

```
### Alternative — <name / structure>
Why it was in contention: <one line>
Why it lost: <the decisive lens or fact>
```

Alternatives must be **genuinely differentiated** finalists. If two candidates collapse under stress-testing into the same trade-off, say so and drop one.

## 6. Catalog entries, consistency checks & ADR-ready record

**Catalog Row(s) to Add or Update:**

| Field | Value |
|---|---|
| Name / Structure | |
| Family / Route | |
| Type (platform / section / product / service / feature) | |
| Status (proposed / active / deprecated) | |
| Description / Scope | |
| Technical Identifier(s) (Route / API / CLI / Package) | |
| Aliases / Do-Not-Use | |
| Supersedes (if any) | |

**Consistency Checks:**
- **Sitemap & Collision Check:** no overlapping routes, colliding categories, or duplicate family names.
- **Information Scent & Usability Check:** labels tested against user mental models; no jargon dumping grounds.
- **Accessibility & Landmark Check:** landmarks defined (`<nav>`, `<main>`, `<aside>`), keyboard accessible, ARIA states defined.
- **Technical URL & Namespace Check:** RESTful slug hierarchy clean, API/CLI patterns adhere to ecosystem conventions.
- **Legal & Brand Voice Flag:** verbal identity cleared, trademark/domain risks flagged if applicable.

**ADR-Ready Decision (drop-in for `docs/decisions/`):**
```
# NNNN — <title>
Status: proposed
Context: <what forced the structural, navigation, or naming decision>
Decision: <the chosen structure, sitemap tree, navigation architecture, or name>
Why: <rationale + the key trade-off vs the strongest alternative>
Consequences: <benefits, trade-offs, migration/redirect plan, what it supersedes>
```

For a **weighty/irreversible** fork (breaking URL restructure, primary navigation redesign, renaming a shipped product), the Chair hands the recommendation to the **founder** and **waits** — it does not execute destructively unasked.

