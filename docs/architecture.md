# Architecture

## Control flow

```text
~/.paseo/config.json
  custom provider command
      |
      v
~/.local/bin/grok-room <role>
      |
      +-- grok-room-sync <role>
      |     +-- copies ~/.grok/auth.json
      |     +-- reads ~/.config/codex-room/overlays/<role>.config.toml
      |     `-- writes ~/.grok-runtime/<role>/
      |
      `-- GROK_HOME=~/.grok-runtime/<role> grok agent stdio
```

## Ownership

| Layer | Owner | Mutable state |
| --- | --- | --- |
| `~/.grok` | Operator/Grok | Canonical authentication |
| `~/.config/codex-room` | This repository | Role overlays and shared workflow instructions |
| `~/.grok-runtime` | `grok-room-sync` | Generated configs, profiles and role-local sessions |
| `~/.paseo` | Paseo | Provider config, agents, projects, worktrees, logs and identity |
| Official Paseo `grok-room` checkout | Git | Source code for CLI, daemon and Desktop |

## Runtime merge

For a role, the sync script generates a standalone Grok profile, disables
subagents/memory/external compatibility discovery, and copies only auth. The
launcher repeats the subagent boundary with `GROK_SUBAGENTS=0`,
`--no-subagents`, and `--disallowed-tools Agent`.

Official Paseo 0.7.2 resolves `agents.providers.<provider>.paseoTools` by the
exact caller provider. Supervisor and Lead are enabled; Peer and Review are
disabled. This controls the direct tool catalog, not shell-level authorization:
an agent with arbitrary shell access could still invoke an absolute CLI path.
