#!/bin/sh
# plan-guard bootstrap — acquire binary then exec (mirror quality-bootstrap).
set -eu
DEST_DIR="${HOME}/.local/bin"
DEST="${DEST_DIR}/plan-guard"
REPO="marcvlima/holding-central-ai-assets"

find_guard() {
  command -v plan-guard 2>/dev/null && return 0
  [ -x "$DEST" ] && echo "$DEST" && return 0
  return 1
}
local_src() {
  for d in "${HOLDING_CENTRAL_AI_ASSETS:-}" "$HOME/Developer/holding-central-ai-assets" "$HOME/Developer/risegen/holding-central-ai-assets"; do
    [ -n "$d" ] || continue
    [ -d "$d/plan-guard/cmd/plan-guard" ] && echo "$d/plan-guard" && return 0
  done
  return 1
}
acquire() {
  mkdir -p "$DEST_DIR"
  SRC="$(local_src || true)"
  if [ -n "$SRC" ] && command -v go >/dev/null 2>&1; then
    ( cd "$SRC" && CGO_ENABLED=0 go build -trimpath -o "$DEST" ./cmd/plan-guard ) >/dev/null 2>&1 && chmod +x "$DEST" && echo "$DEST" && return 0
  fi
  command -v go >/dev/null 2>&1 || { echo "[plan-bootstrap] go not found" >&2; return 1; }
  command -v gh >/dev/null 2>&1 || { echo "[plan-bootstrap] gh not found" >&2; return 1; }
  tmp="$(mktemp -d)"
  if gh repo clone "$REPO" "$tmp/hca" -- --depth 1 --quiet >/dev/null 2>&1 &&
     ( cd "$tmp/hca/plan-guard" && CGO_ENABLED=0 go build -trimpath -o "$DEST" ./cmd/plan-guard ) >/dev/null 2>&1; then
    rm -rf "$tmp"; chmod +x "$DEST"; echo "$DEST"; return 0
  fi
  rm -rf "$tmp"; return 1
}
export PATH="${DEST_DIR}:${PATH}"
GUARD="$(find_guard || true)"
[ -n "$GUARD" ] || GUARD="$(acquire || true)"
[ -n "$GUARD" ] || { echo "[plan-bootstrap] plan-guard missing" >&2; exit 1; }
exec "$GUARD" "$@"
