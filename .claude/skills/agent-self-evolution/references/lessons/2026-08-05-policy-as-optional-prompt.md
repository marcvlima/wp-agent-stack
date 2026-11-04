# Lesson: policy-as-optional-prompt

**Date:** 2026-08-05  
**Category:** `policy-as-optional-prompt`  
**Cost:** Founder correction; quality policy treated as optional; tests written but not committed/gated without being asked.

## Symptom
Agent completes production work, even writes tests, then **asks** the founder whether to run the quality gate or commit tests — as if compliance were optional.

## Claimed
"Partial compliance" + offer to finish tests if the user wants.

## True
Holding unit-test + quality-guard policy is **non-negotiable**. Asking re-delegates mandatory process to the human. Industry evidence: AGENTS.md compliance is probabilistic (~3.5% proactive policy reads); only hooks/Stop/commit gates enforce.

## Detection
- Agent message offers "quer que eu rode testes / faça commit?" after prod edits
- Session ends with prod dirty and no green `.risegen/quality-gate.json`
- Commit without paired tests

## Prevention (harness)
1. quality-guard v1.1 **Stop block** when prod dirty without green marker
2. Matrix always-on: never ask founder to authorize mandatory tests
3. PreToolUse still blocks `git commit` / `--no-verify`
4. Self-evolve this category when it recurs

## Action
Do not ask. Run `quality-guard run`, fix red tests, commit with paired tests.
