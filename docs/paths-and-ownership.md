# Paths and ownership

## Tracked canonical files

```text
~/.config/codex-room/overlays/*.config.toml
~/.config/codex-room/workflow/*.md
~/.local/bin/grok-room
~/.local/bin/grok-room-sync
~/.local/bin/paseo -> ~/projects/supervisors/paseo-grok-room/packages/cli/bin/paseo
~/.local/bin/paseo-local-update
~/.paseo/config.json
```

The repository stores HOME-dependent JSON as `*.template`; installation renders it to the path without `.template`.
The Paseo CLI symlink is created by `scripts/install-paseo-fork`, after the checkout is available.

## Generated files

```text
~/.grok-runtime/<role>/config.toml
~/.grok-runtime/<role>/agent-profile.md
~/.grok-runtime/<role>/sessions/
```

Never edit generated `config.toml` or `agent-profile.md` as the durable source.
Change the role overlay or sync template, then run `scripts/sync-all`.

## Private state

Never commit:

- `~/.grok/auth.json`, copied role auth, or other provider auth stores.
- Paseo daemon keypairs, push tokens, IDs, agent state, worktrees, uploads, logs or PID files.
- Runtime sessions, logs, memories, queues or SQLite databases.
- Backup directories.
