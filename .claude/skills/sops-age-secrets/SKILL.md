---
name: sops-age-secrets
description: >-
  MANDATORY holding SOPS+age secrets skill. Classify first - general
  project-independent secrets go only to holding-general-secrets via SOPS;
  product secrets go to the product repo via SOPS. Encrypt allowlisted dotenv
  to secrets.enc.yaml; decrypt with off-repo age key to secrets.env. Never
  commit age.key or plaintext env. ADRs 0003 and 0004.
version: 1.0.4
---

# Skill: sops-age-secrets (v1.0.4)

**Holding-wide · MANDATORY** for storing secrets in git for multi-machine use
(**product** repos and **`holding-general-secrets`**).

**ADR:** `docs/decisions/0003-sops-age-secrets-holding-standard.md`  
**General secrets ADR:** `docs/decisions/0004-general-secrets-repo.md`  
**This package is self-contained:** scripts under `scripts/` are **OS-agnostic** (macOS, Linux, WSL). No AGENTS.md reinforcement is required beyond installing this skill via APM.

***
## Classification first (NON-NEGOTIABLE)

Before encrypting or inventing a secrets path, classify the credential:

| Class | Where it MUST live | Mechanism |
|---|---|---|
| **General** — independent of any one product/project/domain | **`holding-general-secrets` only** | **SOPS+age** (`secrets.enc.yaml`; wrappers `scripts/encrypt-secrets.sh` / `sync-secrets.sh`) |
| **Product / project** — owned by one product, domain, or host role | That product/tooling repo | **SOPS+age** via **this skill** |

Policy of record for general secrets:
`holding-general-secrets` → ADRs 0002 + 0003

**Everything general, independent of project, is saved in `holding-general-secrets` via SOPS.**
Do not put general keys (e.g. Cloudflare **account** API token spanning all zones)
into product `secrets.enc.yaml`. Do not put product-only keys into the general repo.
Same skill scripts; different repo paths and allowlists.

***
## When to use

- Secrets must work on **more than one machine** via git;
- Encrypt / re-encrypt / decrypt secrets for a holding project;
- Bootstrap a **fresh machine** after restoring the age private key;
- A project needs a secrets layout for the first time;
- The secret is **product/project-scoped** (after classification above).

***
## Non-negotiables

| Commit | Never commit |
|---|---|
| `secrets.enc.yaml` (ciphertext) | `age.key` (private) |
| `.sops.yaml` (public age recipients) | plaintext `.env` / `secrets.env` |
| these scripts | tokens, Wi-Fi PSKs, modem passwords in cleartext |

Local runtime: `secrets.env` mode **600**. Private key mode **600**.

***
## Package layout

```
sops-age-secrets/
├── SKILL.md
├── skill.json
├── scripts/
│   ├── lib.sh                 # portable helpers
│   ├── encrypt-secrets.sh     # ENV_FILE + ENCRYPTED_OUT → ciphertext
│   └── sync-secrets.sh        # ENCRYPTED_IN → secrets.env
└── references/dev-host-layout.md
```

Reference ciphertext for the holding edge stack:  
`holding-central-ai-assets/dev-host/secrets.enc.yaml`  
(project wrappers: `dev-host/scripts/*.sh` call these OS-agnostic scripts).

***
## Prerequisites (any OS)

```bash
# macOS
brew install sops age

# Debian/Ubuntu (example)
# sudo apt install age && install sops from GitHub releases

command -v sops && command -v age-keygen
```

Create age key once (backup offline — never git):

```bash
mkdir -p "${XDG_CONFIG_HOME:-$HOME/.config}/risegen/dev-host"
chmod 700 "${XDG_CONFIG_HOME:-$HOME/.config}/risegen/dev-host" 2>/dev/null || true
age-keygen -o "$HOME/.config/risegen/dev-host/age.key"
chmod 600 "$HOME/.config/risegen/dev-host/age.key"
age-keygen -y "$HOME/.config/risegen/dev-host/age.key"   # public recipient for .sops.yaml
```

***
## Encrypt (update secrets → git)

From **any** OS, with the private key and a source dotenv:

```bash
# Locate skill scripts (APM install path examples)
SKILL_SCRIPTS="$HOME/.claude/skills/sops-age-secrets/scripts"
# or: .../apm_modules/.../sops-age-secrets/scripts
# or: holding-central-ai-assets/sops-age-secrets/scripts

ENV_FILE="/absolute/path/to/source.env" \
ENCRYPTED_OUT="/absolute/path/to/repo/secrets.enc.yaml" \
AGE_KEY_FILE="$HOME/.config/risegen/dev-host/age.key" \
bash "$SKILL_SCRIPTS/encrypt-secrets.sh"
```

Optional: `ALLOW_KEYS="KEY1 KEY2 ..."`.

Then: **commit only** `secrets.enc.yaml` (and `.sops.yaml` if recipients changed).

### Holding dev-host convenience wrapper

```bash
cd holding-central-ai-assets/dev-host
./scripts/encrypt-secrets.sh    # sets ENV_FILE / ENCRYPTED_OUT defaults for this project
```

***
## Sync (decrypt on a machine)

```bash
ENCRYPTED_IN="/absolute/path/to/repo/secrets.enc.yaml" \
AGE_KEY_FILE="$HOME/.config/risegen/dev-host/age.key" \
SECRETS_OUT_DIR="$HOME/.config/risegen/dev-host" \
bash "$SKILL_SCRIPTS/sync-secrets.sh"
# → $SECRETS_OUT_DIR/secrets.env (mode 600)
```

Wrapper:

```bash
cd holding-central-ai-assets/dev-host && ./scripts/sync-secrets.sh
```

Use:

```bash
set -a && . "$HOME/.config/risegen/dev-host/secrets.env" && set +a
```

***
## Fresh machine checklist

1. Install `sops` + `age`
2. Restore `age.key` out-of-band → mode 600
3. `git clone` / `git pull` the repo that holds `secrets.enc.yaml`
4. `sync-secrets.sh` with `ENCRYPTED_IN=...`
5. Never put `age.key` in the clone

***
## APM install (consumer repo)

```yaml
# apm.yml
dependencies:
  apm:
  - marcvlima/holding-central-ai-assets/sops-age-secrets
```

```bash
apm install
# fallback: cp -R holding-central-ai-assets/sops-age-secrets <repo>/.claude/skills/
```

After install, agents invoke this skill by name/packageId; no extra AGENTS.md prose required.

***
## Agent rules (short)

0. **Classify first:** general → `holding-general-secrets`; product → this skill.
1. Prefer these scripts over inventing crypto or paths.
2. Before commit: no `age.key`, no `secrets.env`, no plaintext secret `.env`.
3. Do not print secret values.
4. If `sops`/`age` missing: install, one retry — never fall back to plaintext in git.
