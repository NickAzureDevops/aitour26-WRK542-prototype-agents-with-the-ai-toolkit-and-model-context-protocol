# CI/CD Pipeline Setup Guide

This guide explains how to set up automated deployment pipelines for the Azure AI Foundry workshop.

## Table of Contents

- [GitHub Actions Setup](#github-actions-setup)
- [Azure DevOps Setup](#azure-devops-setup)
- [Best Practices](#best-practices)

## GitHub Actions Setup

### Prerequisites

1. GitHub repository with this code
2. Azure subscription
3. Appropriate permissions to create service principals

### Step 1: Create Azure Service Principal

```bash
# Login to Azure
az login

# Set your subscription
az account set --subscription <subscription-id>

# Create service principal with Contributor role
az ad sp create-for-rbac \
  --name "github-actions-foundry-workshop" \
  --role Contributor \
  --scopes /subscriptions/<subscription-id> \
  --sdk-auth
```

Save the output JSON - you'll need it for GitHub secrets.

### Step 2: Configure GitHub Secrets

Go to your GitHub repository → Settings → Secrets and variables → Actions

Add the following secrets:

| Secret Name | Value | Description |
|------------|-------|-------------|
| `AZURE_CLIENT_ID` | From service principal output | Application (client) ID |
| `AZURE_TENANT_ID` | From service principal output | Directory (tenant) ID |
| `AZURE_SUBSCRIPTION_ID` | Your subscription ID | Azure subscription |
| `AZURE_ENV_NAME` | `dev` or `prod` | Environment name for azd |
| `AZURE_LOCATION` | `eastus` | Azure region |

### Step 3: Enable Workflow

The workflow file is located at `.github/workflows/azure-deploy.yml`

**To trigger deployment:**

1. **Manual**: Go to Actions tab → Select workflow → Run workflow
2. **Automatic**: Push changes to `main` branch (infrastructure files only)

### Step 4: Monitor Deployment

1. Go to Actions tab in your repository
2. Click on the running workflow
3. View real-time logs and deployment summary

## Azure DevOps Setup

### Prerequisites

1. Azure DevOps organization and project
2. Azure subscription
3. Azure DevOps service connection

### Step 1: Create Service Connection

1. Go to Azure DevOps Project Settings
2. Navigate to Service connections
3. Click "New service connection"
4. Select "Azure Resource Manager"
5. Choose "Service principal (automatic)"
6. Select your subscription
7. Name it: `azure-foundry-service-connection`
8. Click "Save"

### Step 2: Create Variable Group

1. Go to Pipelines → Library
2. Click "+ Variable group"
3. Name: `azure-foundry-vars`
4. Add variables:

| Variable Name | Value | Secret? |
|--------------|-------|---------|
| `AZURE_ENV_NAME` | `dev` or `prod` | No |
| `AZURE_LOCATION` | `eastus` | No |
| `AZURE_SUBSCRIPTION_ID` | Your subscription ID | Yes |

5. Click "Save"

### Step 3: Create Pipeline

1. Go to Pipelines → Pipelines
2. Click "New pipeline"
3. Select your repository
4. Choose "Existing Azure Pipelines YAML file"
5. Select `.azdo/azure-pipelines.yml`
6. Click "Continue" then "Run"

### Step 4: Update Service Connection Name

If your service connection has a different name, update line 14 in `.azdo/azure-pipelines.yml`:

```yaml
- name: azureServiceConnection
  value: 'your-service-connection-name'  # Update this
```

### Step 5: Monitor Pipeline

1. View pipeline runs in Pipelines tab
2. Check logs for each stage
3. View deployment summary in the pipeline output

## Pipeline Features

### GitHub Actions

- ✅ Automatic trigger on infrastructure changes
- ✅ Manual workflow dispatch
- ✅ Deployment summary in GitHub UI
- ✅ Federated credentials (more secure)
- ✅ Output variables for downstream jobs

### Azure DevOps

- ✅ Multi-stage pipeline (Provision → Validate)
- ✅ Variable groups for secrets management
- ✅ Service connection integration
- ✅ Python testing stage
- ✅ Detailed logging

## Environment Strategies

### Single Environment

For simple setups, use one environment (e.g., `dev`):

```yaml
env:
  AZURE_ENV_NAME: dev
```

### Multiple Environments

For production-ready setups, use environment-specific workflows:

**Development Environment** (`.github/workflows/azure-deploy-dev.yml`):
```yaml
env:
  AZURE_ENV_NAME: dev
  AZURE_LOCATION: eastus
```

**Production Environment** (`.github/workflows/azure-deploy-prod.yml`):
```yaml
env:
  AZURE_ENV_NAME: prod
  AZURE_LOCATION: westus2
```

## Security Best Practices

### 1. Use Managed Identities

For Azure DevOps agents running in Azure:
```yaml
- task: AzureCLI@2
  inputs:
    azureSubscription: $(azureServiceConnection)
    addSpnToEnvironment: true
```

### 2. Federated Credentials (GitHub Actions)

Use OpenID Connect instead of secrets:
```yaml
- uses: azure/login@v2
  with:
    client-id: ${{ secrets.AZURE_CLIENT_ID }}
    tenant-id: ${{ secrets.AZURE_TENANT_ID }}
    subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}
```

### 3. Least Privilege

Grant only necessary permissions:
- Contributor role scoped to specific resource group
- Avoid subscription-level permissions when possible

### 4. Secret Rotation

Rotate service principal credentials regularly:
```bash
az ad sp credential reset --id <app-id>
```

## Troubleshooting

### Issue: "azd: command not found"

**Solution**: The installation script needs to update PATH:

**GitHub Actions**: Already handled in workflow

**Azure DevOps**: Add to script:
```bash
export PATH=$PATH:$HOME/.azd/bin
```

### Issue: "Insufficient permissions"

**Solution**: Verify service principal has Contributor role:
```bash
az role assignment list --assignee <app-id> --all
```

### Issue: "Environment not found"

**Solution**: Initialize environment first:
```bash
azd init --environment $AZURE_ENV_NAME --subscription $AZURE_SUBSCRIPTION_ID
```

### Issue: "Variable group not found" (Azure DevOps)

**Solution**: 
1. Verify variable group name matches in pipeline
2. Grant pipeline permissions to variable group
3. Check variable group is in same project

## Advanced Configurations

### Approval Gates (Azure DevOps)

Add manual approval before production:

1. Go to Environments
2. Create environment: `production`
3. Add approval check
4. Update pipeline:

```yaml
- stage: Production
  dependsOn: Validate
  condition: succeeded()
  environment: production
  jobs:
  - deployment: DeployProd
    # ... deployment steps
```

### GitHub Environments

1. Go to Settings → Environments
2. Create environment: `production`
3. Add protection rules
4. Update workflow:

```yaml
jobs:
  deploy:
    environment: production
    # ... job steps
```

### Notifications

**GitHub Actions**: Add Slack/Teams notification:
```yaml
- name: Notify Deployment
  uses: 8398a7/action-slack@v3
  with:
    status: ${{ job.status }}
    webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

**Azure DevOps**: Configure in Project Settings → Notifications

## Cost Optimization

### Scheduled Teardown

Add cleanup pipeline for dev environments:

**.github/workflows/azure-cleanup.yml**:
```yaml
name: Cleanup Dev Resources
on:
  schedule:
    - cron: '0 22 * * *'  # 10 PM daily
  workflow_dispatch:

jobs:
  cleanup:
    runs-on: ubuntu-latest
    steps:
    - uses: Azure/setup-azd@v1.0.0
    - uses: azure/login@v2
      # ... login steps
    - name: Teardown
      run: azd down --purge --force
      env:
        AZURE_ENV_NAME: dev
```

### Resource Tagging

Add cost tracking tags in `infra/main.bicep`:
```bicep
var tags = {
  Environment: 'Dev'
  Project: 'AI-Workshop'
  CostCenter: 'Engineering'
  ManagedBy: 'azd'
}
```

## Monitoring Deployments

### Azure Monitor

Track deployment metrics:
- Deployment duration
- Success/failure rates
- Resource costs

### Application Insights

Monitor application after deployment:
```bash
# View recent telemetry
az monitor app-insights query \
  --app $(azd env get-value applicationInsightsName) \
  --analytics-query "requests | take 10"
```

## Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/actions)
- [Azure DevOps Pipelines](https://learn.microsoft.com/azure/devops/pipelines/)
- [Azure Developer CLI CI/CD](https://learn.microsoft.com/azure/developer/azure-developer-cli/configure-devops-pipeline)
- [Workload Identity Federation](https://learn.microsoft.com/azure/active-directory/workload-identities/workload-identity-federation)

## Support

For issues:
- Check pipeline logs
- Review service connection permissions
- Verify secrets are correctly configured
- Test azd commands locally first
