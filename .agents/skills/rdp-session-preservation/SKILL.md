---
name: rdp-session-preservation
description: >-
  MANDATORY before ANY change that touches remote desktop (RDP) or the
  graphical session it shows — RDP daemon, credentials, certificates, share
  mode, displays/monitors/resolution/EDID, connector state, VT switches,
  display manager, compositor, session services, or packages behind them.
  Never end, restart or disrupt the CURRENT session without first signalling
  it and presenting a risk analysis. The decision is the user's. Use when
  asked to fix, change or configure RDP / remote desktop / screen sharing /
  monitors on any host, and before any command that could drop a live
  connection or kill the session.
version: 1.0.0
---

# Skill: rdp-session-preservation (v1.0.0)

**Founder rule (2026-11-04):** any change to RDP must **never kill the current
session without signalling and a risk analysis. The decision is the user's.**

The current session is the user's work: open terminals, running agents,
unsaved files, long jobs. On Wayland the compositor *is* the session — if it
dies, every graphical client dies with it, and processes that needed a
terminal lose it. A dropped RDP connection is also a disruption to signal.

## Procedure (every time, before the first disruptive command)

1. **Inventory the live session** (read-only):
   - graphical session id, seat, state: `loginctl list-sessions`, `loginctl show-session <id>`
   - compositor PID + start time: `ps -o pid,lstart,cmd -C gnome-shell`
   - active RDP connections: established sockets on the RDP port (`ss -tnp state established '( sport = :3389 )'`) and the RDP daemon journal
   - what is running in the session: terminals and their children (agents, tests, builds)
2. **Classify every planned command:**

   | Class | Effect | Examples |
   |---|---|---|
   | `none` | No effect on the session or the connection | reading state, journals, files; editing a file not yet loaded |
   | `reconnect` | The current RDP connection drops or its picture changes; the session survives | restarting the per-user RDP daemon, changing share mode, credentials, certificate; display mode/layout change; connector off/on; VT switch |
   | `session-ending` | The graphical session may end (all its apps die) | restarting display manager / compositor / session units, logout, reboot, toggling the system remote-login path that spawns or replaces a session, kernel/driver/EDID changes that need a reload, killing session processes, upgrading the compositor/RDP stack |

   When unsure, classify one level **higher**. A change that creates or removes
   virtual monitors (RDP "extend") is `session-ending` on hosts where it has
   crashed the compositor before (see the host runbook).
3. **Signal and analyse risk — before executing, not after.** For every
   command above `none`, tell the user:
   - what will happen to the connection and to the session;
   - what can be lost (list the running work found in step 1);
   - how likely it is and why (evidence, prior incidents);
   - how to recover / roll back;
   - a `none` alternative, if one exists (e.g. apply at next login, at next reconnect, or in a maintenance window).
4. **The decision is the user's.** Wait for an explicit go for **that** action.
   An earlier approval does not extend to a new disruptive command. "Fix it"
   is not consent to end the session. No answer means no.
5. **Read back after.** Repeat step 1 and compare: same session id, same
   compositor PID, the connections the user agreed to lose and no others.
   Report any difference immediately, with the recovery path.

## Detector

The violation is mechanical to detect: a change in graphical session id or
compositor PID, or an RDP disconnect, between the step-1 inventory and the
step-5 readback **without** a recorded user go for a command of that class.
Any such difference is reported as an incident, never silently.

## Recovery hints (when a session already died)

- Processes outside the compositor may survive (shell children, user services):
  list user processes started before the crash and report them.
- Agent sessions (e.g. Claude Code) keep a transcript on disk and can usually
  be resumed (`claude --resume <id>` from the same working directory) —
  resuming is itself an action on the user's desktop: offer it, do not do it.

## Complements

| Skill | Role |
|---|---|
| `shared-infra-sot` | Host runbooks (RDP model, known crashes) live in `lakenbeach/holding-shared-infra` |
| `agent-self-evolution` | Record the incident if this rule was broken |
