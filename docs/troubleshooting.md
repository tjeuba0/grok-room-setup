# Troubleshooting

## A role still uses an old model or thinking level

The overlay or Paseo template changed but the generated runtime or daemon catalog was not refreshed.

```bash
scripts/sync-all <role>
paseo daemon reload
```

Existing seats keep the thinking they were created with. Open a new seat.

Confirm launcher effort in `~/.local/bin/grok-room` (`effort=high` or `effort=medium`) and Paseo model `thinkingOptions` in `~/.paseo/config.json`.

## `grok-room-sync` cannot find Grok auth

Grok is not installed or not logged in. This repository copies `~/.grok/auth.json`; it will not create it.

## Paseo does not show Grok Room providers

1. Validate `~/.paseo/config.json` with `jq`.
2. Confirm each Grok provider `command` points to `~/.local/bin/grok-room`.
3. Confirm `~/.local/bin` is on the daemon's PATH.
4. Run `paseo daemon reload`, or restart Paseo when no agent is running.
5. Run `scripts/verify --live`.

## Daemon PID and listener disagree

```bash
cat "$HOME/.paseo/paseo.pid"
lsof -nP -iTCP:6767 -sTCP:LISTEN
```

A wrapper PID and child Node PID can differ. Diagnose before deleting PID or state files.
