#!/usr/bin/env bash
# Canonical curl caller for Lucens's A2A door — discovery, one call, or one turn.
#
#   lucens-call.sh contract
#   lucens-call.sh call mind.state '{}'
#   lucens-call.sh ask "o que você aprendeu no último lab?"
#
# Env: LUCENS_A2A_BASE_URL (or LUCENS_A2A_URL) · LUCENS_AUTH_TOKEN · LUCENS_CALLER
#
# NOTE: this wrapper does NOT follow a task envelope to a terminal state. For any
# long operation, or anything a human waits on, use scripts/lucens_client.py —
# it implements the whole contract (references/client-conformance.md).
set -euo pipefail

BASE="${LUCENS_A2A_BASE_URL:-${LUCENS_A2A_URL:-}}"
TOKEN="${LUCENS_AUTH_TOKEN:-}"
CALLER="${LUCENS_CALLER:-lucens-call.sh}"
UA="${LUCENS_USER_AGENT:-lucens-invocation/1.0 (+risegen holding client)}"

if [[ -z "$BASE" || -z "$TOKEN" ]]; then
  echo "lucens_not_configured: set LUCENS_A2A_BASE_URL and LUCENS_AUTH_TOKEN" >&2
  echo "  canonical base: https://lucens.risegen.ai  (never an IP, never loopback)" >&2
  exit 2
fi
if [[ -n "${LUCENS_MESH_BASE_URL:-}${MESH_AUTH_TOKEN:-}" ]]; then
  echo "warning: LUCENS_MESH_BASE_URL/MESH_AUTH_TOKEN are dead names (the mesh was destroyed)" >&2
fi

DOOR="${BASE%/}"
[[ "$DOOR" == */a2a ]] || DOOR="$DOOR/a2a"

hdrs=(-H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json"
      -H "Accept: application/json" -H "User-Agent: $UA")

case "${1:-}" in
  contract)
    curl -sS "${hdrs[@]}" "$DOOR"
    ;;
  call)
    op="${2:?op required}"
    params="${3:-{\}}"
    python3 - "$op" "$params" "$CALLER" <<'PY' > /tmp/lucens-call.$$.json
import json, sys
op, params, caller = sys.argv[1], json.loads(sys.argv[2] or "{}"), sys.argv[3]
params.setdefault("caller", caller)
json.dump({"op": op, "params": params}, sys.stdout)
PY
    curl -sS -X POST "${hdrs[@]}" --data-binary "@/tmp/lucens-call.$$.json" "$DOOR"
    rm -f "/tmp/lucens-call.$$.json"
    ;;
  ask)
    shift
    python3 - "$*" "$CALLER" <<'PY' > /tmp/lucens-ask.$$.json
import json, sys
note = ("(Floor note: bids must use the exact labels "
        "Salience: / Reason: / Intended act: with a dot decimal.)")
json.dump({"op": "mind_turn",
           "params": {"message": f"{sys.argv[1]}\n\n{note}",
                      "tokens_max": 120000,
                      "caller": sys.argv[2]}}, sys.stdout)
PY
    curl -sS -X POST "${hdrs[@]}" --data-binary "@/tmp/lucens-ask.$$.json" "$DOOR"
    rm -f "/tmp/lucens-ask.$$.json"
    ;;
  *)
    sed -n '2,12p' "$0"
    exit 2
    ;;
esac
