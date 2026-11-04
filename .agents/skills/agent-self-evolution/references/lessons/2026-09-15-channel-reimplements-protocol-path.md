# 2026-09-15 — Channel re-authored the agent render/interact path

**Category:** `channel-reimplements-protocol-path`

## Failure card

- **Symptom:** founder: do not duplicate the agent conversation frontend; keep the real AACP path for render *and* interact.
- **Claimed:** patching door labels / piece names on a vendored conversation copy was “the leftover.”
- **True:** the protocol path already exists: `DialogueSurface` wraps `ConversarSurface`, turns go through `@risegen/gen-web` `streamDialogue` or the native gen port, GenUI is the fail-closed whitelist. The platform vendor had a stub Gen screen and a stale surface without that path. Independent label patches on the fork are a second stack.
- **Cost:** extra session to undo the duplicate and copy the SoT path; devices still waiting on redeploy.

## Generalized rule

**When a protocol already owns how an agent is presented and interacted with, a channel MUST host that path (surface + transport + molecule contract). It NEVER authors a second frontend or a second communication stack for the same interaction. Copy the SoT path; keep fork-only extras that the protocol does not own.**

Detection: a channel Gen/Talk screen that is not `DialogueSurface`/`ConversarSurface` + gen-web/native port, or a vendor copy missing `streamDialogue` / `getGenPort` while the SoT has them.

## Action plan

- Platform vendor hosts the SoT AACP path (`DialogueSurface`, gen port, pieceCopy, presence). Fork-only lab-record extras stay. No `rsync --delete`.
- Test: `aacp-agent-path.test.ts` — Gen hosts DialogueSurface; turns go through streamDialogue / native port; Talk mounts ConversarSurface.
