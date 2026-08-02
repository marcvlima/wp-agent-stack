#!/usr/bin/env bash
# encrypt-secrets.sh — OS-agnostic: allowlisted KEY=value dotenv → SOPS+age ciphertext.
#
# Required env:
#   ENV_FILE          path to source dotenv (plaintext)
#   ENCRYPTED_OUT     path to write secrets.enc.yaml (usually in a git repo)
# Optional:
#   AGE_KEY_FILE      private age key (default ~/.config/risegen/dev-host/age.key)
#   ALLOW_KEYS        space-separated key names (default: holding dev-host allowlist)
#   SOPS_AGE_RECIPIENT  public age recipient; default derived via age-keygen -y
#
# Never commit ENV_FILE or AGE_KEY_FILE. Commit only ENCRYPTED_OUT.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib.sh
. "$SCRIPT_DIR/lib.sh"

require_cmd sops age-keygen

AGE_KEY_FILE="$(abs_path "$(default_age_key)")"
ENV_FILE="${ENV_FILE:-}"
ENCRYPTED_OUT="${ENCRYPTED_OUT:-}"
ALLOW_KEYS="${ALLOW_KEYS:-CLOUDFLARE_API_TOKEN MODEM_ADMIN_USER MODEM_ADMIN_PASSWORD NOIP_DDNS_KEY_USERNAME NOIP_DDNS_KEY_PASSWORD NOIP_HOSTNAME MODEM_LABEL_PASSWORD}"

if [ -z "$ENV_FILE" ] || [ -z "$ENCRYPTED_OUT" ]; then
  cat >&2 <<'EOF'
usage: ENV_FILE=/path/to/.env ENCRYPTED_OUT=/path/to/secrets.enc.yaml encrypt-secrets.sh

Optional:
  AGE_KEY_FILE=...   private age key (default ~/.config/risegen/dev-host/age.key)
  ALLOW_KEYS="KEY1 KEY2 ..."
EOF
  exit 1
fi

ENV_FILE="$(abs_path "$ENV_FILE")"
ENCRYPTED_OUT="$(abs_path "$ENCRYPTED_OUT")"

[ -r "$ENV_FILE" ] || { echo "ERR: ENV_FILE not readable: $ENV_FILE" >&2; exit 1; }
[ -r "$AGE_KEY_FILE" ] || { echo "ERR: age key not found: $AGE_KEY_FILE" >&2; exit 2; }

OUT_DIR="$(dirname "$ENCRYPTED_OUT")"
mkdir -p "$OUT_DIR"

TMP_YAML="$(make_temp .yml)"
TMP_ENC="$(make_temp .enc)"
cleanup() { rm -f "$TMP_YAML" "$TMP_ENC"; }
trap cleanup EXIT

# dotenv KEY=value → YAML KEY: "value" (allowlisted only; skip comments/blank)
# Portable: no GNU-only sed; handle Windows CRLF via tr.
while IFS= read -r line || [ -n "$line" ]; do
  line="$(printf '%s' "$line" | tr -d '\r')"
  case "$line" in
    ''|\#*) continue ;;
  esac
  case "$line" in
    *=*) ;;
    *) continue ;;
  esac
  k="${line%%=*}"
  v="${line#*=}"
  # trim simple surrounding quotes on value
  case "$v" in
    \"*\") v="${v#\"}"; v="${v%\"}" ;;
    \'*\') v="${v#\'}"; v="${v%\'}" ;;
  esac
  case " $ALLOW_KEYS " in
    *" $k "*) printf '%s: "%s"\n' "$k" "$v" >> "$TMP_YAML" ;;
  esac
done < "$ENV_FILE"

[ -s "$TMP_YAML" ] || {
  echo "ERR: no allowlisted keys found in $ENV_FILE" >&2
  echo "     ALLOW_KEYS=$ALLOW_KEYS" >&2
  exit 3
}

PUBKEY="${SOPS_AGE_RECIPIENT:-}"
if [ -z "$PUBKEY" ]; then
  PUBKEY="$(age-keygen -y "$AGE_KEY_FILE")"
fi

# Encrypt via stdin/out — no OS-specific temp path dependency beyond mktemp
SOPS_AGE_KEY_FILE="$AGE_KEY_FILE" sops --age "$PUBKEY" --encrypt --input-type yaml --output-type yaml \
  "$TMP_YAML" > "$TMP_ENC"

# Atomic replace
mv -f "$TMP_ENC" "$ENCRYPTED_OUT"
secure_file "$ENCRYPTED_OUT"
trap - EXIT
rm -f "$TMP_YAML"

echo "OK: wrote $ENCRYPTED_OUT (encrypted)"
echo "    source: $ENV_FILE"
echo "    keys:   $(SOPS_AGE_KEY_FILE="$AGE_KEY_FILE" sops --decrypt "$ENCRYPTED_OUT" 2>/dev/null | awk -F': ' '/^[A-Za-z_][A-Za-z0-9_]*:/{print $1}' | tr '\n' ' ')"
echo "    Next: commit only the ciphertext. Keep age.key and ENV_FILE out of git."
