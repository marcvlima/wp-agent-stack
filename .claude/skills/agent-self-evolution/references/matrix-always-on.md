# Holding matrix — always-on (token budget ~40 lines)

> **Canonical source:** `@holding-central-ai-assets/agent-self-evolution` → this file.
> **Repos** embed a short copy under `## Holding matrix` in each repo `AGENTS.md`.
> **Do not** paste matrix-layers into always-on. Open layers only when the rule applies.

## Mandatory skills (install via APM)

| Skill | When |
|---|---|
| **`agent-self-evolution`** | After **any** agent failure / founder correction — evolve matrix + reconcile |
| `research-before-asserting` | Before claiming a cause/diagnosis/fix |
| `mandatory-soft-skills-for-agents` | Session start + hard problems |
| `memory-bank` | Feature/topic work start + end |
| `sops-age-secrets` | Any secret in git / multi-machine |
| `rise-flow` | Task start in a git repo (drift) |
| `development-flow` | After shared infra/code change before “test it” |
| **`quality-enforcement`** | Production edits: paired tests + `quality-guard run` before commit; hooks enforce |
| **`shared-infra-sot`** | LAN/edge/CPE/home-CF/DDNS work — SoT `lakenbeach/holding-shared-infra`; promote session truths |
| **`rdp-session-preservation`** | Any RDP / remote-desktop / display / graphical-session change — signal + risk analysis before disrupting; the user decides |

Product-only skills (ABG, catalog-guard, connector, …) stay in **product** `AGENTS.md`.

## MUST

1. **English** for all repo artifacts; Portuguese with the user.
2. **Evidence before diagnosis** — alternatives + primary source or probe; label hypotheses until ruled out.
3. **Decide-high / execute-low** — never delegate the *why*; verify executors with commands.
4. **No unplanned external spend** — explicit founder authorization with cost.
5. **No commit/push without founder authorization** (session-traceable commit body when used).
6. **Memory-bank** for non-trivial work: INDEX → one topic folder; update on block end.
7. **Never substitute a nearby subject for the one the requester named.** An empty or
   partial resolver result means *not found in that layer*; a dropped qualifier is a
   partial result wearing a confident score. An unresolved target stops side-effecting
   work — harness-enforced, never prompt-enforced (category
   `domain-knowledge-hardcoded-in-agent`, lessons 2026-08-27 / 2026-08-30).
7. **Stable names over volatile numbers** — LAN aliases, DDNS hostnames; **never** treat an IP as durable identity in plans/prompts, **and never send a live request to an IP literal** when a canonical hostname exists (category `stale-identity-anchor`).
8. **Runtime paths in micro-specs** — absolute host paths, users, secrets env keys (`HOST_SUDO_PASSWORD`, …); never repo-relative paths as if they were on the server.
9. **Secrets first** — check SOPS/dev-host secrets before asking the founder for a password.
10. **Self-evolve on failure** — run `agent-self-evolution` before closing the incident.
11. **Paired tests + quality-guard** — production code changes need test file pairing and a green `quality-guard run` before `git commit` **and before ending a turn**; agents never use `--no-verify` (hooks enforce).
12. **Conclave owns intake and research; fix the condition not the instance** — deliver the ENTIRE unselected session (transcript, outbox, runtime, usage) to every voice; identity of the corpus (paths, hashes, sizes) is allowed; a host timeline, class name, or marker digest is not. The FLOOR names the searches; the host executes exactly those and returns raw, sourced findings (never a pre-drawn conclusion), then the floor rules. A defect on one model/endpoint/input is a CLASS: key the fix on the decidable behaviour, never on the instance's identity (no `if model == X`). (Lessons 2026-09-01 conclave-decides-research-together, host-selection-of-session-evidence; layer `conclave-intake.md`.)
12. **Never ask the founder to authorize mandatory tests** — writing tests, running `quality-guard run`, and pairing are **not optional**; execute them; do not rephrase policy as a question.
13. **Shared infra SoT** — residential/edge knowledge lives in `lakenbeach/holding-shared-infra`; skill `shared-infra-sot` on every repo; never invent topology from chat; promote durable facts into the SoT same block.
14. **Accepted decisions first** — before changing storage/topology, open the accepted ADR; enforce it. Do not re-decide from chat or leftover rows (category `decided-sot-not-enforced`).
15. **Never stop after a phase has returned** — if a standing delivery's current phase has finished or hit its limit, start the next phase in the same breath; narrating the finished phase to the human is not an ending (category `yield-after-phase-complete`).
16. **Driven input is not receipt** — prove the product surface accepted each driven prompt/interaction before counting the turn; never treat the driver's send log or a synthetic label as delivery (category `driver-record-is-not-receipt`).
17. **Product install path is the evaluation path** — after a correction, redeploy to the documented install file and spawn that file for the next evaluation; a PATH lookup or checkout copy is not the product (category `correction-not-on-product-surface`).
18. **Interactive fail-closed is turn-scoped** — a quality abort on a live user turn MUST NOT become “start a new session”; session-kill fail-closed is for unattended loops (category `guardrail-session-kill-on-interactive`).
19. **A session remaining open is not a fixed stream** — if the defect is painted abort or queue chrome, change the bytes the surface renders and the finish class that dequeues; a related session-kill gate is not the fix (category `lifecycle-gate-as-surface-fix`).
20. **Deployment vocabulary is data, not code** — aliases / name→target mappings live in a resolver-backed data layer with confidence and provenance; ambiguity or a miss is a clarification turn, never a heuristic fall-through (category `domain-knowledge-hardcoded-in-agent`).
21. **Membership comes from the domain model** — set/scope/"all of X" membership is derived from the product's own model, never from a replaceable backend's grouping (areas, rooms, tags); when they disagree, the backend is a deployment artifact and the domain model wins (category `backend-membership-as-domain-truth`).
22. **A recurrence is a detection defect first** — when a known failure family returns, add the measurement whose absence let it back and pre-register the fix's adopt/reject rule *before* fixing the new symptom (category `self-reported-effect-without-readback`).
23. **No side-effect-path gap behind a redeploy** — close it or fail-closed-block it before restarting the surface; validate negatives (ambiguous / unknown / no-verb) before any actuating input (category `known-gap-shipped-to-actuating-surface`).
24. **Before rejecting an operation on a model, decide whether it happens at serve time or offline, and read the config before reasoning about the parameters.**
25. **Name the failure before the remedy** — a side-effecting, hard-to-reverse action (restart, reinstall, reset) is only justified by a named, evidenced failure; a diagnosis step listed as "or" a remedy is a prerequisite, not an option (category `restart-without-named-failure`).
26. **Gates parse intent; deny recipes are one command; false positives become fixtures; contracts are generated from the enforcing code** — an enforcement classifier never scans the raw command string, never denies a read-only or scratch-scoped action, ships every false positive as a permanent test fixture, answers a deny with one copy-paste command, and the prose an agent must follow is rendered from the code that validates it (category `gate-string-scanner-false-positives`).
27. **Authorized delivery ends on the default branch** — once the requester has authorized the change, the same turn commits it and pushes the default branch. A green gate, a staged index, a side branch, or a published artifact built from uncommitted files is not delivery. Before the turn ends, the remote default-branch ref contains the change (category `delivery-left-off-default-branch`).

