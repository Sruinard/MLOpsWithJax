param location string = resourceGroup().location

var workspace_name = 'alphabrain${uniqueString(resourceGroup().id)}'

resource mlworkspace 'Microsoft.MachineLearningServices/workspaces@2022-05-01' = {
  name: workspace_name
  location: location
  identity: {
    type: 'SystemAssigned'
  }

  properties: {
    // workspace organization
    friendlyName: 'AlphaBrain Machine Learning workspace'
    description: 'AlphaBrains data science environment for delivering intelligence to its customers'
  }
}

resource mlenvironment 'Microsoft.MachineLearningServices/workspaces/environments@2022-06-01-preview' = {
  name: 'mlops-with-jax'
  parent: mlworkspace
  properties: {
    description: 'Environment for training ml models with JAX.'
  }
}

resource training_environment 'Microsoft.MachineLearningServices/workspaces/environments/versions@2022-06-01-preview' = {
  name: 'container-based-environment'
  parent: mlenvironment
  properties: {
    build: {
      contextUri: '../'
    }
  }
}
resource amlcompute 'Microsoft.MachineLearningServices/workspaces/computes@2022-06-01-preview' = {
  name: '${mlworkspace.name}/cpu-compute-cluster'
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
      vmSize: 'DSv2'
      osType: 'Linux'
      scaleSettings: {
        minNodeCount: 0
        maxNodeCount: 5
      }
    }
  }
}

resource jax_online_endpoint 'Microsoft.MachineLearningServices/workspaces/onlineEndpoints@2022-06-01-preview' = {
  name: 'alphabrain-math-endpoint'
  location: location
  parent: mlworkspace
  properties: {
    authMode: 'AMLToken'
  }
}
