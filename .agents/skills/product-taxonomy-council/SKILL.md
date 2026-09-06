---
name: product-taxonomy-council
description: Convene a standing product-taxonomy, information-architecture, and navigation-governance council WHENEVER a new product/service/feature is being named, an existing structure is questioned, a site/platform sitemap or taxonomy is designed/refactored, or navigation hierarchies and menu systems are designed or changed. The Chief Product Architect always chairs; specialists (Lead Information Architect, Navigation & Menu Systems Architect, Taxonomy & Metadata Architect, Naming & Verbal-Identity Lead, Brand Architect, Platform/DevRel Strategist, Product Manager, Catalog/Governance Steward) ground in the existing catalog, sitemaps, and brand system, research PRIMARY sources on disciplined information architecture (NN/g, Rosenfeld & Morville, Abby Covert, Donna Spencer), cloud service naming (AWS/GCP/Azure), controlled vocabularies (W3C SKOS), and navigation ergonomics, brief on the business/positioning first, generate meaningful non-trivial structures and names, run 2 focused consensus rounds (Sonnet moderates; the top-tier model stays executive), stay unbiased when the founder rejects a proposal, and converge to a decision, sitemap/menu tree, taxonomy schema, catalog entries, and an ADR-ready record.
---

# Product Taxonomy & Information Architecture Council — the standing decision room for structure, taxonomy, navigation & naming coherence

You are convening **a real, senior taxonomy, information architecture, and navigation council** — a Lead Information Architect, a Navigation & Menu Systems Architect, a Taxonomy & Metadata Architect, a Naming & Verbal-Identity Lead, a Brand Architect, a Platform/DevRel Strategist, a Product Manager, and a Catalog/Governance Steward, modeled on the rigorous standards established by the world's leading digital platforms and information architecture pioneers (Nielsen Norman Group, Peter Morville & Louis Rosenfeld's Polar Bear IA framework, Abby Covert, Donna Spencer, and cloud portfolio governance across AWS, GCP, and Azure).

This is not a casual brainstorm: structural decisions, navigation hierarchies, and public service names become **foundational user ergonomics, product wayfinding, and brand equity that are expensive to change**. The **Chief Product Architect always chairs the room**, and the council works in disciplined rounds until it reaches consensus on a decision that protects system clarity, user findability, and business identity.

**Invoke this skill whenever:**
- A **website, platform, application, or system taxonomy/hierarchy** is being designed, structured, or reorganized.
- **Navigation systems, menu hierarchies (global, local, contextual, mega-menus, sidebars, mobile drawers/tabs), wayfinding paths, or sitemaps** are being created or altered.
- A **new product, service, capability, or feature** is being named or categorized.
- An **existing catalog, category model, controlled vocabulary, or URL/slug structure** is questioned, consolidated, or restructured.
- A name, menu item, or navigation tree is about to ship without having been checked against information architecture principles, cognitive load limits, and catalog standards — **stop and convene the council.**

This skill exists to make **structural and naming coherence repeatable**: ground in what already exists, research how disciplined information architecture and classification systems actually work (never from training memory), red-team every candidate structure and label, and bring the founder a decision instead of an unvalidated draft.

## The room (who is always in it)

The **Chief Product Architect** chairs every session (non-negotiable). The standing panel is defined in [`references/roster.md`](references/roster.md) — a Chief Product Architect plus a core of specialists:
- **Lead Information Architect (IA Lead)** (system blueprints, sitemaps, organization schemes, depth-vs-breadth ratios, mental models).
- **Navigation & Menu Systems Architect** (pathfinding UI, global/local/contextual navigation, fat/mega menus, sidebar hierarchies, breadcrumbs, tab bars, mobile navigation ergonomics, wayfinding).
- **Taxonomy & Metadata Architect (Content Ontologist)** (backstage classification, controlled vocabularies, facets, metadata schemas, W3C SKOS ontologies, search/filtering logic).
- **Naming & Verbal-Identity Lead** (candidate names, linguistic screening, microcopy/labeling consistency, information scent, tone).
- **Brand Architect** (naming-architecture model, family discipline, anti-sprawl, multiplatform brand integrity).
- **Platform / DevRel & Systems Strategist** (API/CLI identifiers, RESTful URL slug hierarchies, cloud service naming patterns).
- **Product Manager** (business/roadmap context, user journeys, variant trajectory, SKU/tier proliferation risk).
- **Catalog & Governance Steward** (the living system of record, sitemap registries, collision checks, the ADR-ready record).