## NEVER

1. **Blame an external network/operator** (“ISP blocks X”, “network is broken”) without: full local path proof (listener on target + correct PF/DNAT + firewall) + **external** check on a **stable public hostname**.
2. **Hardcode an IPv4/IPv6 into plans, prompts, or inventory “current” fields, or send a live request to an IP literal** when a canonical hostname exists — an IP is a probe result, never the door (category `stale-identity-anchor`).
3. **Invent RCE/reboot paths** when a product UI/API/secret exists.
4. **Mark feature done with open SKIP/pending security tasks** (e.g. CF-only firewall) untracked.
5. **Put secrets, age keys, or plaintext env in git.**
6. **Commit production changes without paired tests / green quality-guard** (or founder `QUALITY_GUARD_OVERRIDE`).
7. **Treat unit/integration tests or quality-guard as optional, skippable, or “ask the human first”** — that is category `policy-as-optional-prompt`.
8. **Author UI/brand-governed artifacts** (prototypes, mocks, components, brand copy) without first searching sibling checkouts + org repos for the governing design/brand SoT and consuming its tokens/laws — category `authoring-without-sot-grounding`.
9. **Treat a catalog, inventory, or status listing as proof that a live request path works** — a list is not a successful request; fail-closed until the actual request returns success (category `listing-as-liveness`).
10. **End a standing delivery after the current phase has already returned or hit its limit** in order to report status — the next phase starts immediately (category `yield-after-phase-complete`).
11. **Retarget a user surface to an existing unique service while leaving the previous plane’s admission chrome** (auth walls, pickers, send guards) in place — chrome MUST switch with the backend; never reimplement the unique service as a second backend (category `chrome-not-retargeted-with-backend`).
12. **Recover a failed command by repeating human setup** (pair, factory reset, reinstall) before comparing the request to the protocol’s canonical write — one topic, one payload, no alias flood, no extra read that the device cannot answer (category `setup-loop-instead-of-command-path`).
13. **Claim a user-visible stream/UI fix from source or a rebuilt bundle alone** — capture the live protocol envelope (first events); a user-role history payload is never the assistant bubble (category `claimed-surface-fix-without-wire-envelope`).
14. **Re-open a store an accepted ADR already removed from operational SoT, or invent a parallel topology from chat** — search accepted decisions first (category `decided-sot-not-enforced`).
15. **Report a painted abort/queue chrome fixed because a related session-kill or latch gate changed** — the stream bytes must change (category `lifecycle-gate-as-surface-fix`).
16. **Label a gap on a side-effect path as "Phase N debt" in the same delivery that redeploys the surface** (category `known-gap-shipped-to-actuating-surface`).
17. **Skip a process step the requester named, or that policy marks non-optional, because the answer already seems known** — run it before the work it gates (category `mandated-deliberation-skipped`).
18. **Report an effect from the actor's own success signal** — a tool's `verified`/`ok` flag and the agent's own summary are claims, not proof; read the affected state back independently, and where several commands hit one shared physical unit prefer one command carrying the whole set (category `self-reported-effect-without-readback`).
19. **Promote a prohibition to this matrix without naming the detector that fails when it is broken**; never let a test assert the presence of a literal a rule forbids (category `prohibition-without-detector`).
20. **Replace a session the room must read with a host timeline, a host-named class, or a marker digest as the first view of the evidence** — every voice reads the files; host findings are a separate labeled input after that (category `host-selection-of-session-evidence`).
21. **A session remaining open is not a fixed stream** — if the defect is painted abort or queue chrome, change the bytes the surface renders and the finish class that dequeues; a related session-kill gate is not the fix (category `lifecycle-gate-as-surface-fix`).
22. **A turn-scoped quality abort (repetition, ngram, empty decode) into a session-kill on an interactive user surface** — unattended loops may fail-closed; a live user message always proceeds (category `guardrail-session-kill-on-interactive`).
23. **Report a defect on one model/endpoint/input is a CLASS: key the fix on the decidable behaviour, never on the instance's identity** (no `if model == X`). (Lessons 2026-09-01 conclave-decides-research-together, host-selection-of-session-evidence; layer `conclave-intake.md`.)
24. **No side-effect-path gap behind a redeploy** — close it or fail-closed-block it before restarting the surface; validate negatives (ambiguous / unknown / no-verb) before any actuating input (category `known-gap-shipped-to-actuating-surface`).
25. **Expose a forbidden actor as a persona, transport, fallback or liveness probe of the allowed occupant of a role** — a named prohibition is a detector (category `forbidden-actor-as-peer`; layer `actor-roles.md`).
26. **Put a shell loop variable (`$d`, `$SRC`, `$TMP`, `$?`) in a hook command string** a host interpolates as required environment — acquire loops live in a bootstrap file the host does not scan (category `interpolator-unsafe-hook-vars`).
27. **Author a second frontend or communication stack for an agent** when a protocol already owns render and interact — the channel hosts that path (category `channel-reimplements-protocol-path`).
28. **End an authorized delivery with the change only in a worktree, the index, or a side branch** (category `delivery-left-off-default-branch`).
29. **Disrupt or end the user's current remote/graphical session without signalling and a risk analysis** — classify each command (none / reconnect / session-ending), wait for the user's explicit go per command; detector: session id / compositor PID / RDP connections differ before vs after without a recorded go (category `live-session-disrupted-without-consent`; skill `rdp-session-preservation`).

