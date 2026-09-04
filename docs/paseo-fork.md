# Official Paseo checkout

The source of truth for fork provenance is [`paseo/source.toml`](../paseo/source.toml). The expected checkout is:

```text
~/projects/supervisors/paseo-grok-room
```

`scripts/install-paseo-fork` keeps its historical name but clones official
`getpaseo/paseo`, creates local branch `grok-room` from `origin/main`, adds the
existing live checkout only as comparison remote `live-fork`, and links the CLI.
A conflicting link is backed up under `~/.codex-room-backups/`.

Access to official upstream is an operator prerequisite. The installer does not
manage SSH keys or GitHub authentication.
