# CI/CD Pipeline Guide for Omnix

**Last Updated:** 2025-11-20
**Environment:** Proxmox Self-Hosted

---

## Table of Contents

1. [Overview](#overview)
2. [Infrastructure](#infrastructure)
3. [CI/CD Workflows](#cicd-workflows)
4. [Deployment Process](#deployment-process)
5. [Testing Strategy](#testing-strategy)
6. [Troubleshooting](#troubleshooting)
7. [Maintenance](#maintenance)

---

## Overview

Omnix uses a **self-hosted CI/CD pipeline** running on Proxmox infrastructure. This provides:

- ✅ Full control over the build environment
- ✅ Faster build times (no queue)
- ✅ Consistent testing environment
- ✅ Cost-effective (no cloud runner costs)
- ✅ Integration with staging deployments

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     GitHub Repository                        │
│  (code, workflows, configurations)                           │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        │ webhook
                        ▼
┌─────────────────────────────────────────────────────────────┐
│            GitHub Actions Self-Hosted Runner                 │
│  (Proxmox LXC Container: omnix-staging, ID 200)              │
│                                                              │
│  • Ubuntu 24.04                                              │
│  • Docker + Docker Compose                                   │
│  • Python 3.12.3 + venv                                      │
│  • All dependencies installed                                │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        │ runs workflows
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                   CI/CD Workflows                            │
│  • Lint code (flake8)                                        │
│  • Run tests (pytest)                                        │
│  • Deploy to staging                                         │
└─────────────────────────────────────────────────────────────┘
```

---

## Infrastructure

### Proxmox Container Details

**Container:** `omnix-staging` (ID 200)
**OS:** Ubuntu 24.04 LTS
**Location:** `/opt/omnix`

**Key Components:**
- **Runner:** `/opt/actions-runner/` (systemd service)
- **Repository:** `/opt/omnix/`
- **Virtual Environment:** `/opt/omnix/venv/`
- **Staging Deployment:** `/opt/omnix/staging/`

**Access:**
```bash
# From Proxmox host
ssh pve
sudo pct enter 200

# Check runner status
sudo systemctl status actions-runner
```

### Runner Configuration

**Service:** `actions-runner.service`
**User:** `github-runner`
**Labels:** `self-hosted`, `linux`, `proxmox`

**Service Control:**
```bash
# Status
sudo systemctl status actions-runner

# Restart
sudo systemctl restart actions-runner

# Logs
sudo journalctl -u actions-runner -f
```

---

## CI/CD Workflows

### 1. Continuous Integration (`ci.yml`)

**Triggers:**
- Push to `main`, `staging`, `dev` branches
- Pull requests to `main`, `staging`

**Steps:**
1. Checkout code
2. Set up Python environment
3. Install dependencies
4. Run flake8 linting
5. Run pytest test suite

**Configuration:**
```yaml
# .github/workflows/ci.yml
name: CI Pipeline
on:
  push:
    branches: [ main, staging, dev ]
  pull_request:
    branches: [ main, staging ]

jobs:
  test:
    runs-on: self-hosted
    steps:
      # ... see file for details
```

### 2. Staging Deployment (`staging-deploy.yml`)

**Triggers:**
- Push to `staging` branch
- Manual workflow dispatch

**Steps:**
1. Checkout code
2. Verify deployment branch
3. Update staging directory with rsync
4. Install dependencies
5. Run pre-deployment tests
6. Create deployment marker
7. Verify deployment
8. Show deployment summary

**Manual Trigger:**
```bash
# Via GitHub CLI
gh workflow run staging-deploy.yml

# Via GitHub UI
# Actions → Deploy to Staging → Run workflow
```

---

## Deployment Process

### Automatic Deployment

**Triggered by:** Push to `staging` branch

```bash
# Create feature on staging branch
git checkout staging
git pull origin staging
git merge main  # or your feature branch
git push origin staging

# Workflow runs automatically
# Check status: https://github.com/your-repo/actions
```

### Manual Deployment

**Option 1: Using Deployment Script**

```bash
# SSH to Proxmox container
ssh pve
sudo pct enter 200

# Run deployment script
cd /opt/omnix
./scripts/deploy_staging.sh
```

**Option 2: Using GitHub Actions**

```bash
# Trigger workflow manually
gh workflow run staging-deploy.yml
```

### Deployment Verification

After deployment, verify with:

```bash
# Check deployment info
cat /opt/omnix/staging/.deployment_info

# Verify modules import
cd /opt/omnix/staging
source /opt/omnix/venv/bin/activate
python -c "import config; import game_detector; import ai_router"

# Run verification script
python scripts/verify_ci.py
```

---

## Testing Strategy

### Test Organization

```
tests/
├── unit/               # Unit tests (individual components)
├── integration/        # Integration tests (component interaction)
├── edge_cases/         # Edge case and error handling tests
└── archive/            # Archived old tests
```

### Test Categories

| Category | Marker | Purpose |
|----------|--------|---------|
| Unit | `@pytest.mark.unit` | Test individual components |
| Integration | `@pytest.mark.integration` | Test component interaction |
| UI | `@pytest.mark.ui` | Test GUI components (requires display) |
| Slow | `@pytest.mark.slow` | Long-running tests |
| CI Skip | `@pytest.mark.skip_ci` | Skip in CI environment |
| Network | `@pytest.mark.network` | Requires network access |

### Running Tests

**Locally:**
```bash
# All tests
pytest

# Specific category
pytest -m unit
pytest -m integration

# Specific file
pytest tests/unit/test_config.py

# With coverage
pytest --cov=src --cov-report=html
```

**In CI:**
```bash
# Tests run automatically via workflow
# Uses headless Qt platform
export QT_QPA_PLATFORM=offscreen
xvfb-run -a pytest tests/ -v --tb=short
```

### CI-Specific Tests

**File:** `tests/integration/test_ci_pipeline.py`

Tests that verify:
- ✅ Environment setup (Python version, Qt platform)
- ✅ Module imports work in headless environment
- ✅ Core components initialize without display
- ✅ Data persistence works
- ✅ Deployment readiness (required files exist)

---

## Troubleshooting

### Common Issues

#### 1. Runner Offline

**Symptom:** Workflows stuck in "Queued" state

**Solution:**
```bash
ssh pve
sudo pct enter 200
sudo systemctl status actions-runner

# If stopped, restart
sudo systemctl restart actions-runner

# Check logs
sudo journalctl -u actions-runner -n 50
```

#### 2. Tests Failing in CI

**Symptom:** Tests pass locally but fail in CI

**Common Causes:**
- Missing headless Qt platform configuration
- Display-dependent code
- Hardcoded paths

**Solution:**
```bash
# Test locally with same CI environment
export QT_QPA_PLATFORM=offscreen
xvfb-run -a pytest tests/ -v

# Check CI logs for specific error
gh run view --log-failed
```

#### 3. Deployment Fails

**Symptom:** Staging deployment workflow fails

**Solution:**
```bash
# Check deployment logs
gh run view

# Verify staging directory
ssh pve
sudo pct enter 200
ls -la /opt/omnix/staging/

# Check permissions
sudo chown -R github-runner:github-runner /opt/omnix/staging/

# Manual deployment to debug
./scripts/deploy_staging.sh
```

#### 4. Import Errors in CI

**Symptom:** `ModuleNotFoundError` in CI but not locally

**Solution:**
```bash
# Verify dependencies installed
cd /opt/omnix
source venv/bin/activate
pip list

# Reinstall dependencies
pip install -r requirements.txt -r requirements-dev.txt

# Check Python path in workflow
# Ensure pytest.ini has: pythonpath = src
```

### Debugging Workflows

**View Recent Runs:**
```bash
gh run list --limit 10
```

**View Specific Run:**
```bash
gh run view [run-id]
gh run view --log
```

**Re-run Failed Workflow:**
```bash
gh run rerun [run-id]
```

---

## Maintenance

### Regular Tasks

**Daily:**
- ✅ Monitor workflow runs for failures
- ✅ Review test results

**Weekly:**
- ✅ Check runner disk space
- ✅ Review deployment logs
- ✅ Update dependencies (if needed)

**Monthly:**
- ✅ Clean up old backups
- ✅ Review and update test coverage
- ✅ Update runner software

### Monitoring Commands

**Check Disk Space:**
```bash
ssh pve
sudo pct enter 200
df -h
du -sh /opt/omnix/*
```

**Check Runner Health:**
```bash
sudo systemctl status actions-runner
sudo journalctl -u actions-runner --since "24 hours ago"
```

**Check Workflow Statistics:**
```bash
gh run list --limit 30 --json status,conclusion,createdAt
```

### Backup and Recovery

**Create Backup:**
```bash
# Automatic backups created before each deployment
ls -la /opt/omnix/backups/

# Manual backup
./scripts/deploy_staging.sh  # Creates backup automatically
```

**Restore from Backup:**
```bash
cd /opt/omnix/backups
ls -t  # Find latest backup
cp -r staging_backup_YYYYMMDD_HHMMSS ../staging/
```

---

## Scripts and Tools

### Verification Script

**Purpose:** Verify CI/CD pipeline configuration

```bash
python scripts/verify_ci.py
```

**Checks:**
- ✅ Git repository status
- ✅ Workflow files valid
- ✅ Test suite configured
- ✅ Dependencies installed
- ✅ Sample tests run

### Deployment Script

**Purpose:** Deploy to staging environment

```bash
./scripts/deploy_staging.sh
```

**Steps:**
1. Check prerequisites
2. Create backup
3. Deploy code
4. Install dependencies
5. Run tests
6. Create deployment info
7. Verify deployment

---

## Best Practices

### Workflow Development

1. **Test locally first:**
   ```bash
   # Simulate CI environment
   export QT_QPA_PLATFORM=offscreen
   xvfb-run -a pytest tests/ -v
   ```

2. **Use appropriate markers:**
   ```python
   @pytest.mark.skip_ci  # For tests that can't run in CI
   @pytest.mark.requires_api_key  # For tests needing API keys
   ```

3. **Keep workflows fast:**
   - Cache dependencies
   - Run tests in parallel where possible
   - Use appropriate test selection

### Deployment Safety

1. **Always test before deploying:**
   - CI tests must pass
   - Manual testing on dev branch

2. **Use staging for validation:**
   - Deploy to staging first
   - Verify functionality
   - Then merge to main

3. **Monitor deployments:**
   - Check deployment info
   - Review logs
   - Verify critical functions

---

## Resources

### Documentation
- [GitHub Actions Self-Hosted Runners](https://docs.github.com/en/actions/hosting-your-own-runners)
- [Pytest Documentation](https://docs.pytest.org/)
- [Proxmox LXC Containers](https://pve.proxmox.com/wiki/Linux_Container)

### Internal Documentation
- [CLAUDE.md](../CLAUDE.md) - Project overview
- [README.md](../README.md) - User documentation
- [pytest.ini](../pytest.ini) - Test configuration

### Support
- **Issues:** GitHub Issues
- **Repository:** https://github.com/shingoku2/Omnix-All-knowing-gaming-companion

---

**Maintained by:** DevOps Team
**Last Review:** 2025-11-20
