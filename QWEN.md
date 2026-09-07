# Omnix contributor context

Follow [AGENTS.md](AGENTS.md). Omnix 3.0 has one native PyQt6 desktop client and
an installable Python package rooted at `src/omnix`.

Before changing service boundaries or stored data, read
[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) and
[docs/UPGRADING.md](docs/UPGRADING.md).

For CI work, follow [docs/CI_CD_GUIDE.md](docs/CI_CD_GUIDE.md): Python 3.11 on
GitHub-hosted Ubuntu, Windows, and macOS, with offscreen Qt, Linux `libegl1`,
canonicalized filesystem roots, and an audited `setuptools>=83` environment.
