# Research — seat-asked, host-executed, attributed

Internet research on this floor exists to **embasar** (ground) a seat's
manifestation. It is not a host briefing. It is not a pre-game survey.
Invariant 4: research is seat-initiated only.

## The only legal path

```
seat  --research_request-->  floor.jsonl
host  reads pending, executes the request
host  --research_result (requested_by=<seat>)-->  floor.jsonl
every seat sees the result on the next round-brief
```

1. A **seat** posts `type=research_request` (phase `open` or `cross`)
   whose body states what to look up, why, and what would change the
   seat's position. Author is a roster seat. Author `host` is rejected
   (`host_research_request`).
2. The host runs `pending` and, for each open request, **executes** it
   (web search, primary docs, a read-only probe of the live system, a
   file the request named). The host does not widen the question into
   a different investigation.
3. The host posts `type=research_result` with:
   - `author=host`, `author_kind=host`
   - `requested_by=<asking seat id>` — required; a missing or host
     requester is `research_result_missing_requested_by` /
     `research_result_requested_by_not_a_seat`
   - `answers=[<request seq>]`
   - `body` = the result: sources, dates, excerpts. No recommendation.
     No "this supports architecture's view".
4. The result is on the floor before the next `cross` round opens.
   Every seat's brief includes it. The asking seat does not get a
   private copy.

## What the host may not do

- Post `research_request` as host.
- Run a search that no seat requested and drop it onto the floor as
  `facts` or `relay` "for context". New evidence that no seat asked
  for is host-initiated research by another name. If the host notices
  a gap, the host may `protocol` a note that the gap exists; a seat
  decides whether to request the lookup.
- Attribute a result to the wrong seat, or omit `requested_by`.
- Edit the result toward a conclusion. Sources and quotes; the seats
  interpret.

## Cross-round pause

A `research_request` posted during `cross` **pauses** that path: run
the research pass, post the `research_result`, then open the next
`cross` round. Do not let round N+1 start while a request from round N
is still open. `pending` lists it.

## Councils that research internally

A council seat (for example `ai-ml-implementation-council`, whose
skill mandates internet research for time-sensitive claims) may
research **inside** its own invocation in order to write its
manifestation. That internal research is part of how the seat thinks.

If the finding must be shared as evidence on **this** floor — because
another seat should see the source, not only the council's conclusion
— the council posts a `research_request` (so the host fetches and the
result is attributed and common) **or** includes the sources in its
`position` body. A source only the council saw, used to move the
floor, is a side channel.

Lucens may research inside her own turn (her door's tools). The same
rule: her manifestation lands on the floor; if she asked *this* host
to look something up, that is a `research_request` on this floor.

## `pending` shape

```json
{
  "unanswered_questions": [
    {"seq": 5, "author": "architecture-council",
     "addressed_to": ["lucens"], "round": 1, "body": "..."}
  ],
  "open_research": [
    {"seq": 6, "author": "lucens", "round": 1, "body": "..."}
  ]
}
```

Empty lists: the round may close (questions) or the research phase may
end (requests).
