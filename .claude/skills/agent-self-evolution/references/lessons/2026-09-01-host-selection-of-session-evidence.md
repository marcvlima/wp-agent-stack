# Lesson — the host does not pre-analyze a session the conclave must read

**When:** 2026-09-01
**Trigger:** Founder correction during a Code Doctor brainstorm on a live
interactive session. The host had already extracted a chronological trace,
counted markers, and begun naming what failed, before the floor opened.

## Category: `host-selection-of-session-evidence`

## Failure card

```text
SYMPTOM: Founder: you cannot bias; everyone in the brainstorming must
         analyze the session on their own.
CLAIMED: Host treated a compressed timeline, marker counts, and a
         host-named defect sketch as "the dossier" for Doctor Code + Lucens.
TRUE:    The standing rule is that the Doctor and Lucens receive the ENTIRE
         session, never a host selection. The host may add findings only as
         one more input, clearly labeled as the host's, and only after the
         room has the raw files. Pre-digesting the session into a timeline
         or a class name is the selection the rule forbids.
COST:    The room would have deliberated the host's frame instead of the
         session. Searches, class, and backlog would have been steered.
```

## Root process failure (not just technical bug)

The host confused *assembling identity of the corpus* (paths, hashes, sizes,
which files exist) with *interpreting the corpus*. A numbered turn trace, a
"the defect is X" sentence, and a host-chosen highlight of markers are all
selection. The voices in the room cannot analyze the session themselves if
the first document they receive is already a reading of it.

This is the evidence-intake half of the same family as
`conclave-decides-research-together` (the host must not research alone and
hand a conclusion). Intake and research are two moments; both are floor-owned.

## Rule (MUST / NEVER — generalized, category-level)

- **MUST** deliver the complete unselected session to every voice in a
  convened room: full transcript, outbox, runtime, usage, and any sibling
  session files that belong to the same corpus. Identity of the corpus
  (paths, hashes, byte sizes, binary/runtime identity) is allowed.
- **MUST** let every voice read those files itself before the host offers a
  reading. Host findings, if any, are a separate labeled input, never the
  frame.
- **NEVER** replace the session with a host timeline, a host-named class, a
  marker digest, or a "what matters" extract as the room's first view of the
  evidence.
- **NEVER** name the searches or the defect class before the floor has read
  and named them (companion rule: conclave-decides-research-together).

## Detection (how the next agent notices the category)

A first-round conclave ask that contains a numbered chronological trace of
user/assistant turns, a sentence of the form "the defect is …", or a
host-chosen subset of markers *before* a floor reply exists, is this
category. The detector is the ask itself: if the room could skip the files
and still "know" the story, the host selected.

## Related skills

- `agent-self-evolution` (this loop)
- conclave brainstorm / Code Doctor host (floor names searches; host is hands)
- lesson `2026-09-01-conclave-decides-research-together` (research half)

## Evidence pointers (no secrets)

- Founder utterance this session: the host must not bias; everyone in the
  brainstorming analyzes the session on their own.
- Product standing order: entire session to Doctor + Lucens, never a host
  selection; host findings only as one more labeled input.
