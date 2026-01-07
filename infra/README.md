# Infrastructure Deployment

This directory contains the infrastructure-as-code for deploying Azure AI Foundry resources.

## 🚀 Quick Start (Recommended)

Use Azure Developer CLI for the best experience:

```bash
# From repository root
azd provision
```

See [DEPLOYMENT.md](../DEPLOYMENT.md) for detailed instructions.

## 📁 Directory Structure

```
infra/
├── main.bicep                    # Main infrastructure template
├── main.bicepparam              # Parameters for azd deployment
├── main.parameters.json         # Parameters for legacy script
├── foundry.bicep                # Azure AI Foundry account
├── foundry-project.bicep        # AI Foundry project
├── foundry-model-deployment.bicep # Model deployments
├── application-insights.bicep   # Monitoring setup
├── hooks/
│   └── postprovision.sh        # Post-deployment configuration
├── deploy.sh                    # Legacy deployment script (deprecated)
└── cleanup-deleted-resources.sh # Cleanup utility
```

## 🎯 Deployment Methods

### Method 1: Azure Developer CLI (Recommended)

**Pros:**
- ✅ Standardized approach
- ✅ Environment management
- ✅ CI/CD integration
- ✅ Easy cleanup

**Usage:**
```bash
azd provision
```

### Method 2: Bash Script (Legacy)

**Status:** 🚨 Deprecated - Use azd instead

**Usage:**
```bash
cd infra
./deploy.sh
```

## 🏗️ Infrastructure Components

### Resource Group
- **Naming:** `rg-{prefix}-{suffix}`
- **Purpose:** Container for all resources

### Azure AI Foundry
- **Account:** `fdy-{prefix}-{suffix}`
- **Project:** `prj-{prefix}-{suffix}`
- **Models:**
  - GPT-4o (120 TPM capacity)
  - text-embedding-3-small (120 TPM capacity)

### Monitoring
- **Application Insights:** `appi-{prefix}-{suffix}`
- **Purpose:** Telemetry and diagnostics

## 🔧 Configuration

### Using azd

Set environment variables:
```bash
azd env set AZURE_LOCATION "eastus"
azd env set AZURE_RESOURCE_PREFIX "my-workshop"
```

### Using Bicep Parameters

Edit `main.bicepparam` or `main.parameters.json` depending on your method.

## 📝 Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `location` | `eastus` | Azure region |
| `resourcePrefix` | `zava-agent-wks` | Resource name prefix |
| `uniqueSuffix` | Auto-generated | 4-character unique suffix |
| `aiProjectFriendlyName` | `Zava Agent Service Workshop` | Display name |
| `models` | GPT-4o, embeddings | Models to deploy |

## 🧹 Cleanup

### With azd (Recommended)
```bash
azd down
```

### With Azure CLI
```bash
az group delete --name <resource-group-name> --yes
```

### Cleanup Soft-Deleted Resources

If you encounter quota issues from soft-deleted resources:
```bash
./cleanup-deleted-resources.sh
```

## 🔐 Security

### Roles Assigned

The deployment automatically assigns these roles to the signed-in user:
- Azure AI Developer
- Azure AI User
- Azure AI Project Manager

### Service Principal

For CI/CD, create a service principal:
```bash
az ad sp create-for-rbac \
  --name "github-actions-foundry" \
  --role Contributor \
  --scopes /subscriptions/{subscription-id}
```

## 📊 Monitoring

### View Deployment Logs

**With azd:**
```bash
azd provision --debug
```

**With Azure CLI:**
```bash
az deployment sub list --output table
az deployment sub show --name <deployment-name>
```

### Application Insights

After deployment, monitor your application:
```bash
az monitor app-insights query \
  --app <insights-name> \
  --resource-group <rg-name> \
  --analytics-query "requests | take 10"
```

## 🐛 Troubleshooting

### Common Issues

**Quota Exceeded:**
- Try different region
- Clean up soft-deleted resources
- Request quota increase

**Permission Denied:**
- Verify Contributor/Owner role
- Check service principal permissions

**Model Deployment Failed:**
- Verify region supports models
- Check quota availability
- Review deployment logs

### Getting Help

```bash
# Check azd status
azd provision --debug

# Verify Azure login
az account show

# List available regions
az account list-locations -o table
```

## 📚 Additional Resources

- [Azure Developer CLI Docs](https://learn.microsoft.com/azure/developer/azure-developer-cli/)
- [Bicep Documentation](https://learn.microsoft.com/azure/azure-resource-manager/bicep/)
- [Azure AI Foundry](https://learn.microsoft.com/azure/ai-foundry/)
- [Deployment Comparison](../docs/DEPLOYMENT-COMPARISON.md)

## 🔄 Migration from deploy.sh to azd

1. **Install azd:**
   ```bash
   curl -fsSL https://aka.ms/install-azd.sh | bash
   ```

2. **Initialize:**
   ```bash
   azd init
   ```

3. **Provision:**
   ```bash
   azd provision
   ```

That's it! Your resources will be deployed with better management capabilities.

## 💡 Tips

- Use `azd env list` to manage multiple environments
- Run `azd down --purge` to remove all resources and purge soft-deleted ones
- Check `.azure/` directory for environment configurations
- Use `azd env get-values` to see all deployment outputs

## 📞 Support

- **Issues:** [GitHub Issues](https://github.com/NickAzureDevops/aitour26-WRK542-prototype-agents-with-the-ai-toolkit-and-model-context-protocol/issues)
- **Community:** [Microsoft Foundry Discord](https://aka.ms/MicrosoftFoundryDiscord-AITour26)
- **Documentation:** See [DEPLOYMENT.md](../DEPLOYMENT.md)
