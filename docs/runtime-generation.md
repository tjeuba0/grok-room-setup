# Runtime generation

`grok-room-sync` treats each role directory as an isolated Grok home.

```text
copied:   auth.json
isolated: config.toml, agent-profile.md, sessions, hooks and state
room:     role instructions and workflow documents
```

All active roles use `grok-4.6`. Supervisor, Lead and Peer use high effort;
Review uses medium effort. Native Grok subagents are disabled, so normal room
delegation flows only through Paseo.

Runtime snapshots in this repository are optional sanitized audit output. They are ignored by default and are not installation inputs.
