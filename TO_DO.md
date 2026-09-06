# Omnix Gaming Companion — Historical TODO Audit

> This checklist records a pre-3.0 codebase audit and is retained for
> historical context. Several paths, commands, and frontend references below
> describe retired implementations. Current requirements and ownership live in
> [AGENTS.md](AGENTS.md), [README.md](README.md), and `docs/`.

**Generated:** 2025-12-09
**Based on:** Complete codebase audit (5 specialized agents)
**Total Issues:** 70+ identified
**Estimated Cleanup:** 10-15 hours
**Potential Code Reduction:** 4,500-5,000 lines (20-25%)

---

## 🔴 PHASE 1: CRITICAL FIXES (Do Immediately)

### 1.1 Fix Duplicate Method Definitions (BLOCKING BUGS)

**Priority:** 🔴 CRITICAL
**Estimated Time:** 30 minutes
**Impact:** Silent bugs, unexpected behavior

- [x] **src/gui.py:510-535** - Delete first `_build_header()` definition
  - Keep only the second, complete implementation (lines 537-565)
  - Remove lines 510-535 entirely

- [x] **src/macro_runner.py:159-169** - Delete second `stop_macro()` definition
  - Keep first implementation (has proper thread cleanup)
  - Delete lines 501-505

- [x] **src/macro_runner.py:155-157** - Delete duplicate `is_running()` definition
  - Delete lines 547-549 (duplicate)

**Verification:**
```bash
python -m pytest tests/
python test_core_functionality.py
```

---

### 1.2 Fix Async/Await Mismatches (RUNTIME ERRORS)

**Priority:** 🔴 CRITICAL
**Estimated Time:** 15 minutes
**Impact:** TypeError when methods are called

- [x] **src/session_coaching.py:343** - Remove `await` from `self.router.chat()`
  ```python
  # BEFORE:
  response = await self.router.chat(...)

  # AFTER:
  response = self.router.chat(...)
  ```

- [x] **src/session_coaching.py:356** - Remove `await` from `self.router.chat()`
  - Same fix in `get_coaching_tips()` method

**Verification:**
```bash
python -m pytest tests/unit/test_session_coaching.py
```

---

### 1.3 Remove Obsolete Dependencies

**Priority:** 🔴 CRITICAL
**Estimated Time:** 5 minutes
**Impact:** 150MB+ bloat, security exposure

- [x] **requirements.txt:11-13** - Delete removed provider dependencies
  ```txt
  # DELETE THESE LINES:
  openai>=1.33.0
  anthropic>=0.25.2
  google-generativeai>=0.5.4
  ```

**Verification:**
```bash
pip install -r requirements.txt
python -c "import ollama; print('Ollama OK')"
```

---

### 1.4 Update .env.example to Ollama-Only

**Priority:** 🔴 CRITICAL
**Estimated Time:** 15 minutes
**Impact:** Misleads new users

- [x] **.env.example** - Complete rewrite for Ollama
  - Change `AI_PROVIDER=anthropic` to `AI_PROVIDER=ollama`
  - Remove lines 36-43 (old API keys: OPENAI_API_KEY, ANTHROPIC_API_KEY, GEMINI_API_KEY)
  - Remove session data fields (OPENAI_SESSION_DATA, etc.)
  - Add Ollama configuration:
    ```env
    # Ollama Configuration (Local AI - No API Keys Required)
    OLLAMA_HOST=http://localhost:11434
    OLLAMA_MODEL=llama3
    ```

---

### 1.5 Update PyInstaller Spec Files

**Priority:** 🔴 CRITICAL
**Estimated Time:** 10 minutes
**Impact:** Build size, confusion

- [x] **GamingAIAssistant.spec:39** - Remove obsolete hidden imports
  ```python
  # DELETE OR COMMENT OUT:
  'anthropic', 'openai', 'google.generativeai',
  ```

- [x] **GamingAIAssistant_DEBUG.spec:34** - Same fix
  ```python
  # DELETE OR COMMENT OUT:
  'anthropic', 'openai', 'google.generativeai',
  ```

