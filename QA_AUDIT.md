# QA Audit – Omnix All-knowing Gaming Companion

## Phase 1 – Recon & Test Plan

### App Surface Map
- **Core loop**: `main.py` bootstraps config, credential store, game detector, AI assistant, info scraper, and GUI overlay (`src/gui.py`). The README highlights automatic game detection, multi-provider AI, knowledge packs, macros, and session coaching as flagship capabilities.【F:README.md†L3-L33】【F:main.py†L1-L167】
- **Configuration & secrets**: `.env` loading plus encrypted credential storage via `Config` and `CredentialStore`; session tokens persisted alongside overlay geometry and macro/keybind JSON state.【F:src/config.py†L18-L121】【F:src/credential_store.py†L23-L174】
- **Game awareness**: `GameDetector` (process scans) and `GameWatcher` (foreground monitoring + Qt signals) pipe executable matches into `GameProfileStore` for prompts/game metadata.【F:src/game_detector.py†L1-L118】【F:src/game_watcher.py†L1-L140】
- **Knowledge system**: `KnowledgePackStore` (JSON persistence), ingestion pipeline (files/URLs/notes), TF-IDF-based `KnowledgeIndex`, and `KnowledgeIntegration` combine retrieved chunks into chat prompts and log usage.【F:src/knowledge_store.py†L1-L60】【F:src/knowledge_ingestion.py†L1-L200】【F:src/knowledge_index.py†L305-L415】【F:src/knowledge_integration.py†L1-L120】
- **Macros & automation**: `macro_manager.py` defines macro schema, `macro_runner.py` executes steps using pynput, and `settings_tabs.py` surfaces macros/keybind wiring in the UI.【F:src/macro_manager.py†L1-L120】【F:src/macro_runner.py†L1-L120】【F:src/settings_tabs.py†L1-L120】
- **Overlay UX**: `src/gui.py` implements dashboard + overlay, hooking to settings dialog tabs, session recap dialog, and system tray actions.【F:src/gui.py†L780-L900】
- **Testing assets**: `pytest` suite touches modules (game profiles, knowledge system, macros, modules import smoke) plus UI import checks in `src/ui/test_design_system.py`.

### Test Plan
| Area | Happy Path | Edge Cases / Error Paths | Performance/Load | Security/Privacy |
| --- | --- | --- | --- | --- |
| **Boot/config & setup** | Launch `main.py`, run setup wizard, verify config saves, overlay toggles. | Invalid `.env`, missing keys, corrupted encrypted store, credential migration. | Repeated config save/load while hot reloading. | Ensure encrypted storage never falls back to plaintext, protect session tokens. |
| **AI provider routing** | Provider selection, chat requests, provider tests in settings. | Expired keys, rate limits, provider swapping mid-session. | Burst chat sending, backpressure on worker threads. | Key handling, request logging, session token leakage. |
| **Game detection & profiles** | Auto-detect built-in games, auto-switch prompts, update session logger. | Unsupported OS (Linux/mac), duplicate custom IDs, stale persisted profiles, fallback to generic. | Watching loop CPU usage at 1–2s intervals. | Windows-only APIs (ctypes) gating detection. |
| **Knowledge packs** | Ingest file/URL/note, index, query from chat, view/manage packs in settings. | Missing dependencies, pack disabled, pack not persisted before indexing, config-dir overrides. | TF-IDF reindex cost as packs grow, repeated queries per turn. | External ingestion should sanitize URLs, avoid SSRF, respect local filesystem boundaries. |
| **Macro/keybind system** | Record/generate macro, bind hotkey, run via overlay. | `pynput` missing, macros disabled, invalid steps, repeated macros hitting timeouts. | Macro loops with high repeat counts, keyboard controller thread exhaustion. | Prevent unsafe macros (rapid input), respect anti-cheat toggles. |
| **Session logging/coaching** | Questions/answers recorded, recap dialog shows stats. | Disk full, log rotation, logging disabled, timezone shifts. | Large backlog of events (500+) and recap generation latency. | Logs contain sensitive chat; ensure stored locally only. |
| **UI/UX** | Dashboard buttons open relevant tabs, knowledge/macro tabs update, overlay theme stable. | Missing Qt dependencies, DPI scaling, settings tab navigation, system tray availability. | Overlay idle CPU, chat worker concurrency. | Clipboard access, screenshot handling (if any). |

