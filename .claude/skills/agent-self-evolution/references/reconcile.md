# Reconcile matrix + skill across repos

## Canonical home

`holding-central-ai-assets/agent-self-evolution/` (APM package).

## What reconcile does

1. Ensures consumer `apm.yml` lists  
   `marcvlima/holding-central-ai-assets/agent-self-evolution`
2. Vendors skill into `.agents/skills/agent-self-evolution/` and/or `.claude/skills/agent-self-evolution/`
3. Ensures repo `AGENTS.md` contains the **Holding matrix** block (idempotent marker)
4. Ensures `CLAUDE.md` imports AGENTS when that is the project convention

## New repository checklist

- [ ] Create `AGENTS.md` with Holding matrix block first
- [ ] `CLAUDE.md` → `@AGENTS.md`
- [ ] `apm.yml` dependency on `agent-self-evolution` (+ other core skills)
- [ ] `memory-bank/` skeleton
- [ ] Run `scripts/reconcile-agents-matrix.sh` from holding after first push of the skill

## Script

From holding-central-ai-assets:

```bash
bash agent-self-evolution/scripts/reconcile-agents-matrix.sh
# optional:
# REPOS="/path/a /path/b" bash agent-self-evolution/scripts/reconcile-agents-matrix.sh
```

## After reconcile

Founder-authorized commit per repo:

```text
chore(agents): install agent-self-evolution + holding matrix stub
```
