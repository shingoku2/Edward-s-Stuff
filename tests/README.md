# Omnix Test Suite

This directory contains the comprehensive test suite for the Omnix Gaming Companion.

## Structure

```
tests/
├── __init__.py                 # Package initialization
├── conftest.py                 # Shared pytest fixtures
├── helpers.py                  # Test utility functions
├── README.md                   # This file
│
├── unit/                       # Unit tests
│   ├── test_config.py          # Config module tests
│   ├── test_game_detector.py   # Game detection tests
│   ├── test_game_profiles.py   # Game profile tests
│   ├── test_ai_assistant.py    # AI assistant tests
│   ├── test_ai_router.py       # AI router tests
│   ├── test_providers.py       # Provider tests
│   ├── test_credential_store.py # Credential storage tests
│   ├── test_macro_system.py    # Macro and keybind tests
│   ├── test_knowledge_system.py # Knowledge pack tests
│   ├── test_game_watcher.py    # Game watcher tests
│   └── test_utils.py           # Utility function tests
│
├── integration/                # Integration tests
│   ├── test_ai_integration.py  # AI component integration
│   └── test_session_management.py # Session management
│
├── edge_cases/                 # Edge case and error tests
│   └── test_edge_cases.py      # Boundary condition tests
│
└── build/                      # Pre-build validation tests
    └── test_prebuild.py        # Build readiness checks
```

## Running Tests

### Run all tests
```bash
pytest
```

### Run specific test category
```bash
pytest tests/unit/                 # Unit tests only
pytest tests/integration/          # Integration tests only
pytest tests/edge_cases/           # Edge cases only
pytest tests/build/                # Pre-build tests only
```

### Run specific test file
```bash
pytest tests/unit/test_config.py
pytest tests/unit/test_macro_system.py
```

### Run tests with markers
```bash
pytest -m unit                     # All unit tests
pytest -m integration              # All integration tests
pytest -m "not slow"               # Exclude slow tests
pytest -m "not requires_api_key"   # Exclude tests needing API keys
pytest -m "not ui"                 # Exclude UI tests
```

### Run with coverage
```bash
pytest --cov=src --cov-report=html
```

### Run in verbose mode
```bash
pytest -v
pytest -vv                         # Extra verbose
```

## Test Markers

Tests are categorized using pytest markers:

- `@pytest.mark.unit` - Unit tests for individual components
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.ui` - UI/GUI tests (may require display)
- `@pytest.mark.slow` - Tests that take longer to run
- `@pytest.mark.skip_ci` - Tests to skip in CI environment
- `@pytest.mark.requires_api_key` - Tests requiring API keys
- `@pytest.mark.network` - Tests requiring network access
- `@pytest.mark.windows` - Windows-specific tests
- `@pytest.mark.linux` - Linux-specific tests
- `@pytest.mark.macos` - macOS-specific tests

## Shared Fixtures

Common test fixtures are defined in `conftest.py`:

- `temp_dir` - Temporary directory for test files
- `clean_config_dir` - Clean configuration directory
- `mock_api_key` - Mock API key for testing
- `mock_game_profile` - Sample game profile
- `game_detector` - GameDetector instance
- `game_profile_store` - GameProfileStore instance
- `config` - Test Config instance
- `macro_store` - MacroStore instance
- `knowledge_pack_store` - KnowledgePackStore instance
- `knowledge_index` - KnowledgeIndex instance
- `session_logger` - SessionLogger instance
- `sample_knowledge_pack` - Sample knowledge pack
- `sample_macro` - Sample macro

## Test Helpers

Utility functions in `helpers.py`:

- `create_test_config_file()` - Create test config files
- `create_temp_text_file()` - Create temporary text files
- `cleanup_test_profile()` - Clean up test game profiles
- `has_any_api_key()` - Check for configured API keys
- `is_headless_environment()` - Check if running headless
- `assert_valid_game_profile()` - Validate game profile
- `assert_valid_macro()` - Validate macro
- `assert_valid_knowledge_pack()` - Validate knowledge pack

## Writing New Tests

### Basic unit test structure

```python
import pytest


@pytest.mark.unit
class TestMyComponent:
    """Test MyComponent functionality"""

    def test_initialization(self):
        """Test component initialization"""
        from my_module import MyComponent

        component = MyComponent()
        assert component is not None

    def test_method_behavior(self):
        """Test specific method behavior"""
        from my_module import MyComponent

        component = MyComponent()
        result = component.do_something()
        assert result == expected_value
```

### Using fixtures

```python
import pytest


@pytest.mark.unit
class TestWithFixtures:
    """Test using shared fixtures"""

    def test_with_temp_dir(self, temp_dir):
        """Test using temporary directory"""
        import os
        test_file = os.path.join(temp_dir, "test.txt")
        # Use temp_dir for test files
        assert os.path.exists(temp_dir)

    def test_with_config(self, config):
        """Test using shared config"""
        assert config.ai_provider in ["anthropic", "openai", "gemini"]
```

### Testing edge cases

```python
import pytest


@pytest.mark.unit
class TestEdgeCases:
    """Test edge cases and error handling"""

    def test_empty_input(self):
        """Test handling empty input"""
        from my_module import MyComponent

        component = MyComponent()
        # Should handle gracefully
        result = component.process("")
        assert result is not None

    def test_invalid_input(self):
        """Test handling invalid input"""
        from my_module import MyComponent

        component = MyComponent()
        with pytest.raises(ValueError):
            component.process(None)
```

## Continuous Integration

Tests are automatically run in GitHub Actions on:
- Pull requests
- Pushes to main branch
- Manual workflow dispatch

CI environment automatically:
- Skips UI tests (headless environment)
- Skips tests marked with `@pytest.mark.skip_ci`
- Uses offscreen Qt platform for PyQt6 tests
- Sets test master password for credential store

## Coverage

Coverage reports are generated with:
```bash
pytest --cov=src --cov-report=html
```

View HTML report at: `htmlcov/index.html`

## Troubleshooting

### Import errors
Ensure `src` directory is in Python path. This is configured in `pytest.ini`:
```ini
[pytest]
pythonpath = src
```

### GUI test failures in headless environment
UI tests are automatically skipped in CI. To run locally without display:
```bash
export QT_QPA_PLATFORM=offscreen
pytest
```

### API key test failures
Tests requiring API keys are marked with `@pytest.mark.requires_api_key` and `@pytest.mark.skip_ci`. They are skipped automatically in CI.

To run locally with API keys:
```bash
export ANTHROPIC_API_KEY=your_key_here
pytest -m requires_api_key
```

## Best Practices

1. **Use appropriate markers** - Mark tests with correct categories
2. **Use fixtures** - Leverage shared fixtures from `conftest.py`
3. **Isolate tests** - Each test should be independent
4. **Clean up** - Tests should clean up any created resources
5. **Descriptive names** - Test names should describe what they test
6. **One assertion focus** - Each test should focus on one behavior
7. **Fast tests** - Keep tests fast; mark slow tests with `@pytest.mark.slow`
8. **Skip appropriately** - Use `pytest.skip()` for environment-specific tests

## Migration Notes

This test suite was refactored from individual test files to an organized pytest structure. Old test files in the root directory have been migrated to this structure with:

- Converted from custom test runners to pytest
- Removed code duplication using shared fixtures
- Standardized imports and assertions
- Added proper categorization with markers
- Organized into logical subdirectories

For the old test structure, see git history before this refactoring.
