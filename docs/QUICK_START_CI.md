# CI/CD Quick Start Guide

Quick reference for working with the Omnix CI/CD pipeline.

## Quick Commands

### Testing

```bash
# Run all tests
pytest

# Run specific test category
pytest -m unit
pytest -m integration

# Run with coverage
pytest --cov=src --cov-report=html

# Simulate CI environment
export QT_QPA_PLATFORM=offscreen
xvfb-run -a pytest tests/ -v
```

### Verification

```bash
# Verify CI/CD pipeline
python scripts/verify_ci.py

# Check workflow status
gh run list --limit 5

# View latest run
gh run view

# Re-run failed workflow
gh run rerun
```

### Deployment

```bash
# Deploy to staging (automatic)
git checkout staging
git merge main
git push origin staging

# Deploy to staging (manual)
./scripts/deploy_staging.sh

# Verify deployment
cat /opt/omnix/staging/.deployment_info
```

### Runner Management

```bash
# Check runner status
ssh pve
sudo pct enter 200
sudo systemctl status actions-runner

# Restart runner
sudo systemctl restart actions-runner

# View logs
sudo journalctl -u actions-runner -f
```

## Workflow Files

- `.github/workflows/ci.yml` - Main CI pipeline
- `.github/workflows/staging-deploy.yml` - Staging deployment

## Test Structure

```
tests/
├── unit/               # Component tests
├── integration/        # Integration tests
│   └── test_ci_pipeline.py  # CI-specific tests
├── edge_cases/         # Edge cases
└── conftest.py         # Test fixtures
```

## Common Issues

### Tests fail in CI but pass locally

```bash
# Use same environment as CI
export QT_QPA_PLATFORM=offscreen
xvfb-run -a pytest tests/ -v
```

### Runner is offline

```bash
ssh pve
sudo pct enter 200
sudo systemctl restart actions-runner
```

### Deployment fails

```bash
# Check deployment logs
gh run view --log-failed

# Manual deployment
./scripts/deploy_staging.sh
```

## Resources

- [Full CI/CD Guide](CI_CD_GUIDE.md)
- [CLAUDE.md](../CLAUDE.md) - Project documentation
- [pytest.ini](../pytest.ini) - Test configuration

## Status URLs

- **Actions:** https://github.com/shingoku2/Omnix-All-knowing-gaming-companion/actions
- **Repository:** https://github.com/shingoku2/Omnix-All-knowing-gaming-companion
