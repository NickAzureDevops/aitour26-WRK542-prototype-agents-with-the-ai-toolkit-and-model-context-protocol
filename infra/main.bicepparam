using './main.bicep'

param location = readEnvironmentVariable('AZURE_LOCATION', 'eastus')
param resourcePrefix = readEnvironmentVariable('AZURE_RESOURCE_PREFIX', 'zava-agent-wks')
param uniqueSuffix = readEnvironmentVariable('AZURE_UNIQUE_SUFFIX', take(uniqueString(subscription().id, location), 4))
param aiProjectFriendlyName = 'Zava Agent Service Workshop'
param aiProjectDescription = 'Project resources required for the Zava Agent Workshop.'
param models = [
  {
    name: 'gpt-4o'
    format: 'OpenAI'
    version: '2024-08-06'
    skuName: 'GlobalStandard'
    capacity: 120
  }
  {
    name: 'text-embedding-3-small'
    format: 'OpenAI'
    version: '1'
    skuName: 'GlobalStandard'
    capacity: 120
  }
]
