#!/bin/bash

# Validation script to check if the repository is ready for azd deployment
# Run this script before attempting deployment to catch common issues early

set -e

echo "🔍 Validating Azure Developer CLI (azd) Setup"
echo "=============================================="
echo ""

# Color codes for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

ERRORS=0
WARNINGS=0

# Function to print success
print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

# Function to print error
print_error() {
    echo -e "${RED}✗${NC} $1"
    ((ERRORS++))
}

# Function to print warning
print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
    ((WARNINGS++))
}

# Check 1: Azure Developer CLI installed
echo "Checking Azure Developer CLI..."
if command -v azd &> /dev/null; then
    AZD_VERSION=$(azd version 2>&1 | head -1 || echo "unknown")
    print_success "Azure Developer CLI installed: $AZD_VERSION"
else
    print_error "Azure Developer CLI not installed"
    echo "  Install: curl -fsSL https://aka.ms/install-azd.sh | bash"
fi

# Check 2: Azure CLI installed
echo "Checking Azure CLI..."
if command -v az &> /dev/null; then
    AZ_VERSION=$(az version --query '"azure-cli"' -o tsv 2>/dev/null || echo "unknown")
    print_success "Azure CLI installed: $AZ_VERSION"
else
    print_error "Azure CLI not installed"
    echo "  Install: https://learn.microsoft.com/cli/azure/install-azure-cli"
fi

# Check 3: Required files exist
echo "Checking required files..."
REQUIRED_FILES=(
    "azure.yaml"
    "infra/main.bicep"
    "infra/main.bicepparam"
    "infra/hooks/postprovision.sh"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        print_success "Found: $file"
    else
        print_error "Missing: $file"
    fi
done

# Check 4: Azure login status
echo "Checking Azure authentication..."
if command -v az &> /dev/null; then
    if az account show &> /dev/null; then
        ACCOUNT=$(az account show --query name -o tsv 2>/dev/null || echo "unknown")
        SUBSCRIPTION=$(az account show --query id -o tsv 2>/dev/null || echo "unknown")
        print_success "Logged into Azure"
        echo "  Account: $ACCOUNT"
        echo "  Subscription: $SUBSCRIPTION"
    else
        print_warning "Not logged into Azure"
        echo "  Run: az login"
    fi
fi

# Check 5: Bicep CLI
echo "Checking Bicep..."
if command -v az &> /dev/null; then
    if az bicep version &> /dev/null; then
        BICEP_VERSION=$(az bicep version 2>&1 | grep -oP 'version \K[0-9.]+' || echo "unknown")
        print_success "Bicep installed: $BICEP_VERSION"
    else
        print_warning "Bicep not installed"
        echo "  Install: az bicep install"
    fi
fi

# Check 6: Python (for MCP servers)
echo "Checking Python..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    print_success "Python installed: $PYTHON_VERSION"
    
    # Check Python version is 3.11 or higher
    if python3 -c "import sys; exit(0 if sys.version_info >= (3, 11) else 1)" 2>/dev/null; then
        print_success "Python version is 3.11+"
    else
        print_warning "Python version should be 3.11 or higher"
    fi
else
    print_warning "Python not installed (needed for MCP servers)"
    echo "  Install: https://www.python.org/downloads/"
fi

# Check 7: Git
echo "Checking Git..."
if command -v git &> /dev/null; then
    GIT_VERSION=$(git --version | awk '{print $3}')
    print_success "Git installed: $GIT_VERSION"
else
    print_error "Git not installed"
fi

# Check 8: Bicep template validation
echo "Validating Bicep templates..."
if command -v az &> /dev/null && [ -f "infra/main.bicep" ]; then
    if az bicep build --file infra/main.bicep --stdout &> /dev/null; then
        print_success "Bicep template is valid"
    else
        print_error "Bicep template has syntax errors"
        echo "  Run: az bicep build --file infra/main.bicep"
    fi
fi

# Check 9: Documentation files
echo "Checking documentation..."
DOC_FILES=(
    "DEPLOYMENT.md"
    "docs/QUICKSTART.md"
    "docs/INDEX.md"
)

for file in "${DOC_FILES[@]}"; do
    if [ -f "$file" ]; then
        print_success "Found: $file"
    else
        print_warning "Missing documentation: $file"
    fi
done

# Check 10: Hook script permissions
echo "Checking hook script permissions..."
if [ -f "infra/hooks/postprovision.sh" ]; then
    if [ -x "infra/hooks/postprovision.sh" ]; then
        print_success "postprovision.sh is executable"
    else
        print_warning "postprovision.sh is not executable"
        echo "  Fix: chmod +x infra/hooks/postprovision.sh"
    fi
fi

# Summary
echo ""
echo "=============================================="
echo "Validation Summary"
echo "=============================================="

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}✓ All checks passed!${NC}"
    echo ""
    echo "You're ready to deploy:"
    echo "  azd init"
    echo "  azd provision"
elif [ $ERRORS -eq 0 ]; then
    echo -e "${YELLOW}⚠ Validation passed with $WARNINGS warning(s)${NC}"
    echo ""
    echo "You can proceed, but consider fixing warnings:"
    echo "  azd init"
    echo "  azd provision"
else
    echo -e "${RED}✗ Validation failed with $ERRORS error(s) and $WARNINGS warning(s)${NC}"
    echo ""
    echo "Please fix the errors above before deploying."
    exit 1
fi

echo ""
echo "📚 Documentation:"
echo "  Quick Start: docs/QUICKSTART.md"
echo "  Full Guide: DEPLOYMENT.md"
echo "  Index: docs/INDEX.md"
echo ""