**Assumptions**: Tests executed in a Linux container lacking graphical stack (`libGL.so.1`), so GUI automation relies on import checks rather than live rendering. Actual game detection requires Windows APIs; Linux/mac coverage limited to verifying graceful degradation.

## Phase 2 – Systematic Testing Results

### Test Execution Summary
- `pytest -q` across repo (86 tests). Result: 3 failures (PyQt6 import blocked by missing `libGL`, custom profile resolution mismatch due to stale persisted profile, knowledge index query returning zero chunks).【3f54fd†L1-L48】

### Issue Inventory
| # | Title | Area | Steps to Reproduce | Expected vs Actual | Severity | Type | Suspected Root Cause | Proposed Fix |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | PyQt6 `libGL` dependency missing on Linux | UI/Dependencies | `pytest src/ui/test_design_system.py::test_imports` or run GUI on Linux without OpenGL libs. | **Expected**: Qt widgets import cleanly. **Actual**: ImportError `libGL.so.1` halts UI tests and prevents overlay launch.【3f54fd†L1-L24】 | Medium | Bug / Environment | PyQt6 requires system OpenGL runtime; container/installer not bundling `libgl1`. | Document Linux prerequisites (apt `libgl1-mesa-glx`), add preflight check raising actionable message, and update build scripts to package dependency for AppImage/installer. |
| 2 | Custom profile creation is non-idempotent and reads stale disk state | Game Profiles | Run `TestProfileIntegration.test_custom_profile_resolution` twice without deleting `~/.gaming_ai_assistant/game_profiles.json`. | **Expected**: calling `create_profile` updates custom profile data. **Actual**: method returns False when ID exists; loader keeps older prompt (“Custom prompt”), so resolution mismatches test expectation.【F:src/game_profile.py†L362-L387】【F:test_game_profiles.py†L395-L417】【3f54fd†L24-L36】 | Medium | UX/Data Integrity | `GameProfileStore.create_profile` forbids overwriting custom IDs and persists to a shared home directory, so repeated creations never update prior data. | Allow explicit overwrite (or auto-upgrade) when caller is the owner of that custom profile, or expose `upsert_profile` that writes new prompt atomically; tests can then use temp dirs to avoid polluting real config. |
| 3 | Knowledge index rebuild ignores provided pack and globalizes storage path | Knowledge System | Instantiate `KnowledgeIndex` with temp `config_dir` and call `add_pack` with an in-memory `KnowledgePack`. | **Expected**: `add_pack` indexes supplied pack (or uses config_dir store). **Actual**: method immediately calls `rebuild_index_for_game`, which re-fetches packs via global `get_knowledge_pack_store()` pointing to `~/.gaming_ai_assistant`; newly created pack is invisible so query returns zero chunks.【F:src/knowledge_index.py†L305-L415】【F:src/knowledge_store.py†L24-L44】【F:test_knowledge_system.py†L243-L256】【3f54fd†L36-L48】 | High | Bug / Data | Tight coupling to global store and ignoring constructor `config_dir` prevents hermetic indexing and breaks regression tests. | Let `KnowledgeIndex` accept an optional store instance (default global) and use it inside `rebuild_index_for_game`; alternatively, when `add_pack` is called, insert that pack into an internal index before rebuilding so tests and unsaved packs work. |
| 4 | Dashboard “AI/Game Profiles/Knowledge” buttons cannot open specific settings tab | UI/UX | Click “AI Provider”/“Game Profiles”/“Knowledge Pack” dashboard buttons in overlay. | **Expected**: Settings dialog opens directly on the corresponding tab. **Actual**: `open_settings_tab` simply calls `open_advanced_settings()` and ignores `tab_index` (TODO), so dialog always shows default tab.【F:src/gui.py†L802-L817】【F:src/gui.py†L870-L875】 | Medium | UX | `TabbedSettingsDialog` lacks an exposed tab-selection API and the wiring in `MainWindow.open_settings_tab` was left as TODO. | Add method on settings dialog to `setCurrentIndex`, pass tab index from button handlers, and ensure dialog is created before setting. |
| 5 | Encryption master key stored in plaintext when keyring unavailable | Security | Launch app on a platform lacking system keyring support (e.g., minimal Windows Sandbox) so `keyring.set_password` fails. | **Expected**: User warned and asked for secure fallback. **Actual**: `_fallback_store_key` writes the Fernet key bytes to `~/.gaming_ai_assistant/master.key` without additional protection beyond filesystem permissions, meaning compromise of that file decrypts all API keys.【F:src/credential_store.py†L118-L158】 | High | Security | Credential store silently downgrades to on-disk key while still advertising “encrypted” storage, reducing secrecy to obfuscation. | Prompt users before falling back, support OS-specific DPAPI/Keychain alternatives, or password-protect the fallback key with user-provided passphrase. |
| 6 | Game detection marketed as cross-platform but implemented Windows-only | Game Detection | Run app on Linux/mac (no Windows APIs available). | **Expected**: Automatic detection per README “monitors 50+ games”. **Actual**: `_get_foreground_executable` hard-codes Windows check and logs warning before returning None, so game detection never triggers outside Windows.【F:README.md†L12-L33】【F:src/game_watcher.py†L86-L115】 | Medium | UX/Scope mismatch | Game detection relies on `ctypes`/Win32 foreground window APIs without alternative strategies. | Update README/install docs to clarify Windows-only detection and consider implementing platform-specific fallbacks (Steam/Linux process scan, macOS accessibility API). |
| 7 | Knowledge index/store cannot be redirected per config directory | Knowledge System | Instantiate `KnowledgeIndex(config_dir=tempdir)` and `KnowledgePackStore(config_dir=tempdir)` expecting isolation. | **Expected**: Both components honor provided config dir. **Actual**: `rebuild_index_for_game` imports the module-level singleton `get_knowledge_pack_store()` which always points to `~/.gaming_ai_assistant`, ignoring the index’s `config_dir`. Tests therefore leak into user state and can’t run hermetically.【F:src/knowledge_index.py†L305-L318】【F:src/knowledge_store.py†L24-L44】【F:src/knowledge_store.py†L328-L337】 | Medium | Maintainability/Testability | Hardcoded global store prevents injecting per-environment storage. | Accept `knowledge_store` dependency in `KnowledgeIndex.__init__`, defaulting to the global if not provided, and ensure `rebuild_index_for_game` uses that instance. |

