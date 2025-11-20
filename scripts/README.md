# Omnix CI/CD Scripts

Automation scripts for CI/CD pipeline and deployment management.

## Scripts

### `verify_ci.py`

**Purpose:** Verify CI/CD pipeline configuration and health

**Usage:**
```bash
python scripts/verify_ci.py
```

**Checks:**
- ✅ Git repository status and remotes
- ✅ GitHub Actions workflow files
- ✅ Test suite configuration
- ✅ Python dependencies (pytest, flake8)
- ✅ Self-hosted runner status
- ✅ Sample test execution

**Output:** Color-coded status report with pass/fail for each check

**Example:**
```
======================================================================
Git Repository Status
======================================================================

✓ Git repository detected
✓ Current branch: main
✓ Git remote configured

======================================================================
Summary
======================================================================

✓ Git Repository: OK
✓ Workflow Files: OK
✓ Test Suite: OK
✓ Dependencies: OK
✓ Self-Hosted Runner: OK
✓ Sample Tests: OK

Results: 6/6 checks passed

✓ CI/CD pipeline is fully operational!
```

---

### `deploy_staging.sh`

**Purpose:** Deploy application to Proxmox staging environment

**Usage:**
```bash
./scripts/deploy_staging.sh
```

**Steps:**
1. **Check Prerequisites** - Verify environment and tools
2. **Create Backup** - Backup current staging deployment
3. **Deploy Code** - Sync code with rsync
4. **Install Dependencies** - Update Python packages
5. **Run Tests** - Execute pre-deployment tests
6. **Create Deployment Info** - Record deployment metadata
7. **Verify Deployment** - Validate deployment success
8. **Show Summary** - Display deployment results

**Environment Variables:**
- `STAGING_DIR` - Staging directory (default: `/opt/omnix/staging`)
- `VENV_PATH` - Virtual environment path (default: `/opt/omnix/venv`)
- `BACKUP_DIR` - Backup directory (default: `/opt/omnix/backups`)

**Example:**
```bash
# Use custom staging directory
STAGING_DIR=/custom/path ./scripts/deploy_staging.sh

# Use custom venv
VENV_PATH=/custom/venv ./scripts/deploy_staging.sh
```

**Output:**
```
========================================
Omnix Staging Deployment
========================================

[INFO] Starting deployment process...

========================================
Checking Prerequisites
========================================

[SUCCESS] All prerequisites met

========================================
Creating Backup
========================================

[INFO] Creating backup: staging_backup_20251120_123456
[SUCCESS] Backup created at /opt/omnix/backups/staging_backup_20251120_123456

... (more steps) ...

========================================
Deployment Summary
========================================

✓ Staging deployment completed successfully!

Deployment Details:
  - Staging Directory: /opt/omnix/staging
  - Virtual Environment: /opt/omnix/venv
  - Backup Directory: /opt/omnix/backups

Next Steps:
  1. Review deployment info: cat /opt/omnix/staging/.deployment_info
  2. Test the application manually
  3. Monitor logs for any issues
```

**Exit Codes:**
- `0` - Deployment successful
- `1` - Deployment failed (tests failed, verification failed, etc.)

**Backup Management:**
- Creates timestamped backup before each deployment
- Keeps last 5 backups automatically
- Backups stored in `$BACKUP_DIR`

**Recovery:**
```bash
# List backups
ls -lt /opt/omnix/backups/

# Restore from backup
cp -r /opt/omnix/backups/staging_backup_YYYYMMDD_HHMMSS /opt/omnix/staging/
```

---

## Usage Patterns

### Pre-Commit Workflow

```bash
# Before committing changes
python scripts/verify_ci.py

# If all checks pass, commit and push
git add .
git commit -m "Your changes"
git push
```

### Staging Deployment Workflow

```bash
# Option 1: Automatic (via GitHub Actions)
git checkout staging
git merge main
git push origin staging  # Triggers workflow

# Option 2: Manual
ssh pve
sudo pct enter 200
cd /opt/omnix
./scripts/deploy_staging.sh
```

### Troubleshooting Workflow

```bash
# Verify pipeline health
python scripts/verify_ci.py

# Check runner
ssh pve
sudo pct enter 200
sudo systemctl status actions-runner

# View recent deployments
ls -lt /opt/omnix/backups/
cat /opt/omnix/staging/.deployment_info
```

---

## Development

### Adding New Scripts

1. Create script in `scripts/` directory
2. Add shebang: `#!/bin/bash` or `#!/usr/bin/env python3`
3. Make executable: `chmod +x scripts/your_script.sh`
4. Document in this README
5. Add to version control

### Testing Scripts

```bash
# Test verify_ci.py
python scripts/verify_ci.py

# Test deploy_staging.sh (dry run not supported, use caution)
# Review script before running
cat scripts/deploy_staging.sh

# Test in controlled environment first
STAGING_DIR=/tmp/test_staging ./scripts/deploy_staging.sh
```

---

## Dependencies

### verify_ci.py
- Python 3.8+
- pytest (optional, for test execution)
- flake8 (optional, for linting check)
- gh CLI (optional, for workflow status)

### deploy_staging.sh
- bash 4.0+
- rsync
- Python 3.8+
- git

---

## Maintenance

### Regular Tasks

**Weekly:**
```bash
# Verify pipeline health
python scripts/verify_ci.py

# Check deployment backups
du -sh /opt/omnix/backups/*
```

**Monthly:**
```bash
# Clean old backups (keeps last 5 automatically)
# Manual cleanup if needed
ls -t /opt/omnix/backups/ | tail -n +6 | xargs -I {} rm -rf /opt/omnix/backups/{}
```

---

## Related Documentation

- [CI/CD Guide](../docs/CI_CD_GUIDE.md) - Comprehensive CI/CD documentation
- [Quick Start](../docs/QUICK_START_CI.md) - Quick reference guide
- [CLAUDE.md](../CLAUDE.md) - Full project documentation

---

**Last Updated:** 2025-11-20
