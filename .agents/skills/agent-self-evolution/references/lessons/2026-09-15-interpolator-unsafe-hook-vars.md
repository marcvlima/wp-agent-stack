# 2026-09-15 — Hook command string scanned as required env

**Category:** `interpolator-unsafe-hook-vars`

## Failure card

- **Symptom:** `pre_tool_use hook (project/settings) failed, ignored: hook not executed: required env var(s) not set: ${d}`
- **Claimed:** the quality/evolution guard hook was running.
- **True:** the host interpolates `$NAME` / `${NAME}` in the hook *command string* and refuses exec when that name is unset. `for d in … $d` in the inlined acquire recipe is a shell loop variable, not an env var. The hook never ran (fail-open).
- **Cost:** every PreToolUse in the session skipped the gate; founder had to stop the turn and name the error.

## Generalized rule

**A hook command string MUST only interpolate names the host process always has (typically `HOME` and `PATH`). Acquire loops, `$?`, `$SRC`, `$TMP`, `$d` belong in a file the host does not scan (bootstrap script), never in the command string. A generator that emits those tokens is broken; reinstall must rewrite already-poisoned recipes, not skip them because they already mention bootstrap.**

Detection: hook command contains `$d` / `${d}` / `$?` / `$SRC` / `$TMP` → do not exec; rewrite.

## Action plan

- `evolution-guard` `InstallRecipe` / `evHookCmd` match quality-guard: bootstrap file holds the loop; hook string is interpolator-safe; rewrite migrates poisoned bootstrap recipes.
- Tests: `TestEvHookCmdInterpolatorSafe`, `TestRewritePoisonedBootstrapRecipe`, quality-guard install writes no unsafe `$NAME`.
- Reinstall on every checkout whose `.claude/settings.json` still inlined `$d`.
