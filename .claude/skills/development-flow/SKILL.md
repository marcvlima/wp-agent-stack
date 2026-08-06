# Development Flow — Rebuild & Redeploy Before Retest

Directive for any agent working across repositories: **after changing shared/infrastructure
components (platform, connector, CLI, engine), rebuild and redeploy the affected artifacts
before asking the user to test.** A code edit without redeploy is not yet testable.

## Plan fidelity (NON-NEGOTIABLE)

When a plan is **registered** for the work unit, that plan is **law**. No plan detailing
and no implementation may deviate from requirements and directives explicitly defined or
approved by the **founder** or **human developer** without an **explicit reconciliation**
recorded on disk (`plan-guard reconcile` / reconciliation log).

- If blocked: first **hunt alternatives that still fulfill the plan**.
- Only if impossible: **request** reconciliation — agents never self-approve.
- Silent descoping, unapproved pivots, and “skip this requirement” are process failures.

**Gate order before “ready to retest”:**

1. **plan-guard** green when a plan is active (`plan-guard run` → `status` valid YES)  
2. **quality-guard** green (paired tests)  
3. **rebuild + redeploy** (this skill)  
4. only then signal the user to retest  

Binary + skill: `plan-guard` / `plan-fidelity` in `holding-central-ai-assets`.

## Why this exists

Agent sessions span multiple repositories. A change in one repo (e.g. a platform auth fix)
is invisible to end-to-end tests until the changed component is rebuilt and, when applicable,
reinstalled into the runtime path. Asking the user to retest before this step is complete
wastes their time and breaks trust in the agent's feedback loop.

## The core directives (non-negotiable)

1. Before any "ready to test" or "please verify" message to the user, the agent MUST ensure all
   artifacts changed during the session are rebuilt and redeployed. This check is as mandatory
   as running lint/tests.
2. **Deployed Artifacts 100% Repository Independence (NON-NEGOTIABLE)**: NO deployed artifact
   (binaries, executables, plugins, configs, assets) may have any link or dependency on the
   source code repository (checkout). Deployed artifacts post-build are ALWAYS 100% autonomous
   and independent of the repository in any situation.

## Deployed Artifacts Independence Principles

- **Zero Repository Coupling Post-Build**: After build and deployment, binaries, executables, plugins,
  configuration files, and assets MUST NEVER depend on or search for files inside the source repository
  directory (checkout).
- **System-level Runtime Paths Only**: The deployed runtime on the machine (e.g., `~/.local/bin/rgai`,
  `~/.risegen/bin/rgai-engine`, `~/.risegen/plugins/`, VS Code installed extensions) must load and
  resolve 100% of its resources from system deployment directories (`~/.local/bin`, `~/.risegen/`),
  never scanning for files in `cwd` nor depending on repository presence.
- **Binary Resolution Precedence**: The VS Code extension and any integration channel MUST resolve
  unconditionally to the official deployed system installation (`~/.local/bin/rgai`), NEVER
  prioritizing local `./rgai` executables residing at the root of a source code checkout.

## Redeploy procedures by artifact type

### Go binary (platform, connector, CLI tools)

```bash
go build -o <output-path> ./cmd/<name>
```

For a project consumed by other components (e.g. a platform API server deployed to dev),
also restart the service or notify the operator.

### CLI tool consumed by VS Code or TUI (e.g. rgai)

The VS Code extension resolves the CLI binary with this precedence (see locate.ts):

1. `risegen.rgaiPath` setting if explicitly set
2. `~/.local/bin/rgai` (deployed product install location — unconditionally outranks workspace checkouts)
3. Bare `rgai` on PATH

After a CLI change, the required sequence is:

1. Rebuild the CLI binary:
   `CGO_ENABLED=0 GOOS=darwin GOARCH=arm64 go build -trimpath -o ./rgai ./cmd/rgai`
2. Codesign and copy to install location:
   `codesign -s - -f ./rgai && cp -f ./rgai ~/.local/bin/rgai && codesign -s - -f ~/.local/bin/rgai`
3. **Kill any running process** (`ps -eo pid,command | grep -E 'rgai|opencode'`)
   — a live session holds the old binary in memory
4. Only then tell the user to reload the window; the respawn picks the fresh binary from `~/.local/bin/rgai`

### Shared library / internal package

When changing `internal/` packages consumed by the same repo's own binaries, just `go build`
the consuming binary (compiled languages catch staleness at link time). When the internal
package is consumed across repos (e.g. `risegen-ai-platform/api/internal/auth`), the consumer
repos themselves must be rebuilt.

## Testing protocol

0. **Quality gate first (NON-NEGOTIABLE when `quality-guard` is installed)** —
   production edits require **paired tests** and a green `quality-guard run`
   (writes `.risegen/quality-gate.json`) **before** commit and before claiming
   readiness. Never use `git commit --no-verify`. See skill `quality-enforcement`.
1. **Unit/integration tests** — run the surface `gate_cmd` (or `quality-guard run`)
   in the changed repo before claiming the change is correct.
2. **Local rebuild & codesign** — compile and codesign the changed artifact(s) per the procedure above.
3. **Ecosystem consistency & Independence** — verify the deployed binary operates 100% independently of
   the repository path.
4. **User retest signal** — only after (0–1) tests pass, (2) the artifact is rebuilt, codesigned and redeployed,
   and (3) any running process is killed/respawned, tell the user it is ready to test.

## Definition of "redeploy"

- **Go binary**: `go build` to the target path + codesign + copy to `~/.local/bin`.
- **Shared lib**: `go build` of every consumer binary (or `go install ./...`).
- **VS Code**: `CGO_ENABLED=0 GOOS=darwin GOARCH=arm64 go build -trimpath -o ./rgai ./cmd/rgai`
  + codesign + copy to `~/.local/bin/rgai` + extension package/install + kill + reload window instruction.
- **Python/node**: the applicable install/build step for the language.

A rebuild is not "done" until the binary at the path the consumer resolves is the new one and is 100% independent of the repository.
