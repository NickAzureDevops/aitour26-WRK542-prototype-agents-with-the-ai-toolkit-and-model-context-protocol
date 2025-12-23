# Quick Start Guide

Get up and running with the Azure AI Foundry Agent Workshop in minutes!

## Prerequisites Checklist

- [ ] Azure Subscription ([Get a free account](https://azure.microsoft.com/free/))
- [ ] Azure Developer CLI installed
- [ ] Azure CLI installed
- [ ] Python 3.11 or later
- [ ] Visual Studio Code

## 5-Minute Setup

### 1. Install Tools (One-Time Setup)

**Windows (PowerShell as Administrator)**:
```powershell
# Install Azure Developer CLI
powershell -ex AllSigned -c "Invoke-RestMethod 'https://aka.ms/install-azd.ps1' | Invoke-Expression"

# Install Azure CLI (if not already installed)
winget install -e --id Microsoft.AzureCLI
```

**macOS**:
```bash
# Install Azure Developer CLI
curl -fsSL https://aka.ms/install-azd.sh | bash

# Install Azure CLI (if not already installed)
brew install azure-cli
```

**Linux (Ubuntu/Debian)**:
```bash
# Install Azure Developer CLI
curl -fsSL https://aka.ms/install-azd.sh | bash

# Install Azure CLI (if not already installed)
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
```

### 2. Clone Repository

```bash
git clone https://github.com/NickAzureDevops/aitour26-WRK542-prototype-agents-with-the-ai-toolkit-and-model-context-protocol.git
cd aitour26-WRK542-prototype-agents-with-the-ai-toolkit-and-model-context-protocol
```

### 3. Login to Azure

```bash
azd auth login
az login
```

### 4. Deploy Azure Resources

```bash
# Initialize environment
azd init

# When prompted:
# - Environment name: dev (or your preferred name)
# - Subscription: Select your Azure subscription
# - Location: eastus (or your preferred region)

# Provision resources (takes 5-10 minutes)
azd provision
```

### 5. Verify Setup

```bash
# Check that .env file was created
cat src/.env

# You should see:
# - PROJECT_ENDPOINT
# - AZURE_OPENAI_ENDPOINT
# - AZURE_OPENAI_KEY
# - GPT_MODEL_DEPLOYMENT_NAME
# - EMBEDDING_MODEL_DEPLOYMENT_NAME
# - APPLICATIONINSIGHTS_CONNECTION_STRING
```

### 6. Install Python Dependencies

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.lock.txt
```

### 7. Test Your Setup

```bash
cd src
python -m pytest tests/test_servers_startup.sh
```

## 🎉 You're Ready!

Your Azure AI Foundry environment is now set up and ready for the workshop!

## What Was Deployed?

- **Resource Group**: `rg-zava-agent-wks-XXXX`
- **AI Foundry Account**: For managing AI resources
- **AI Project**: Your workspace for building agents
- **GPT-4o Model**: Deployed and ready to use
- **Text Embedding Model**: For semantic search
- **Application Insights**: For monitoring and telemetry

## Next Steps

1. **Open VS Code**: 
   ```bash
   code .
   ```

2. **Install AI Toolkit Extension**:
   - Open VS Code
   - Go to Extensions (Ctrl+Shift+X)
   - Search for "AI Toolkit"
   - Install it

3. **Explore MCP Servers**:
   ```bash
   cd src/mcp_servers
   ls -la
   ```

4. **Follow the Workshop**:
   - Check the `docs/` folder for workshop materials
   - Review `src/instructions/` for agent configuration examples

## Common Commands

```bash
# View deployed resources
azd env get-values

# List all resources in your resource group
az resource list --resource-group $(azd env get-value resourceGroupName) --output table

# Open Azure Portal to your resource group
az group show --name $(azd env get-value resourceGroupName) --query id -o tsv | \
  xargs -I {} open "https://portal.azure.com/#@/resource{}"
```

## Troubleshooting

### Issue: "azd: command not found"

**Solution**: Restart your terminal after installing azd, or manually add it to PATH.

### Issue: "Insufficient permissions"

**Solution**: Ensure you're using an account with Contributor or Owner role on the subscription.

### Issue: "Quota exceeded for model deployment"

**Solution**: Try a different region or request quota increase:
```bash
# Deploy to West US 2 instead
azd env set AZURE_LOCATION "westus2"
azd provision
```

### Issue: "Can't find .env file"

**Solution**: Check if provisioning completed successfully:
```bash
azd provision
```

## Cleanup (When You're Done)

```bash
# Delete all Azure resources
azd down

# Remove local environment
rm -rf .venv
rm -f src/.env src/resources.txt
```

## Need Help?

- **Documentation**: See [DEPLOYMENT.md](../DEPLOYMENT.md) for detailed instructions
- **Comparison**: See [docs/DEPLOYMENT-COMPARISON.md](DEPLOYMENT-COMPARISON.md) for deployment methods
- **Issues**: File an issue on GitHub
- **Community**: Join the [Microsoft Foundry Discord](https://aka.ms/MicrosoftFoundryDiscord-AITour26)

## Estimated Costs

This workshop deploys resources that incur costs:

- **Azure AI Foundry**: ~$1-2/day when idle
- **GPT-4o**: Pay-per-token (~$0.01 per 1K tokens)
- **Embeddings**: Pay-per-token (~$0.0001 per 1K tokens)
- **Application Insights**: ~$2-3/month for typical usage

**Remember to run `azd down` when finished to avoid unnecessary charges!**

## Workshop Time Estimate

- **Setup**: 10-15 minutes
- **Workshop Content**: 60-90 minutes
- **Total**: ~2 hours

Happy learning! 🚀
