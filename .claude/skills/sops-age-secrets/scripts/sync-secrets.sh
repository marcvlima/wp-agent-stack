#!/usr/bin/env bash
# sync-secrets.sh — OS-agnostic: decrypt SOPS+age ciphertext → local secrets.env (mode 600).
#
# Required env:
#   ENCRYPTED_IN      path to secrets.enc.yaml (in a git checkout)
# Optional:
#   AGE_KEY_FILE      private age key (default ~/.config/risegen/dev-host/age.key)
#   SECRETS_OUT_DIR   directory for secrets.env (default ~/.config/risegen/dev-host)
#   SECRETS_OUT       full path override for secrets.env
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib.sh
. "$SCRIPT_DIR/lib.sh"

require_cmd sops

AGE_KEY_FILE="$(abs_path "$(default_age_key)")"
ENCRYPTED_IN="${ENCRYPTED_IN:-}"
OUT_DIR="$(default_secrets_out_dir)"
OUT="${SECRETS_OUT:-$OUT_DIR/secrets.env}"

if [ -z "$ENCRYPTED_IN" ]; then
  cat >&2 <<'EOF'
usage: ENCRYPTED_IN=/path/to/secrets.enc.yaml sync-secrets.sh

Optional:
  AGE_KEY_FILE=...
  SECRETS_OUT_DIR=...   (default ~/.config/risegen/dev-host)
  SECRETS_OUT=...       (full path to secrets.env)
EOF
  exit 1
fi

ENCRYPTED_IN="$(abs_path "$ENCRYPTED_IN")"
OUT="$(abs_path "$OUT")"
OUT_DIR="$(dirname "$OUT")"

[ -r "$ENCRYPTED_IN" ] || { echo "ERR: ENCRYPTED_IN not readable: $ENCRYPTED_IN" >&2; exit 1; }
[ -r "$AGE_KEY_FILE" ] || {
  echo "ERR: age key not found at $AGE_KEY_FILE (mode 600, never committed)" >&2
  echo "     restore it out-of-band, then retry." >&2
  exit 2
}

secure_dir "$OUT_DIR"

TMP="$(make_temp)"
cleanup() { rm -f "$TMP"; }
trap cleanup EXIT

SOPS_AGE_KEY_FILE="$AGE_KEY_FILE" sops --decrypt "$ENCRYPTED_IN" > "$TMP"

# YAML "KEY: value" or "KEY: \"value\"" → dotenv KEY=value (portable awk)
awk '
  /^[A-Za-z_][A-Za-z0-9_]*:/ {
    key=$1
    sub(/:$/, "", key)
    val=$0
    sub(/^[^:]+:[[:space:]]*/, "", val)
    gsub(/\r/, "", val)
    if (val ~ /^".*"$/) { sub(/^"/, "", val); sub(/"$/, "", val) }
    if (val ~ /^'\''.*'\''$/) { sub(/^'\''/, "", val); sub(/'\''$/, "", val) }
    print key "=" val
  }
' "$TMP" > "$OUT"

secure_file "$OUT"
trap - EXIT
rm -f "$TMP"

count="$(grep -c '=' "$OUT" 2>/dev/null || echo 0)"
echo "OK: wrote $OUT (mode 600)"
echo "    source: $ENCRYPTED_IN"
echo "    keys present: $count"
