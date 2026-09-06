# AI Assistant Council roster — L0 (always in context)

One line per seat, ≤15 tokens. 16 seats · no reserved seats.
The Moderator (strongest model) never holds a seat; the founder ratifies.

## Assistant delivery (founding seats)

1. **realtime-voice-pipeline** — full-duplex audio, VAD, barge-in, end-to-end latency budgets
2. **llm-serving-efficiency** — inference serving, prefill/KV cache, quantization, speculative decoding
3. **orchestration-harness** — agent loop, tool calling, context injection, memory, MCP
4. **conversational-ux** — feedback signals, persona consistency, error recovery, multimodal cues
5. **grounding-safety** — hallucination control, guardrails, small-model truthfulness limits
6. **edge-performance-portability** — cross-hardware/OS tiers, thermal, degradation ladders
7. **speech-technologies** — streaming ASR, hotword biasing, TTS streaming, narrowband audio
8. **evaluation-benchmarks** — voice-agent benchmarks, latency measurement discipline, regression harnesses
9. **reliability-operations** — daemon lifecycle, failure modes, observability, session recovery
10. **product-strategy-market** — market bar, cost per interaction, competitive positioning

## AI research & generative AI (added v1.2.0)

11. **frontier-research-scaling** — scaling laws, reasoning RL, distillation, capability trajectory
12. **generative-media** — diffusion/flow image, video, music, voice cloning, provenance
13. **retrieval-knowledge** — RAG, hybrid/graph retrieval, memory, citations, freshness
14. **interpretability-model-science** — circuits, calibration, quantization damage, causal failure analysis
15. **human-ai-work-adoption** — jagged frontier, workflow fit, trust calibration, real task completion
16. **ai-governance-compliance** — EU AI Act, LGPD/GDPR, licences, biometric consent, C2PA

## Boundary with sibling councils

- Deep **training/serving engineering** (cluster topology, engine argv, kernels,
  fine-tuning recipes) belongs to `ai-ml-implementation-council`; seats 2 and 11
  here speak to the *assistant's* choices and escalate implementation there.
- **Brand/UI/UX** decisions belong to `agency-brainstorm`; **taxonomy, IA and
  navigation** to `product-taxonomy-council`. Seat 4 owns conversational
  interaction, not visual design systems.
