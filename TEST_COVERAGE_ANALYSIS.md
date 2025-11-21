# Omnix Test Coverage Analysis & Recommendations

**Date:** 2025-11-21
**Current Coverage:** 22.9% (11/48 modules with tests)
**Total Test Lines:** ~3,734 LOC

---

## Executive Summary

The Omnix codebase currently has **limited test coverage** with only 11 out of 48 core modules having dedicated test files. While the existing tests demonstrate good practices (proper fixtures, unit/integration separation, mock usage), significant gaps exist in critical areas like the macro system, knowledge management, GUI components, and session management.

**Key Findings:**
- ✅ Strong foundation: Good test organization and fixtures in place
- ❌ Low coverage: 77% of modules lack dedicated tests
- ❌ Critical gaps: Macro system, knowledge integration, UI components
- ❌ Integration testing: Limited end-to-end workflow tests

---

## Current Test Coverage

### ✅ Modules WITH Tests (11/48)

| Module | Test File | Coverage Notes |
|--------|-----------|----------------|
| `ai_assistant.py` | `tests/unit/test_ai_assistant.py` | Unit tests for assistant |
| `ai_router.py` | `tests/unit/test_ai_router.py` | Provider routing tests |
| `config.py` | `tests/unit/test_config.py` | Config loading, saving, corruption recovery |
| `credential_store.py` | `test_credential_store.py` | Encryption, keyring fallback |
| `game_detector.py` | `tests/unit/test_game_detector.py` | Process detection mocking |
| `game_watcher.py` | `test_game_watcher.py` | Thread-based monitoring |
| `gui.py` | `tests/test_gui.py` | Minimal GUI initialization |
| `providers.py` | `test_providers.py` | Provider implementations |
| `session_coaching.py` | `test_session_coaching.py` | AI coaching generation |
| `ui/components/dashboard.py` | `test_dashboard.py` | Dashboard component |
| `utils.py` | `tests/unit/test_utils.py` | Utility functions |

### ❌ Modules WITHOUT Tests (37/48)

**High-Priority Missing Tests:**
- **Macro System** (5 modules): `macro_manager.py`, `macro_runner.py`, `macro_store.py`, `macro_ai_generator.py`, `keybind_manager.py`
- **Knowledge System** (4 modules): `knowledge_index.py`, `knowledge_integration.py`, `knowledge_ingestion.py`, `knowledge_store.py`
- **Session Management** (1 module): `session_logger.py`
- **Game Profiles** (2 modules): `game_profile.py`, `game_profiles_tab.py`

**Medium-Priority Missing Tests:**
- **Settings & UI** (6 modules): `settings_dialog.py`, `settings_tabs.py`, `providers_tab.py`, `knowledge_packs_tab.py`, `appearance_tabs.py`, `setup_wizard.py`
- **Theming** (3 modules): `theme_manager.py`, `theme_compat.py`, `ui/theme_manager.py`
- **UI Components** (9 modules): All components in `ui/components/` except `dashboard.py`

**Low-Priority Missing Tests:**
- **Infrastructure** (2 modules): `error_recovery.py`, `filelock.py`
- **Provider Testing** (1 module): `provider_tester.py`
- **UI Utilities** (2 modules): `ui/design_system.py`, `ui/tokens.py`

---

## Priority 1: Critical Gaps (MUST FIX)

### 1. Macro System Testing ⚠️ **CRITICAL**

**Current State:** Zero dedicated tests for the entire macro execution pipeline
**Risk:** Macros can execute keyboard/mouse automation with safety implications
**Impact:** High - Could break user workflows or cause safety issues

**Recommended Tests:**

#### `tests/unit/test_macro_manager.py`
```python
- test_macro_step_creation_all_types()
- test_macro_step_validation()
- test_macro_creation_with_steps()
- test_macro_serialization_deserialization()
- test_macro_step_validation_failures()
- test_macro_max_repeat_limit()
- test_macro_timeout_configuration()
```

#### `tests/unit/test_macro_runner.py`
```python
- test_macro_execution_state_machine()
- test_key_press_execution() [mocked pynput]
- test_mouse_click_execution() [mocked pynput]
- test_delay_execution_with_jitter()
- test_macro_stop_mid_execution()
- test_execution_timeout_enforcement()
- test_max_repeat_enforcement()
- test_error_handling_invalid_key()
```

#### `tests/unit/test_macro_store.py`
```python
- test_save_macro_to_disk()
- test_load_macro_from_disk()
- test_list_macros_for_game()
- test_delete_macro()
- test_update_existing_macro()
- test_corrupted_macro_file_recovery()
```

