#!/usr/bin/env bash
# Every paired test of the lucens-invocation package. Standard library only.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
fail=0
for t in "$HERE"/test_*.py; do
  echo "== $(basename "$t")"
  python3 "$t" -v 2>&1 | tail -3 || fail=1
  python3 "$t" >/dev/null 2>&1 || fail=1
done
if [[ "$fail" != "0" ]]; then
  echo "FAILED" >&2
  exit 1
fi
echo "all green"
