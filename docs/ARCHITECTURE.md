# Omnix architecture

```text
PyQt desktop UI
       |
Application services (AI, game watcher, sessions, macros, capabilities)
       |
Integrations (Ollama, process discovery, input automation, licensing)
       |
Persistence (JSON stores, encrypted credentials, SQLite FTS5)
```

`src/omnix/__main__.py` is the composition root. It owns startup order: logging,
profile migration, configuration, credentials, integrations, and finally the
GUI. Other modules must not mutate `sys.path` or import through the old flat
`src.<module>` namespace.

The UI uses `omnix.ui.tokens` and reusable components under
`omnix.ui.components`. Background AI and model-discovery work stays off the UI
thread and receives cooperative interruption requests during shutdown.

`DesktopCapabilities` is the authority for OS integration. Unsupported
features remain visible but disabled with a reason; integrations should not
silently fall back. In particular, Linux Wayland cannot execute macros or
register pynput global hotkeys.

User profile changes go through ordered `MigrationManager` steps. Every changed
profile is backed up, each JSON write is atomic, and a newer unknown schema is a
hard error. New migrations must be idempotent and include unit tests.

Knowledge file ingestion treats path containment as a security boundary. It
resolves both the candidate file and each allowed root before using
component-aware `Path.relative_to()` checks. This preserves traversal defenses
without rejecting equivalent macOS or Windows path aliases. Tests for this
boundary must use disposable directories rather than real user paths.

The desktop license client sends a license key and random installation UUID to
a narrow Supabase Edge Function. Only the function service role can read license
or seat tables. The application stores the installation UUID and last successful
validation timestamp in its encrypted credential vault.
