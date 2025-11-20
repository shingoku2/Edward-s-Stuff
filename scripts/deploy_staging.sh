#!/bin/bash
# Staging Deployment Script for Omnix
# Deploys the application to the Proxmox staging environment

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
STAGING_DIR="${STAGING_DIR:-/opt/omnix/staging}"
VENV_PATH="${VENV_PATH:-/opt/omnix/venv}"
BACKUP_DIR="${BACKUP_DIR:-/opt/omnix/backups}"

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}\n"
}

check_prerequisites() {
    print_header "Checking Prerequisites"

    # Check if running on correct host
    log_info "Verifying deployment environment..."

    # Check if staging directory exists
    if [ ! -d "$STAGING_DIR" ]; then
        log_warning "Staging directory doesn't exist. Creating it..."
        mkdir -p "$STAGING_DIR"
    fi

    # Check if venv exists
    if [ ! -d "$VENV_PATH" ]; then
        log_error "Virtual environment not found at $VENV_PATH"
        exit 1
    fi

    # Check if rsync is available
    if ! command -v rsync &> /dev/null; then
        log_error "rsync is required but not installed"
        exit 1
    fi

    log_success "All prerequisites met"
}

create_backup() {
    print_header "Creating Backup"

    if [ -d "$STAGING_DIR" ] && [ "$(ls -A $STAGING_DIR)" ]; then
        BACKUP_NAME="staging_backup_$(date +%Y%m%d_%H%M%S)"
        BACKUP_PATH="$BACKUP_DIR/$BACKUP_NAME"

        log_info "Creating backup: $BACKUP_NAME"
        mkdir -p "$BACKUP_DIR"
        cp -r "$STAGING_DIR" "$BACKUP_PATH"

        log_success "Backup created at $BACKUP_PATH"

        # Keep only last 5 backups
        log_info "Cleaning up old backups (keeping last 5)..."
        cd "$BACKUP_DIR"
        ls -t | tail -n +6 | xargs -r rm -rf
    else
        log_warning "No existing staging deployment to backup"
    fi
}

deploy_code() {
    print_header "Deploying Code"

    log_info "Syncing code to staging directory..."

    # Get the repository root (assuming script is in scripts/ subdirectory)
    REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

    rsync -av --delete \
        --exclude='.git' \
        --exclude='venv' \
        --exclude='__pycache__' \
        --exclude='*.pyc' \
        --exclude='.env' \
        --exclude='htmlcov' \
        --exclude='.pytest_cache' \
        --exclude='dist' \
        --exclude='build' \
        --exclude='*.egg-info' \
        "$REPO_ROOT/" "$STAGING_DIR/"

    log_success "Code synchronized to $STAGING_DIR"
}

install_dependencies() {
    print_header "Installing Dependencies"

    log_info "Activating virtual environment..."
    source "$VENV_PATH/bin/activate"

    log_info "Installing Python dependencies..."
    cd "$STAGING_DIR"
    pip install -q -r requirements.txt

    log_success "Dependencies installed"
}

run_tests() {
    print_header "Running Pre-Deployment Tests"

    log_info "Activating virtual environment..."
    source "$VENV_PATH/bin/activate"

    log_info "Running CI pipeline tests..."
    cd "$STAGING_DIR"
    export QT_QPA_PLATFORM=offscreen

    if pytest tests/integration/test_ci_pipeline.py -v --tb=short; then
        log_success "All tests passed"
    else
        log_error "Tests failed. Deployment aborted."
        exit 1
    fi
}

create_deployment_info() {
    print_header "Creating Deployment Info"

    cd "$STAGING_DIR"

    DEPLOY_TIME=$(date -u +"%Y-%m-%d %H:%M:%S UTC")
    COMMIT_SHA=$(git rev-parse HEAD 2>/dev/null || echo "N/A")
    COMMIT_MSG=$(git log -1 --pretty=%B 2>/dev/null || echo "N/A")
    BRANCH=$(git branch --show-current 2>/dev/null || echo "N/A")

    cat > .deployment_info << EOF
Deployment Information
======================
Deployment Time: $DEPLOY_TIME
Commit SHA: $COMMIT_SHA
Branch: $BRANCH
Commit Message: $COMMIT_MSG
Deployed By: $(whoami)
Host: $(hostname)
Staging Directory: $STAGING_DIR
EOF

    log_success "Deployment info created"
    cat .deployment_info
}

verify_deployment() {
    print_header "Verifying Deployment"

    log_info "Activating virtual environment..."
    source "$VENV_PATH/bin/activate"

    log_info "Verifying module imports..."
    cd "$STAGING_DIR"

    if python -c "import config; import game_detector; import ai_router; print('✓ All critical modules imported successfully')"; then
        log_success "Module verification passed"
    else
        log_error "Module verification failed"
        exit 1
    fi

    log_info "Verifying file structure..."
    REQUIRED_FILES=(
        "main.py"
        "requirements.txt"
        "src/config.py"
        "src/game_detector.py"
        "src/ai_router.py"
    )

    for file in "${REQUIRED_FILES[@]}"; do
        if [ -f "$file" ]; then
            log_success "  ✓ $file"
        else
            log_error "  ✗ $file missing"
            exit 1
        fi
    done

    log_success "Deployment verification complete"
}

show_summary() {
    print_header "Deployment Summary"

    echo -e "${GREEN}✓ Staging deployment completed successfully!${NC}\n"
    echo "Deployment Details:"
    echo "  - Staging Directory: $STAGING_DIR"
    echo "  - Virtual Environment: $VENV_PATH"
    echo "  - Backup Directory: $BACKUP_DIR"
    echo ""
    echo "Next Steps:"
    echo "  1. Review deployment info: cat $STAGING_DIR/.deployment_info"
    echo "  2. Test the application manually"
    echo "  3. Monitor logs for any issues"
    echo ""
}

# Main deployment flow
main() {
    print_header "Omnix Staging Deployment"

    log_info "Starting deployment process..."

    check_prerequisites
    create_backup
    deploy_code
    install_dependencies
    run_tests
    create_deployment_info
    verify_deployment
    show_summary

    exit 0
}

# Run main function
main
