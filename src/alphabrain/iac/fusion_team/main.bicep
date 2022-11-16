param location string = resourceGroup().location
param environmentName string = 'csu-nl-app-mlops'
param containerRegistryName string = 'microbrainmlops'

param logAnalyticsWorkspaceName string = 'logs-${environmentName}-${uniqueString(resourceGroup().id)}'
param appInsightsName string = 'appins-${environmentName}-${uniqueString(resourceGroup().id)}'

var uuid = uniqueString(resourceGroup().id)
var department_name = 'alphabrain'
var workspace_name = '${department_name}-platform-${uuid}'
var unique_endpoint_name = 'moe${uuid}'

resource logAnalyticsWorkspace 'Microsoft.OperationalInsights/workspaces@2020-03-01-preview' = {
  name: logAnalyticsWorkspaceName
  location: location
  properties: any({
    retentionInDays: 30
    features: {
      searchVersion: 1
    }
    sku: {
      name: 'PerGB2018'
    }
  })
}

resource appInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: appInsightsName
  location: location
  kind: 'web'
  properties: {
    Application_Type: 'web'
    WorkspaceResourceId: logAnalyticsWorkspace.id
  }
}

resource environment 'Microsoft.App/managedEnvironments@2022-01-01-preview' = {
  name: environmentName
  location: location
  properties: {
    daprAIInstrumentationKey: appInsights.properties.InstrumentationKey
    appLogsConfiguration: {
      destination: 'log-analytics'
      logAnalyticsConfiguration: {
        customerId: logAnalyticsWorkspace.properties.customerId
        sharedKey: logAnalyticsWorkspace.listKeys().primarySharedKey
      }
    }
  }
}

resource containerRegistry 'Microsoft.ContainerRegistry/registries@2021-12-01-preview' existing = {
  name: '${containerRegistryName}${uniqueString(resourceGroup().id)}'
}

module containerAppsRestAPI './modules/application.bicep' = {
  name: 'microbrain_restapi'
  params: {
    location: location
    containerAppName: 'microbrainrestapi'
    environmentID: environment.id

    containerImage: '${containerRegistryName}${uniqueString(resourceGroup().id)}.azurecr.io/microbrain:latest'
    command: [ 'python', 'alphabrain/app.py' ]
    containerPort: 8000
    env: [
      {
        name: 'PORT_NUMBER'
        value: 'Application running on port 8000'
      }
      {
        name: 'SUBSCRIPTION_ID'
        value: subscription().id
      }
      {
        name: 'RESOURCE_GROUP'
        value: resourceGroup().name
      }
      {
        name: 'AZUREML_WORKSPACE_NAME'
        value: workspace_name
      }
      {
        name: 'AZUREML_ONLINE_ENDPOINT_NAME'
        value: unique_endpoint_name
      }
    ]
    containerRegistryName: containerRegistry.name
    containerLoginServer: containerRegistry.properties.loginServer
    containerRegistryPassword: containerRegistry.listCredentials().passwords[0].value

  }
}

module containerAppsGraphQL './modules/application.bicep' = {
  name: 'microbrain_graphql'
  params: {
    location: location
    containerAppName: 'microbraingraphql'
    environmentID: environment.id
    containerImage: '${containerRegistryName}${uniqueString(resourceGroup().id)}.azurecr.io/microbrain:latest'
    containerPort: 8181
    command: [ 'python', 'alphabrain/graphql_api.py' ]

    env: [
      {
        name: 'PORT_NUMBER'
        value: 'Application running on port 8181'
      }
      {
        name: 'ALPHABRAIN_ENDPOINT'
        value: 'https://${containerAppsRestAPI.outputs.fqdn}'
      }
    ]
    containerRegistryName: containerRegistry.name
    containerLoginServer: containerRegistry.properties.loginServer
    containerRegistryPassword: containerRegistry.listCredentials().passwords[0].value

  }
}

var gatewayContainerApp = {
  appName: 'gateway'
  containerImage: '${containerRegistryName}${uniqueString(resourceGroup().id)}.azurecr.io/gateway:latest'
  containerPort: 7000
  env: [
    {
      name: 'ALPHABRAIN_ENDPOINT'
      value: 'https://${containerAppsGraphQL.outputs.fqdn}/graphql'
    }
  ]
}

module gatewayApp './modules/application.bicep' = {
  name: 'gateway'
  params: {
    location: location
    containerAppName: gatewayContainerApp.appName
    environmentID: environment.id
    containerImage: gatewayContainerApp.containerImage
    containerPort: gatewayContainerApp.containerPort

    env: gatewayContainerApp.env
    containerRegistryName: containerRegistry.name
    containerLoginServer: containerRegistry.properties.loginServer
    containerRegistryPassword: containerRegistry.listCredentials().passwords[0].value

  }
}

output location string = location
output environmentId string = environment.id
