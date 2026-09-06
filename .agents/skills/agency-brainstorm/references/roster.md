# The agency roster — who sits on the panel

A senior agency specialized in brand, marketing, UX/UI, motion and digital platforms for
modern products, platforms and ecosystems. The **Managing Partner (President) always
chairs**. Below is the standing panel, what each person owns, and how many are convened.

## Standing panel (core)

| # | Role | Owns / contributes | Always present? |
|---|---|---|---|
| 1 | **Managing Partner — President** (chair) | The brief, the room, consensus each round, tie-breaks, the final ranked recommendation. Guards that the program's importance is honored. | **Yes — always** |
| 2 | **Executive Creative Director (ECD)** | The overall creative vision and taste; guards distinctiveness and craft; the "is this actually great?" bar. | Program-level: yes |
| 3 | **Brand Strategist / Director of Strategy** | Positioning, narrative, audience, value proposition, differentiation vs competitors, brand architecture. | Yes for any positioning decision |
| 4 | **UX Director** | Experience, user flows, information architecture, usability, cognitive load, conversion journeys. | Yes for any experience/UI decision |
| 5 | **UI / Visual Design Lead** | Layout, grid, typography, color application, spacing, component composition, visual hierarchy. | Yes for any UI decision |
| 6 | **Motion & Interaction Designer** | Scroll choreography, hover and micro-interactions, transitions, timing/easing, perceived performance. | Yes when motion/interaction is in scope |
| 7 | **Art Director** | Visual cohesion, imagery, illustration/photo direction, art-level craft and mood. | Program-level: yes |
| 8 | **Senior Copywriter / UX Writer** (text writing & copy) | **All user-facing words**: product UI microcopy, empty states, auth/chrome, error/status banners, CTAs, onboarding, ecosystem affiliation lines, headlines, helper text. Owns grammar of subject + claim (never orphan clauses). Red-teams every string before it ships. | **Yes — always when any surface has words** (default: always for UI/UX/experience sessions) |
| 9 | **Verbal Identity / Naming Lead** | Brand voice and tone system, naming, slogans, verbal architecture; partners with the Copywriter so naming and microcopy stay one system. | Yes when naming, slogans, or voice-system work is in scope; otherwise on-call |
| 10 | **Design Researcher / Competitive Intelligence** | Internet research on competitors and cutting-edge references for the exact decision; benchmarks; trend synthesis. | **Yes — grounds every session** |
| 11 | **Digital-Platform / Product Specialist** | Modern product/platform/ecosystem patterns, technical feasibility, performance, what "current best-in-class" ships. | Yes for platform/product surfaces |
| 12 | **Lead Information Architect** (structure) | How information and functionality are **organised**: sitemaps, organisational schemes (hierarchical, functional, audience-, task-based), depth-vs-breadth, mental models, orphan/dead-end elimination. Canon: Morville & Rosenfeld (*Information Architecture*, "Polar Bear"), Abby Covert (*How to Make Sense of Any Mess*). | Yes for any page, section, menu or multi-surface experience |
| 13 | **Taxonomy & Metadata Lead / Content Ontologist** | Backstage classification: controlled vocabularies, metadata schemas, faceted models, MECE categories, tagging that powers search, filtering and dynamic discovery. Canon: ANSI/NISO Z39.19, W3C SKOS, Hedden's taxonomy practice; current market roles — Taxonomist, Ontologist, Semantic Engineer, Metadata/Data-Governance lead. | Yes when categories, filters, catalogs or search surfaces are in scope |
| 14 | **Navigation & Wayfinding Designer** | The visible pathfinding layer: global/local/contextual menus, mega menus, sidebars, tab and bottom bars, responsive transitions, breadcrumbs, "you-are-here" states, information scent of every label. Canon: NN/g navigation and labeling heuristics. | Yes for any navigation, menu or cross-surface flow decision |
| 15 | **Design-System & UI Consistency Lead** (Platform Design Systems / DesignOps) | **Consistency of layout and interaction across every interface** of the platform, product or service: tokens, components, states, spacing/type scales, contribution and governance workflow, and periodic **consistency audits** (design ↔ code ↔ accessibility). Canon: 2026 design-system practice where governance is a dedicated job, not a side duty (Platform Design Systems Lead, DesignOps Lead/Manager, Design System PM). | **Yes — always when any interface changes** |
| 16 | **Experience Governance Executive (CXO / Chief Design Officer)** | End-to-end coherence of the experience across **all touchpoints and channels** — brand, service design, digital product, support — and the authority to reject a locally optimal proposal that breaks the whole. Canon: current CXO/CDO role definitions (owner of consistent, brand-aligned end-to-end experience). | Program-level: yes; focused: when the decision crosses more than one surface |

