# Repository Guidelines

## Project Structure & Module Organization
- `src/`: Core Python app (game detection, AI routing, macro system, GUI). Common touchpoints: `ai_assistant.py`, `providers.py`, `game_detector.py`, `knowledge_*`, `macro_*`, `gui.py`.
- `frontend/`: Vite + React + TypeScript UI; run commands from this directory (`src/` holds components/styles).
- `tests/`: Pytest suite mirroring modules; shared fixtures live in `conftest.py`; settings in `pytest.ini` and `.coveragerc`.
- `scripts/` plus `build/` and `dist/`: helper scripts and packaged artifacts; `BUILD_WINDOWS.bat` and `build_windows_exe.py` drive bundling.
- `docs/` and root markdown files: user guides, QA reports, and setup references.

## Build, Test, and Development Commands
- Install runtime deps: `pip install -r requirements.txt`; dev tooling: `pip install -r requirements-dev.txt`.
- Run app: `python main.py` (reads `.env` or launches the Setup Wizard).
- Backend checks: `pytest` or `pytest --cov=src --cov-report=term-missing`; format/lint via `pre-commit run --all-files` or `black . && isort . && flake8`.
- Frontend: `cd frontend && npm install`; develop with `npm run dev`, lint with `npm run lint`, build with `npm run build`.
- Packaging (Windows): `BUILD_SIMPLE.bat` for a quick build; `BUILD_WINDOWS.bat` for the full EXE bundle.

## Coding Style & Naming Conventions
- Python: Black (100-char lines), isort (black profile, width 100), flake8 max line length 127 with `E203` ignored. Prefer type hints, concise docstrings on modules/classes, `snake_case` functions/vars, `PascalCase` classes, `UPPER_SNAKE_CASE` constants.
- Frontend: TypeScript React functional components; components use `PascalCase.tsx`, utilities `camelCase.ts`; follow ESLint rules in `frontend/.eslintrc.cjs`.
- Keep configuration, API keys, and secrets out of logs and commits; use `.env` (see `.env.example`).

## Testing Guidelines
- Add tests in `tests/` using `test_*.py` naming; mirror the module layout where possible. Use `pytest -k` for focused runs and `pytest --cov=src` before PRs; generate coverage HTML with `--cov-report=html` when chasing gaps.
- Reuse fixtures from `conftest.py`; apply markers from `pytest.ini` (e.g., `-m "not slow"`) to scope heavier scenarios.

## Commit & Pull Request Guidelines
- Commit messages in imperative, present tense (e.g., "Add macro replay safeguards"); group related changes per commit and run lint + tests before pushing.
- PRs: include a concise summary, linked issue/ticket when applicable, test evidence (`pytest`/coverage output), and screenshots for UI changes (PyQt GUI or `frontend/`). Call out config or migration steps in the description.

## Security & Configuration Tips
- Never commit keys; rely on the system keyring in `credential_store.py` and `.env` entries. Rotate exposed secrets immediately.
- Validate new dependencies with `bandit -r src` and `safety check`; keep pins in `requirements*.txt` and `frontend/package-lock.json` up to date.
