# 📋 Documentation Index

Welcome to the Azure AI Foundry Agent Workshop documentation!

## 🚀 Getting Started

Start here if you're new to this project:

1. **[Quick Start Guide](QUICKSTART.md)** ⭐ **Start Here!**
   - 5-minute setup guide
   - Prerequisites checklist
   - Step-by-step deployment
   - Verification steps

## 📖 Deployment Guides

### Core Deployment
- **[Deployment Guide](../DEPLOYMENT.md)** - Comprehensive deployment documentation
  - Prerequisites
  - Deployment methods (azd vs bash script)
  - What gets deployed
  - Troubleshooting
  - Cleanup

### Decision Making
- **[Deployment Comparison](DEPLOYMENT-COMPARISON.md)** - Compare deployment approaches
  - Azure Developer CLI (azd) vs Bash Script
  - Feature comparison table
  - Migration guide
  - Recommendations

### Advanced Topics
- **[CI/CD Setup Guide](CICD-SETUP.md)** - Automated deployment pipelines
  - GitHub Actions setup
  - Azure DevOps setup
  - Security best practices
  - Environment strategies

## 📁 Repository Structure

```
.
├── azure.yaml              # Azure Developer CLI configuration
├── DEPLOYMENT.md           # Main deployment guide
├── README.MD               # Project overview
│
├── infra/                  # Infrastructure as Code
│   ├── main.bicep         # Main infrastructure template
│   ├── main.bicepparam    # Parameters for azd
│   ├── hooks/
│   │   └── postprovision.sh
│   └── README.md          # Infrastructure documentation
│
├── docs/                   # Documentation
│   ├── QUICKSTART.md      # Quick start guide
│   ├── DEPLOYMENT-COMPARISON.md
│   ├── CICD-SETUP.md      # CI/CD configuration
│   └── INDEX.md           # This file
│
├── .github/               # GitHub configuration
│   └── workflows/
│       └── azure-deploy.yml
│
└── .azdo/                 # Azure DevOps configuration
    └── azure-pipelines.yml
```

## 🎯 Common Tasks

### First Time Setup
```bash
# 1. Install Azure Developer CLI
curl -fsSL https://aka.ms/install-azd.sh | bash

# 2. Clone and navigate to repository
git clone <repo-url>
cd <repo-name>

# 3. Login and initialize
azd auth login
azd init

# 4. Deploy
azd provision
```

### Update Deployment
```bash
# Make infrastructure changes in infra/ directory
# Then provision again
azd provision
```

### View Deployed Resources
```bash
# List environment variables
azd env get-values

# Show resource group in Azure Portal
az group show --name $(azd env get-value resourceGroupName)
```

### Cleanup
```bash
# Delete all resources
azd down

# Or purge soft-deleted resources too
azd down --purge
```

## 📚 Documentation by Role

### Workshop Participant
1. [Quick Start Guide](QUICKSTART.md) - Get started quickly
2. [Deployment Guide](../DEPLOYMENT.md) - Understanding your environment
3. Workshop materials in `lab/` directory

### Instructor/Presenter
1. [Deployment Guide](../DEPLOYMENT.md) - Prepare infrastructure
2. [CI/CD Setup](CICD-SETUP.md) - Automate deployments
3. Session materials in `session-delivery-resources/`

### DevOps Engineer
1. [CI/CD Setup Guide](CICD-SETUP.md) - Pipeline configuration
2. [Deployment Comparison](DEPLOYMENT-COMPARISON.md) - Choose the right method
3. Infrastructure code in `infra/` directory

### Developer
1. [Quick Start Guide](QUICKSTART.md) - Get environment running
2. [Infrastructure README](../infra/README.md) - Understand the infrastructure
3. Application code in `src/` directory

## 🔍 Finding Information

### By Topic

**Deployment**
- First time: [Quick Start](QUICKSTART.md)
- Detailed: [Deployment Guide](../DEPLOYMENT.md)
- Comparison: [Deployment Comparison](DEPLOYMENT-COMPARISON.md)

**Automation**
- CI/CD: [CI/CD Setup](CICD-SETUP.md)
- GitHub Actions: `.github/workflows/azure-deploy.yml`
- Azure DevOps: `.azdo/azure-pipelines.yml`

**Infrastructure**
- Overview: [Infrastructure README](../infra/README.md)
- Bicep templates: `infra/*.bicep`
- Parameters: `infra/main.bicepparam`

