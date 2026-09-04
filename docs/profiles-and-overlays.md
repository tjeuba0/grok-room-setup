# Profiles and overlays

The word “profile” appears at three different levels:

1. **Paseo custom provider:** `grok-supervisor`, `grok-lead`, `grok-peer`, or `grok-review` extends generic ACP.
2. **Room overlay:** the reference role instructions embedded into a generated Grok agent profile.
3. **Grok agent profile:** the generated `agent-profile.md` selected by the launcher.

Changing a Paseo provider model affects the picker. The launcher independently
pins the same model and effort; keep both aligned deliberately.

The only review profile is `review-fast`: `grok-review/grok-4.6` at medium effort.
There is no DEEP or DUAL profile and no slow-model fallback.

`local-writer` maps to `grok-peer`; `review-fast` maps to `grok-review`.
Neither child provider receives Paseo orchestration tools.
