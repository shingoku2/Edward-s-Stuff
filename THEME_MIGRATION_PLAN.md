# Theme System Migration Plan

**Date:** 2025-11-17
**Branch:** claude/migrate-to-refractor-01EEx3HspZzAfFx4vUYBtZ7n
**Status:** In Progress

## Executive Summary

This document outlines the migration plan to consolidate Omnix's dual theme systems into a single unified design system.

## Problem Statement

Omnix currently has **two separate theming systems** that are not fully integrated:

### Legacy System (`src/theme_manager.py`)
- Uses `Theme` dataclass with basic color/font settings
- Modified through Appearance Settings UI (`src/appearance_tabs.py`)
- Saved to `~/.gaming_ai_assistant/theme.json`
- Generates QSS stylesheets dynamically

### New Design System (`src/ui/design_system.py`, `src/ui/tokens.py`)
- Modern token-based design system
- Used by all new UI components in `src/ui/components/`
- Generates comprehensive QSS stylesheets
- More maintainable and extensible

### Current Issues
1. Users changing settings in Appearance tab may not see full effects on new components
2. Two sources of truth for styling creates confusion
3. Settings don't fully propagate between systems
4. `src/ui/theme_bridge.py` attempts to bridge them but it's a temporary solution
5. Maintenance burden of keeping two systems in sync

## Migration Goals

1. **Single Source of Truth:** Consolidate all theming to the new design system
2. **Backward Compatibility:** Preserve user theme preferences during migration
3. **Improved UX:** Theme changes should immediately affect all UI components
4. **Maintainability:** Reduce code duplication and complexity
5. **Extensibility:** Make it easier to add new themes and customization options

## Affected Files

### Files Using Legacy Theme System
- `src/theme_manager.py` (654 lines) - **TO DEPRECATE**
- `src/ui/theme_bridge.py` (234 lines) - **TO REMOVE**
- `src/appearance_tabs.py` (~700 lines) - **TO REFACTOR**
- `src/gui.py` (1,800 lines) - **TO UPDATE**
- `src/settings_dialog.py` - **TO UPDATE**
- `src/settings_tabs.py` - **TO UPDATE**

### New Design System Files
- `src/ui/tokens.py` (284 lines) - Design tokens
- `src/ui/design_system.py` (840 lines) - Stylesheet generator
- `src/ui/components/*` - All components already use new system

## Migration Strategy

### Phase 1: Preparation & Analysis ✅
- [x] Analyze current theme systems
- [x] Identify all files using legacy system
- [x] Document current state and dependencies
- [x] Create migration plan

### Phase 2: Extend New Design System
- [ ] Add dynamic token updates to `ui/tokens.py`
- [ ] Create `OmnixThemeManager` class to replace legacy `ThemeManager`
- [ ] Add persistence layer for user theme customizations
- [ ] Ensure backward compatibility for loading old `theme.json` files

### Phase 3: Refactor Appearance Settings
- [ ] Update `appearance_tabs.py` to directly modify design tokens
- [ ] Replace legacy `Theme` references with new token system
- [ ] Add live preview capability
- [ ] Ensure all UI elements update in real-time

### Phase 4: Update Main Application
- [ ] Refactor `gui.py` to use new design system
- [ ] Remove `ThemeManager` initialization
- [ ] Apply new design system to main window
- [ ] Update all direct theme references

### Phase 5: Update Settings System
- [ ] Update `settings_dialog.py` to use new design system
- [ ] Update `settings_tabs.py` to use new design system
- [ ] Remove all legacy theme imports

### Phase 6: Migration & Data Compatibility
- [ ] Create migration script for old `theme.json` files
- [ ] Add automatic migration on first run after update
- [ ] Preserve user customizations during migration
- [ ] Test with various theme configurations

### Phase 7: Cleanup
- [ ] Remove `theme_bridge.py`
- [ ] Deprecate `theme_manager.py` (keep temporarily for reference)
- [ ] Update all documentation
- [ ] Update CLAUDE.md to remove technical debt section
- [ ] Clean up imports across codebase

### Phase 8: Testing
- [ ] Test theme changes propagate to all UI elements
- [ ] Test theme persistence (save/load)
- [ ] Test backward compatibility with old configs
- [ ] Test on different platforms (Windows, macOS, Linux)
- [ ] Verify no visual regressions

### Phase 9: Documentation & Deployment
- [ ] Update README.md
- [ ] Update CLAUDE.md
- [ ] Update developer documentation
- [ ] Create migration guide for users (if needed)
- [ ] Commit and push changes

## Technical Implementation Details

### New OmnixThemeManager Class

