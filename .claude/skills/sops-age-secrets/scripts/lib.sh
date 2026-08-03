#!/usr/bin/env bash
# Portable helpers for sops-age-secrets (POSIX-ish bash; macOS, Linux, WSL).
# shellcheck shell=bash

set -euo pipefail

# Expand ~ and relative paths; no OS-specific home tricks.
abs_path() {
  local p="${1:?}"
  case "$p" in
    /*) printf '%s\n' "$p" ;;
    ~*) printf '%s\n' "${p/#\~/$HOME}" ;;
    *)  printf '%s\n' "$(pwd)/$p" ;;
  esac
}

require_cmd() {
  local c
  for c in "$@"; do
    command -v "$c" >/dev/null 2>&1 || {
      echo "ERR: required command not found: $c" >&2
      echo "     install: sops (https://github.com/getsops/sops) and age (https://github.com/FiloSottile/age)" >&2
      exit 127
    }
  done
}

# mktemp portable: prefer TMPDIR; fall back to /tmp
make_temp() {
  local suffix="${1:-}"
  if [ -n "$suffix" ]; then
    mktemp "${TMPDIR:-/tmp}/sops-age.XXXXXX${suffix}"
  else
    mktemp "${TMPDIR:-/tmp}/sops-age.XXXXXX"
  fi
}

# chmod 600 if the OS supports symbolic modes (all modern Unix do)
secure_file() {
  local f="${1:?}"
  chmod 600 "$f" 2>/dev/null || chmod u=rw,go= "$f"
}

secure_dir() {
  local d="${1:?}"
  mkdir -p "$d"
  chmod 700 "$d" 2>/dev/null || chmod u=rwx,go= "$d"
}

default_age_key() {
  # Prefer XDG-style config; works on Linux and macOS when HOME is set.
  printf '%s\n' "${AGE_KEY_FILE:-$HOME/.config/risegen/dev-host/age.key}"
}

default_secrets_out_dir() {
  printf '%s\n' "${SECRETS_OUT_DIR:-$HOME/.config/risegen/dev-host}"
}
