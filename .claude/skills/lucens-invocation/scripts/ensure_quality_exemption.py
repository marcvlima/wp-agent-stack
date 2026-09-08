#!/usr/bin/env python3
"""A vendored skill is not the consumer repo's code surface.

Measured 2026-09-08, across the whole holding fleet: vendoring this package's
`scripts/lucens_client.py` and its tests into `.claude/skills/` and
`.agents/skills/` switched quality-guard's **python** surface ON in 14
repositories that have no Python of their own. `pytest -q` then ran at the repo
root, collected nothing (pytest skips dot-directories), exited 5, and the gate
went red — blocking every commit in those repos, ours and everyone else's.

The scripts and tests of a vendored skill are authored and gated in
`holding-central-ai-assets`, where the package lives and where its own tests
run. In a consumer repo they are an upstream artifact, exactly like a vendored
bundle: `exemptions.generated` is where they belong.

Usage:  ensure_quality_exemption.py <path to quality-surfaces.yaml>
Idempotent; exits 0 and changes nothing when both globs are already exempt.
"""
from __future__ import annotations

import sys
from pathlib import Path

WANTED = ["**/.claude/skills/**", "**/.agents/skills/**"]


def ensure(text: str) -> str:
    """Return `text` with both vendored-skill globs present under exemptions.generated."""
    lines = text.splitlines()
    out: list[str] = []
    in_exemptions = False
    generated_line = -1
    seen: set[str] = set()

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("exemptions:"):
            in_exemptions = True
        elif in_exemptions and stripped.startswith("generated:"):
            generated_line = len(out)
            for glob in WANTED:
                if glob in line:
                    seen.add(glob)
            if "[" in line and "]" in line:  # inline list form
                missing = [g for g in WANTED if g not in line]
                if missing:
                    head, _, tail = line.rpartition("]")
                    sep = "" if head.rstrip().endswith("[") else ", "
                    line = head + sep + ", ".join(f'"{g}"' for g in missing) + "]" + tail
                seen.update(WANTED)
        elif generated_line >= 0 and stripped.startswith("- "):
            for glob in WANTED:
                if glob in line:
                    seen.add(glob)
        elif stripped and not line[:1].isspace() and not stripped.startswith("#"):
            in_exemptions = False
        out.append(line)

    missing = [g for g in WANTED if g not in seen]
    if missing:
        if generated_line >= 0:
            for glob in reversed(missing):
                out.insert(generated_line + 1, f'    - "{glob}"')
        else:
            if not in_exemptions and not any(l.strip().startswith("exemptions:") for l in out):
                out.append("exemptions:")
            out.append("  generated:")
            for glob in missing:
                out.append(f'    - "{glob}"')

    result = "\n".join(out)
    return result if result.endswith("\n") else result + "\n"


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        print(__doc__)
        return 2
    path = Path(argv[0])
    if not path.exists():
        print(f"no quality-surfaces.yaml at {path}")
        return 0
    before = path.read_text()
    after = ensure(before)
    if after != before:
        path.write_text(after)
        print("quality exemptions added")
    else:
        print("quality exemptions present")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main(sys.argv[1:]))
