# LCA Metadata
# Delay: 30 seconds

# =========================
# VM Life Cycle Action (PowerShell)
# Pull outputs from ARM/Bicep deployment and write .env
# =========================

# --- logging to both Skillable log + file ---
$logDir = "C:\logs"
if (-not (Test-Path $logDir)) { New-Item -ItemType Directory -Path $logDir | Out-Null }
$logFile = Join-Path $logDir "vm-init_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"
"[$(Get-Date -Format s)] VM LCA start" | Tee-Object -FilePath $logFile

function Log {
    param([string]$m)
    $ts = "[$(Get-Date -Format s)] $m"
    $ts | Tee-Object -FilePath $logFile -Append
}

# --- Skillable tokens / lab values ---
$UniqueSuffix = "@lab.LabInstance.Id"
$TenantId     = "@lab.CloudSubscription.TenantId"
$AppId        = "@lab.CloudSubscription.AppId"
$Secret       = "@lab.CloudSubscription.AppSecret"
$SubId        = "@lab.CloudSubscription.Id"

# Resource group where your template deployed
$ResourceGroup = "@lab.CloudResourceGroup(rg-zava-agent-wks).Name"

# --- Azure login (service principal) ---
Log "Authenticating to Azure tenant $TenantId, subscription $SubId"
$sec  = ConvertTo-SecureString $Secret -AsPlainText -Force
$cred = [pscredential]::new($AppId, $sec)

Connect-AzAccount `
    -ServicePrincipal `
    -Tenant $TenantId `
    -Credential $cred `
    -Subscription $SubId | Out-Null

$ctx = Get-AzContext
Log "Logged in as: $($ctx.Account) | Sub: $($ctx.Subscription.Name) ($($ctx.Subscription.Id))"

#######################################################
# Create .env (LabUser repo src folder)

# --- Find deployment and read OUTPUTS ---
$deployment = Get-AzResourceGroupDeployment -ResourceGroupName $ResourceGroup `
    | Sort-Object Timestamp `
    | Select-Object -First 1

if (-not $deployment) {
    Log "No RG-scope deployments found. Trying subscription-scope..."
    $deployment = Get-AzDeployment `
        | Sort-Object Timestamp -Descending `
        | Select-Object -First 1
}

if (-not $deployment) {
    throw "Could not locate any ARM/Bicep deployments to read outputs from."
}

$scope = if ([string]::IsNullOrEmpty($deployment.Location)) { "subscription" } else { $deployment.Location }
Log "Using deployment: $($deployment.DeploymentName) | Scope: $scope"

$outs = $deployment.Outputs

# Required outputs
$projectsEndpoint = $outs.projectsEndpoint.value
$applicationInsightsConnectionString = $outs.applicationInsightsConnectionString.value

if (-not $projectsEndpoint) { throw "Deployment output 'projectsEndpoint' not found." }
if (-not $applicationInsightsConnectionString) { throw "Deployment output 'applicationInsightsConnectionString' not found." }

Log "projectsEndpoint captured"
Log "applicationInsightsConnectionString captured"

# --- Static workshop values ---
$GPT_MODEL_DEPLOYMENT_NAME        = "gpt-4o"
$EMBEDDING_MODEL_DEPLOYMENT_NAME  = "text-embedding-3-small"

# Derive Azure OpenAI endpoint
$azureOpenAIEndpoint = $projectsEndpoint -replace 'api/projects/.*$', ''

# Azure OpenAI key
$aiFoundryName = if ($outs.aiFoundryName) { $outs.aiFoundryName.value } else { $null }
if (-not $aiFoundryName) { throw "Deployment output 'aiFoundryName' not found." }

Log "Retrieving Azure OpenAI key for $aiFoundryName"
$keys = Get-AzCognitiveServicesAccountKey `
    -ResourceGroupName $ResourceGroup `
    -Name $aiFoundryName

$azureOpenAIKey = $keys.Key1

# -----------------------------
# Target repo src folder
# -----------------------------
$targetPath = "C:\Users\LabUser\aitour26-WRK542-prototype-agents-with-the-ai-toolkit-and-model-context-protocol\src"

if (-not (Test-Path $targetPath)) {
    throw "Target path not found: $targetPath"
}

# --- Write .env ---
$ENV_FILE_PATH = Join-Path $targetPath ".env"
if (Test-Path $ENV_FILE_PATH) {
    Remove-Item -Path $ENV_FILE_PATH -Force
}

@"
PROJECT_ENDPOINT="$projectsEndpoint"
AZURE_OPENAI_ENDPOINT="$azureOpenAIEndpoint"
AZURE_OPENAI_KEY="$azureOpenAIKey"
GPT_MODEL_DEPLOYMENT_NAME="$GPT_MODEL_DEPLOYMENT_NAME"
EMBEDDING_MODEL_DEPLOYMENT_NAME="$EMBEDDING_MODEL_DEPLOYMENT_NAME"
APPLICATIONINSIGHTS_CONNECTION_STRING="$applicationInsightsConnectionString"
AZURE_TRACING_GEN_AI_CONTENT_RECORDING_ENABLED="true"
"@ | Set-Content -Path $ENV_FILE_PATH -Encoding UTF8

Log "Created .env at $ENV_FILE_PATH"

# --- Write resources.txt ---
$aiProjectName = if ($outs.aiProjectName) { $outs.aiProjectName.value } else { $null }
$applicationInsightsName = if ($outs.applicationInsightsName) { $outs.applicationInsightsName.value } else { $null }

$RESOURCES_FILE_PATH = Join-Path $targetPath "resources.txt"
if (Test-Path $RESOURCES_FILE_PATH) {
    Remove-Item -Path $RESOURCES_FILE_PATH -Force
}

@(
    "Azure AI Foundry Resources:",
    "- Resource Group Name: $ResourceGroup",
    "- AI Project Name: $aiProjectName",
    "- Foundry Resource Name: $aiFoundryName",
    "- Application Insights Name: $applicationInsightsName"
) | Out-File -FilePath $RESOURCES_FILE_PATH -Encoding utf8

Log "Created resources.txt at $RESOURCES_FILE_PATH"

Log "VM LCA complete."