Optional specialists — **UX Researcher & IA Validation Specialist (Tree Testing / Card Sorting)**, **Content Architect / Headless CMS Strategist**, **Accessibility & Inclusive Navigation Specialist (a11y)**, **Legal/Trademark Screener**, **Localization / Global Taxonomy Reviewer**, **Customer/Support-Experience Rep** — are convened as the decision requires.

The Chief Product Architect **sizes the room**: a full platform sitemap overhaul or new top-level product family convenes the full panel; a focused navigation menu adjustment or feature naming inside an existing family convenes the Chair + the relevant subset (see the sizing guide in `roster.md`).

**How the room is run** — two modes (see [`references/process.md`](references/process.md)):
- **Delegated (preferred when the host supports subagents):** spawn one subagent per active role so perspectives are genuinely independent. Each round is synthesized by a dedicated **Sonnet moderator** — this is a process function, not a domain vote. The **Chief Product Architect runs on the top-tier model and stays executive**: it sets the brief, ratifies each round's consensus, breaks ties, and owns the final decision. Per decide-high/execute-low, moderation (structured, repetitive synthesis) is delegated; the decision is not.
- **In-context (always available):** the executing agent role-plays the full panel as a structured, **attributed** multi-round transcript, with the moderator voice and the Chair's executive ratification kept visibly distinct even though both run on the same agent.

## Non-negotiable rules

1. **The Chief Product Architect always presides and stays executive.** They set the brief and the definition of "good", ratify an explicit consensus every round, break ties, and own the final decision + ADR-ready record. The Chair is never replaced by the moderator.
2. **Ground in the source of truth FIRST.** Before proposing any hierarchy, menu, or name, load the existing product/service catalog, sitemaps, navigation trees, brand system / verbal-identity guide, and any prior naming/IA ADRs. Never contradict a locked structure or family silently — a proposal that overturns one must call it out as a **supersession** with reasons. (See "Grounding" below.)
2b. **ADR-conflict gate (HARD RULE — same as architecture-council).** Phase 0 sweeps the **entire** ADR index of the owning repo(s) and the organization's source-of-truth repo (every file, by listing — not a guessed subset). Accepted ADRs constrain the decision space; **founder-fixed rulings are immutable inputs, never options**. An option conflicting with an accepted ADR may only be presented as a labeled **SUPERSESSION PROPOSAL** — conflicting ADR named, violated clause quoted — and cannot be ranked #1, ratified, or recorded as accepted **without the founder's explicit, specific assent**. The deliverable includes an **ADR compliance table** (ADR · clause · complies/CONFLICTS→pending assent); an unresolved conflict makes the decision void.
3. **Research PRIMARY sources; never decide from training memory.** For every load-bearing claim, consult authoritative IA, taxonomy, and navigation frameworks (Nielsen Norman Group guidelines, Rosenfeld/Morville/Arango *Information Architecture for the Web and Beyond*, Donna Spencer *Card Sorting*, Abby Covert *How to Make Sense of Any Mess*, W3C SKOS / ANSI/NISO Z39.19 taxonomy standards) and official cloud-provider naming/branding documentation (AWS, GCP, Azure). State what was verified vs assumed, and cite the sources used.
4. **Optimize for human findability, cognitive load, and strong information scent.** A navigation tree or taxonomy fails if users must guess where items live or drill through excessive arbitrary levels (keep cognitive hierarchies within 3–4 levels; favor strong, mutually exclusive categorization with unmistakable labeling). Backstage taxonomy must power robust search and faceting; front-stage navigation must provide predictable wayfinding with clear "you are here" orientation.
5. **Red-team every candidate structure and label.** An assigned devil's-advocate attacks each finalist for navigation dead-ends, ambiguous categorization, cognitive overload in menus, internal catalog collisions, external trademark/domain risk, translation/localization traps, and "mini-brand" sprawl.
6. **Run exactly 2 focused consensus rounds; Sonnet moderates; the top model stays executive.** Round 1 diverges wide (generate broad, stress-test against the ten lenses, cut); Round 2 converges (refine the survivors, screen finalists, specify sitemap/menu/taxonomy depth, decide). Two rounds keep feedback cycles fast and cheap — do not pad to more rounds, and do not fake convergence. Only a genuinely foundational, ecosystem-wide platform restructure may add a third round, and only if the Chair records why the 2-round output was insufficient.
7. **Brief first — understand the system context, not just the isolated slot.** Before generating, the Chair captures and records a short brief: what the site/platform/product *does*, user mental models, task flows, **market positioning and value proposition**, and the founder's qualitative desires (e.g. "shallow and discoverable", "dense for power users", "striking but not trivial"). These become explicit **evaluation variables** every candidate is judged against.
8. **Follow industry best practice AND think outside the box.** Ground in how disciplined IA, navigation systems, and naming programs actually work (rule 3), then design **meaningful, intuitive, and scalable** structures — avoid generic "dumping grounds" (e.g. "Miscellaneous", "Other", "Resources" with no clear scent) and trivial unoriginal names.
9. **On rejection, generate — do not defend (anti-bias rule).** When the founder rejects a proposal, the council must NOT re-litigate, anchor on, or re-pitch the rejected option. Treat the rejection as a **new, binding constraint** and genuinely work to produce *fresh, valid* alternatives that fit the founder's expressed scenario and desire **better**. The red-team explicitly checks each new round for anchoring bias on prior rejects.
10. **Deliver decision-grade, buildable output.** A structural/naming decision (sitemap/hierarchy tree, navigation menu specification, taxonomy/metadata schema, catalog rows, ADR-ready record, and consistency checks). Format in [`references/output.md`](references/output.md).
11. **Do not decide the irreversible for the human.** Restructuring an active production platform's primary navigation, breaking existing URLs, or renaming an already-shipped customer-facing product is expensive to reverse. Present findings, trade-offs and a recommendation — and **wait** for the founder before executing anything destructive or hard to undo.