```python
# src/ui/theme_manager.py (NEW)
class OmnixThemeManager:
    """
    Modern theme manager using the Omnix design system.
    Replaces the legacy ThemeManager.
    """

    def __init__(self):
        self.tokens = OmnixDesignTokens()
        self.design_system = OmnixDesignSystem()
        self.config_file = os.path.expanduser("~/.gaming_ai_assistant/theme.json")

    def load_theme(self):
        """Load user theme customizations"""
        # Load from theme.json, migrate if needed
        pass

    def save_theme(self):
        """Save current theme customizations"""
        # Save to theme.json in new format
        pass

    def update_color(self, color_key: str, value: str):
        """Update a specific color token"""
        setattr(self.tokens.colors, color_key, value)
        self._notify_observers()

    def update_spacing(self, spacing_key: str, value: int):
        """Update a spacing token"""
        setattr(self.tokens.spacing, spacing_key, value)
        self._notify_observers()

    def get_stylesheet(self) -> str:
        """Generate complete stylesheet"""
        return self.design_system.generate_complete_stylesheet()

    def migrate_legacy_theme(self, legacy_theme: dict):
        """Migrate old Theme format to new tokens"""
        # Map old theme values to new tokens
        pass
```

### Theme Persistence Format

**Old Format (theme.json):**
```json
{
  "theme": {
    "mode": "dark",
    "primary_color": "#14b8a6",
    "background_color": "#1e1e1e",
    ...
  }
}
```

**New Format (theme.json v2):**
```json
{
  "version": 2,
  "tokens": {
    "colors": {
      "bg_primary": "#1A1A2E",
      "accent_primary": "#00BFFF",
      ...
    },
    "spacing": {
      "base": 16,
      ...
    },
    "typography": {
      "size_base": 11,
      ...
    }
  },
  "customizations": {
    "user_modified": ["colors.accent_primary", "spacing.base"],
    "timestamp": "2025-11-17T10:00:00Z"
  }
}
```

### Migration Function

```python
def migrate_legacy_theme_file():
    """
    Migrate old theme.json to new format.
    Called automatically on first run.
    """
    old_file = os.path.expanduser("~/.gaming_ai_assistant/theme.json")

    if not os.path.exists(old_file):
        return  # No migration needed

    with open(old_file, 'r') as f:
        old_data = json.load(f)

    # Check if already migrated
    if old_data.get('version') == 2:
        return

    # Create backup
    backup_file = old_file + '.backup'
    shutil.copy(old_file, backup_file)

    # Migrate
    new_data = {
        "version": 2,
        "tokens": {
            "colors": {
                "accent_primary": old_data['theme'].get('primary_color', COLORS.accent_primary),
                "bg_primary": old_data['theme'].get('background_color', COLORS.bg_primary),
                # ... map all colors
            }
        },
        "customizations": {
            "migrated_from": "v1",
            "timestamp": datetime.now().isoformat()
        }
    }

    # Save migrated version
    with open(old_file, 'w') as f:
        json.dump(new_data, f, indent=2)
```

## Risks & Mitigation

### Risk 1: Breaking User Customizations
**Mitigation:**
- Implement automatic migration with backup
- Test migration with various theme configurations
- Preserve all user customizations

### Risk 2: Visual Regressions
**Mitigation:**
- Thorough testing on all platforms
- Side-by-side comparison before/after
- Keep screenshots of current UI for reference

### Risk 3: Performance Impact
**Mitigation:**
- Stylesheet generation should be no slower than current
- Cache generated stylesheets
- Profile performance before/after

### Risk 4: Incomplete Migration
**Mitigation:**
- Comprehensive grep/search for all legacy theme usage
- Unit tests for all modified components
- Integration tests for theme application

## Success Criteria

- [ ] All UI components use the new design system exclusively
- [ ] Theme changes in Appearance Settings affect all UI elements
- [ ] User theme preferences are preserved during migration
- [ ] No visual regressions compared to current state
- [ ] Code is more maintainable (less duplication)
- [ ] Documentation is updated and accurate
- [ ] All tests pass

## Timeline

**Estimated Effort:** 6-8 hours

- Phase 1 (Preparation): ✅ Complete
- Phase 2 (Extend Design System): 1-2 hours
- Phase 3 (Refactor Appearance): 2-3 hours
- Phase 4-5 (Update Main App): 1-2 hours
- Phase 6 (Migration): 1 hour
- Phase 7 (Cleanup): 30 minutes
- Phase 8 (Testing): 1-2 hours
- Phase 9 (Documentation): 30 minutes

## Next Steps

1. Start Phase 2: Extend the new design system
2. Create `OmnixThemeManager` class
3. Implement dynamic token updates
4. Add persistence layer

## References

- Current Technical Debt: CLAUDE.md (lines 525-582)
- Design System Documentation: src/ui/DESIGN_SYSTEM.md
- Design Tokens: src/ui/tokens.py
- Legacy Theme Manager: src/theme_manager.py
- Theme Bridge: src/ui/theme_bridge.py

---

**Author:** Claude (AI Assistant)
**Last Updated:** 2025-11-17
