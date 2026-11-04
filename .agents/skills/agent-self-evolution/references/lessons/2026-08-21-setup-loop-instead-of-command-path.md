# Setup loop instead of command path

## Category: `setup-loop-instead-of-command-path`

## Failure card

SYMPTOM: After a successful off, the next on timed out. The agent opened pairing again and asked the founder to re-join the device.

CLAIMED: The device left the mesh; recovery is re-pair.

TRUE: The actuator published four MQTT `/set` topics (friendly name, IEEE, and endpoint `/l2`) plus a Zigbee `/get` for one gang change. The protocol documents a single `…/<friendly>/set` JSON. Tuya modules timeout on successive commands. A GET timeout is not evidence the device left the network.

COST: Founder time in repeated pairing; trust; the on command was never retried on the canonical path.

## Root process failure (not just technical bug)

Treating human setup (pair / reset / reinstall) as the next step after a command timeout, instead of comparing the local request shape to the protocol SoT.

## Rule (MUST / NEVER — generalized, category-level)

MUST compare a failed actuation to the protocol's canonical request (one write, documented topic, documented payload) before asking a human to repeat setup.

NEVER recover a timed-out command by repeating pairing, factory reset, or reinstall until duplicate writes, extra reads, and alias floods are ruled out.

## Detection (how the next agent notices the category)

- Next action after a timeout is "put it in pairing / reset / reinstall"
- The tool log shows more than one publish for one logical command
- Unverified reason is a read timeout, not a join/leave event

## Related skills

- `research-before-asserting`
- `mandatory-soft-skills-for-agents`
- `agent-self-evolution`

## Evidence pointers (no secrets)

- Protocol: zigbee2mqtt.io MQTT `FRIENDLY_NAME/set` (JSON, one topic)
- Community: Koenkk/zigbee2mqtt#27941 (Tuya successive-toggle timeout)
- Tool: Spatium `z2m_set` `publishZ2MPayload` previously published friendly + IEEE + endpoint topics
