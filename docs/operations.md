# Operations

## Change a role

1. Edit `home/.config/codex-room/overlays/<role>.config.toml`.
2. Run `make test`.
3. Run `scripts/install --apply` to install the changed source.
4. Run `scripts/sync-all <role>`.
5. Run `scripts/verify`.

## Run the workflow pilot

The shared protocol and role overlays implement a setup-only workflow pilot.
Read `docs/workflow-pilot.md`, install and sync changed sources, then collect a
sanitized aggregate report with:

```bash
./scripts/workflow-pilot-report --format json /path/to/rollout.jsonl
```

Do not commit raw rollout JSONL. It can contain prompts, source, and tool data.
The pilot does not enforce ownership or ordering atomically; observed misses are
evidence for deciding whether a Paseo runtime mechanism is warranted.

## Change the Paseo provider catalog

1. Edit `home/.paseo/config.json.template`.
2. Run `make test`.
3. Install with backup using `scripts/install --apply`.
4. Restart Paseo explicitly.
5. Run `scripts/verify --live`.

The installer does not restart the daemon because an active restart can interrupt running agents.

Before cutover, verify every live agent is idle, snapshot `~/.paseo`,
`~/.config/codex-room`, `~/.grok-runtime`, and the CLI symlink under a private
backup directory, then test the new daemon on port 6768. Rollback restores those
paths and relinks the previous checkout before restarting port 6767.

After editing `~/.paseo/config.json` by hand, run `paseo daemon reload` so the
Desktop picker sees new thinking defaults. Reload does not change seats that
are already open.

## Historical migration helpers

`codex-room-hard-cut`, `codex-review-apply`, and the two candidate JSON files
are leftover recovery tools from the previous room layout. They are not used
by the live Grok providers.

## Update official Paseo on the local `grok-room` branch

Run `paseo-local-update` only when no important agent turn or Desktop operation is active. It pulls with rebase, builds, replaces the app and restarts the daemon.
