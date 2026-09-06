# Technology Stack: Omnix

## Omnix 3.0 runtime
- **Primary Language:** Python 3.11+
- **Application Framework:** PyQt6 (Main application shell, system tray, and heavy-duty window management).
- **Package:** `src/omnix` with `omnix.__main__:main` as the composition root.
- **Process Monitoring:** `psutil` for passive game detection.
- **Input & Automation:** `pynput` for recording and executing mouse/keyboard macros.
- **Environment Management:** `python-dotenv`; JSON configuration and versioned migrations.
- **Security:** `cryptography` and `keyring` for local credential and sensitive data protection.

## Desktop UI
- **Framework:** Native PyQt6 dashboard and always-on-top overlay.
- **Components:** Reusable controls in `src/omnix/ui/components` with centralized tokens.
- **Theme:** Restrained dark palette with accessible contrast and a single cool accent.

## AI & Intelligence
- **Inference Engine:** Ollama-first local LLM orchestration behind the provider factory.
- **Data Ingestion:** `beautifulsoup4`, `lxml`, and `requests` for web scraping and wiki processing.
- **Document Analysis:** `pypdf` and `pdfplumber` for ingestion of PDFs and game manuals.
- **Search System:** SQLite FTS5 candidate retrieval with TF-IDF semantic reranking.

## Deployment & Build
- **Packaging:** PyInstaller specs for unsigned Windows, macOS, and Linux bundles.
- **Testing:** `pytest` with headless Qt and cross-platform CI.
- **Linting & Analysis:** Black, isort, flake8 fatal checks, Bandit, and targeted mypy.
- **Licensing:** Supabase Edge Function; clients have no direct license-table access.
