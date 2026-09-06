# The session protocol — phases and rounds

The council works in disciplined phases. The core is a series of **consensus rounds** that move from wide divergence to a single structural, navigation, or naming decision. The Chief Product Architect chairs throughout, stays the decision authority, and keeps a running log.

## Two execution modes

Pick based on what the host supports; **state which you used**.

- **Delegated (preferred when subagents are available).** Spawn **one subagent per active role**, each given: the brief, the grounding (sitemaps + catalog + brand + prior ADRs), the research, and its discipline's mandate. Each round, roles respond **independently**. A dedicated **Sonnet moderator** subagent reads the round's independent outputs and drafts the round's consensus; the **Chair** (the Chief Product Architect, running on the top-tier model) reads the moderator's draft, resolves anything the moderator could not, and **ratifies** the round. This yields genuinely independent perspectives, keeps the high-volume synthesis work on a cheaper model, and keeps the actual decision on the top-tier model. Dispatch role subagents **in parallel** each round with a **shared brief + shared verified facts** so they cannot diverge on the facts.
- **In-context (always available).** The executing agent role-plays the whole panel as a structured, **attributed** transcript ("Chief Product Architect:", "Lead Information Architect:", "Navigation & Menu Systems Architect:", …), with a distinct **"Moderator:"** line synthesizing each round before a distinct **"Chief Product Architect (ratifies):"** line closes it — the split stays visible even though one agent executes both.

## Phase 0 — Convene & ground

1. **Read AND write the brief.** State exactly what is being structured, reorganized, or named, the candidate trees/names on the table (if any), the constraints, and what "good" means for this decision. Then capture the **system and business brief** (3–5 lines, binding): what the site/platform/product *does*, target user mental models and tasks, **market positioning and value proposition**, and the founder's qualitative desires. These are evaluation variables every candidate is scored against. **On a re-run after a rejection:** also record *what was rejected and why*, and treat it as a binding constraint (do not re-propose it or anchor on it — see Phase 2).
2. **Chair sizes the room** (see `roster.md`): platform overhaul/new family → full panel; focused navigation/taxonomy adjustment → Chair + the disciplines the decision touches.
3. **Ground in the source of truth.** Load existing sitemaps, navigation router definitions, the product/service catalog, brand guidelines, and prior ADRs. Treat existing structures as **locked baseline** unless the council explicitly supersedes one (with reasons).
4. **No records yet →** capture the constraints **with the human**: domain, target personas, core tasks, non-goals, and definition of "good".
5. **Record the grounding facts** — the locked names/routes/families + verified facts the council must honor.

## Phase 1 — Primary-source research

Before generating structures or candidate names, establish the **architectural discipline** the decision should follow. The relevant specialists consult **primary sources** for their load-bearing claims — **never training memory**:

- **Lead Information Architect + Navigation Architect:** authoritative IA and navigation frameworks — Nielsen Norman Group (NN/g) research on menu visibility, mega-menus, sidebar navigation, sitemaps, and breadcrumbs; Peter Morville & Louis Rosenfeld (*Information Architecture for the World Wide Web*); Abby Covert (*How to Make Sense of Any Mess*); Donna Spencer (*Card Sorting* and IA category patterns).
- **Taxonomy & Metadata Architect:** classification standards — ANSI/NISO Z39.19 (Guidelines for the Construction, Format, and Management of Monolingual Controlled Vocabularies) and W3C SKOS (Simple Knowledge Organization System) for hierarchical, associative, and faceted categorization models.
- **Platform/DevRel + Brand Architect:** official cloud-provider service naming and documentation architecture — AWS (foundational vs utility prefixes, service taxonomy), GCP (resource hierarchies, product naming guidelines), and Azure (Cloud Adoption Framework naming and resource-abbreviation catalog).
- **Naming & Verbal-Identity Lead:** naming-architecture models (branded house, house of brands, endorsed, hybrid) and linguistic/trademark screening funnels.

Share a concise **fact sheet** with the panel: each key fact tagged **verified** (with source) or **assumed** (flagged as a risk).

