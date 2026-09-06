# Windows release checklist

1. Create a fresh Python 3.11+ environment and install `.[dev,build]`.
2. Run the full headless test suite and fatal lint/security checks.
3. Build with `GamingAIAssistant.spec` and verify the executable on Windows.
4. Confirm Ollama connectivity, profile migration backups, credential storage,
   and Accessibility/input permissions where applicable.
5. Publish the unsigned bundle with its matching version and checksum.

The GitHub release workflow performs the cross-platform build matrix. Code
signing and update delivery require a separate production security process.