**Troubleshooting**
- Deployment issues: [Deployment Guide - Troubleshooting](../DEPLOYMENT.md#troubleshooting)
- CI/CD issues: [CI/CD Setup - Troubleshooting](CICD-SETUP.md#troubleshooting)

## 📊 Architecture

### Infrastructure Components

```
┌─────────────────────────────────────────┐
│         Resource Group                  │
│                                         │
│  ┌──────────────────────────────────┐  │
│  │   Azure AI Foundry Account       │  │
│  │                                  │  │
│  │  ┌──────────────────────────┐   │  │
│  │  │   AI Project             │   │  │
│  │  │                          │   │  │
│  │  │  - GPT-4o               │   │  │
│  │  │  - text-embedding-3     │   │  │
│  │  └──────────────────────────┘   │  │
│  └──────────────────────────────────┘  │
│                                         │
│  ┌──────────────────────────────────┐  │
│  │   Application Insights           │  │
│  │   (Monitoring & Telemetry)       │  │
│  └──────────────────────────────────┘  │
└─────────────────────────────────────────┘
```

### Deployment Flow

```
Developer/CI
     │
     ├─ azd provision
     │       │
     │       ├─ Reads azure.yaml
     │       ├─ Loads infra/main.bicep
     │       ├─ Uses infra/main.bicepparam
     │       ├─ Deploys to Azure
     │       └─ Runs hooks/postprovision.sh
     │             └─ Creates src/.env
     │
     └─ Resources Ready!
```

## 🆘 Getting Help

### Documentation
- Check this index for relevant guides
- Search documentation using Ctrl+F
- Review troubleshooting sections

### Community
- [Microsoft Foundry Discord](https://aka.ms/MicrosoftFoundryDiscord-AITour26)
- [GitHub Issues](https://github.com/NickAzureDevops/aitour26-WRK542-prototype-agents-with-the-ai-toolkit-and-model-context-protocol/issues)
- [Microsoft Foundry Forum](https://aka.ms/MicrosoftFoundryForum-AITour26)

### Official Resources
- [Azure Developer CLI Docs](https://learn.microsoft.com/azure/developer/azure-developer-cli/)
- [Azure AI Foundry Docs](https://learn.microsoft.com/azure/ai-foundry/)
- [Bicep Documentation](https://learn.microsoft.com/azure/azure-resource-manager/bicep/)

## 🔄 Recent Updates

### December 2024
- ✅ Added Azure Developer CLI (azd) support
- ✅ Created comprehensive deployment documentation
- ✅ Added CI/CD pipeline examples
- ✅ Deprecated legacy bash script
- ✅ Added quick start guide

## 📝 Contributing

Improvements to documentation are welcome!

1. Check existing documentation
2. Create or update relevant files
3. Update this index if needed
4. Submit pull request

## 💡 Tips

- **Bookmark this page** - Quick reference to all docs
- **Start with Quick Start** - Fastest way to get running
- **Use azd** - It's the recommended approach
- **Check troubleshooting first** - Common issues are documented
- **Join the community** - Get help from others

## 🎓 Learning Path

**Beginner:**
1. Read [Quick Start](QUICKSTART.md)
2. Deploy using `azd provision`
3. Explore deployed resources in Azure Portal

**Intermediate:**
1. Review [Deployment Guide](../DEPLOYMENT.md)
2. Understand [Infrastructure README](../infra/README.md)
3. Modify parameters and redeploy

**Advanced:**
1. Set up [CI/CD Pipeline](CICD-SETUP.md)
2. Create multiple environments
3. Customize infrastructure templates

## 📞 Support Channels

| Issue Type | Contact Method |
|-----------|---------------|
| Deployment problems | [Deployment Guide - Troubleshooting](../DEPLOYMENT.md#troubleshooting) |
| CI/CD setup | [CI/CD Setup - Troubleshooting](CICD-SETUP.md#troubleshooting) |
| Infrastructure questions | [Infrastructure README](../infra/README.md) |
| Bug reports | [GitHub Issues](https://github.com/NickAzureDevops/aitour26-WRK542-prototype-agents-with-the-ai-toolkit-and-model-context-protocol/issues) |
| General questions | [Microsoft Foundry Discord](https://aka.ms/MicrosoftFoundryDiscord-AITour26) |

---

**Last Updated:** December 2024  
**Version:** 1.0.0  
**Status:** ✅ Complete