#### `tests/unit/test_keybind_manager.py`
```python
- test_register_system_keybind()
- test_register_macro_keybind()
- test_keybind_conflict_detection()
- test_keybind_trigger_execution()
- test_disable_keybind()
- test_game_specific_keybind_scoping()
```

#### `tests/integration/test_macro_workflow.py` ⭐ **NEW**
```python
- test_create_record_execute_macro_workflow()
- test_macro_keybind_trigger_workflow()
- test_macro_execution_with_game_context()
- test_concurrent_macro_execution_prevention()
```

**Estimated LOC:** ~800 lines
**Estimated Effort:** 2-3 days

---

### 2. Knowledge System Testing ⚠️ **CRITICAL**

**Current State:** Partial tests exist in `tests/test_knowledge.py` and `tests/unit/test_knowledge_system.py`
**Gap:** Missing tests for integration layer and edge cases
**Impact:** High - Core feature for game-specific assistance

**Recommended Additional Tests:**

#### `tests/unit/test_knowledge_index.py` ⭐ **NEW**
```python
- test_tfidf_embedding_generation()
- test_index_rebuild_after_restart() [REGRESSION TEST for 78a2050]
- test_chunk_similarity_search()
- test_index_persistence_format()
- test_vocabulary_persistence() [CRITICAL - tests fix from 2025-11-19]
- test_search_quality_after_restart() [REGRESSION TEST]
- test_index_update_with_new_content()
- test_concurrent_index_access()
```

#### `tests/unit/test_knowledge_integration.py` ⭐ **NEW**
```python
- test_knowledge_augmentation_to_ai_prompt()
- test_should_use_knowledge_packs_logic()
- test_knowledge_context_formatting()
- test_relevance_threshold_filtering()
- test_max_chunks_in_context()
- test_game_profile_knowledge_pack_association()
```

#### `tests/unit/test_knowledge_ingestion.py` ⭐ **NEW**
```python
- test_ingest_pdf_file()
- test_ingest_docx_file()
- test_ingest_markdown_file()
- test_ingest_url_with_beautifulsoup()
- test_path_traversal_prevention() [SECURITY]
- test_file_size_limit_enforcement() [SECURITY]
- test_chunk_text_with_overlap()
```

#### `tests/unit/test_knowledge_store.py` ⭐ **NEW**
```python
- test_save_load_knowledge_pack()
- test_get_packs_for_game()
- test_enable_disable_pack()
- test_delete_knowledge_pack()
- test_corrupted_pack_file_recovery()
```

#### `tests/integration/test_knowledge_e2e.py` ⭐ **NEW**
```python
- test_ingest_index_query_workflow()
- test_knowledge_augmentation_in_ai_response()
- test_multi_pack_query_aggregation()
- test_pack_update_index_refresh()
```

**Estimated LOC:** ~600 lines
**Estimated Effort:** 2-3 days

---

### 3. Session Management Testing

**Current State:** `session_coaching.py` has tests, but `session_logger.py` has none
**Impact:** Medium-High - Session data integrity crucial for coaching

**Recommended Tests:**

#### `tests/unit/test_session_logger.py` ⭐ **NEW**
```python
- test_log_event_to_memory()
- test_event_persistence_to_disk()
- test_session_timeout_detection()
- test_max_events_in_memory_limit()
- test_max_events_on_disk_limit()
- test_get_session_events_for_game()
- test_clear_session()
- test_corrupted_session_file_recovery()
```

#### `tests/integration/test_session_management.py` (expand existing)
```python
- test_session_creation_on_game_detection()
- test_session_event_logging_workflow()
- test_session_coaching_generation()
- test_session_recap_dialog_display()
- test_multi_session_management()
```

**Estimated LOC:** ~300 lines
**Estimated Effort:** 1-2 days

---

### 4. Game Profile System Testing

**Current State:** Archive tests exist but not active
**Impact:** High - Core feature for game detection

**Recommended Tests:**

#### `tests/unit/test_game_profile.py` ⭐ **NEW**
```python
- test_game_profile_creation()
- test_builtin_vs_custom_profiles()
- test_profile_serialization()
- test_profile_store_save_load()
- test_get_profile_by_executable()
- test_get_profile_for_game_name()
- test_custom_profile_override_builtin()
- test_profile_validation()
```

**Estimated LOC:** ~250 lines
**Estimated Effort:** 1 day

---

## Priority 2: Important Enhancements

### 5. GUI Component Testing