## Grounding: the source of truth (read before proposing)

At the start (Phase 0), establish the binding context:

- **Existing sitemap / navigation tree present?** Inspect the current user surface, router configurations, menu trees, and sitemaps. Treat existing structures as baseline truth unless the council explicitly supersedes them.
- **Existing catalog present?** Find wherever the ecosystem's product/service names live today (a catalog doc, a brand-system repo, prior `docs/decisions/` ADRs). Load it and treat existing names/families as **locked** unless the council explicitly supersedes one.
- **Brand system / verbal-identity guide present?** Load it — voice, tone, labeling rules, and naming do's-and-don'ts already decided for the ecosystem.
- **A naming or IA standard already exists?** Prior council outputs (ADRs) are the standard; honor them or explicitly supersede them.
- **No records yet →** capture the constraints **with the human**: what domain/platform this belongs to, target user personas, core task journeys, non-goals, and what "good" means for this structure or name.
- **The brief (rule 7) — always captured, records or not.** State in 3–5 lines: what the site/platform/product *does*, who it is for, user mental models, **market positioning and value proposition**, and the founder's qualitative desire.

Record the **grounding facts** (locked names/families/routes + verified findings) + the **brief** the council must honor; every proposal is checked against them.

## Relentless Method (MANDATORY — read references/relentless-method.md)

Every session runs under the Relentless Method: grit before barriers (two alternatives before any "can't"), negative-claims quarantine (test, don't inherit), metrics interrogation (numbers carry their environment), iterative research until the result, pre-registered decision rules, an out-of-the-box round, veto alchemy, proactive validation on cheap executors, no lazy WATCH, and silent no-op hunting. A synthesis that violates these is not ready for the ratifier.

## Flow (summary)

[`references/process.md`](references/process.md) has the full protocol. In short:
**Phase 0** ground + **brief** (sitemaps + catalog + brand + prior ADRs + the business/user brief per rule 7) → **Phase 1** primary-source research (NN/g IA & navigation guidelines + Rosenfeld/Morville/Spencer IA practice + W3C SKOS taxonomy standards + AWS/GCP/Azure naming discipline) → **Phase 2** two consensus rounds — **Round 1 diverge** (generate wide + meaningful structural/naming candidates, stress-test against the ten lenses, cut), **Round 2 converge** (refine survivors, screen finalists, specify menu trees/sitemaps/catalog rows, decide) → **Phase 3** converge to a structural/naming decision, sitemap/navigation spec, taxonomy schema, catalog entries, an ADR-ready record, and consistency checks.

**Every session runs exactly 2 rounds** (diverge, then converge). Each round is synthesized by a **Sonnet moderator**; the **Chief Product Architect (top-tier model) stays executive** throughout. Deliver the decision to the invoking agent (or the founder). This skill decides **what the structure/name is and why**; the invoking agent applies it, and an accepted decision should be recorded as an ADR in the owning repo.
