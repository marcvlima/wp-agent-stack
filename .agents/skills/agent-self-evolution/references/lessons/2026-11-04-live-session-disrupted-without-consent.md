# Live remote session disrupted without signalling

## Category: live-session-disrupted-without-consent

## Failure card

SYMPTOM: While fixing remote-desktop display behaviour on a Linux host, the agent ran a connector off/on, a VT switch and a display-mode change while the user had a live RDP connection — none signalled beforehand. The user then found their running session gone and said it could not have happened.
CLAIMED: Nothing — the commands were narrated only after they ran.
TRUE: The graphical session had actually died earlier, from a compositor segfault right after an RDP "extend" virtual monitor was created (before the agent's first command). But the agent's own commands were each capable of dropping the connection or the session, and the user was given no risk analysis and no decision.
COST: The user's running agent session (terminal + Claude Code) died with the compositor; trust in remote maintenance; a correction turn.

## Root process failure

The agent treated "fix it" as consent to any command that served the fix, including ones that disrupt the user's live session. Risk was reported after the fact instead of decided by the user beforehand.

## Rule (MUST / NEVER — generalized)

MUST: Before any command that can drop a live remote connection or end the graphical session, inventory the session, classify the command (none / reconnect / session-ending), signal it with a risk analysis, and wait for the user's explicit go for that command.

NEVER: Disrupt or end the user's current session without signalling and a risk analysis. The decision is the user's; an earlier approval does not cover a new disruptive command.

## Detection

Compare graphical session id, compositor PID and established RDP connections before and after the work. A difference with no recorded user go for a command of that class is this category. Skill `rdp-session-preservation` carries the procedure.

## Action plan

- New canonical skill `rdp-session-preservation` (procedure + classification + detector).
- Matrix always-on: mandatory-skills row + NEVER line.
- Host runbook records the compositor crash in extend mode and the recovery path (transcript resume).

## Evidence pointers (no secrets)

- Host journal 2026-11-03 23:43:41 "Added virtual monitor Meta-0" → 23:43:47 "GNOME Shell crashed with signal 11" → greeter → autologin new session 23:44:05.
- Agent's disruptive commands 2026-11-04 00:5x: connector status off/on, `chvt 3; chvt 2`, `gdctl set` (display mode).
- Runbook: `lakenbeach/holding-shared-infra` `docs/runbooks/nex-global-linux-host.md`.