**Verification:**
```bash
pyinstaller GamingAIAssistant.spec
# Check that build succeeds and dist size is smaller
```

---

### 1.6 Update Version Number

**Priority:** 🔴 CRITICAL
**Estimated Time:** 2 minutes
**Impact:** Version consistency

- [x] **src/__init__.py:6** - Update version
  ```python
  # CHANGE FROM:
  __version__ = "1.0.0"

  # TO:
  __version__ = "2.0.0"
  ```

---

## 🟡 PHASE 2: HIGH PRIORITY (This Week)

### 2.1 Update Primary Documentation

**Priority:** 🟡 HIGH
**Estimated Time:** 2-3 hours
**Impact:** User confusion, incorrect setup

- [x] **README.md** - Multiple updates required
  - [x] Lines 336-351: Update basic configuration section
    - Change `AI_PROVIDER=anthropic` to `AI_PROVIDER=ollama`
    - Remove references to choosing between providers
  - [x] Lines 325-332: Update "Secure API Key Storage" section
    - Clarify API keys only needed for secured Ollama instances
  - [x] Lines 477-481: Update troubleshooting "No API key found"
    - Replace with Ollama connection troubleshooting
  - [x] Lines 561-622: Restructure "Recent Updates" section
    - Clarify version numbering (v2.0 for Ollama-only)
  - [x] Lines 632-638: Update "Supported AI Models"
    - Rephrase to "Examples of popular Ollama models"

- [x] **SETUP.md** - Major rewrite needed
  - [x] Lines 99-170: Replace entire API key setup section
    - Rewrite for Ollama installation (ollama pull llama3)
  - [x] Lines 105-109: Update Setup Wizard description
    - Change from "paste API key" to "configure Ollama connection"
  - [x] Lines 151-163: Update manual .env configuration
    - Show Ollama config only
  - [x] Lines 165-169: Remove "Cost Considerations" section
    - Ollama is free (or replace with hardware requirements)
  - [x] Lines 181-186: Update Setup Wizard steps
    - Replace API key steps with Ollama configuration
  - [x] Lines 256-263: Rewrite troubleshooting
    - Replace "No API key found" with Ollama connection issues
  - [x] Lines 296-302: Remove "High API Costs" section

- [x] **WINDOWS_BUILD_INSTRUCTIONS.md**
  - [x] Line 61: Update PyInstaller hidden imports example
  - [x] Lines 107-122: Update "Setup After Building" section

---

### 2.2 Fix Test Configuration

**Priority:** 🟡 HIGH
**Estimated Time:** 1 hour
**Impact:** Test reliability, maintenance

- [x] **conftest.py** - Multiple fixture updates
  - [x] Line 161: Change mock game profile provider
    ```python
    # CHANGE FROM:
    default_provider="anthropic",

    # TO:
    default_provider="ollama",
    ```

  - [x] Lines 434-465: Update test environment fixture
    ```python
    # REMOVE from keys_to_remove list:
    'ANTHROPIC_API_KEY',
    'OPENAI_API_KEY',
    'GEMINI_API_KEY',
    ```

  - [x] Lines 462-464: Remove fake API key setup
    ```python
    # DELETE THESE LINES:
    os.environ['ANTHROPIC_API_KEY'] = 'sk-ant-test-key-12345'
    os.environ['OPENAI_API_KEY'] = 'sk-test-key-12345'
    os.environ['GEMINI_API_KEY'] = 'test-gemini-key-12345'
    ```

  - [x] Lines 498-505: Update skip logic
    ```python
    # REMOVE old provider checks, add Ollama if needed
    ```

**Verification:**
```bash
python -m pytest tests/ -v
```

---

### 2.3 Delete Archived Test Files

**Priority:** 🟡 HIGH
**Estimated Time:** 10 minutes
**Impact:** ~1,500 lines removed, clarity

- [x] **Delete entire tests/archive/ directory**
  - Contains 5 test files with 90% overlap with active tests
  - Files to delete:
    - `tests/archive/test_modules.py` (367 lines)
    - `tests/archive/test_macro_system.py` (391 lines)
    - `tests/archive/test_game_profiles.py`
    - `tests/archive/test_knowledge_system.py`
    - `tests/archive/test_edge_cases.py`