## Phase 2 — The rounds

Each round has the same shape:

1. **Propose / react** — each active role contributes a structural proposal, navigation tree, taxonomy mapping, candidate name, or critique from its discipline (independent in delegated mode). **Generate meaningfully, outside the box:** favor clean, discoverable hierarchies, intuitive pathfinding, and resonant names over generic dumping grounds (e.g. "Resources", "Other") or trivial names. **On a re-run after a rejection, the rejected proposal and its near-variants are off the table** — roles must produce fresh directions that fit the founder's stated desire *better*, never re-pitch or defend the reject.
2. **Stress-test against the ten structural & naming lenses** — every surviving candidate is tested against:
   - **1. Distinctiveness & Orthogonality** — categories and names do not overlap; mutually exclusive, collectively exhaustive (MECE) boundaries.
   - **2. Information Scent & Findability** — labels immediately telegraph what lies behind them; users accurately predict where items live (NN/g).
   - **3. Cognitive Depth & Hierarchy Balance** — tree depth does not exceed 3–4 levels; breadth is balanced to prevent choice paralysis.
   - **4. Menu Architecture & Interactive Ergonomics** — desktop vs mobile navigation responsiveness, scanability, mega-menu organization, sidebar grouping, and clear "you are here" wayfinding cues.
   - **5. Taxonomy & Metadata Rigor** — backstage controlled vocabularies and facets support powerful search and filtering without cluttering primary nav.
   - **6. Verbal-Identity & Labeling Clarity** — unambiguous terminology, tone alignment, pronounceability, and zero vague filler words.
   - **7. Brand-Architecture & Ecosystem Fit** — matches the chosen architecture model (branded house, endorsed, etc.); prevents "mini-brand" sprawl.
   - **8. Developer & Technical-Identifier Coherence** — clean RESTful URL slug hierarchies (`/category/subcategory/item`), API namespaces, CLI command syntax.
   - **9. Reversibility & Migration Impact** — cost to migrate existing bookmarks/URLs, redirect strategy, and customer cognitive disruption.
   - **10. Governance & Maintenance Buildability** — scalable for future additions without requiring frequent navigation redesigns.
   Weak candidates are cut with a recorded reason.
3. **Moderator synthesizes; Chair ratifies** — the moderator (Sonnet) drafts the round's agreed position; the Chair (top-tier model) resolves conflicts, breaks ties, and ratifies. An assigned **devil's advocate / red-team** attacks forced or premature consensus.
4. **Refine** — surviving proposals are sharpened for the next round.

The two rounds **narrow deliberately**: **Round 1 diverges wide** (broad structural options, sitemap layouts, candidate names, evaluated against the ten lenses, cut weak ones). **Round 2 converges** (refine survivors, specify sitemap trees, menu layouts, URL paths, catalog rows, decide). **Every session runs exactly 2 rounds** — fast, disciplined feedback cycles; do not pad rounds and do not fake convergence.

Keep a short **running log**: one line per round with the consensus reached.

## Phase 3 — Converge & deliver

Distill to **one structural/naming decision** (or a small ranked shortlist if the founder must pick). The decision is specified to implementation depth: sitemap tree diagram, menu system layout matrix, taxonomy/facet schema, catalog rows, rationale, ten-lens assessment, and alternatives considered. The Chair gives the **final call**, and — for weighty/irreversible forks (breaking URL restructuring, platform top-level renames) — hands it to the **founder** rather than executing silently.

Produce, in the format of [`output.md`](output.md):
- the structural/naming decision with honest trade-offs against alternatives;
- the **sitemap & navigation hierarchy specification** (tree diagram + menu layout);
- the **taxonomy & metadata schema** (controlled vocabulary / facets);
- the **catalog row(s)** to add/update;
- an **ADR-ready decision** (Context · Decision · Why · Consequences · Status);
- **consistency checks** against existing systems, accessibility, and brand standards.

Hand the deliverable to the invoking agent or the founder.

