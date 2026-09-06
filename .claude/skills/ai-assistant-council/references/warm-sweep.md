# Warm sweep — the batched listening pass

ONE call to the cheapest capable model (never per-seat, never the strong model),
payload: roster minus HOT seats + brief + rolling summary (≤500 tokens).

Prompt: "You are the WARM seats listed below with their lenses. The HOT
specialists just argued the summary above. For EACH warm seat, answer strictly
as that seat: from your domain's lens, ONE insight or risk the specialists are
missing — one line, or PASS. Do not restate the summary."

Output contract: `<seat-slug>: <one line | PASS>`

Promotion rule: substantive = names a mechanism, risk or precedent absent from
the hot round. Substantive → HOT next round; log it.