### Prioritized Fix List
1. **KnowledgeIndex rebuild/global-store coupling (Issues 3 & 7)** – Blocks knowledge features entirely in clean environments and fails tests; fix unlocks semantic search and stabilizes CI.
2. **CredentialStore fallback security (Issue 5)** – Leaking encryption key defeats “secure storage” promise; address before release.
3. **Custom profile overwrite behavior (Issue 2)** – Prevents users from updating their own custom prompts and breaks reproducible tests.
4. **Dashboard tab navigation (Issue 4)** – UX regression impacting discoverability of AI/game/knowledge settings.
5. **LibGL prerequisite messaging (Issue 1) & platform detection clarity (Issue 6)** – Improve onboarding reliability; lower severity but high visibility.

## Phase 3 – Specialized Helpers
1. **Navigator – Surface Mapper & Impact Analyzer**
   - **Purpose**: Given a bug/feature, locate relevant modules (config, GUI, knowledge, macros) and summarize cross-module impacts.
   - **Inputs**: Plain-text description of an issue or feature request.
   - **Outputs**: Ordered list of files/classes/functions with line references, dependency notes (e.g., `KnowledgeIndex -> KnowledgePackStore`), and a minimal change outline.
   - **Example**: Input “fix knowledge indexing for temp dirs” → identifies `src/knowledge_index.py`, `src/knowledge_store.py`, constructor signatures, and outlines injecting store dependency before rebuild.

2. **PatchCrafter – Targeted Fix & Refactor Generator**
   - **Purpose**: Produce high-quality diffs once Navigator pinpoints surfaces, focusing on bugfixes/refactors without breaking style guides.
   - **Inputs**: Navigator’s change outline plus current code excerpts.
   - **Outputs**: Ready-to-apply unified diffs with brief rationale per hunk, handling updates to tests/config/docs alongside code.
   - **Example**: Given Navigator’s plan for dashboard tab switching, emits `TabbedSettingsDialog.set_active_tab()` implementation and `MainWindow.open_settings_tab` updates.

3. **Guardscribe – Regression & Test Author**
   - **Purpose**: Extend/author unit or integration tests ensuring discovered bugs stay fixed (e.g., knowledge index, custom profiles, security fallbacks).
   - **Inputs**: Description of expected behavior plus modified modules/diffs.
   - **Outputs**: Pytest cases or Qt smoke tests validating new behavior, including fixtures for temp config dirs and dependency mocks.
   - **Workflow**: Navigator → PatchCrafter → Guardscribe ensures each fix is located, implemented, and covered by regression tests before merge.
