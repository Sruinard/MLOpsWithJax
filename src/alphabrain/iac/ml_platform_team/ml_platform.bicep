param location string = resourceGroup().location

var uuid = uniqueString(resourceGroup().id)
var department_name = 'mb'
var workspace_name = '${department_name}-pf-${uuid}'
var application_insights_name = '${department_name}-ain${uuid}'
var container_registry_name = '${department_name}platformcr${uuid}'

resource applicationInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: application_insights_name
  location: location
  kind: 'web'
  properties: {
    Application_Type: 'web'
    DisableIpMasking: false
    DisableLocalAuth: false
    Flow_Type: 'Bluefield'
    ForceCustomerStorageForProfiler: false
    ImmediatePurgeDataOn30Days: true
    IngestionMode: 'ApplicationInsights'
    publicNetworkAccessForIngestion: 'Enabled'
    publicNetworkAccessForQuery: 'Disabled'
    Request_Source: 'rest'
  }
}

resource MLStorageAccount 'Microsoft.Storage/storageAccounts@2021-01-01' = {
  name: '${department_name}storage${uuid}'
  location: location
  sku: {
    name: 'Standard_RAGRS'
  }
  identity: {
    type: 'SystemAssigned'
  }
  kind: 'StorageV2'

  properties: {

    encryption: {
      services: {
        blob: {
          enabled: true
        }
        file: {
          enabled: true
        }
      }
      keySource: 'Microsoft.Storage'
    }
    supportsHttpsTrafficOnly: true
  }
}

resource containerRegistry 'Microsoft.ContainerRegistry/registries@2021-09-01' = {
  name: container_registry_name
  location: location
  sku: {
    name: 'Premium'
  }
  properties: {
    adminUserEnabled: true
    networkRuleBypassOptions: 'AzureServices'
  }
}

resource MLkeyVault 'Microsoft.KeyVault/vaults@2021-04-01-preview' = {
  name: 'kv-${uuid}'
  location: location
  properties: {
    tenantId: tenant().tenantId
    sku: {
      name: 'standard'
      family: 'A'
    }
    accessPolicies: []
    enableSoftDelete: true
  }
}

resource amlcompute 'Microsoft.MachineLearningServices/workspaces/computes@2022-06-01-preview' = {
  name: '${mlworkspace.name}/cpu-cluster'
  location: location
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    computeType: 'AmlCompute'
    description: 'Machine Learning cluster for training and serving ml models'
    disableLocalAuth: true
    properties: {
      vmPriority: 'Dedicated'
      vmSize: 'STANDARD_D2'
      osType: 'Linux'
      scaleSettings: {
        minNodeCount: 1
        maxNodeCount: 5
      }
    }
  }
}

resource mlworkspace 'Microsoft.MachineLearningServices/workspaces@2022-06-01-Preview' = {
  name: workspace_name
  location: location
  identity: {
    type: 'SystemAssigned'
  }

  properties: {
    // workspace organization
    friendlyName: 'AlphaBrain Machine Learning workspace'
    description: 'AlphaBrains data science environment for delivering intelligence to its customers'
    keyVault: MLkeyVault.id
    applicationInsights: applicationInsights.id
    storageAccount: MLStorageAccount.id
    containerRegistry: containerRegistry.id

  }
}

var roleDefinitionResourceId = 'f6c7c914-8db3-469d-8ca1-694a8f32e121' // AzureML data sciencist role

resource WorkspaceContributorAccess 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(resourceGroup().id, subscription().id, roleDefinitionResourceId)
  properties: {
    principalId: amlcompute.identity.principalId
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', roleDefinitionResourceId)
    principalType: 'ServicePrincipal'
  }
}

output containerRegistryName string = containerRegistry.name
output MLWorkspaceName string = mlworkspace.name
