#!/bin/bash

# Post-provision hook for Azure Developer CLI
# This script runs after 'azd provision' completes
# It retrieves deployment outputs and creates .env file for the application

set -e

echo "Running post-provision script..."

# Get the current environment name
AZURE_ENV_NAME=$(azd env get-value AZURE_ENV_NAME)

if [ -z "$AZURE_ENV_NAME" ]; then
    echo "Error: AZURE_ENV_NAME not set"
    exit 1
fi

# Get outputs from azd
PROJECTS_ENDPOINT=$(azd env get-value projectsEndpoint)
RESOURCE_GROUP_NAME=$(azd env get-value resourceGroupName)
AI_FOUNDRY_NAME=$(azd env get-value aiFoundryName)
AI_PROJECT_NAME=$(azd env get-value aiProjectName)
APPLICATIONINSIGHTS_CONNECTION_STRING=$(azd env get-value applicationInsightsConnectionString)
APPLICATION_INSIGHTS_NAME=$(azd env get-value applicationInsightsName)
SUBSCRIPTION_ID=$(azd env get-value subscriptionId)

# Calculate Azure OpenAI endpoint from projects endpoint
AZURE_OPENAI_ENDPOINT=$(echo "$PROJECTS_ENDPOINT" | sed 's|api/projects/.*||')

# Get the Azure OpenAI API key
echo "Retrieving Azure OpenAI API key..."
AZURE_OPENAI_KEY=$(az cognitiveservices account keys list \
  --name "$AI_FOUNDRY_NAME" \
  --resource-group "$RESOURCE_GROUP_NAME" \
  --query key1 -o tsv)

if [ -z "$AZURE_OPENAI_KEY" ] || [ "$AZURE_OPENAI_KEY" = "null" ]; then
  echo "Warning: Could not retrieve Azure OpenAI API key."
fi

# Create src directory if it doesn't exist
mkdir -p ./src

ENV_FILE_PATH="./src/.env"

# Delete the file if it exists
[ -f "$ENV_FILE_PATH" ] && rm "$ENV_FILE_PATH"

# Write to the .env file
{
  echo "PROJECT_ENDPOINT=$PROJECTS_ENDPOINT"
  echo "AZURE_OPENAI_ENDPOINT=$AZURE_OPENAI_ENDPOINT"
  echo "AZURE_OPENAI_KEY=$AZURE_OPENAI_KEY"
  echo "GPT_MODEL_DEPLOYMENT_NAME=\"gpt-4o\""
  echo "EMBEDDING_MODEL_DEPLOYMENT_NAME=\"text-embedding-3-small\""
  echo "APPLICATIONINSIGHTS_CONNECTION_STRING=\"$APPLICATIONINSIGHTS_CONNECTION_STRING\""
  echo "AZURE_TRACING_GEN_AI_CONTENT_RECORDING_ENABLED=\"true\""
} > "$ENV_FILE_PATH"

echo "✅ Created .env file at $ENV_FILE_PATH"

RESOURCES_FILE_PATH="./src/resources.txt"

# Delete the file if it exists
[ -f "$RESOURCES_FILE_PATH" ] && rm "$RESOURCES_FILE_PATH"

# Write to the resources.txt file
{
  echo "Azure AI Foundry Resources:"
  echo "- Resource Group Name: $RESOURCE_GROUP_NAME"
  echo "- AI Project Name: $AI_PROJECT_NAME"
  echo "- Foundry Resource Name: $AI_FOUNDRY_NAME"
  echo "- Application Insights Name: $APPLICATION_INSIGHTS_NAME"
} > "$RESOURCES_FILE_PATH"

echo "✅ Created resources file at $RESOURCES_FILE_PATH"

echo ""
echo "🎉 Post-provision completed successfully!"
echo ""
echo "📋 Resource Information:"
echo "  Resource Group: $RESOURCE_GROUP_NAME"
echo "  AI Project: $AI_PROJECT_NAME"
echo "  Foundry Resource: $AI_FOUNDRY_NAME"
echo "  Application Insights: $APPLICATION_INSIGHTS_NAME"
echo ""