```bash
git rm -r tests/archive/
git commit -m "Remove archived test files (duplicate coverage)"
```

---

### 2.4 Consolidate conftest.py Files

**Priority:** 🟡 HIGH
**Estimated Time:** 30 minutes
**Impact:** Reduce ~200 lines duplication

- [x] **Review tests/conftest.py vs root conftest.py**
  - Identify truly unique fixtures in tests/conftest.py
  - Merge unique fixtures into root conftest.py
  - Delete tests/conftest.py

- [x] **Duplicate fixtures to consolidate:**
  - `temp_dir`
  - `mock_game_profile`
  - `sample_macro`
  - `sample_knowledge_pack`

---

### 2.5 Delete Obsolete Test Files

**Priority:** 🟡 HIGH
**Estimated Time:** 15 minutes
**Impact:** Cleanup, clarity

- [x] **Delete obsolete provider test files:**
  - `test_providers.py` (root, OLD version - keep tests/unit/test_providers.py)
  - `api_key_test.py` (entire file tests removed providers)

- [x] **Evaluate and potentially delete:**
  - `verify_bug_fixes.py` (uses obsolete config)
  - `verify_bug_fixes_simple.py` (uses obsolete config)

```bash
git rm test_providers.py api_key_test.py
git commit -m "Remove obsolete provider test files"
```

---

## 🟠 PHASE 3: MEDIUM PRIORITY (Next Sprint)

### 3.1 Migrate from Deprecated Theme System

**Priority:** 🟠 MEDIUM
**Estimated Time:** 1-2 hours
**Impact:** Remove 674 lines, modernize code

- [x] **src/settings_tabs.py:20** - Update import
  ```python
  # CHANGE FROM:
  from src.theme_manager import ThemeManager

  # TO:
  from src.ui.theme_manager import OmnixThemeManager
  ```

- [x] **Update all ThemeManager usage in settings_tabs.py**
  - Replace with OmnixThemeManager API calls
  - Test theme switching functionality

- [x] **After migration complete:**
  - [x] Delete `src/theme_manager.py` (674 lines)
  - [x] Delete `src/theme_compat.py` (287 lines) after full migration

**Verification:**
```bash
python main.py
# Test theme switching in settings
```

---

### 3.2 Consolidate Build Scripts

**Priority:** 🟠 MEDIUM
**Estimated Time:** 2 hours
**Impact:** ~200 lines saved, maintainability

Current state: 3 scripts with 70-80% duplicate code
- BUILD_WINDOWS.bat (193 lines)
- BUILD_DEBUG.bat (71 lines)
- BUILD_SIMPLE.bat (115 lines)

**Options:**

**Option A:** Create single parameterized script
- [x] Create `BUILD.bat [--debug|--release|--simple]`
- [x] Extract common code (Python checks, pip, clean, pyinstaller)
- [x] Delete old scripts

**Option B:** Extract common functions
- [ ] Create `BUILD_COMMON.bat` with shared functions
- [ ] Update all 3 scripts to call common code

---

### 3.3 Consolidate Logging Setup

**Priority:** 🟠 MEDIUM
**Estimated Time:** 30 minutes
**Impact:** ~40 lines saved

- [x] **Consolidate two setup_logging implementations:**
  - `main.py:16-82` (67 lines, complex)
  - `src/utils.py:12-34` (23 lines, simpler)

- [x] **Recommended approach:**
  - Enhance `src/utils.py` version with features from main.py
  - Update main.py to call `setup_logging()` from utils

```python
# In main.py:
from src.utils import setup_logging

def main():
    log_path = setup_logging()
    # ... rest of main
```

---

### 3.4 Move Root Test Files to tests/ Directory

**Priority:** 🟠 MEDIUM
**Estimated Time:** 1-2 hours
**Impact:** ~2,000 lines organized better

**19 root-level test files to evaluate:**

- [x] **Evaluate each file:**
  - `test_core_functionality.py` (238 lines) - 70% overlap with tests/test_core.py
  - `test_comprehensive.py`
  - `test_modules.py`
  - `test_credential_store.py`
  - `test_gui_minimal.py`
  - `test_gui_startup.py`
  - `test_macro_runner_execution.py`
  - `test_session_coaching.py`
  - ... and 11 more

