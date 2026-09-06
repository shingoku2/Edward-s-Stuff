# Plan: Settings Implementation & Dynamic HUD (Superseded)

> **Historical plan.** Retained for auditability only. Omnix 3.0 uses the
> PyQt6 UI in `src/omnix/ui`; React/Tauri milestones below are no longer
> actionable. See `docs/UPGRADING.md` for the current migration path.

## Phase 1: Backend Infrastructure (Python) [checkpoint: 8015144]
- [x] Task: Extend `JSBridge` with new slots for fetching current config and saving updated settings. 51377a6
- [x] Task: Implement `MacroManager` bridge methods for recording/editing macros from JS. 9d5089c
- [x] Task: Enhance `GameDetector` to emit detailed process information (Name, PID, Executable Path). af4cabb
- [x] Task: Implement a periodic "System Stats" emitter in `MainWindow` to send CPU/RAM usage to React. 599b76e
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Backend Infrastructure (Python)' (Protocol in workflow.md)

## Phase 2: React Settings Module (Frontend)
- [ ] Task: Create a `SettingsContext` to manage local/unsaved settings state in React.
- [ ] Task: Implement the "Appearance" tab with working sliders/toggles for opacity and scaling.
- [ ] Task: Implement the "AI/LLM" tab for model selection and API key management.
- [ ] Task: Implement the "Keybinds/Macros" tab to list and trigger recording of macros.
- [ ] Task: Add "Save Changes" and "Discard" footer buttons to the Settings module.
- [ ] Task: Conductor - User Manual Verification 'Phase 2: React Settings Module (Frontend)' (Protocol in workflow.md)

## Phase 3: HUD & Real-time Integration
- [ ] Task: Update `CentralHUD` component to subscribe to game detection and system stats signals.
- [ ] Task: Implement the session timer logic in React (started/stopped via backend signals).
- [ ] Task: Replace all placeholder text in the HUD with dynamic data from the `JSBridge`.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: HUD & Real-time Integration' (Protocol in workflow.md)

## Phase 4: Persistence & Feedback
- [ ] Task: Implement the `saveSettings` logic to update `config.yaml` via the bridge.
- [ ] Task: Add visual feedback (toast/notification) for successful save or error.
- [ ] Task: Verify that settings changes (like UI opacity) are applied globally and immediately.
- [ ] Task: Conductor - User Manual Verification 'Phase 4: Persistence & Feedback' (Protocol in workflow.md)

## Phase 5: Final Verification & Polish
- [ ] Task: Comprehensive bug scrub of the settings save/discard workflow.
- [ ] Task: Visual QA to ensure the HUD data is readable during gameplay.
- [ ] Task: Conductor - User Manual Verification 'Phase 5: Final Verification & Polish' (Protocol in workflow.md)
