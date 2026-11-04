# 2026-09-19 — Restart issued without naming the service failure

**Category:** `restart-without-named-failure`

## Failure card

- **Symptom:** A Spatium agent restarted the Zigbee2MQTT add-on (a side-effecting,
  hard-to-reverse service action) without first naming the service failure that
  justified the restart.
- **Claimed:** the restart was the remedy, and the underlying service failure was
  either already known or not required to be stated.
- **True:** the diagnosis tool that names the failure (`addon_logs` for the add-on,
  `zigbee_network_info` for the coordinator) was available and was not called before
  the restart. The system prompt listed "check addon_logs for zigbee2mqtt, or
  restart the add-on via manage_addon" as **alternatives** ("or"), so the agent took
  the restart branch without ever naming what was failing. The restart was issued
  blind: no evidence of *why* the service was down, no read-back that the named
  failure was the one the restart addressed.
- **Cost:** a service restart performed without a named cause — the restart may not
  address the real failure, the failure is not recorded for the next diagnosis, and
  the agent's report cannot say what it fixed. Trust in the recovery path erodes
  because the action is not tied to evidence.

## Generalized rule

**A side-effecting, hard-to-reverse remedy (restart, reinstall, reset) MUST be
preceded by a named, evidenced failure — never by a symptom alone. When a prompt
lists a diagnosis step and a remedy as alternatives ("check logs **or** restart"),
the diagnosis is a prerequisite of the remedy, not a co-equal option; the remedy
branch is gated on the diagnosis having run. If the diagnosis tool is unavailable
or returns nothing, say so and stop — do not restart blind.**

Detection: a tool call issues a restart/reinstall/reset and the preceding tool calls
in the same turn contain no diagnosis call (logs, status, health) that names the
failure; or a prompt/flow lists a diagnosis step and a remedy joined by "or"; or a
report says "restarted X" but cannot state what failure the restart addressed.

## Action plan

- Matrix always-on MUST line added (below): "Name the failure before the remedy."
- Product prompt (`agent/system-prompt.ts`) must gate the restart branch on the
  diagnosis having run — change the "or" into a prerequisite, or the host must
  require a named failure before a restart tool call is accepted.
- This lesson + INDEX row.

## Evidence pointers (no secrets)

- `agent/system-prompt.ts` — the "or" that made `addon_logs` optional before
  `manage_addon` restart.
- `tools/ha-mcp/internal/tools/recover_radio.go` — the restart path
  (`restartZigbee2mqtt`) that fires on bridge-offline without naming the failure.
- `tools/ha-mcp/internal/tools/addon_logs.go` — the available diagnosis tool that
  names the failure and was not called first.