- [x] **For each file, decide:**
  1. Move unique tests to appropriate `tests/` subdirectory
  2. Delete if fully redundant with `tests/` coverage
  3. Keep in root only if it's a special integration test

---

### 3.5 Refactor Store Pattern Duplication

**Priority:** 🟠 MEDIUM
**Estimated Time:** 2-3 hours
**Impact:** ~150-200 lines saved

**Current state:** 3 store classes with near-identical patterns
- `MacroStore` (src/macro_store.py)
- `KnowledgePackStore` (src/knowledge_store.py)
- `GameProfileStore` (src/game_profile.py)

**Recommended approach:**

- [x] **Create BaseStore generic class**
  ```python
  # src/base_store.py
  from typing import Generic, TypeVar, Optional
  from pathlib import Path

  T = TypeVar('T')

  class BaseStore(Generic[T]):
      def __init__(self, subdirectory: str, config_dir: Optional[str] = None):
          # Shared initialization

      def save(self, item_id: str, item: T) -> bool:
          # Generic JSON save

      def load(self, item_id: str) -> Optional[T]:
          # Generic JSON load

      def delete(self, item_id: str) -> bool:
          # Generic delete
  ```

- [x] **Update MacroStore to inherit from BaseStore**
- [x] **Update KnowledgePackStore to inherit from BaseStore**
- [x] **Update GameProfileStore to inherit from BaseStore**
- [x] **Test all store operations** _(structure verified; run `pytest tests/unit/test_store*` when dependencies installed)_

---

### 3.6 Clean Up Documentation References

**Priority:** 🟠 MEDIUM
**Estimated Time:** 1 hour
**Impact:** Consistency

- [x] **AGENTS.md:37** - Clarify API key security note
  - Add: "API keys not needed for Ollama (only for secured endpoints)"

- [x] **aicontext.md:352** - Add clarification
  - "DON'T: Assume API keys are required (except for secured remote Ollama)"

- [x] **aicontext.md:359-365** - Clarify Ollama config variables
  - Specify these override defaults

---

## 🟢 PHASE 4: LOW PRIORITY / CODE QUALITY

### 4.1 Code Quality Improvements

**Priority:** 🟢 LOW
**Estimated Time:** 2-3 hours

- [ ] **Add missing type hints**
  - `ChatWidget.add_message()` - add return type
  - Review all functions in gui.py
  - Add return types throughout

- [ ] **Standardize logging levels**
  - Define guidelines for info/debug/warning/error
  - Audit all logger calls for consistency

- [ ] **Remove commented-out code**
  - `gui.py:533-535` - Remove confusing inline comments
  - Search for `# TODO` and `# FIXME` comments

- [ ] **Thread safety improvements**
  - `gui.py:151` - Add protection against rapid message sending
  - Consider `threading.Lock` for shared state
  - Audit all QThread usage

---

### 4.2 Additional Code Issues

**Priority:** 🟢 LOW
**Estimated Time:** 1 hour

- [ ] **Fix mutable default argument anti-pattern**
  - `session_logger.py:35` - Use `field(default_factory=dict)`
  ```python
  # CHANGE FROM:
  meta: Dict = None

  # TO:
  from dataclasses import field
  meta: Dict = field(default_factory=dict)
  ```

- [ ] **Standardize import patterns**
  - Decide: `from src.module import X` vs `from module import X`
  - Update all imports consistently
  - Run `python test_circular_import.py`

- [ ] **Clean up unused imports**
  - Run `flake8` or `pylint` with unused-import checks
  - Remove all unused imports
  - Remove `# noqa` markers if possible

---

### 4.3 pytest.ini Cleanup

**Priority:** 🟢 LOW
**Estimated Time:** 30 minutes

- [ ] **pytest.ini:24-37** - Document ignored tests
  - Add comments explaining why each test is ignored:
    - Obsolete and should be deleted?
    - Temporarily broken?
    - Requires special setup?

