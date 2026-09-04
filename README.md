# Grok Room Setup

Reproducible configuration for a four-role Grok room running through official Paseo:

```text
Paseo provider
  -> grok-room <supervisor|lead|peer|review>
  -> grok-room-sync
  -> isolated ~/.grok-runtime/<role>
  -> Grok ACP stdio
```

This repository deliberately does **not** own `~/.grok`. Each operator installs
and authenticates Grok independently. The sync script copies only the existing
Grok auth into four isolated role homes and generates each role's profile and
config. Native Grok subagents are disabled in config, environment, and CLI flags.

## What gets installed

The `home/` directory mirrors `$HOME`:

| Repository source | Local destination |
| --- | --- |
| `home/.config/codex-room/` | `~/.config/codex-room/` |
| `home/.local/bin/codex-room*` | `~/.local/bin/` |
| `home/.paseo/config.json.template` | `~/.paseo/config.json` |

`scripts/install-paseo-fork` is retained as a compatibility command name. It
clones official upstream, creates the local `grok-room` branch, and links:

```text
~/.local/bin/paseo
  -> ~/projects/supervisors/paseo-grok-room/packages/cli/bin/paseo
```

`@@HOME@@` placeholders are rendered during installation. Runtime databases, sessions, logs, auth files, keypairs, tokens, worktrees, and backups are never installed from or exported into Git.

## Install

Prerequisites:

- macOS or a Unix-like environment with Bash, Python 3, Git, Node, npm, and jq.
- Grok installed and authenticated.
- `~/.local/bin` on `PATH`.

```bash
git clone <this-repository-url> codex-room-setup
cd codex-room-setup

./scripts/doctor
./scripts/install                 # dry-run only
./scripts/install --apply         # backup and install
./scripts/install-paseo-fork      # clone/verify official Paseo and link its CLI
./scripts/sync-all                # materialize four GROK_HOME directories
./scripts/verify                  # verify installed files and runtimes
```

The installer backs up every replaced file under:

```text
~/.codex-room-backups/install-<UTC timestamp>/
```

It never writes to `~/.codex`.

## Paseo Desktop

After the official checkout exists at `~/projects/supervisors/paseo-grok-room`:

```bash
paseo daemon start
paseo daemon status
paseo-local-update
```

That command updates the checkout, installs dependencies, builds and signs the local Desktop app, backs up the previous `/Applications/Paseo.app`, restarts the daemon, and opens Paseo.

## Roles

| Role | Default model | Reasoning | Paseo tools |
| --- | --- | --- | --- |
| Supervisor | `grok-4.6` | high | yes |
| Lead | `grok-4.6` | high | yes |
| Peer | `grok-4.6` | high | no |
| Review FAST | `grok-4.6` | medium | no |

Only Supervisor and Lead receive Paseo's agent catalog. Peer and Review have no
direct `create_agent`, and every role launches Grok with native `Agent` removed.
Review also removes native edit/write tools. Grok 1.0.13 ACP does not initialize
under its `read-only` sandbox, so Review uses the workspace sandbox plus a
behavioral read-only contract. Read [docs/architecture.md](docs/architecture.md)
before changing these boundaries.

## Common operations

```bash
# Regenerate all role runtimes after changing an overlay
./scripts/sync-all

# Validate source only, without requiring installed runtimes
./scripts/verify --source

# Include live Paseo checks
./scripts/verify --live

# Export sanitized runtime summaries for local comparison
./scripts/export-runtime-snapshots

# Summarize one historical Codex rollout session for benchmarking
./scripts/session-usage --role peer --session-id SESSION_ID

# Count workflow-pilot markers without exporting rollout content
./scripts/workflow-pilot-report --format json /path/to/rollout.jsonl
```

See [docs/session-usage-benchmark.md](docs/session-usage-benchmark.md) for token,
request, tool-call, timing, and API-equivalent cost definitions.
See [docs/workflow-pilot.md](docs/workflow-pilot.md) for the setup-only workflow
experiment and the evidence threshold for adding Paseo enforcement.

The older Codex launchers and guarded candidate files remain as rollback
references; they are not active providers in the Grok Room configuration.