**Current State:** Only `gui.py` and `dashboard.py` have tests
**Gap:** No tests for settings dialogs, tabs, or wizard
**Impact:** Medium - UI bugs affect user experience

**Recommended Tests:**

#### `tests/gui/test_settings_dialog.py` ⭐ **NEW**
```python
- test_settings_dialog_initialization()
- test_tab_switching()
- test_save_settings()
- test_cancel_settings()
- test_apply_button_state()
```

#### `tests/gui/test_setup_wizard.py` ⭐ **NEW**
```python
- test_wizard_flow_all_steps()
- test_provider_selection()
- test_api_key_validation()
- test_test_connection()
- test_wizard_completion()
```

#### `tests/gui/test_providers_tab.py` ⭐ **NEW**
```python
- test_add_api_key()
- test_switch_provider()
- test_test_connection_success()
- test_test_connection_failure()
```

**Estimated LOC:** ~400 lines
**Estimated Effort:** 2 days

---

### 6. UI Design System Testing

**Current State:** `src/ui/test_design_system.py` exists but may be outdated
**Gap:** No tests for components library
**Impact:** Medium - Ensures consistent UI

**Recommended Tests:**

#### `tests/ui/test_design_tokens.py` ⭐ **NEW**
```python
- test_color_tokens_defined()
- test_typography_tokens_defined()
- test_spacing_tokens_defined()
- test_token_format_validation()
```

#### `tests/ui/test_components.py` ⭐ **NEW**
```python
- test_button_variants()
- test_input_validation()
- test_card_rendering()
- test_modal_lifecycle()
- test_layout_composition()
```

**Estimated LOC:** ~300 lines
**Estimated Effort:** 1-2 days

---

## Priority 3: Integration & E2E Tests

### 7. End-to-End Workflow Testing

**Current State:** Limited integration tests
**Gap:** No complete user workflow tests
**Impact:** High - Catches real-world issues

**Recommended Tests:**

#### `tests/e2e/test_game_assistance_workflow.py` ⭐ **NEW**
```python
- test_launch_game_detect_ask_question_workflow()
- test_knowledge_pack_query_workflow()
- test_macro_execution_workflow()
- test_session_logging_coaching_workflow()
```

#### `tests/e2e/test_first_run_experience.py` ⭐ **NEW**
```python
- test_setup_wizard_complete_flow()
- test_first_game_detection()
- test_first_ai_question()
```

#### `tests/e2e/test_customization_workflow.py` ⭐ **NEW**
```python
- test_create_custom_game_profile()
- test_create_knowledge_pack()
- test_create_macro()
- test_bind_macro_to_hotkey()
```

**Estimated LOC:** ~500 lines
**Estimated Effort:** 2-3 days

---

## Priority 4: Edge Cases & Error Handling

### 8. Robustness Testing

**Current State:** `tests/edge_cases/test_edge_cases.py` exists
**Gap:** Needs expansion for all modules

**Recommended Tests:**

#### `tests/edge_cases/test_error_recovery.py` ⭐ **NEW**
```python
- test_corrupted_config_recovery()
- test_missing_dependency_graceful_fail()
- test_api_rate_limit_handling()
- test_network_failure_retry()
- test_disk_full_error_handling()
```

#### `tests/edge_cases/test_concurrent_access.py` ⭐ **NEW**
```python
- test_concurrent_config_writes()
- test_concurrent_macro_execution_prevention()
- test_concurrent_index_updates()
```

**Estimated LOC:** ~300 lines
**Estimated Effort:** 1-2 days

---

## Priority 5: Performance & Security

### 9. Performance Testing

#### `tests/performance/test_knowledge_search_performance.py` ⭐ **NEW**
```python
- test_search_performance_large_corpus()
- test_index_build_time()
- test_embedding_generation_batch()
```

### 10. Security Testing

#### `tests/security/test_security.py` ⭐ **NEW**
```python
- test_credential_encryption_strength()
- test_path_traversal_prevention_knowledge_ingestion()
- test_macro_execution_safety_limits()
- test_api_key_not_logged()
- test_xss_prevention_in_knowledge_content()
```

**Estimated LOC:** ~400 lines
**Estimated Effort:** 2 days

---

## Recommended Testing Infrastructure Improvements

### 1. Code Coverage Tracking
```bash
# Add to CI/CD pipeline
pytest --cov=src --cov-report=html --cov-report=term-missing

# Target: 70% coverage (currently ~23%)
```