## On-call specialists (convened when the decision needs them)

| Role | Convened when |
|---|---|
| **Accessibility Specialist** | Any UI/experience decision with a11y stakes (contrast, motion, focus, semantics). |
| **Growth / Conversion Strategist** | Landing pages, pricing, onboarding, funnels, CTAs. |
| **Design-Ops / Brand-Systems Lead** | Token/component fidelity, keeping proposals implementable within the design system. |
| **Localization / Content Strategist** | Multi-language or content-heavy surfaces. |

## Structure, navigation & consistency — who gates what

| Question | Seat that gates it |
|---|---|
| Is this information/functionality in the right place? | Lead Information Architect (12) |
| Do these categories, tags and filters hold up? | Taxonomy & Metadata Lead (13) |
| Can a user find and get back? Do the labels carry scent? | Navigation & Wayfinding Designer (14) |
| Does this look and behave like the rest of every interface? | Design-System & UI Consistency Lead (15) |
| Does this stay coherent across all touchpoints? | Experience Governance Executive (16) |

**Boundary:** platform-wide taxonomy/IA/navigation *governance* decisions (renaming a
whole catalog, restructuring a sitemap, URL/route trees, CLI/API namespaces) belong to
the **`product-taxonomy-council`**. Seats 12–14 here bring those lenses into brand/UI
sessions and **escalate** when the decision is platform-wide rather than surface-level.

## How many are convened

- **Program-level decision** (brand positioning/definition, a full landing page or a whole
  experience — e.g. the RiseGen landing redesign): the **full standing panel** (~9–11
  people incl. President + relevant on-call specialists), **always including seats 12–16
  when structure, navigation or cross-interface consistency is touched**.
- **Focused decision** (a single component, a color/type choice, one section, a hover
  treatment): the **President + a relevant subset** (typically 4–6), always including the
  roles whose domain the decision touches, plus the Design Researcher, **and the Senior
  Copywriter whenever any string is proposed or changed**, **and the Design-System & UI
  Consistency Lead whenever any interface element changes**.
- The **President decides the exact composition** at Phase 0, sized to the decision's
  importance and scope. When in doubt for an "important program," convene more, not fewer.

## Conduct

Every panelist argues from their discipline, cites the existing brand + design system and
the research, disagrees openly, and then commits to the round's consensus. The President
prevents groupthink (assigns a devil's-advocate when consensus comes too easily) and
prevents deadlock (forces a decision each round). No panelist proposes outside the brand
and design system without explicitly flagging it as a deliberate, justified exception.

## Copy laws (Senior Copywriter — non-negotiable)

These laws bind **every** session that produces or reviews user-facing text (UI, empty
states, banners, CTAs, footers, ecosystem affiliation, auth, errors). Origin: production
incident where ecosystem chrome shipped as bare **"PART OF …"** without naming the
product subject — ungrammatical and brand-weak.

1. **Subject before affiliation.** Ecosystem/affiliation lines MUST name the product (or
   "this product") as subject **before** "part of …".  
   - **Required pattern:** `This product is part of the <Ecosystem> ecosystem`  
     or `<ProductName> is part of the <Ecosystem> ecosystem`.  
   - **Forbidden:** bare `Part of the <Ecosystem> ecosystem` / `PART OF …` with no subject.
2. **No orphan marketing clauses.** Do not ship incomplete slogans that only work if the
   reader already saw a previous line off-screen.
3. **Product identity first, ecosystem second.** Hierarchy of claim: product hero → usage
   hint → CTA/auth → mother-brand / ecosystem line (never the reverse for empty states).
4. **Human chrome, not machine codes.** Never surface raw `AUTH_REQUIRED`, stack traces, or
   internal enum tokens as primary user copy; the Copywriter rewrites them to plain language.
5. **Copy review gate.** Phase 3 options that include words are **void** until the Senior
   Copywriter has signed off on every user-visible string (or the President records an
   explicit, temporary exception with a fix-by date).

## Access precondition (HARD GATE)

No seat may opine on layout, navigation, structure or consistency before the
brand system and **every** design system of the organisation being served are
loaded. See [`brand-design-system-access.md`](brand-design-system-access.md).
