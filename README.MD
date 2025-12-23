<p align="center">
<img src="img/Banner-MS-AI-Tour-26.png" alt="decorative banner" width="1200"/>
</p>

# [Microsoft AI Tour 2026](https://aitour.microsoft.com)

## 🔥WRK542: Prototype Agents with the AI Toolkit and Model Context Protocol (MCP)

[![Microsoft Foundry Discord](https://dcbadge.limes.pink/api/server/Pwpvf3TWaw)](https://aka.ms/MicrosoftFoundryDiscord-AITour26)
[![Microsoft Foundry Developer Forum](https://img.shields.io/badge/GitHub-Microsoft_Foundry_Developer_Forum-blue?style=for-the-badge&logo=github&color=adff2f&logoColor=fff)](https://aka.ms/MicrosoftFoundryForum-AITour26)

If you will be delivering this session, check the [session-delivery-sources](./session-delivery-resources/) folder for slides, scripts, and other resources.

### Session Description

Learn how to build a conversational AI agent in VS Code using the AI toolkit, Microsoft Foundry and the Model Context Protocol (MCP). You'll explore and compare models to find the best fit for your agent, configure its instructions and enable sales analysis and product inventory management.

### 🧠 Learning Outcomes

By the end of this session, learners will be able to:

-  Explore and compare models to select the best fit for their business scenario
-  Augment models with prompts and data to get more accurate and grounded responses 
-  Prototype an agent by combining models and instructions with tools via MCP (Model Context Protocol)

### 💻 Technologies Used

1. [AI toolkit for Visual Studio Code](https://code.visualstudio.com/docs/intelligentapps/overview)
1. [GitHub models](https://github.com/features/models)
1. [Microsoft Foundry Models](https://learn.microsoft.com/en-us/azure/ai-foundry/concepts/foundry-models-overview)
1. [MCP - Model Context Protocol](https://modelcontextprotocol.io/docs/getting-started/intro)

### 🚀 Deployment Instructions

#### Prerequisites

Before deploying this project, ensure you have:

- An active [Azure subscription](https://azure.microsoft.com/free/)
- [Azure CLI](https://learn.microsoft.com/cli/azure/install-azure-cli) installed and configured
- [Python 3.11+](https://www.python.org/downloads/) installed
- [Git](https://git-scm.com/downloads) installed
- [Visual Studio Code](https://code.visualstudio.com/) with the [AI Toolkit extension](https://marketplace.visualstudio.com/items?itemName=ms-windows-ai-studio.windows-ai-studio)

#### Step 1: Clone the Repository

```bash
git clone https://github.com/NickAzureDevops/aitour26-WRK542-prototype-agents-with-the-ai-toolkit-and-model-context-protocol.git
cd aitour26-WRK542-prototype-agents-with-the-ai-toolkit-and-model-context-protocol
```

> **Note:** If you've forked this repository, replace the URL with your fork's URL.

#### Step 2: Deploy Azure Infrastructure

The project includes automated deployment scripts to provision the required Azure resources:

1. **Sign in to Azure:**
   ```bash
   az login
   ```

2. **Set your active subscription** (if you have multiple):
   ```bash
   az account set --subscription "<your-subscription-id>"
   ```

3. **Deploy the infrastructure:**
   ```bash
   cd infra
   ./deploy.sh
   ```

   The deployment script will:
   - Create a resource group with a unique suffix
   - Deploy Azure AI Foundry hub and project
   - Deploy GPT-4o and text-embedding-3-small models
   - Set up Application Insights for monitoring
   - Create a `.env` file in the `src/` directory with all necessary credentials
   - Assign required Azure roles to your account

   > **Note:** The deployment may take 10-15 minutes to complete.

#### Step 3: Set Up Python Environment

1. **Create and activate a virtual environment:**

   On macOS/Linux:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

   On Windows:
   ```powershell
   python -m venv .venv
   .venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.lock.txt
   ```

3. **Install the shared package:**
   ```bash
   pip install -e ./shared
   ```

#### Step 4: Verify Configuration

After deployment, verify that the `.env` file was created:

```bash
cat src/.env
```

The file should contain:
- `PROJECT_ENDPOINT`: Your Azure AI Foundry project endpoint
- `AZURE_OPENAI_ENDPOINT`: Your Azure OpenAI endpoint
- `AZURE_OPENAI_KEY`: Your Azure OpenAI API key
- `GPT_MODEL_DEPLOYMENT_NAME`: Model deployment name (gpt-4o)
- `EMBEDDING_MODEL_DEPLOYMENT_NAME`: Embedding model deployment name (text-embedding-3-small)
- `APPLICATIONINSIGHTS_CONNECTION_STRING`: Application Insights connection string
- `AZURE_TRACING_GEN_AI_CONTENT_RECORDING_ENABLED`: Enable AI tracing (true)

#### Step 5: Open in VS Code

Open the project in Visual Studio Code and authenticate with Azure:

```bash
code .
```

1. Install the AI Toolkit extension if not already installed
2. Click on the Microsoft Foundry icon in the sidebar
3. Sign in to Azure when prompted
4. Select your AI Foundry project

#### Running the Application

Follow the instructions in the [src/readme.md](./src/readme.md) file for specific guidance on running MCP servers and the agent application.

#### Cleanup

To remove all deployed Azure resources:

1. **Find your resource group name** in the `src/resources.txt` file created during deployment, or list your resource groups:
   ```bash
   cat src/resources.txt
   # Or list all resource groups matching the naming pattern
   az group list --query "[?contains(name, 'rg-zava-agent-wks')].name" -o table
   ```

2. **Delete the resource group** (replace with your actual resource group name):
   ```bash
   az group delete --name rg-zava-agent-wks-<your-unique-suffix> --yes --no-wait
   ```

> **Tip:** The resource group name follows the pattern `rg-zava-agent-wks-XXXX` where XXXX is a randomly generated 4-character suffix.

### 🔗 Session Resources
| Resources          | Links                             | Description        |
|:-------------------|:----------------------------------|:-------------------|
| Additional Resources for this session | [https://learn.microsoft.com](https://learn.microsoft.com?ocid=AITour26_resourcecenter_cnl) | Links specific to this session |

### 📚 Continued Learning Resources
| Resources          | Links                             | Description        |
|:-------------------|:----------------------------------|:-------------------|
| AI Tour 2026 Resource Center | [https://aka.ms/AITour26-Resource-Center](https://aka.ms/AITour26-Resource-Center?ocid=AITour26_resourcecenter_cnl) | Links to all repos for AI Tour 26 Sessions |
| Microsoft Foundry Community Discord | [![Microsoft Foundry Discord](https://dcbadge.limes.pink/api/server/Pwpvf3TWaw)](https://aka.ms/MicrosoftFoundryDiscord-AITour26)| Connect with the Microsoft Foundry Community! |
| Learn at AI Tour | [https://aka.ms/LearnAtAITour](https://aka.ms/LearnAtAITour?ocid=AITour26_resourcecenter_cnl) | Continue learning on Microsoft Learn |

### 🌐 Multi-Language Support

*Coming soon*

## Content Owners

<!-- TODO: Add yourself as a content owner
1. Change the src in the image tag to {your github url}.png
2. Change INSERT NAME HERE to your name
3. Change the github url in the final href to your url. -->


<table>
<tr>
    <td align="center"><a href="http://github.com/gloveboxes">
        <img src="https://github.com/gloveboxes.png" width="100px;" alt="Dave Glover"
/><br />
        <sub><b>Dave Glover (Python)
</b></sub></a><br />
            <a href="https://github.com/gloveboxes" title="talk">📢</a>
    </td>
<tr>
 <td align="center"><a href="http://github.com/carlotta94c">
        <img src="https://github.com/carlotta94c.png" width="100px;" alt="Carlotta Castelluccio"/><br />
        <sub><b>Carlotta Castelluccio</b></sub></a><br />
            <a href="https://github.com/carlotta94c" title="talk">📢</a> 
    </td>
</tr>
</table>

## Responsible AI 

Microsoft is committed to helping our customers use our AI products responsibly, sharing our learnings, and building trust-based partnerships through tools like Transparency Notes and Impact Assessments. Many of these resources can be found at [https://aka.ms/RAI](https://aka.ms/RAI).
Microsoft’s approach to responsible AI is grounded in our AI principles of fairness, reliability and safety, privacy and security, inclusiveness, transparency, and accountability.

Large-scale natural language, image, and speech models - like the ones used in this sample - can potentially behave in ways that are unfair, unreliable, or offensive, in turn causing harms. Please consult the [Azure OpenAI service Transparency note](https://learn.microsoft.com/legal/cognitive-services/openai/transparency-note?tabs=text) to be informed about risks and limitations.

The recommended approach to mitigating these risks is to include a safety system in your architecture that can detect and prevent harmful behavior. [Azure AI Content Safety](https://learn.microsoft.com/azure/ai-services/content-safety/overview) provides an independent layer of protection, able to detect harmful user-generated and AI-generated content in applications and services. Azure AI Content Safety includes text and image APIs that allow you to detect material that is harmful. Within Azure AI Foundry portal, the Content Safety service allows you to view, explore and try out sample code for detecting harmful content across different modalities. The following [quickstart documentation](https://learn.microsoft.com/azure/ai-services/content-safety/quickstart-text?tabs=visual-studio%2Clinux&pivots=programming-language-rest) guides you through making requests to the service.

Another aspect to take into account is the overall application performance. With multi-modal and multi-models applications, we consider performance to mean that the system performs as you and your users expect, including not generating harmful outputs. It's important to assess the performance of your overall application using [Performance and Quality and Risk and Safety evaluators](https://learn.microsoft.com/azure/ai-studio/concepts/evaluation-metrics-built-in). You also have the ability to create and evaluate with [custom evaluators](https://learn.microsoft.com/azure/ai-studio/how-to/develop/evaluate-sdk#custom-evaluators).

You can evaluate your AI application in your development environment using the [Azure AI Evaluation SDK](https://microsoft.github.io/promptflow/index.html). Given either a test dataset or a target, your generative AI application generations are quantitatively measured with built-in evaluators or custom evaluators of your choice. To get started with the azure ai evaluation sdk to evaluate your system, you can follow the [quickstart guide](https://learn.microsoft.com/azure/ai-studio/how-to/develop/flow-evaluate-sdk). Once you execute an evaluation run, you can [visualize the results in Azure AI Foundry portal ](https://learn.microsoft.com/azure/ai-studio/how-to/evaluate-flow-results).
