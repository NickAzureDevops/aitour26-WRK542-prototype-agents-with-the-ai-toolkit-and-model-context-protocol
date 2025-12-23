# Deployment Guide

This guide provides detailed instructions for deploying the Azure AI Foundry resources required for the WRK542 workshop.

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Deployment Methods](#deployment-methods)
  - [Method 1: Azure Developer CLI (Recommended)](#method-1-azure-developer-cli-recommended)
  - [Method 2: Bash Script (Legacy)](#method-2-bash-script-legacy)
- [What Gets Deployed](#what-gets-deployed)
- [Post-Deployment](#post-deployment)
- [Troubleshooting](#troubleshooting)
- [Cleanup](#cleanup)

## Overview

The deployment creates an Azure AI Foundry workspace with the following components:
- Azure AI Foundry account and project
- Azure OpenAI deployments (GPT-4o, text-embedding-3-small)
- Application Insights for monitoring and tracing
- Necessary role assignments for the signed-in user

## Prerequisites

Before deploying, ensure you have:

1. **Azure Subscription**: Active Azure subscription with appropriate permissions
2. **Azure Developer CLI**: Version 1.5.0 or later
   ```bash
   azd version
   ```
3. **Azure CLI**: For authentication and resource management
   ```bash
   az --version
   ```
4. **Required Permissions**: 
   - Subscription Contributor or Owner role
   - Ability to create service principals (for role assignments)

## Deployment Methods

### Method 1: Azure Developer CLI (Recommended)

The Azure Developer CLI (azd) provides a standardized way to deploy Azure applications with the following benefits:
- Consistent environment management
- Built-in support for CI/CD integration
- Automatic parameter handling
- Better state management

#### Step-by-Step Guide

1. **Clone the repository** (if not already done)
   ```bash
   git clone https://github.com/NickAzureDevops/aitour26-WRK542-prototype-agents-with-the-ai-toolkit-and-model-context-protocol.git
   cd aitour26-WRK542-prototype-agents-with-the-ai-toolkit-and-model-context-protocol
   ```

2. **Authenticate with Azure**
   ```bash
   azd auth login
   az login
   ```

3. **Initialize the environment** (first time only)
   ```bash
   azd init
   ```
   
   When prompted:
   - **Environment name**: Choose a name (e.g., `dev`, `prod`, `workshop`)
   - **Subscription**: Select your Azure subscription
   - **Location**: Choose an Azure region (recommended: `eastus`, `westus2`, `northeurope`)

4. **Customize deployment (optional)**
   
   You can set custom values before provisioning:
   ```bash
   # Set custom resource prefix
   azd env set AZURE_RESOURCE_PREFIX "my-workshop"
   
   # Set custom location
   azd env set AZURE_LOCATION "westus2"
   ```

5. **Provision Azure resources**
   ```bash
   azd provision
   ```
   
   This command will:
   - Create a resource group
   - Deploy Azure AI Foundry resources
   - Deploy AI models
   - Configure Application Insights
   - Set up role assignments
   - Create `.env` file with connection details

6. **Verify deployment**
   ```bash
   # Check environment variables
   azd env get-values
   
   # Verify .env file was created
   cat src/.env
   ```

#### Environment Management

```bash
# List all environments
azd env list

# Switch between environments
azd env select <environment-name>

# View environment variables
azd env get-values

# Set a specific variable
azd env set KEY_NAME "value"
```

### Method 2: Bash Script (Legacy)

The traditional deployment script is still available for backwards compatibility.

```bash
cd infra
./deploy.sh
```

**Note**: This method is being phased out in favor of azd for better maintainability and CI/CD integration.

## What Gets Deployed

The deployment creates the following Azure resources:

| Resource Type | Naming Convention | Purpose |
|--------------|------------------|---------|
| Resource Group | `rg-{prefix}-{suffix}` | Container for all resources |
| AI Foundry Account | `fdy-{prefix}-{suffix}` | Azure AI Foundry workspace |
| AI Project | `prj-{prefix}-{suffix}` | Project within the Foundry workspace |
| Application Insights | `appi-{prefix}-{suffix}` | Monitoring and telemetry |
| Model Deployments | `gpt-4o`, `text-embedding-3-small` | OpenAI models |

**Default Configuration**:
- **Location**: East US
- **Resource Prefix**: `zava-agent-wks`
- **Unique Suffix**: Auto-generated (4 characters)
- **GPT-4o Capacity**: 120 tokens per minute
- **Embedding Capacity**: 120 tokens per minute

## Post-Deployment

After successful deployment:

1. **Environment File**: Check `src/.env` for connection details
   ```bash
   cat src/.env
   ```

2. **Resource Information**: Review `src/resources.txt` for deployed resource names
   ```bash
   cat src/resources.txt
   ```

3. **Azure Portal**: Verify resources in the [Azure Portal](https://portal.azure.com)
   - Navigate to your resource group
   - Confirm all resources are running
   - Check AI Foundry deployments

4. **Test Connection**: Run the test script to verify connectivity
   ```bash
   cd src
   python -m pytest tests/test_servers_startup.sh
   ```

## Troubleshooting

### Common Issues

#### Issue: "Subscription not registered for resource provider"

**Solution**: Register required resource providers
```bash
az provider register --namespace Microsoft.CognitiveServices
az provider register --namespace Microsoft.MachineLearningServices
```

#### Issue: "Insufficient quota for model deployment"

**Solution**: Request quota increase or choose a different region
```bash
# Check current quota
az cognitiveservices account list-usage \
  --name <foundry-name> \
  --resource-group <resource-group-name>
```

#### Issue: "azd command not found"

**Solution**: Install Azure Developer CLI
```bash
# Windows
powershell -ex AllSigned -c "Invoke-RestMethod 'https://aka.ms/install-azd.ps1' | Invoke-Expression"

# Linux/MacOS
curl -fsSL https://aka.ms/install-azd.sh | bash
```

#### Issue: "Role assignment failed"

**Solution**: Verify you have necessary permissions
```bash
# Check your current permissions
az role assignment list --assignee $(az ad signed-in-user show --query id -o tsv)
```

### Debugging

Enable verbose logging:
```bash
# For azd
azd provision --debug

# For Azure CLI
az deployment sub create --debug
```

View deployment logs:
```bash
# List recent deployments
az deployment sub list --output table

# Get deployment details
az deployment sub show --name <deployment-name>
```

## Cleanup

### Delete all resources

**Using azd** (Recommended):
```bash
azd down
```

**Using Azure CLI**:
```bash
# Get resource group name
RESOURCE_GROUP=$(azd env get-value resourceGroupName)

# Delete the resource group
az group delete --name $RESOURCE_GROUP --yes --no-wait
```

**Manual cleanup**:
1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to Resource Groups
3. Select your resource group
4. Click "Delete resource group"
5. Confirm by typing the resource group name

### Clean up local environment

```bash
# Remove azd environment
azd env delete <environment-name>

# Remove generated files
rm -f src/.env src/resources.txt
```

## CI/CD Integration

The `azure.yaml` file is configured for CI/CD integration:

### GitHub Actions

```yaml
name: Deploy

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - uses: azure/login@v1
      with:
        creds: ${{ secrets.AZURE_CREDENTIALS }}
    - name: Provision
      run: azd provision --no-prompt
```

### Azure DevOps

```yaml
trigger:
- main

pool:
  vmImage: ubuntu-latest

steps:
- task: AzureCLI@2
  inputs:
    azureSubscription: 'Your-Service-Connection'
    scriptType: 'bash'
    scriptLocation: 'inlineScript'
    inlineScript: |
      curl -fsSL https://aka.ms/install-azd.sh | bash
      azd provision --no-prompt
```

## Additional Resources

- [Azure Developer CLI Documentation](https://learn.microsoft.com/azure/developer/azure-developer-cli/)
- [Azure AI Foundry Documentation](https://learn.microsoft.com/azure/ai-foundry/)
- [Bicep Documentation](https://learn.microsoft.com/azure/azure-resource-manager/bicep/)
- [Model Context Protocol](https://modelcontextprotocol.io/)

## Support

For issues or questions:
- File an issue in the [GitHub repository](https://github.com/NickAzureDevops/aitour26-WRK542-prototype-agents-with-the-ai-toolkit-and-model-context-protocol/issues)
- Join the [Microsoft Foundry Discord](https://aka.ms/MicrosoftFoundryDiscord-AITour26)