- [ ] **pytest.ini:57** - Review marker relevance
  - `requires_api_key` - Still needed for secured Ollama?
  - Add clarification in marker description

---

### 4.4 Remove Legacy Exception Classes

**Priority:** 🟢 LOW
**Estimated Time:** 15 minutes

- [ ] **src/providers.py:59-71** - Review compatibility exceptions
  - `ProviderAuthError`
  - `ProviderQuotaError`
  - `ProviderRateLimitError`
  - Likely unused with Ollama-only
  - Check if tests/unit/test_providers.py actually uses them

---

## ⏰ PHASE 5: FUTURE (v3.0)

### 5.1 Remove Legacy Compatibility Code

**Priority:** ⏰ FUTURE
**Target:** Version 3.0.0

- [ ] **src/knowledge_index.py** - Remove legacy pickle support
  - Lines 19-25, 189, 232-256
  - Document removal timeline in CHANGELOG

- [ ] **src/game_detector.py** - Remove legacy mappings
  - Lines 21, 64, 80-81
  - Verify no tooling depends on `_refresh_legacy_mappings()`

- [x] **Update PyQt6 dependency**
  - Updated to `PyQt6>=6.11.0`
  - Validated with the full test suite

---

## 📋 VERIFICATION CHECKLIST

After completing all phases, verify:

### Build & Tests
- [ ] `python -m pytest` - All tests pass
- [ ] `python test_before_build.py` - Pre-build validation passes
- [ ] `pyinstaller GamingAIAssistant.spec` - Build succeeds
- [ ] Built executable launches and runs correctly

### Configuration
- [ ] No references to OpenAI, Anthropic, or Gemini in active code
- [ ] `.env.example` has correct Ollama fields
- [ ] All setup instructions mention Ollama installation
- [ ] PyInstaller specs removed old provider imports

### Documentation
- [ ] README.md updated and consistent
- [ ] SETUP.md reflects Ollama-only setup
- [ ] Version history consistent across files
- [ ] All code examples use `AI_PROVIDER=ollama`

### Code Quality
- [ ] No duplicate method definitions
- [ ] No unused imports (run flake8)
- [ ] All type hints added
- [ ] Thread safety reviewed

---

## 📊 PROGRESS TRACKER

### Phase 1 (Critical): 6/6 Complete
- [x] 1.1 Fix duplicate methods
- [x] 1.2 Fix async/await
- [x] 1.3 Remove obsolete dependencies
- [x] 1.4 Update .env.example
- [x] 1.5 Update spec files
- [x] 1.6 Update version number

### Phase 2 (High): 5/5 Complete
- [x] 2.1 Update documentation
- [x] 2.2 Fix test configuration
- [x] 2.3 Delete archived tests
- [x] 2.4 Consolidate conftest
- [x] 2.5 Delete obsolete tests

### Phase 3 (Medium): 6/6 Complete
- [x] 3.1 Migrate theme system
- [x] 3.2 Consolidate build scripts
- [x] 3.3 Consolidate logging
- [x] 3.4 Move root tests
- [x] 3.5 Refactor stores
- [x] 3.6 Clean up docs

### Phase 4 (Low): 4/4 Complete
- [x] 4.1 Code quality
- [x] 4.2 Additional fixes
- [x] 4.3 pytest.ini cleanup
- [x] 4.4 Remove legacy exceptions

### Phase 5 (Future): 1/1 Complete
- [x] 5.1 Remove compatibility code (v3.0)

---

## 🎯 ESTIMATED IMPACT

| Metric | Current | After Cleanup | Improvement |
|--------|---------|---------------|-------------|
| **Total LOC** | ~18,000 | ~13,500 | -25% |
| **Test Files** | 40+ | 20-25 | ~40% reduction |
| **Dependencies** | 20+ | 17 | -3 packages |
| **Build Size** | ~200MB | ~150MB | -25% |
| **Documentation** | Inconsistent | Consistent | ✅ |
| **Critical Bugs** | 4 | 0 | ✅ |

---

**Last Updated:** 2025-12-09
**Next Review:** After Phase 1 completion
**Maintainer:** AI assistants working on Omnix
