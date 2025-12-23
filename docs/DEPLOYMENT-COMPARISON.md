# Deployment Method Comparison

This document compares the two deployment approaches available for this project.

## Overview

| Feature | Azure Developer CLI (azd) | Bash Script (deploy.sh) |
|---------|--------------------------|-------------------------|
| **Complexity** | Simple, standardized | Custom, manual |
| **Environment Management** | Built-in | Manual |
| **State Management** | Automatic | None |
| **CI/CD Integration** | Native support | Custom setup required |
| **Parameter Management** | Environment-based | Command-line arguments |
| **Credentials** | Managed by azd | Manual handling |
| **Cleanup** | `azd down` | Manual deletion |
| **Multiple Environments** | Easy (dev, test, prod) | Difficult |
| **Error Recovery** | Better | Limited |
| **Documentation** | Microsoft-maintained | Project-specific |

## Azure Developer CLI (azd) - Recommended

### Advantages

1. **Standardization**: Uses Microsoft's recommended practices for Azure deployments
2. **Environment Management**: Built-in support for multiple environments (dev, test, prod)
3. **State Tracking**: Automatically tracks deployed resources
4. **CI/CD Ready**: Native integration with GitHub Actions and Azure DevOps
5. **Simplified Workflow**: Single command for provision, deploy, and cleanup
6. **Better Error Handling**: Improved error messages and recovery options
7. **Community Support**: Large community and Microsoft support
8. **Template Ecosystem**: Compatible with Azure Developer CLI templates

### Typical Workflow

```bash
# First time setup
azd init
azd provision

# Updates
azd provision

# Cleanup
azd down
```

### Use Cases

- ✅ Production deployments
- ✅ Multi-environment setups (dev, test, prod)
- ✅ CI/CD pipelines
- ✅ Team collaboration
- ✅ Long-term projects

## Bash Script (deploy.sh) - Legacy

### Advantages

1. **Direct Control**: Full control over deployment process
2. **Customization**: Can be modified for specific needs
3. **Transparency**: All steps are visible in the script
4. **No Additional Tools**: Only requires Azure CLI

### Limitations

1. **Manual Environment Management**: Need to track resources manually
2. **No State Tracking**: Can't easily determine what's deployed
3. **Limited Error Recovery**: Basic error handling
4. **No Built-in Multi-Environment**: Requires custom logic
5. **CI/CD Setup**: Need to create custom pipelines
6. **Cleanup Complexity**: Manual resource tracking needed

### Typical Workflow

```bash
cd infra
./deploy.sh

# Manual cleanup
az group delete --name <resource-group-name>
```

### Use Cases

- ⚠️ Quick prototypes (but azd is still better)
- ⚠️ Learning the deployment steps (but azd is more clear)
- ⚠️ Custom deployment requirements (but azd supports hooks)

## Migration Guide

If you're currently using `deploy.sh`, migrating to `azd` is straightforward:

### Step 1: Install azd

```bash
# Windows
powershell -ex AllSigned -c "Invoke-RestMethod 'https://aka.ms/install-azd.ps1' | Invoke-Expression"

# Linux/MacOS
curl -fsSL https://aka.ms/install-azd.sh | bash
```

### Step 2: Initialize azd

```bash
azd init
```

### Step 3: Provision with azd

```bash
azd provision
```

Your resources will be deployed identically to the bash script, but with better management capabilities.

### Step 4: Verify

```bash
# Check deployed resources
azd env get-values

# Verify .env file
cat src/.env
```

## Key Differences in Implementation

### Parameter Handling

**Bash Script**:
```bash
# Hardcoded in script
RG_LOCATION="eastus"
RESOURCE_PREFIX="zava-agent-wks"
UNIQUE_SUFFIX=$(head /dev/urandom | tr -dc a-z0-9 | head -c 4)
```

**azd**:
```bash
# Environment-based
azd env set AZURE_LOCATION "eastus"
azd env set AZURE_RESOURCE_PREFIX "zava-agent-wks"
# Unique suffix auto-generated per environment
```

### Output Management

**Bash Script**:
```bash
# Manual parsing of deployment output
PROJECTS_ENDPOINT=$(jq -r '.properties.outputs.projectsEndpoint.value' output.json)
```

**azd**:
```bash
# Automatic environment variable management
azd env get-value projectsEndpoint
```

### Role Assignment

Both methods handle role assignments similarly, but azd integrates better with Azure RBAC:

**Bash Script**: Direct `az role assignment create` commands

**azd**: Same commands, but executed in context of managed environment

## Recommendations

### For New Projects
- **Use Azure Developer CLI (azd)** - It's the modern, recommended approach

### For Existing Projects
- **Migrate to azd** - The benefits far outweigh the migration effort

### For Production
- **Definitely use azd** - Better for team collaboration and CI/CD

### For Quick Tests
- **Still use azd** - It's just as fast once installed

## Additional Resources

- [Azure Developer CLI Documentation](https://learn.microsoft.com/azure/developer/azure-developer-cli/)
- [azd Templates](https://azure.github.io/awesome-azd/)
- [Best Practices](https://learn.microsoft.com/azure/developer/azure-developer-cli/best-practices)

## Conclusion

While the bash script (`deploy.sh`) works, **Azure Developer CLI (azd) is the recommended approach** for all scenarios. It provides:
- Better tooling
- Easier management
- Industry-standard practices
- Future-proof deployment patterns

The small effort to learn azd pays off immediately with better deployment management and team collaboration.
