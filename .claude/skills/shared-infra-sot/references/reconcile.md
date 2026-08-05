# Reconcile — install shared-infra-sot on every holding repository

## What reconcile does

For each target repo that exists on disk:

1. Ensures `apm.yml` lists `marcvlima/holding-central-ai-assets/shared-infra-sot`
2. Vendors this skill into `.agents/skills/shared-infra-sot` and `.claude/skills/shared-infra-sot`
3. Injects or refreshes the `<!-- HOLDING-SHARED-INFRA-SOT:… -->` block in `AGENTS.md` (creates AGENTS.md if missing)

## Run

```bash
cd /path/to/holding-central-ai-assets
bash shared-infra-sot/scripts/reconcile-shared-infra-sot.sh
```

### Options

| Env | Meaning |
|---|---|
| `REPOS="/a /b"` | Explicit list of repo roots |
| `RISEGEN_ROOT=/Users/…/risegen` | Discover `*/` git repos under this root and add them |
| `DRY_RUN=1` | Print actions only |

## New repository checklist

- [ ] `apm.yml` depends on `shared-infra-sot` (+ usually `agent-self-evolution`)
- [ ] Run reconcile (or `apm install` then ensure AGENTS marker)
- [ ] Agent can open skill and cite `lakenbeach/holding-shared-infra`

## After skill version bump

1. Bump `skill.json` version
2. Re-run reconcile so vendored copies update
3. Commit consumers when founder authorizes
