---
name: local-inference-policy
description: Mandatory rules and architecture for the local inference model, the Connector, and the Gateway. Dictates the default model (gemma-4-26b-a4b-1gpu), architecture, proper lifecycle management (stop/start), and forbids bypassing the Gateway.
---

# Local Inference Policy & Architecture (NON-NEGOTIABLE)

This skill dictates the unbreakable rules regarding the local inference ecosystem within RiseGen, detailing the architecture between the Connector, Model Runtime, and Gateway.

## 1. The Default Local Model Mandate
By explicit founder mandate, the **default and ONLY local inference model** for the code lane is:
`gemma-4-26b-a4b-1gpu` (Gemma 4 26B-A4B AWQ + MTP, 1x GPU, 120k context, explicitly managed by the connector).

- **FORBIDDEN:** Agents are strictly forbidden from changing, modifying, or lowering the performance configurations (like max context or MTP tokens) of this model, or replacing it with another model/quant, without **explicit prior authorization from the founder**.
- **FORBIDDEN:** Agents must not disable MTP to "save memory" or "fix OOMs" without founder approval.

## 2. Architecture: Connector, Model Runtime, and Gateway
The local inference stack is strictly composed of the following layers. **Never invent direct paths that bypass them.**

1. **Inference Connector (Go CLI - port 8000 internally):**
   - Discovers hardware, maps capabilities to the catalog, and provisions the local engine (vLLM).
   - Serves the model internally (`gemma-4-26b-a4b-1gpu` and its recipe names).
   - Responsible for sending heartbeats to the Platform Gateway to announce the node's availability.

2. **Model Runtime (Python/Uvicorn - port 8001):**
   - Acts as a proxy and translation layer (applying model-specific templates, routing, stripping hardware suffixes like `-1gpu`).
   - Forwards inbound traffic from the Gateway into the vLLM engine.
   - The Gateway consumes *this* layer, not the engine directly.

3. **Platform Gateway (nex-global.risegen.ai):**
   - The central nervous system of RiseGen.
   - Routes global traffic to the active local nodes based on heartbeats.
   - **FORBIDDEN:** Agents MUST NOT consume or probe local models directly on `127.0.0.1:8000` or `8001` for inference tasks. **All inference consumption MUST go through the Gateway (`https://nex-global.risegen.ai/v1/chat/completions`) using the registered API keys (e.g., from `~/.risegen/credentials.json`), unless explicitly authorized by the founder.**

## 3. Lifecycle Management: Starting and Stopping
Never use raw `kill`, `pkill`, or ad-hoc scripts to stop the engine. Never run `vllm serve` manually.

### Access & Credentials
- All commands that alter the connector service MUST run under the `risegenai` sudo privileges (the password is in the holding-general-secrets repo).
- Sudo execution pattern: `echo 'risegenai' | sudo -S <command>`

### Stopping the Model
To stop the local inference engine and free the VRAM properly (avoiding zombie CUDA contexts):
```bash
echo 'risegenai' | sudo -S systemctl stop risegen-connector-gemma4.service
```

### Starting / Redeploying the Model
To start or apply a new configuration:
```bash
echo 'risegenai' | sudo -S systemctl restart risegen-connector-gemma4.service
```
Always check the logs after starting to ensure the engine is fully warm and the heartbeat reports `models_reported=1`:
```bash
echo 'risegenai' | sudo -S journalctl -u risegen-connector-gemma4.service -n 50 -f
```

## 4. Agent Guidelines
- If a model OOMs, look for connector-level config flags (like `--gpu-memory-utilization`) to adjust budget safely, rather than stripping features (like context size or MTP).
- The official model ID to request from the Gateway is exactly `gemma-4-26b-a4b-1gpu`. The Gateway routes it correctly.
