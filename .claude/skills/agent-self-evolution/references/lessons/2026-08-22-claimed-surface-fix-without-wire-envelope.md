# Claimed surface fix without the live wire envelope

## Category: `claimed-surface-fix-without-wire-envelope`

## Failure card

SYMPTOM: After a renderer rebuild the founder still saw the old pairing chrome (not the radar) and the assistant bubble repeating the user message.

CLAIMED: The discovery molecule and echo-ignore lived in source and in the rebuilt JS bundle, so a hard refresh would show the radar and stop the echo.

TRUE: The live stream’s first event is a Task whose `history` is `ROLE_USER`. The extractor treated that as assistant text, so the bubble echoed the prompt for the whole wait. The radar molecule was not on that envelope until a later tool; the Portuguese ask “descoberta” did not match “descobrir”, so the host never seeded radar. A rebuilt SVG in the bundle cannot paint a molecule the wire never sent.

COST: Founder retest on a stale diagnosis; a second correction for the same surface.

## Root process failure (not just technical bug)

Source, unit tests, and a production bundle hash of a widget are proxies. They do not prove the live protocol emits the molecule on the first events, nor that the first event is not the user’s own text. The previous turn stopped at “the chunk contains `rg-radar-sweep`” instead of folding the live SSE.

## Rule (MUST / NEVER — generalized, category-level)

MUST capture the live protocol envelope (first events) of a user-visible stream before claiming the surface is fixed.

NEVER treat a rebuilt renderer, a CSS class in a chunk, or a unit test of the widget as proof that the live conversation will paint that widget or will not echo the user turn.

A user-role history payload is never the assistant bubble.

## Detection (how the next agent notices the category)

- The first streaming event’s extracted text equals the user prompt.
- The widget exists in the shipped bundle but the stream metadata for that turn has no matching molecule.
- The ask language (inflected form) is not in the host trigger regex.
- The host still paints the previous chrome (progress bar) on the same wait the new widget was meant to replace.

## Related skills

- `research-before-asserting`
- `development-flow`
- holding layer `user-visible-verification` (product AGENTS stubs)

## Evidence pointers (no secrets)

- Live A2A EVENT 1: `result.task.history[0].role = ROLE_USER` with the user text.
- After the fix, EVENT 3 WORKING metadata includes `device_discovery` with `pairing: true` on “iniciar a descoberta”.
- Extract of EVENT 1 is empty string; `shouldIgnore` is not the only gate.