## Layers (open only when needed)

| Layer | Path under skill `references/matrix-layers/` |
|---|---|
| Diagnosis rigor | `diagnosis-and-network.md` |
| Plans & micro-specs | `plans-and-micro-specs.md` |
| Secrets & host access | `secrets-and-host-access.md` |
| Git & delivery | `git-and-delivery.md` |
| Shared infra SoT | skill `@holding-central-ai-assets/shared-infra-sot` + repo `lakenbeach/holding-shared-infra` |
| Unique-service chrome | `unique-service-chrome.md` |
| Conclave / Doctor Code intake | `conclave-intake.md` |
| Actor roles | `actor-roles.md` |

- **An executor fault is never a verdict.** A command that could not start, a pin that never reached the launch, or a dependency saturated between preflight and launch is an infrastructure state (name it: unrunnable / saturated / unreachable / credential-unusable), never a result charged to the subject — verify your own environment first (lesson `2026-08-21-unrunnable-is-not-a-verdict`).
- **A remedy is owed the evidence its predecessor was denied.** Reject an option on a probe and you must run the same class of probe on its replacement *before* writing the decision down — evidence for what you eliminate and reputation for what you recommend is an argument, not a comparison. Identity is a **measurement, never an attribute**: before claiming "only <principal> can do this", read back who the acting credential actually is. And never make a gate required until the intended approver has cleared it once (lesson `2026-09-01-asymmetric-verification-of-a-remedy`).
- **A fault you name is a fault you own; a fix that breeds a fault is the fixer's.** The next failure after a correction is first checked against that correction (`regression_by_correction`); every fault an agent names gets a row and a correction cycle in that session or a handoff line with its row and reason — never "material for later"; a correction that only adds a control is `symptom_fix`; every handoff states what still stands between the system and its objective, by root cause (lesson `2026-10-02-correction-generates-new-problems`, ascent-rite-monitor D44).