### 2. Test Markers Expansion
```python
# pytest.ini - Add more markers
[pytest]
markers =
    unit: Unit tests
    integration: Integration tests
    e2e: End-to-end tests
    gui: GUI tests (requires display)
    slow: Slow tests (>1s)
    security: Security tests
    performance: Performance tests
```

### 3. Parameterized Testing
```python
# Example: Test all AI providers with same tests
@pytest.mark.parametrize("provider", ["anthropic", "openai", "gemini"])
def test_provider_chat(provider, mock_api_key):
    # Test implementation
    pass
```

### 4. Mock Fixtures Library
Create `tests/mocks.py` with reusable mocks:
```python
@pytest.fixture
def mock_pynput_keyboard():
    """Mock pynput keyboard for macro tests"""
    pass

@pytest.fixture
def mock_ai_response():
    """Mock AI provider response"""
    pass
```

---

## Testing Best Practices to Adopt

### 1. Arrange-Act-Assert Pattern
```python
def test_example():
    # Arrange
    config = Config(require_keys=False)

    # Act
    result = config.save()

    # Assert
    assert result is True
```

### 2. Test Isolation
- Use `temp_dir` fixture for all file operations
- Mock external dependencies (APIs, system calls)
- Clean up resources in fixtures

### 3. Descriptive Test Names
```python
# BAD
def test_macro():
    pass

# GOOD
def test_macro_execution_stops_on_timeout():
    pass
```

### 4. Test Edge Cases
- Empty inputs
- None values
- Invalid data types
- Boundary conditions
- Concurrent access
- Error conditions

---

## Implementation Roadmap

### Phase 1: Critical Foundation (Week 1-2)
- [ ] Macro system tests (Priority 1.1)
- [ ] Knowledge system tests (Priority 1.2)
- [ ] Session logger tests (Priority 1.3)
- [ ] Game profile tests (Priority 1.4)

**Target:** Bring coverage from 23% → 45%

### Phase 2: GUI & Integration (Week 3-4)
- [ ] GUI component tests (Priority 2.5)
- [ ] Settings dialog tests (Priority 2.5)
- [ ] E2E workflow tests (Priority 3.7)

**Target:** Bring coverage from 45% → 60%

### Phase 3: Robustness & Quality (Week 5-6)
- [ ] Edge case tests (Priority 4.8)
- [ ] Performance tests (Priority 5.9)
- [ ] Security tests (Priority 5.10)
- [ ] UI component tests (Priority 2.6)

**Target:** Bring coverage from 60% → 70%+

---

## Metrics & Goals

### Current State
- **Module Coverage:** 22.9% (11/48)
- **Line Coverage:** Unknown (need to run pytest --cov)
- **Test Files:** 27 files
- **Test LOC:** ~3,734 lines

### Target State (6 weeks)
- **Module Coverage:** 70%+ (34/48)
- **Line Coverage:** 70%+
- **Test Files:** 50+ files
- **Test LOC:** ~8,000+ lines

### Success Metrics
- ✅ All Priority 1 modules have comprehensive unit tests
- ✅ Critical workflows have E2E tests
- ✅ CI/CD runs full test suite on every commit
- ✅ Coverage reports generated and tracked
- ✅ No regressions in tested code

---

## Quick Wins (Can Implement Immediately)

1. **Add coverage reporting to CI/CD**
   ```yaml
   # .github/workflows/ci.yml
   - name: Run tests with coverage
     run: pytest --cov=src --cov-report=term-missing
   ```

2. **Create `tests/mocks.py` with common mocks**

3. **Expand `conftest.py` with more fixtures**

4. **Add `test_macro_manager.py` - highest priority module**

5. **Add `test_knowledge_index.py` - test recent bug fix**

---

## Conclusion

Omnix has a solid testing foundation with good organization and practices, but **significant gaps exist in critical areas**. Prioritizing tests for the macro system, knowledge system, and session management will provide the highest return on investment in terms of:

1. **Bug Prevention** - Catch issues before production
2. **Refactoring Confidence** - Safe to improve code
3. **Documentation** - Tests serve as usage examples
4. **Regression Prevention** - Prevent fixed bugs from returning

**Recommended Immediate Actions:**
1. Start with **macro system tests** (highest risk area)
2. Add **knowledge index regression tests** for recent bug fix
3. Implement **coverage tracking** in CI/CD
4. Create **E2E smoke tests** for critical workflows

**Estimated Total Effort:** 8-12 weeks for full roadmap
**Minimum Viable Effort:** 2-3 weeks for Priority 1 tests

---

**Document Version:** 1.0
**Last Updated:** 2025-11-21
**Author:** AI Assistant Analysis
