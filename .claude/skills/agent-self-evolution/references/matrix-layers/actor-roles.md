# Actor roles (layer)

Open when a named actor is forbidden from occupying a role that another named
actor already holds (assistant vs mind, renderer vs engine, console vs product).

## MUST

- Keep distinct actors in distinct roles. A console, a mind, or a unique
  service is not a drop-in persona of the product actor.
- If a prohibition exists, land a **detector** that fails when the forbidden
  actor reappears as a persona, transport, fallback host, or liveness probe of
  the allowed occupant.
- A comment that "defaults to the allowed occupant" is not a wiring. The
  request path the surface actually sends is the fact.

## NEVER

- Add the forbidden actor as a peer persona or transport "for polymorphism".
- Fall back to the forbidden actor's host when the allowed occupant's port or
  turn server is absent — that is a silent role collapse.
- Probe the forbidden actor's liveness to decide whether the allowed occupant
  is available.
- Treat an unused class named after the allowed occupant as proof the surface
  talks to them.

## Detector

A source/unit test that fails if the forbidden actor is importable on that
surface, or if the resolved turn host is the forbidden actor's host. Presence
of a comment is not the detector (category `prohibition-without-detector`).
