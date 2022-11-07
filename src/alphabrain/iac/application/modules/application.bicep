param containerAppName string
param location string
param environmentID string

param containerImage string
param containerPort int
param command array

param isPrivateRegistry bool = true
param containerRegistryName string
param containerLoginServer string
@secure()
param containerRegistryPassword string

// to find the role definition id, use: https://docs.microsoft.com/en-us/azure/role-based-access-control/built-in-roles
param isExternalIngress bool = true
param enableIngress bool = true
param minReplicas int = 1
param env array = []
var cpu = json('1.5')
var memory = '3Gi'

resource containerApp 'Microsoft.App/containerApps@2022-06-01-preview' = {
  // resource containerApp 'Microsoft.App/containerApps@2022-01-01-preview' = {
  name: containerAppName
  location: location
  identity: {
    type: 'SystemAssigned'
  }

  properties: {

    managedEnvironmentId: environmentID
    configuration: {
      secrets: [
        {
          name: 'container-registry-password'
          value: containerRegistryPassword
        }
      ]

      registries: isPrivateRegistry ? [
        {
          server: containerLoginServer
          username: containerRegistryName
          passwordSecretRef: 'container-registry-password'
        }
      ] : null
      ingress: enableIngress ? {
        external: isExternalIngress
        targetPort: containerPort
        transport: 'auto'
      } : {}
    }
    template: {
      containers: [
        {
          command: command
          image: containerImage
          name: containerAppName
          env: env
          resources: {
            cpu: cpu
            memory: memory
          }

        }
      ]
      scale: {
        minReplicas: minReplicas
        maxReplicas: 3
      }
    }
  }
}

var roleDefinitionResourceId = 'f6c7c914-8db3-469d-8ca1-694a8f32e121' // AzureML data sciencist role

resource WorkspaceContributorAccess 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(environmentID, containerApp.id, resourceGroup().id, subscription().id, roleDefinitionResourceId)
  properties: {
    principalId: containerApp.identity.principalId
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', roleDefinitionResourceId)
    principalType: 'ServicePrincipal'
  }
}

output fqdn string = enableIngress ? containerApp.properties.configuration.ingress.fqdn : 'Ingress not enabled'
