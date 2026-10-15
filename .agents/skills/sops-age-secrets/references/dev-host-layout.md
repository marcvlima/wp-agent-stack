# Reference implementation — `dev-host/`

Canonical scripts and ciphertext live under:

`holding-central-ai-assets/dev-host/`

## Files

| File | Role |
|---|---|
| `.sops.yaml` | age public recipient(s) for path_regex `.*secrets\.enc\.yaml$` |
| `secrets.enc.yaml` | SOPS-encrypted YAML; **committed** |
| `scripts/encrypt-secrets.sh` | Allowlisted keys from `ENV_FILE` (default engageRise `.env`) → encrypt |
| `scripts/sync-secrets.sh` | Decrypt → `~/.config/risegen/dev-host/secrets.env` |

## Commands

```bash
# Encrypt (machine that has age.key + source dotenv)
cd holding-central-ai-assets/dev-host
ENV_FILE=/path/to/.env ./scripts/encrypt-secrets.sh   # optional ENV_FILE
# default ENV_FILE: ~/Developer/engagerise/engageriseapp/.env

# Decrypt (any machine with age.key)
./scripts/sync-secrets.sh
```

## Env vars

| Variable | Default | Meaning |
|---|---|---|
| `AGE_KEY_FILE` | `~/.config/risegen/dev-host/age.key` | Private age key |
| `ENV_FILE` | engageRise app `.env` | Plaintext source for encrypt |
| `SECRETS_OUT_DIR` | `~/.config/risegen/dev-host` | Directory for `secrets.env` |

## Tools

- `sops` (Mozilla SOPS)
- `age` / `age-keygen`

## See also

- ADR 0003 — holding-wide standard
- Skill root: `sops-age-secrets/SKILL.md`
